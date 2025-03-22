princeprocessor
set up (if need run C++ on Vscode)
set up C++ for VScode
install extension Code Runner + C++ in Vscode download msys2 and run ... add .. to become environment path (like https://code.visualstudio.com/docs/languages/cpp) place libstdc++-6.dll file somewhere in /ucrt folder into C++ run code folder(GUESS/src/) fix path in config/config_setup_cpp.txt (so that can use g++ in C++ session)

For reference: https://code.visualstudio.com/docs/languages/cpp Download msys2 MSYS2 on its website for newest https://www.freecodecamp.org/news/how-to-install-c-and-cpp-compiler-on-windows/ C++ programming with Visual Studio Code

exe error place libstdc++-6.dll file somewhere in /ucrt folder into C++ run code folder(GUESS/src/) https://stackoverflow.com/questions/74734500/cant-find-entry-point-zst28-throw-bad-array-new-lengthv-in-dll-filepath




window set up 
install chocolatey online guide 
install make: 
```bash
choco install make 
```
in prince directory , run :
```bash
make 
```
now can run git bash 
```bash
 ./pp64.bin 
```


Usage  
first run make for c file to create ./pp64.bin -h
guide https://www.youtube.com/watch?v=ghL2WzJQwzY&list=PLz7eHzfof8WUTMtx5SPe4FQQr_raTw9Xg&index=12

cd src 
./pp64.bin -h : for help 

./pp64.bin dataset/wordlist.txt --pw-min=8 --keyspace


give permission for bin file to be executed (if in linux)
chmod +x bin_file_path







==============

Standalone password candidate generator using the PRINCE algorithm

The name PRINCE is used as an acronym and stands for PRobability INfinite Chained Elements, which are the building blocks of the algorithm

Brief description
--------------

The princeprocessor is a password candidate generator and can be thought of as an advanced combinator attack. Rather than taking as input two different wordlists and then outputting all the possible two word combinations though, princeprocessor only has one input wordlist and builds "chains" of combined words. These chains can have 1 to N words from the input wordlist concatenated together. So for example if it is outputting guesses of length four, it could generate them using combinations from the input wordlist such as:

- 4 letter word
- 2 letter word + 2 letter word
- 1 letter word + 3 letter word
- 3 letter word + 1 letter word
- 1 letter word + 1 letter word + 2 letter word
- 1 letter word + 2 letter word + 1 letter word
- 2 letter word + 1 letter word + 1 letter word
- 1 letter word + 1 letter word + 1 letter word + 1 letter word

Detailed description
--------------

I'm going to write a detailed description in case I'm extremely bored. Till that, use the following resources:

- My talk about princeprocessor on Passwords^14 conference in Trondheim, Norway. Slides: https://hashcat.net/events/p14-trondheim/prince-attack.pdf
- Thanks to Matt Weir, he made a nice analysis of princeprocessor. You can find the post on his blog: http://reusablesec.blogspot.de/2014/12/tool-deep-dive-prince.html

Compile
--------------

Simply run make

Binary distribution
--------------

Binaries for Linux, Windows and OSX: https://github.com/jsteube/princeprocessor/releases
