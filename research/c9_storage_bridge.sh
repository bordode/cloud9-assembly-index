#!/bin/bash
# C9 Storage Bridge: Find Android downloads from Termux
# Run this in Termux to locate ALL downloaded files

echo "========================================"
echo "C9 STORAGE BRIDGE"
echo "Finding your downloaded files..."
echo "========================================"
echo ""

# Step 1: Check if termux-setup-storage has been run
if [ -d "$HOME/storage" ]; then
    echo "[OK] termux-setup-storage detected"
    echo ""
else
    echo "[MISSING] Running termux-setup-storage now..."
    echo "  (Grant permission when Android dialog pops up)"
    termux-setup-storage
    echo ""
fi

# Step 2: Search ALL possible Android download locations
echo "--- Searching Android storage ---"
SEARCH_PATHS=(
    "$HOME/storage/shared/Download"
    "$HOME/storage/downloads"
    "$HOME/storage/shared/Documents"
    "/sdcard/Download"
    "/sdcard/Documents"
    "/storage/emulated/0/Download"
    "/storage/emulated/0/Documents"
    "$HOME/downloads"
    "$HOME/Downloads"
    "$HOME"
)

found_count=0
for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo ""
        echo "[$path]:"
        # List C9-related files
        ls -lah "$path" 2>/dev/null | grep -iE "(cloud9|c9_|subhalo|tng|collatz|bridge|tar\.gz|\.py$|\.json$|\.csv$)" || echo "  (no C9 files found)"

        # Count total files
        count=$(ls "$path" 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            found_count=$((found_count + 1))
        fi
    fi
done

echo ""
echo "========================================"
echo "SEARCH SUMMARY"
echo "========================================"

if [ "$found_count" -eq 0 ]; then
    echo "NO files found in standard locations."
    echo ""
    echo "Try these manual checks:"
    echo "  1. Open your Android file manager"
    echo "  2. Go to Downloads or Documents"
    echo "  3. Look for files named:"
    echo "     - cloud9-assembly-2026-0816.tar.gz"
    echo "     - c9_*.py"
    echo "     - C9-COLLECTION-*.json"
    echo "     - subhalo*.csv"
    echo ""
    echo "If found, note the EXACT path and run:"
    echo "  cp /sdcard/Download/FILENAME ~/cloud9-assembly-2026-0816/"
else
    echo "Found files in $found_count location(s)."
    echo ""
    echo "--- QUICK COPY COMMANDS ---"
    echo ""

    # Auto-generate copy commands for common cases
    if [ -d "$HOME/storage/shared/Download" ]; then
        echo "From Android Downloads:"
        echo "  mkdir -p ~/cloud9-assembly-2026-0816/subhalo_data"
        echo "  cp ~/storage/shared/Download/*subhalo* ~/cloud9-assembly-2026-0816/subhalo_data/ 2>/dev/null"
        echo "  cp ~/storage/shared/Download/*tng* ~/cloud9-assembly-2026-0816/subhalo_data/ 2>/dev/null"
        echo "  cp ~/storage/shared/Download/cloud9-assembly*.tar.gz ~/ 2>/dev/null"
        echo ""
    fi

    if [ -d "$HOME/downloads" ]; then
        echo "From Termux downloads:"
        echo "  cp ~/downloads/*subhalo* ~/cloud9-assembly-2026-0816/subhalo_data/ 2>/dev/null"
        echo "  cp ~/downloads/*tng* ~/cloud9-assembly-2026-0816/subhalo_data/ 2>/dev/null"
        echo ""
    fi
fi

echo "========================================"
echo "--- CURRENT C9 REPO STATUS ---"
echo "========================================"
if [ -d "$HOME/cloud9-assembly-2026-0816" ]; then
    echo "Repo exists at: ~/cloud9-assembly-2026-0816"
    echo ""
    echo "Files in repo:"
    find "$HOME/cloud9-assembly-2026-0816" -maxdepth 2 -type f | head -20
    echo ""
    echo "Files in subhalo_data:"
    ls -la "$HOME/cloud9-assembly-2026-0816/subhalo_data/" 2>/dev/null || echo "  (subhalo_data/ is empty or missing)"
else
    echo "Repo NOT found at ~/cloud9-assembly-2026-0816"
    echo "You may need to extract the tarball first:"
    echo "  cd ~"
    echo "  tar -xzf PATH_TO_TARBALL"
fi

echo ""
echo "========================================"
echo "If files are in Android Downloads but not visible:"
echo "  1. Run: termux-setup-storage"
echo "  2. Grant storage permission in Android dialog"
echo "  3. Files will appear at: ~/storage/shared/Download/"
echo "========================================"
