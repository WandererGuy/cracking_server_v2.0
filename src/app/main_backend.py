from fastapi import FastAPI, HTTPException, Form
from fastapi.staticfiles import StaticFiles
import configparser
import uvicorn
import os 
import sys
import uuid
import requests
from utils.common import fix_path
from routers.model import reply_bad_request, reply_success, reply_server_error
from routers.model import MyHTTPException, my_exception_handler
from utils.common import empty_to_none, empty_to_false

from routers.backend.crack_only_hash import router as crack_only_hash_router
from routers.backend.target_wordlist import router as generate_target_wordlist_router
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir,'static')
config = configparser.ConfigParser()
config_path = os.path.join(current_dir, 'config.ini')
config.read(config_path)
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['PORT_BACKEND'] 
production = config['DEFAULT']['production']
num_workers = int(config['DEFAULT']['num_workers'])

script_name = 'main_backend'
app = FastAPI()
app.mount("/static", StaticFiles(directory=static_path), name="static")
app.add_exception_handler(MyHTTPException, my_exception_handler)

app.include_router(crack_only_hash_router)
app.include_router(generate_target_wordlist_router)
    
def main():
    print ('INITIALIZING FASTAPI SERVER')
    if empty_to_false(production) == False: 
        uvicorn.run(f"{script_name}:app", host=host_ip, port=int(port_num), reload=True, workers=num_workers)
    else: uvicorn.run(f"{script_name}:app", host=host_ip, port=int(port_num), reload=False, workers=num_workers)


if __name__ == "__main__":
    main()
    