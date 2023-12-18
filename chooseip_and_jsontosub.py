import json
import base64
import csv
import subprocess
import os

# 每天  3:00 执行 chooseip_and_jsontosub.py 先IP优选 再将优选IP写入 json文件 并将 json文件 转为 订阅文件，最后提交github
# 0 3 * * * cd /Users/mac/my_cfip_vless && /Users/mac/anaconda3/bin/python chooseip_and_jsontosub.py

# 执行 CloudflareST 进行IP优选
subprocess.run(["/usr/bin/sudo", "./CloudflareST", "-tl", "200", "-sl", "9"], check=True)

# 获取当前工作路径
current_dir = os.getcwd()

# csv文件路径
csv_path = os.path.join(current_dir,"result.csv")

# 打开CSV文件并读取IP地址
with open(csv_path, 'r') as f:
    reader = csv.reader(f)
    next(reader)  # 跳过表头
    ip_addresses = [row[0] for _, row in zip(range(10), reader)]  # 获取前10个IP地址

# json文件的路径
json_path = os.path.join(current_dir,"my_cfip_with_rules.json")

# 打开JSON文件并加载数据
with open(json_path, 'r') as f:
    data = json.load(f)

# 在数据中更新服务器地址
ip_index = 0
for outbound in data['outbounds']:
    if 'server' in outbound and ip_index < len(ip_addresses):
        outbound['server'] = ip_addresses[ip_index]
        ip_index += 1

# 将更新后的数据写回JSON文件
with open(json_path, 'w') as f:
    json.dump(data, f, indent=4)
# 更新完json


# 开始将json转订阅链接
# Load the data from the JSON file
with open(json_path) as f:
    data = json.load(f)

# Extract the vless nodes
vless_nodes = [node for node in data['outbounds'] if node['type'] == 'vless']

# Generate the links for each node
links = []
for node in vless_nodes:
    i = 1
    link = f"vless://{node['uuid']}@{node['server']}:{node['server_port']}?encryption=none&sni=icon.mark-jones-w.workers.dev&fp=randomized&type=ws&host=icon.mark-jones-w.workers.dev&path=%2F%3Fed%3D2048#icon.EdsonWong.dev{i}"
    i += 1
    links.append(link)

# Convert the links to a Shadowrocket subscription link
links_str = '\n'.join(links)
links_base64 = base64.b64encode(links_str.encode()).decode()

# submission path
sub_path = os.path.join(current_dir,"cfipsub.txt")

# Write the base64 links to the subscribe file
with open(sub_path, 'w') as f:
    f.write(links_base64)

# Add specific files to staging area
# subprocess.run(["git", "add", "cfipsub.txt", "my_cfip_with_rules.json"], check=True)
subprocess.run(["git", "add", "."], check=True)

# Commit changes
subprocess.run(["git", "commit", "-m", "mbp2015"], check=True)

# Force push to the 'sb' branch
subprocess.run(["git", "push", "-f", "origin", "mbp2015"], check=True)
