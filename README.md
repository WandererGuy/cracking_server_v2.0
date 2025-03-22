# Usage
change to ip of the host in src/app/config.ini


# to setup (for me)
```
git clone https://github.com/WandererGuy/cracking_server_v1.0.git
pip install fastapi uvicorn pydantic python-multipart tqdm openpyxl pandas psutil requests unidecode

copy hashcat folder 
copy wordlist_samples folder 
```
## 2 WAYS:
use START.bat

### ALTERNATIVELY, 
```bash
conda activate ...
python src/app/main.py
```
in another terminal
```bash
conda activate ...
python src/app/main_status.py
```
in another terminal
```bash
conda activate ...
python src/app/main_update.py
```
in another terminal
```bash
conda activate ...
python src/app/main_backend.py
```
# if add more file type support ot  hash type support , remember to add more in
remember : support file type is different to support hash type , support hash type can be more than support file type , like MD5

--- in src\app\routers\config.py
fix all value
<!-- --- in src\app\routers\extract_hash.py -->
<!-- hashcat_hash_code_dict -->
<!-- find_hash() -->

<!-- --- in src\app\utils\common.py -->
<!-- ls
support_file_type -->
<!-- gen_extract_command() -->

<!-- --- in src\app\routers\backend\crack_file_lock_hash.py
supprort_file_type -->

<!-- --- in src\app\utils\backend\validate_hashfile.py -->
<!-- support_hash_type -->
<!-- hash_type_to_hashcat_hash_code_dict -->
# Full Setup Script for Environment

This document provides detailed instructions to set up the environment for your project, including installation of necessary tools, creating virtual environments, and setting up specific software for different operating systems.<br>
Aside the code, hashcat, jtr, hydra have to be built from source code of their github repo<br>
though i already have 3 folder name : jtr, hashcat, hydra , it is still recommended u replace 3 folders <br>
with your own build/compile one to match your system config, path (instruction down below)<br>
My system is window 11
## I. For Kali (Note: Not in use anymore)

### 1. Install VSCode

Follow these steps to install Visual Studio Code:

1. **Download the DEB package** for VSCode from the [official site](https://code.visualstudio.com/Download) or use the guide:
    - [Install DEB files on Ubuntu](https://phoenixnap.com/kb/install-deb-files-ubuntu)

2. **Install VSCode** by running the following command:
    ```bash
    sudo dpkg -i <package_path>
    ```
3. **install venv**
Install venv <br>
https://gist.github.com/Geoyi/d9fab4f609e9f75941946be45000632b

### 2. Install Virtual Environment (venv)

Follow the guide to install and set up the virtual environment:

1. **Update system packages:**
    ```bash
    sudo apt update -y
    ```

2. **Install Python 3:**
    ```bash
    sudo apt install python3 -y
    ```

3. **Navigate to your project folder:**
    ```bash
    cd /home/manh264/Desktop/kali_api
    ```

4. **Create a virtual environment:**
    ```bash
    python3 -m venv env
    ```

5. **Activate the virtual environment:**
    ```bash
    source env/bin/activate
    ```

6. **Install necessary Python packages:**
    ```bash
    pip install fastapi uvicorn pydantic python-multipart tqdm pandas openpyxl
    ```

---

## II. For Windows

### 1. Install Conda

1. **Install Conda** (if not already installed). If you don't have Conda, [download and install Anaconda](https://www.anaconda.com/products/individual).

2. **Create a Conda environment**:
    ```bash
    conda create --name <env_name> python==3.10
    conda activate <env_name>
    ```

### 2. Install necessary packages

Install the required Python packages in your Conda environment:
```bash
pip install fastapi uvicorn pydantic python-multipart tqdm openpyxl pandas pyyaml

```
# III. For Windows: Build from Source with Cygwin

## 1. Install Cygwin (favor for jtr)

To install Cygwin, follow one of these guides:<br>

notice that: 
Cygwin maps Windows drives under /cygdrive/, thats how u can access window file in cygwin<br>

first install cygwin <br>
can download like online vid <br>
https://www.youtube.com/watch?v=J3XQbrJ2GeU<br>


or like jtr set up is also ok <br>
https://github.com/openwall/john/blob/bleeding-jumbo/doc/INSTALL<br>


after that :<br>
tackle issue of ssl<br>
For ssl <br>
In folder download setup-x86_64.exe for cygwin , open terminal  <br>
```bash
setup-x86_64.exe -q -P openssl-devel
setup-x86_64.exe -q -P openssl
setup-x86_64.exe -q -P libssl-dev -P libssl-devel
```

## 2. HEADS UP NOTICE
HEADS UP NOTICE: to build/compile jtr + hydra from source with cygwin :<br>
1. in cygwin terminal do : 
```bash 
./configure 
```
Inside the folder, do a ./configure This will check all your environment variables, paths, etc and create a 'make' file. <br>
2. Then in cygwin terminal do : 
```bash 
make
```
 That should compile a binary. <br>
3. Then in cygwin terminal do : 
```bash 
make install
```
make install Will essentially copy the main program elements into the proper<br>
places to run the app.. However, this does not take into account dependencies... (Which is what apt-get, dpkg, emerge take care of...)<br>
4. then the .exe file will appear in folder, which is done, now u can call hydra inside hydra folder <br>

## 3. Do it your self with jtr, hydra
first git clone 2 repo then compile for each of them <br>
<br>
-------- jtr --------<br>
https://github.com/openwall/john/blob/bleeding-jumbo/doc/INSTALL<br>


will have to copy necessary cygwin dll missing into the need folder run hydra or jtr , dll will be noticed by window as missing (dll from folder install cygwin)<br>
Notice: i copy all dll in cygwin folder into the need folder <br>
(tell by window notice when u try to run exe file , by tapping 2 times into exe file u wish to use, terminal wont show us error)<br>
so tap 2 times into exe file john.exe (in /run of john the ripper folder) and hydra.exe <br>


-------- hydra --------<br>
https://github.com/vanhauser-thc/thc-hydra<br>
HOW TO COMPILE<br>

To configure, compile and install hydra, just type: (same as jtr)

```bash 
./configure
make
make install
```

## 4. hash cat
-------- hashcat --------<br>
https://www.msys2.org/docs/updating/<br>
https://github.com/hashcat/hashcat/blob/master/BUILD_MSYS2.md<br>


i remove jtr/run/arch.h (file corrupted somehow) (hopes nothing go wrong)