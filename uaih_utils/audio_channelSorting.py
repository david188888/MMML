from pydub import AudioSegment
import os
import shutil
from tqdm import tqdm

def check_audio_channels(file_path):
    audio = AudioSegment.from_file(file_path)
    channels = audio.channels
    if channels == 1:
        return True
    elif channels == 2:
        return False
    else:
        return False


dst_dir1 = 'dataset/mp3_1chan'
dst_dir2 = 'dataset/mp3_2chan'


if not os.path.exists(dst_dir1):
        os.makedirs(dst_dir1)

if not os.path.exists(dst_dir2):
        os.makedirs(dst_dir2)

src_dir = 'dataset/mp3_full'

all_files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]

chan1 = []
chan2 = []

for f in tqdm(all_files):
    if check_audio_channels(os.path.join(src_dir,f)):
        
    # if check_audio_channels('dataset/mp3_full/13005111442.mp3'):
        chan1.append(f)
    else:
        chan2.append(f)
print("Copying...1Channel")
for file in tqdm(chan1):
        shutil.copy(os.path.join(src_dir, file), os.path.join(dst_dir1, file))
print("Copying...2Channels")
for file in tqdm(chan2):
        shutil.copy(os.path.join(src_dir, file), os.path.join(dst_dir2, file))