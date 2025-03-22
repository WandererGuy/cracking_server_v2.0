import subprocess
import os 
def execute_command(command):
    """Execute the given command and return stdout, stderr."""
    
    result = subprocess.run(command,
                            capture_output=True, 
                            cwd="jtr/run",
                            shell=True,
                            text=True, 
                            encoding = 'utf-8')
    return result.stdout, result.stderr


                    


def handle_stderr(stderr):
        zip_err_1 = 'compressed length of AES entry too short'
        zip_err_2 = 'not encrypted, or stored with non-handled compression type'
        if zip_err_1 in stderr or zip_err_2 in stderr:
            detail="Errors: zip file contains file that is empty/ have no data in it or the file is corrupted."
            return detail
        else:
            detail=f"Errors: {stderr}"
            return detail
