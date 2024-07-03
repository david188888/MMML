# 删除data下面重名的音频文件，只保留wav格式的音频文件

import os
import librosa


for file in os.listdir('data'):
    file_path = os.path.join('data', file)
    if not os.path.isfile(file_path):
        continue # 忽略非文件项
    
    file_name, file_extension = os.path.splitext(file)
    
    # 定义输出文件的路径为.wav格式
    target_file = os.path.join('data', f"{file_name}.wav")
    
    # 如果文件已是.wav格式，直接添加到列表
    if file_extension.lower() == '.wav':
        continue
    else: # 否则，删除mp3重名文件
        os.remove(file_path)
        print(f"删除文件{file_path}")
        
print("删除完成")

