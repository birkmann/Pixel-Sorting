#!/bin/bash

# Default number of variations if not provided
VARIATIONS=${1:-10}

echo "--- Starting Pixel Sorting Pipeline ---"
echo "Generating $VARIATIONS variations per image..."

# Step 1: Generate Animations (Input -> Output -> Scaled -> Animated)
python3 animate.py "$VARIATIONS"

if [ $? -ne 0 ]; then
    echo "Error during animation generation."
    exit 1
fi

# Step 2: Finalize (Animated -> Final Merged Loop)
echo "--- Merging Animations into Final Loop ---"
python3 finalize.py

if [ $? -ne 0 ]; then
    echo "Error during finalization."
    exit 1
fi

echo "--- Pipeline Complete! Check the 'final' folder. ---"
