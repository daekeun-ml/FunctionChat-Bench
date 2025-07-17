import os
import json
import pandas as pd
import re
from tqdm import tqdm
from dotenv import load_dotenv
"""
This is a package that collects commonly used basic utilities.
"""

# .env 파일 로드
load_dotenv()

def get_env_var(key, default=None):
    """
    환경 변수를 가져옵니다. 환경 변수가 없는 경우 기본값을 반환합니다.
    
    Parameters:
        key (str): 환경 변수 키
        default: 환경 변수가 없는 경우 반환할 기본값
        
    Returns:
        환경 변수 값 또는 기본값
    """
    return os.environ.get(key, default)


def substitute_env_vars(text):
    """
    텍스트에서 ${VAR_NAME} 형태의 환경변수 플레이스홀더를 실제 환경변수 값으로 치환합니다.
    
    Parameters:
        text (str): 치환할 텍스트
        
    Returns:
        str: 환경변수가 치환된 텍스트
    """
    def replace_var(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))  # 환경변수가 없으면 원본 유지
    
    return re.sub(r'\$\{([^}]+)\}', replace_var, text)


def load_config_with_env_vars(config_path):
    """
    설정 파일을 로드하고 환경변수를 치환합니다.
    
    Parameters:
        config_path (str): 설정 파일 경로
        
    Returns:
        dict: 환경변수가 치환된 설정 딕셔너리
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config_text = f.read()
    
    # 환경변수 치환
    config_text = substitute_env_vars(config_text)
    
    # JSON 파싱
    return json.loads(config_text)


def is_exist_file(file_path):
    if os.path.exists(file_path):
        if os.path.getsize(file_path) == 0:
            os.remove(file_path)
            return False
        else:
            return True
    return False


def delete_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
    except PermissionError:
        print(f"Permission denied: cannot delete {file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"Failed to create directory {path}: {e}")


def load_to_tsv(file_name):
    df = pd.read_csv(file_name, delimiter='\t', lineterminator='\n')
    return [item for idx, item in df.iterrows()]


def load_to_json(file_name):
    datas = None
    with open(file_name, 'r') as ff:
        try:
            datas = json.loads(ff.read())
        except Exception as e:
            print(file_name)
            print("[Exception]", e)
            raise e
    return datas


def load_to_jsonl(input_file_path):
    output = []
    with open(input_file_path) as f:
        for line in tqdm(f.readlines()):
            try:
                output.append(json.loads(line))
            except Exception as e:
                print(line)
                print("[Exception]", e)
                raise e
    return output


def save_to_jsonl(data, filename):
    if isinstance(data, list):
        with open(filename, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    else:
        raise Exception(f"save_to_jsonl error : data type is invalid. ({type(data)})")


def get_output_filename(source_file):
    if '/' in source_file:
        filepath, filename = source_file.rsplit('/', 1)
    else:
        filepath, filename = '.', source_file
    filename_prefix = filename.rsplit('.', 1)[0]
    return f"{filepath}/{filename_prefix}.convert.jsonl"


def save_cache(data, cache_path):
    with open(cache_path, 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False))
    return cache_path


def load_cache(cache_path):
    with open(cache_path, 'r') as f:
        return json.loads(f.read())


def create_directory_if_not_exists(directory_path):
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Directory '{directory_path}' created successfully or already exists.")
    except Exception as e:
        print(f"Failed to create directory '{directory_path}'. Error: {e}")
