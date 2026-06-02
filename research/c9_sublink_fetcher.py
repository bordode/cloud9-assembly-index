#!/usr/bin/env python3
"""
TNG100-1 Sublink Batch Fetcher with Resume & Error Recovery
=============================================================

Cloud-9 Assembly Index (A_c) v2.1.2 â Merger Tree Ingestion Pipeline

Fetches sublink merger-tree metadata for IllustrisTNG100-1 halos,
computes C_time temporal complexity, and persists progress across
interruptions. Designed for polite API usage with exponential backoff.

Usage:
    python c9_sublink_fetcher.py --halo-list halo_ids.txt --output ac_results.csv
    python c9_sublink_fetcher.py --resume  # picks up from checkpoint.json
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = "https://www.tng-project.org/api/"
SIMULATION = "TNG100-1"
SNAPSHOT = 99  # z=0
CHECKPOINT_FILE = "c9_sublink_checkpoint.json"
LOG_FILE = "c9_sublink_fetcher.log"

# Rate limiting: be polite to the TNG public API
DEFAULT_BATCH_SIZE = 10
DEFAULT_DELAY_SECONDS = 2.0
MAX_RETRIES = 5
BACKOFF_BASE = 2.0  # seconds
REQUEST_TIMEOUT = 30  # seconds

# C_time normalization bounds (TNG100-1 typical range)
Z_FORM_MIN = 0.5
Z_FORM_MAX = 5.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("c9_sublink")


# ---------------------------------------------------------------------------
# HTTP Session with Retry Logic
# ---------------------------------------------------------------------------
def create_session() -> requests.Session:
    """Create a requests session with retry adapter and timeouts."""
    session = requests.Session()
    # Mount adapter for both http and https with retries
    adapter = HTTPAdapter(
        max_retries=requests.packages.urllib3.util.retry.Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_BASE,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "User-Agent": "Cloud9-Ac-Research/2.1.2 (Academic Data Ingestion; contact: user@institution.edu)"
    })
    return session


# ---------------------------------------------------------------------------
# Single Halo Fetch
# ---------------------------------------------------------------------------
def fetch_halo_sublink(
    session: requests.Session,
    halo_id: int,
    base_url: str = BASE_URL,
    simulation: str = SIMULATION,
    snapshot: int = SNAPSHOT,
) -> Optional[Dict]:
    """
    Fetch sublink merger-tree data for a single halo.

    Returns dict with keys:
        - halo_id
        - n_mergers_major
        - n_mergers_minor
        - formation_redshift
        - merger_redshifts (list)
        - fetch_success (bool)
        - error (str or None)
    """
    url = f"{base_url}{simulation}/snapshots/{snapshot}/subhalos/{halo_id}/sublink/"

    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        # Extract relevant fields with safe defaults
        sublink = data.get("sublink", data)  # handle nested or flat structure

        # Formation redshift: often in 'snapnum' or direct 'z' fields
        # TNG API structure varies; inspect common paths
        z_form = _extract_formation_redshift(sublink)

        # Merger counts: count entries with desc_id or mass_ratio changes
        n_major, n_minor, merger_zs = _extract_mergers(sublink)

        return {
            "halo_id": halo_id,
            "n_mergers_major": n_major,
            "n_mergers_minor": n_minor,
            "formation_redshift": z_form,
            "merger_redshifts": merger_zs,
            "fetch_success": True,
            "error": None,
        }

    except requests.exceptions.RequestException as e:
        logger.warning(f"Halo {halo_id}: network error â {type(e).__name__}: {e}")
        return _failed_record(halo_id, f"network: {e}")
    except (KeyError, ValueError, TypeError) as e:
        logger.warning(f"Halo {halo_id}: parse error â {type(e).__name__}: {e}")
        return _failed_record(halo_id, f"parse: {e}")


def _failed_record(halo_id: int, error_msg: str) -> Dict:
    return {
        "halo_id": halo_id,
        "n_mergers_major": np.nan,
        "n_mergers_minor": np.nan,
        "formation_redshift": np.nan,
        "merger_redshifts": [],
        "fetch_success": False,
        "error": error_msg,
    }


def _extract_formation_redshift(sublink_data) -> Optional[float]:
    """Best-effort extraction of formation redshift from TNG sublink payload."""
    # Try common field names / paths
    if isinstance(sublink_data, dict):
        for key in ["formation_redshift", "z_form", "zform", "redshift_form"]:
            if key in sublink_data and sublink_data[key] is not None:
                return float(sublink_data[key])
        # Try nested tree walk: earliest snapshot -> redshift lookup
        # Simplified: if 'snapnum' exists, map snapnum 99 -> z=0, snapnum 50 -> z~1
        if "snapnum" in sublink_data:
            snap = int(sublink_data["snapnum"])
            # Rough TNG100-1 snapnum-to-z mapping (approximate)
            # Full mapping requires snapshot list; we approximate
            if snap >= 90:
                return 0.5
            elif snap >= 70:
                return 1.0
            elif snap >= 50:
                return 2.0
            else:
                return 3.0
    return np.nan


def _extract_mergers(sublink_data) -> Tuple[int, int, List[float]]:
    """Extract major/minor merger counts and redshifts from sublink tree."""
    n_major = 0
    n_minor = 0
    merger_zs = []

    if not isinstance(sublink_data, dict):
        return n_major, n_minor, merger_zs

    # If API returns a list of progenitor entries
    tree = sublink_data.get("tree", sublink_data.get("progenitors", []))
    if isinstance(tree, list):
        for entry in tree:
            if not isinstance(entry, dict):
                continue
            mass_ratio = entry.get("mass_ratio", entry.get("mpb_mass_ratio", 1.0))
            z = entry.get("redshift", entry.get("z", np.nan))
            if mass_ratio is not None and mass_ratio < 0.3:
                n_major += 1
                if not np.isnan(z):
                    merger_zs.append(float(z))
            elif mass_ratio is not None and mass_ratio < 0.5:
                n_minor += 1

    # Fallback: if no tree, try direct counts
    if n_major == 0 and n_minor == 0:
        n_major = sublink_data.get("n_mergers_major", 0)
        n_minor = sublink_data.get("n_mergers_minor", 0)

    return n_major, n_minor, merger_zs


# ---------------------------------------------------------------------------
# C_time Computation (from v2.1.2 redefinition)
# ---------------------------------------------------------------------------
def compute_c_time(
    sublink_row: Dict,
    snapshot_redshift: float = 0.0,
    z_min: float = Z_FORM_MIN,
    z_max: float = Z_FORM_MAX,
) -> float:
    """
    Compute temporal assembly complexity C_time from sublink record.

    Returns 0.0 if data is missing or invalid.
    """
    z_form = sublink_row.get("formation_redshift")
    if z_form is None or np.isnan(z_form):
        return 0.0

    C_form = (float(z_form) - z_min) / (z_max - z_min)
    C_form = float(np.clip(C_form, 0, 1))

    n_mergers = sublink_row.get("n_mergers_major", 0) or 0
    merger_zs = sublink_row.get("merger_redshifts", [])

    # Recent mergers: last ~2 Gyr at z=0 => z > 0.15
    recent_mergers = sum(1 for z in merger_zs if z > snapshot_redshift + 0.15)

    C_history = float(np.log1p(n_mergers) / np.log1p(20))
    C_recent = float(np.log1p(recent_mergers) / np.log1p(5))

    C_time = 0.6 * C_form + 0.4 * (0.7 * C_history + 0.3 * C_recent)
    return float(np.clip(C_time, 0, 1))


# ---------------------------------------------------------------------------
# Checkpoint / Resume Logic
# ---------------------------------------------------------------------------
def load_checkpoint(path: str = CHECKPOINT_FILE) -> Dict:
    """Load checkpoint; return empty structure if missing."""
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"completed": [], "failed": [], "results": []}


def save_checkpoint(state: Dict, path: str = CHECKPOINT_FILE):
    """Atomic write of checkpoint JSON."""
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, default=str)
    os.replace(tmp, path)
    logger.info(f"Checkpoint saved: {len(state['completed'])} completed, {len(state['failed'])} failed")


def merge_with_existing_df(
    checkpoint: Dict,
    existing_df: Optional[pd.DataFrame] = None,
    ac_fixed_col: str = "A_c_fixed",
) -> pd.DataFrame:
    """Merge checkpoint results into existing dataframe or create new one."""
    records = checkpoint["results"]
    if not records:
        return existing_df.copy() if existing_df is not None else pd.DataFrame()

    new_df = pd.DataFrame(records)
    new_df["C_time"] = new_df.apply(lambda row: compute_c_time(row), axis=1)

    if existing_df is not None and not existing_df.empty:
        df = existing_df.copy()
        # Update rows by halo_id
        for _, row in new_df.iterrows():
            mask = df["halo_id"] == row["halo_id"]
            if mask.any():
                df.loc[mask, "C_time"] = row["C_time"]
                df.loc[mask, "n_mergers_major"] = row["n_mergers_major"]
                df.loc[mask, "formation_redshift"] = row["formation_redshift"]
                df.loc[mask, "fetch_success"] = row["fetch_success"]
            else:
                df = pd.concat([df, row.to_frame().T], ignore_index=True)
        return df
    return new_df


# ---------------------------------------------------------------------------
# Main Batch Orchestrator
# ---------------------------------------------------------------------------
def run_batch_fetch(
    halo_ids: List[int],
    existing_df: Optional[pd.DataFrame] = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    delay: float = DEFAULT_DELAY_SECONDS,
    resume: bool = True,
    output_csv: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch sublink data for all halo_ids with batching, retries, and resume.

    Parameters:
    -----------
    halo_ids : list of int
        Full list of halo IDs to process.
    existing_df : pd.DataFrame or None
        Existing dataframe with A_c_fixed etc. to merge into.
    batch_size : int
        Halos per batch.
    delay : float
        Seconds to sleep between batches.
    resume : bool
        If True, load checkpoint and skip already-completed IDs.
    output_csv : str or None
        If provided, write final dataframe to CSV after each batch.

    Returns:
    --------
    pd.DataFrame with merged results.
    """
    session = create_session()
    checkpoint = load_checkpoint() if resume else {"completed": [], "failed": [], "results": []}

    # Determine remaining work
    completed_set = set(checkpoint["completed"])
    failed_set = set(checkpoint["failed"])
    remaining = [hid for hid in halo_ids if hid not in completed_set]

    total = len(halo_ids)
    n_done = len(completed_set)
    n_rem = len(remaining)

    logger.info(f"Batch fetch starting: {n_done}/{total} already done, {n_rem} remaining")

    if n_rem == 0:
        logger.info("Nothing to do. All halos already processed.")
        return merge_with_existing_df(checkpoint, existing_df)

    # Process in batches
    for i in range(0, n_rem, batch_size):
        batch = remaining[i : i + batch_size]
        logger.info(f"Batch {i//batch_size + 1}: halos {batch}")

        for halo_id in batch:
            record = fetch_halo_sublink(session, halo_id)

            if record["fetch_success"]:
                checkpoint["completed"].append(halo_id)
                checkpoint["results"].append(record)
            else:
                checkpoint["failed"].append(halo_id)
                checkpoint["results"].append(record)

            # Micro-delay between individual requests inside batch
            time.sleep(0.3)

        # Save checkpoint after every batch
        save_checkpoint(checkpoint)

        # Merge and optionally write CSV
        df = merge_with_existing_df(checkpoint, existing_df)
        if output_csv:
            df.to_csv(output_csv, index=False)
            logger.info(f"Intermediate CSV written: {output_csv}")

        # Polite delay between batches
        if i + batch_size < n_rem:
            logger.info(f"Sleeping {delay}s before next batch...")
            time.sleep(delay)

    logger.info(f"Batch fetch complete. Success: {len(checkpoint['completed'])}, Failed: {len(checkpoint['failed'])}")
    return df


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Cloud-9 TNG Sublink Batch Fetcher")
    parser.add_argument("--halo-list", type=str, help="Text file with one halo ID per line")
    parser.add_argument("--existing-csv", type=str, help="Existing CSV with A_c_fixed to merge into")
    parser.add_argument("--output", type=str, default="c9_ac_total_results.csv", help="Output CSV path")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY_SECONDS)
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint.json")
    parser.add_argument("--no-resume", dest="resume", action="store_false", help="Start fresh")
    parser.set_defaults(resume=True)
    return parser.parse_args()


