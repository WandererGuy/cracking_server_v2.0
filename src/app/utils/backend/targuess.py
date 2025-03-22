
import requests
def targuess_generate(targuess_train_result_refined_path, 
                      targuess_url, 
                      target_info: dict, 
                      max_mask_generate: int):
    '''
    return 
        {
    "status_code": 200,
    "message": "Result saved successfully",
    "result": {
        "path": "C:/Users/Admin/CODE/work/PASSWORD_CRACK/TarGuess-I-main/static/generated_target_wordlist/1da75da8-fc05-4aa8-8424-486ba44182b0.txt",
        "url": "http://192.168.1.5:4003/static/generated_target_wordlist/1da75da8-fc05-4aa8-8424-486ba44182b0.txt"
    }
}
    '''
    payload = {
    'full_name': target_info['full_name'],
    'birth': target_info['birth'], 
    'email': target_info['email'],
    'account_name': target_info['account_name'],
    'id_num': target_info['id_num'],
    'phone': target_info['phone'],
    'max_mask_generate': max_mask_generate,
    'train_result_refined_path': targuess_train_result_refined_path,
    'other_keywords': target_info['other_keywords']}
    files=[
    ]
    headers = {}
    response = requests.request("POST", targuess_url, headers=headers, data=payload, files=files)
    return response
