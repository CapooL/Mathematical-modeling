# 读取文件
with open('record_1.txt', 'r') as f:
    lines = f.readlines()

# 对每一行的字典进行排序
sorted_lines = []
for line in lines:
    # 使用eval()函数将字符串转换为字典
    d = eval(line)
    # 只保留队员的键值对
    d = {k: v for k, v in d.items() if isinstance(k, str)}
    # 对字典进行排序，并转换回字符串
    sorted_d = str(dict(sorted(d.items())))
    sorted_lines.append(sorted_d)

# 去除重复的行
unique_lines = list(set(sorted_lines))

# 写入新的文件
with open('result.txt', 'w') as f:
    for line in unique_lines:
        f.write(line + '\n')
