#!/bin/bash
# C9 Subhalo File Finder
# Searches common locations for TNG data files

echo "========================================"
echo "C9 Subhalo File Finder"
echo "========================================"
echo ""

# Common patterns to search for
PATTERNS=(
    "*subhalo*"
    "*tng100*"
    "*merger_tree*"
    "*snapshot99*"
    "*halo*catalog*"
    "*illustris*"
)

# Directories to search
SEARCH_DIRS=(
    "$HOME"
    "$HOME/downloads"
    "$HOME/storage"
    "$HOME/cloud9"
    "$HOME/termux"
    "/sdcard"
    "/sdcard/Download"
    "$HOME/data"
)

echo "Searching for TNG/subhalo files..."
echo ""

found_any=false

for dir in "${SEARCH_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        for pattern in "${PATTERNS[@]}"; do
            results=$(find "$dir" -maxdepth 3 -iname "$pattern" -type f 2>/dev/null)
            if [ -n "$results" ]; then
                echo "[FOUND in $dir]:"
                echo "$results" | while read -r file; do
                    size=$(du -h "$file" 2>/dev/null | cut -f1)
                    echo "  $file ($size)"
                done
                echo ""
                found_any=true
            fi
        done
    fi
done

if [ "$found_any" = false ]; then
    echo "No TNG/subhalo files found in common locations."
    echo ""
    echo "Please check:"
    echo "  1. Google Drive downloads folder"
    echo "  2. termux-storage (run: termux-setup-storage)"
    echo "  3. Any custom download directories"
    echo ""
    echo "Expected files:"
    echo "  - tng100-1_snapshot99_subhalos.csv"
    echo "  - tng100-1_merger_trees.json"
    echo "  - tng_validation_suite.py"
fi

echo ""
echo "========================================"
echo "To copy found files to your repo:"
echo "  mkdir -p ~/cloud9-assembly-2026-0816/subhalo_data"
echo "  cp /path/to/file ~/cloud9-assembly-2026-0816/subhalo_data/"
echo "========================================"
