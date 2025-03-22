from fastapi import Form, APIRouter
import os 
import configparser
import subprocess
from utils.validate_hashfile import hashfile_validate
from routers.model import reply_bad_request, reply_success, reply_server_error

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
config_path = os.path.join(parent_dir,'config.ini')


router = APIRouter()
@router.post("/validate-hashfile/")
async def validate_hashfile_function(  
    hash_file: str = Form(...),
    hashcat_hash_code: str = Form(...),
    hash_dump_folder: str = Form(...),
                    ):
    valid, message = hashfile_validate(hash_file, hashcat_hash_code, hash_dump_folder)
    return reply_success(message = message, result = valid)