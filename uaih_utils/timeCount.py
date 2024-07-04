import os
import librosa
from tqdm import tqdm

def get_audio_duration(file_path):
    """
    获取单个音频文件的时长（秒）
    """
    y, sr = librosa.load(file_path, sr=None)
    return librosa.get_duration(y=y, sr=sr)

def get_total_duration(folder_path):
    """
    获取指定文件夹中所有音频文件的总时长（秒）
    """
    total_duration = 0.0
    for file_name in tqdm(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.lower().endswith(('.wav', '.flac', '.aac', '.m4a')):
            total_duration += get_audio_duration(file_path)
    return total_duration

if __name__ == '__main__':
    folder_path = 'dataset/processed_audio'  # 替换为你的文件夹路径
    total_duration = get_total_duration(folder_path)
    print(f"文件夹 {folder_path} 中所有音频文件的总时长为 {total_duration / 3600:.2f} 小时")
