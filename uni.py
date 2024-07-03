import csv

input_file = 'output.csv'
output_file = 'uni_output.csv'

# 用于存储唯一的数据
unique_records = set()

with open(input_file, 'r', encoding='utf-8') as infile:
    lines = infile.readlines()
    
    for line in lines:
        # 分割每行数据为文件名，手机号和文本
        parts = line.strip().split(',')
        if len(parts) == 3:
            filename, phone, text = parts
            
            # 将唯一记录添加到集合中
            unique_records.add((filename, phone, text))

# 将唯一数据写入CSV文件
with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['filename', 'phone', 'text'])
    
    for record in unique_records:
        writer.writerow(record)

print("数据已成功写入 CSV 文件，并去除了重复项")
