collect wordlist 


small wordlist but efficient (therefore must be real world wordlist)
since some hash have long time hashing 
unique wordlist for no duplication
chunk into 50MB for efficient progress easy load restire and checkpoint 
sort to length to easy load
alphabet order for easier hashcat maybe 


nice command :

sort -u -o dict_sorted_uniqued.txt v1/*
split -b 50M "$file" "${dirname}__${filename}___"

split "/mnt/c/Users/Admin/Downloads/rockyou2021.txt dictionary from kys234 on RaidForums/rockyou2021.txt" -C 268435456 --additional-suffix=.txt

split -b 50M "$file" "${dirname}__${filename}___"
split -b 50M "rockyou2021_002.txt" "rockyou2021_002__" --additional-suffix=.txt