def main():
    args = parse_args()

    # Load halo IDs
    if args.halo_list:
        with open(args.halo_list, "r") as f:
            halo_ids = [int(line.strip()) for line in f if line.strip().isdigit()]
    else:
        # Default: fetch IDs 0-99 if no list provided
        halo_ids = list(range(100))
        logger.info("No --halo-list provided; defaulting to 0-99")

    # Load existing dataframe if provided
    existing_df = None
    if args.existing_csv and os.path.exists(args.existing_csv):
        existing_df = pd.read_csv(args.existing_csv)
        logger.info(f"Loaded existing CSV: {len(existing_df)} rows")

    df = run_batch_fetch(
        halo_ids=halo_ids,
        existing_df=existing_df,
        batch_size=args.batch_size,
        delay=args.delay,
        resume=args.resume,
        output_csv=args.output,
    )

    # Final write
    df.to_csv(args.output, index=False)
    logger.info(f"Final output written: {args.output} ({len(df)} rows)")

    # Summary stats
    if "C_time" in df.columns:
        valid_ctime = df["C_time"].dropna()
        logger.info(f"C_time distribution: mean={valid_ctime.mean():.3f}, std={valid_ctime.std():.3f}")
    if "fetch_success" in df.columns:
        n_ok = df["fetch_success"].sum()
        logger.info(f"Fetch success rate: {n_ok}/{len(df)} ({100*n_ok/len(df):.1f}%)")


if __name__ == "__main__":
    main()
