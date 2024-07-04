from pydub import AudioSegment
import os

def split_stereo_to_mono(input_file, Loutput_dir,Routput_dir):
    # 读取音频文件
    audio = AudioSegment.from_file(input_file)
    
    # 获取左右声道
    left_channel = audio.split_to_mono()[0]
    right_channel = audio.split_to_mono()[1]
    
    # 获取文件名和扩展名
    base_name = os.path.basename(input_file)
    name, ext = os.path.splitext(base_name)
    
    # 创建输出文件路径
    left_output_path = os.path.join(Loutput_dir, f"{name}_left{ext}")
    right_output_path = os.path.join(Routput_dir, f"{name}_right{ext}")
    
    # 导出左右声道文件
    left_channel.export(left_output_path, format="mp3")
    right_channel.export(right_output_path, format="mp3")
    
    print(f"Processed {input_file} -> {left_output_path}, {right_output_path}")

# 设置输入和输出目录
input_dir = "dataset/mp3_2chan"
L_output_dir = "dataset/mp3_seped_L"
R_output_dir = "dataset/mp3_seped_R"

# 创建输出目录（如果不存在）
os.makedirs(L_output_dir, exist_ok=True)
os.makedirs(R_output_dir, exist_ok=True)

# 获取所有MP3文件
mp3_files = [f for f in os.listdir(input_dir) if f.endswith(".mp3")]

# 分离每个文件的左右声道
for mp3_file in mp3_files:
    input_path = os.path.join(input_dir, mp3_file)
    split_stereo_to_mono(input_path, L_output_dir,R_output_dir)
