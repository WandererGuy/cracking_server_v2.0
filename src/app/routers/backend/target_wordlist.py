from fastapi import Form, APIRouter
import os 
from utils.common import handle_response
from utils.frontend_validation import is_utf8, target_input_validation, kw_ls_check
from utils.common import empty_to_none
from utils.backend.targuess import targuess_generate
from routers.model import reply_bad_request, reply_success


script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(script_dir))
config_path = os.path.join(parent_dir,'config.ini')

import configparser
config = configparser.ConfigParser()
config.read(config_path)
host_ip = config['DEFAULT']['host'] 
TARGUESS_PORT_NUM = config['DEFAULT']['TARGUESS_PORT_NUM'] 
MAX_MASK_GENERATE_WORDLIST = int(config['DEFAULT']['MAX_MASK_GENERATE_WORDLIST'])  # max mask number to create wordlist
# can only achieve max mask if all information is provided 

TARGUESS_URL_WORDLIST = f"http://{host_ip}:{TARGUESS_PORT_NUM}/generate-target-wordlist/"

router = APIRouter()

@router.post("/only-generate-target-wordlist/")
async def only_generate_target_wordlist(
    full_name: str = Form(None),
    birth: str = Form(None),
    email: str = Form(None),
    account_name: str = Form(None),
    id_num: str = Form(None),
    phone: str = Form(None),
    other_keywords: str = Form(None),
    targuess_train_result_refined_path: str = Form(...),
    ):
    TARGUESS_TRAIN_RESULT_REFINED_PATH = targuess_train_result_refined_path


    target_info = {
        "full_name": full_name,
        "birth": birth,
        "email": email,
        "account_name": account_name,
        "id_num": id_num,
        "phone": phone,
        "other_keywords": other_keywords
    }
    if other_keywords.strip() != '':
        keyword_ls = other_keywords.split(',')
        new_kw_ls = []
        for kw in keyword_ls:
            new_kw_ls.append(kw.replace(' ', ''))
        res, false_kw = kw_ls_check(new_kw_ls)
        if not res:
            return reply_bad_request(f'keyword \'{false_kw}\' must be in same class: all letter, all digit or all special character')

    # standardize input 
    for key, value in target_info.items():
        target_info[key] = empty_to_none(value)
        if target_info[key] != None:
            is_utf8(target_info[key])
    
    target_input_validation(target_info)

    # start working 
    res = targuess_generate(targuess_train_result_refined_path = TARGUESS_TRAIN_RESULT_REFINED_PATH,
                            targuess_url = TARGUESS_URL_WORDLIST, 
                            target_info = target_info, 
                            max_mask_generate = MAX_MASK_GENERATE_WORDLIST)
    return handle_response(res)
