#!/bin/bash

# # Specify the directory containing the files
# directory="/mnt/c/Users/Admin/CODE/work/PASSWORD_CRACK/PASSCRACK_MATERIAL/WORDLISTS/ALL_wordlists/rockyou_2021/rockyou_2021_v1"
# cd "$directory"

# # Loop through all files in the directory
# for file in "$directory"/*; do
#   # Check if it's a regular file
#   if [[ -f "$file" && "$file" == *.txt ]]; then
#     # Get the filename without the path
#     filename=$(basename "$file")
    
#     # Use the split command with the filename as the prefix
#     split -b 50M "$file" "${dirname}__{filename}___"
    
#     echo "Split $file into smaller parts"
#   fi
# done

# Specify the directory containing the files
directory="/mnt/c/Users/Admin/CODE/work/PASSWORD_CRACK/PASSCRACK_MATERIAL/WORDLISTS/ALL_wordlists/002"
cd "$directory"

# Loop through all files in the directory
for file in "$directory"/*; do
  # Check if it's a regular file
  if [[ -f "$file" && "$file" == *.txt ]]; then
    # Get the filename without the path
    dirname=$(dirname "$file")
    filename=$(basename "$file" .txt)

    # Use the split command with the directory and filename as the prefix
    split -b 50M "$file" "${dirname}__${filename}___" --additional-suffix=.txt
    
    echo "Split $file into smaller parts"
  fi
done

