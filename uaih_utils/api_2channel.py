import base64
import hashlib
from tqdm import tqdm
import hmac
import json
import os
import time
import requests
import sqlite3
import urllib
import librosa
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
api_upload = '/upload'
api_get_result = '/getResult'
conn = sqlite3.connect('asr_status.db')
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS asr (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appId TEXT,
        signa TEXT,
        ts INTEGER,
        fileSize INTEGER,
        fileName TEXT,
        duration TEXT,
        orderId TEXT,
        text TEXT
    )
''')

def insert_into_table(data_dict, table_name='asr', db_file='asr_status.db'):
    try:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        columns = ', '.join(data_dict.keys())
        placeholders = ', '.join('?' * len(data_dict))
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'

        cur.execute(sql, tuple(data_dict.values()))

        conn.commit()
        print(f"Inserted data into {table_name} successfully.")

    except sqlite3.Error as e:
        print(f"Error inserting data into {table_name}: {e}")

    finally:
        if conn:
            conn.close()

from pydub import AudioSegment
from pydub.silence import split_on_silence

def process_audio_segment(file_path, silence_thresh, min_silence_len, keep_silence):
    audio_segment = AudioSegment.from_wav(file_path)
    chunks = split_on_silence(audio_segment, 
                              min_silence_len=min_silence_len, 
                              silence_thresh=silence_thresh, 
                              keep_silence=keep_silence)
    combined_chunk = AudioSegment.empty()
    for chunk in tqdm(chunks):
        combined_chunk += chunk
    return combined_chunk

def remove_silence_and_save(audio_files, output_dir, file_prefix, silence_thresh=-40, min_silence_len=1000, keep_silence=200, max_workers=64):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    def process_and_save(file_path):
        processed_audio = process_audio_segment(file_path, silence_thresh, min_silence_len, keep_silence)
        output_file_path = os.path.join(output_dir, f"{file_prefix}_{os.path.basename(file_path)}")
        processed_audio.export(output_file_path, format="wav")
        return output_file_path

    processed_files = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for file_path in tqdm(audio_files):
            future = executor.submit(process_and_save, file_path)
            processed_files.append(future.result())
    return processed_files

class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()

    def get_signa(self):
        m2 = hashlib.md5()
        m2.update((self.appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        signa = hmac.new(self.secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return signa

    def upload(self):
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {
            'appId': self.appid,
            'signa': self.signa,
            'ts': self.ts,
            "fileSize": file_len,
            "fileName": file_name,
            "duration": "200"
        }
        data = open(upload_file_path, 'rb').read(file_len)

        response = requests.post(url=lfasr_host + api_upload + "?" + urllib.parse.urlencode(param_dict),
                                 headers={"Content-type": "application/json"}, data=data)
        result = json.loads(response.text)
        return result, param_dict

    def get_result(self):
        uploadresp, previous_dict = self.upload()
        if uploadresp['code'] == '26625':
            raise TimeoutError
        
        orderId = uploadresp['content']['orderId']
        param_dict = {
            'appId': self.appid,
            'signa': self.signa,
            'ts': self.ts,
            'orderId': orderId,
            'resultType': "transfer,predict"
        }

        status = 3
        while status == 3:
            response = requests.post(url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                                     headers={"Content-type": "application/json"})
            result = json.loads(response.text)
            status = result['content']['orderInfo']['status']
            print("status=", status)
            if status == 4:
                break
            time.sleep(5)
        data = result['content']['orderResult']
        all_text = []
        data = json.loads(data)
        lattice = data.get('lattice') if data.get('lattice') else []
        for i in lattice:
            json_1best = json.loads(i.get('json_1best'))
            for i in json_1best['st']['rt']:
                for j in i['ws']:
                    all_text.append(j['cw'][0]['w'])
        all_text = ''.join(all_text)
        return all_text

def convert_to_wav(source_file, target_file):
    data, sr = librosa.load(source_file, sr=None)
    sf.write(target_file, data, sr)
    return True

def collect_and_convert_audios(folder_path):
    wav_files = []
    for file in tqdm(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, file)
        if not os.path.isfile(file_path):
            continue
        file_name, file_extension = os.path.splitext(file)
        target_file = os.path.join(folder_path, f"{file_name}.wav")
        if file_extension.lower() == '.wav':
            wav_files.append(file_path)
        else:
            conversion_success = convert_to_wav(file_path, target_file)
            if conversion_success:
                wav_files.append(target_file)
            else:
                print(f"警告：文件{file}转换失败，未添加至列表。")
    return wav_files

def remove_mp3_files(folder_path):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if not os.path.isfile(file_path):
            continue
        file_name, file_extension = os.path.splitext(file)
        if file_extension.lower() != '.wav':
            os.remove(file_path)

def main(folder_path, output_dir, file_prefix, sample_size=None):
    wav_files_pre = collect_and_convert_audios(folder_path)
    processed_files = remove_silence_and_save(wav_files_pre, output_dir, file_prefix)

    if sample_size is not None:
        processed_files = random.sample(processed_files, min(sample_size, len(processed_files)))

    with open('Output-cn-7.4.txt', 'a+', encoding='utf-8') as f, ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(RequestApi(appid="6ec56b9d",
                                              secret_key="41c5959915dc37c7f35a309c66b047d8",
                                              upload_file_path=i).get_result): i for i in processed_files}
        for future in tqdm(as_completed(futures)):
            i = futures[future]
            try:
                time.sleep(0.3)
                result1 = future.result()
                f.write(f"The {i} file has been transcribed as follows:\n{result1}\n\n")
                print(result1)
            except TimeoutError as e:
                print(f'failed when upload {i}')
                break
            except Exception as e:
                print(f"Error processing file {i}: {e}")

    with open('Output.json', 'a', encoding='utf-8') as op:
        json_results = {i: future.result() for future, i in futures.items()}
        json.dump(json_results, op, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    folder_path = 'dataset/mp3_seped_L'
    output_dir = 'processed_audio'
    file_prefix = 'processed'
    
    # 设置sample_size为你想要的样本数量，或者将其设为None以处理所有文件
    sample_size = 10  # 将其设为None以处理所有文件
    
    main(folder_path, output_dir, file_prefix, sample_size)
