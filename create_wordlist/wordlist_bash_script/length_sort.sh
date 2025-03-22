#!/bin/bash

# Parent directory where the word length folders will be created
parent_dir="sorted_words"

# Directory containing the wordlist files
wordlist_dir="wordlists"

# Create the parent directory if it doesn't exist
mkdir -p "$parent_dir"

# Loop through each file in the directory
for wordlist_file in "$wordlist_dir"/*.txt; do
  # Check if the file exists (in case the directory is empty)
  if [[ -f "$wordlist_file" ]]; then
    echo "Processing file: $wordlist_file"
    
    # Read each word from the current wordlist file
    while read -r word; do
      # Get the length of the word
      word_length=${#word}
      
      # Create a folder inside the parent directory for the word length if it doesn't exist
      mkdir -p "$parent_dir/$word_length"
      
      # Append the word to a file inside the corresponding length folder within the parent directory
      echo "$word" >> "$parent_dir/$word_length/words.txt"
    done < "$wordlist_file"
  fi
done
