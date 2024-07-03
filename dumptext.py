import csv
import re

input_file = 'Output-cn.txt'
output_file = 'output.csv'

# 正则表达式匹配模式
pattern = re.compile(r'The audio_proc\\(\d+\.wav) file has been transcribed as follows:\n(.*?)\n\n', re.DOTALL)

with open(input_file, 'r', encoding='utf-8') as infile:
    content = infile.read()
    
# 提取文件名和对应的文本
matches = pattern.findall(content)

# 写入CSV文件
with open(output_file, 'a+', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['filename', 'phone', 'text'])
    
    for filename, text in matches:
        phone = filename.split('.')[0]
        writer.writerow([filename, phone, text])

print("数据已成功写入 CSV 文件")
