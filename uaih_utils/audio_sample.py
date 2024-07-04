import os
import random
import shutil

def copy_random_files(src_dir, dst_dir, ratio):
    # 确保目标文件夹存在
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    # 获取源文件夹中的所有文件
    all_files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]

    # 计算需要复制的文件数量
    num_files_to_copy = int(len(all_files) * ratio)

    # 随机选择文件
    files_to_copy = random.sample(all_files, num_files_to_copy)

    # 复制文件到目标文件夹
    for file in files_to_copy:
        shutil.copy(os.path.join(src_dir, file), os.path.join(dst_dir, file))

    print(f"已复制 {num_files_to_copy} 个文件到 {dst_dir}")

# 示例使用
src_directory = 'dataset/mp3_full'  # 源文件夹路径
dst_directory = 'dataset/mp3_sample'  # 目标文件夹路径
copy_ratio = 0.02  # 复制比例，20%

copy_random_files(src_directory, dst_directory, copy_ratio)
