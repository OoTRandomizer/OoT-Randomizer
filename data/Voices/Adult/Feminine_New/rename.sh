#!/bin/bash

# Loop through each file in the current directory
for file in *; do
    if [[ -f "$file" ]]; then
        # Extract the part of the filename before the first occurrence of ".aiff"
        # Rename the file
        mv "$file" "$file.aifc"
        echo "Renamed: $file"
    fi
done
