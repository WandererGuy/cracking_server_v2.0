from fastapi import FastAPI, HTTPException, Form
# Read the config file
import configparser
import uvicorn
import os 
from routers.model import reply_bad_request, reply_success, reply_server_error
from fastapi.staticfiles import StaticFiles
from utils.common import empty_to_false
from routers.model import MyHTTPException, my_exception_handler
import requests 
import asyncio
import uuid 
from utils.common import fix_path
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir,'static')
hashcat_hash_code_folder = os.path.join(static_path,'backend','hashcat_hash_code')
hash_dump_folder = os.path.join(static_path,'backend','hash_dump')

hashcat_temp_output = os.path.join(static_path,'hashcat_temp_output.txt')
backend_temp_output = os.path.join(static_path,'backend_temp_output.txt')
backend_temp_step = os.path.join(static_path,'backend_temp_step.txt')

config = configparser.ConfigParser()
config_path = os.path.join(current_dir, 'config.ini')
config.read(config_path)

host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port_update'] 
production = config['DEFAULT']['production']

from contextlib import asynccontextmanager
from routers.extract_hash import find_hashcat_hash_code


def write_backend_status(content):
    with open(backend_temp_output, 'w', encoding='utf-8') as f:
        if 'generating' in content.lower() or 'validating' in content.lower():
            f.write(content)
        else: 
            f.write(content)
            f.write('\n')
            with open(hashcat_temp_output, 'r', encoding='utf-8') as f_hc:
                progress = f_hc.read() 
            with open(hashcat_temp_output, 'r', encoding='utf-8') as f_hc:
                lines = f_hc.readlines()
                for line in lines:
                    if 'progress' in line.lower():
                        progress_line = line
                        f.write(progress_line)
                        f.write('\n')
                    if 'speed' in line.lower():
                        speed_line = line
                        f.write(speed_line)
                f.write('\n\n')
                f.write(progress)
async def periodic_request():
    while True:
        try:
            with open(backend_temp_step, 'r') as f:
                content = f.read()
            write_backend_status(content)
            print('update backend status')
        except Exception as e:
            print(f"An error occurred: {e}")
        await asyncio.sleep(5)  # Wait for 5 seconds before the next request

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(periodic_request()) # start up action 
    print("Started periodic HTTP requests every 5 seconds.")
    yield
    pass # shutdown action 

script_name = 'main_update'
app = FastAPI(lifespan=lifespan)

def main():
    print ('INITIALIZING FASTAPI SERVER')
    if empty_to_false(production) == False: 
        uvicorn.run(f"{script_name}:app", host=host_ip, port=int(port_num), reload=True)
    else: uvicorn.run(f"{script_name}:app", host=host_ip, port=int(port_num), reload=False)

if __name__ == "__main__":
    main()