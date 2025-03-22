from fastapi import FastAPI, HTTPException, Form
import os 
import uvicorn
import logging
from pydantic import BaseModel
import configparser
import subprocess
from pydantic import BaseModel, validator, ValidationError
from utils.common import *
from fastapi.staticfiles import StaticFiles
from routers.hash_crack import router as hash_crack_router
from routers.extract_hash import router as extract_hash_router 
from routers.prince import router as prince_router 
from routers.validate_hashfile import router as validate_hashfile_router
from routers.model import MyHTTPException, my_exception_handler
from utils.common import empty_to_false

from starlette.responses import RedirectResponse

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='fastapi.log', filemode='w')
# logger = logging.getLogger(__name__)

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to config.ini
config_path = os.path.join(script_dir, 'config.ini')

# Read the config file
config = configparser.ConfigParser()
config.read(config_path)

host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 
production = config['DEFAULT']['production']
num_workers = int(config['DEFAULT']['num_workers'])
script_name = 'main'
app = FastAPI()
app.include_router(hash_crack_router)
app.include_router(extract_hash_router)
app.include_router(prince_router)
app.include_router(validate_hashfile_router)
app.add_exception_handler(MyHTTPException, my_exception_handler)


static_path = os.path.join(script_dir, 'static')
os.makedirs(static_path, exist_ok=True)
os.makedirs("wordlist_samples", exist_ok=True)
os.makedirs(os.path.join(static_path, "cracked_hash"), exist_ok=True)
os.makedirs(os.path.join(static_path, "extract_hash_results"), exist_ok=True)
os.makedirs(os.path.join(static_path, "potfiles"), exist_ok=True)
os.makedirs(os.path.join(static_path, "prince_wordlist"), exist_ok=True)
os.makedirs(os.path.join(static_path, "prince_wordlist_output"), exist_ok=True)
os.makedirs(os.path.join(static_path, "backend","cracked_hash"), exist_ok=True)
os.makedirs(os.path.join(static_path, "backend","remaining_hash"), exist_ok=True)
os.makedirs(os.path.join(static_path,"backend",'hashcat_hash_code'), exist_ok=True)
os.makedirs(os.path.join(static_path,'backend','hash_dump'), exist_ok=True)
os.makedirs(os.path.join(static_path,'session'), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    """
    # Redirect
    to documentation (`/docs/`).
    """
    return RedirectResponse(url="/docs/")


def main():
    print ('INITIALIZING FASTAPI SERVER')
    if empty_to_false(production) == False: 
        uvicorn.run(f"{script_name}:app", host=host_ip, port=int(port_num), reload=True, workers=num_workers)
    else: uvicorn.run(f"{script_name}:app", host=host_ip, port=int(port_num), reload=False, workers=num_workers)



if __name__ == "__main__":
    main()
