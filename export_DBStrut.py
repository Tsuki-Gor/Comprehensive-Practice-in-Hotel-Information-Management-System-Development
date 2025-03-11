import subprocess
import os

# 数据库连接配置
user = 'root'
password = 'Tsuki'
database = 'dbdesign'

# 指定输出目录（确保该目录存在）
output_dir = "C:/Users/mircocrift/Desktop/mysql_backup"  # 例如：Windows 目录
# output_dir = "/home/user/mysql_backup"  # 例如：Linux 目录

# 确保目录存在
os.makedirs(output_dir, exist_ok=True)

# 生成完整的文件路径
structure_file = os.path.join(output_dir, "data.sql")
sample_file = os.path.join(output_dir, "sample_data.sql")
final_file = os.path.join(output_dir, "final_dump.sql")

# 1. 导出表结构（不包含数据）
cmd_structure = f'mysqldump -u {user} -p{password} --no-data {database} > "{structure_file}"'

# 2. 导出每个表的前两条数据
cmd_sample = f'mysqldump -u {user} -p{password} --no-create-info --where="1 LIMIT 2" {database} > "{sample_file}"'

# 执行命令
print("正在导出表结构...")
result_structure = subprocess.run(cmd_structure, shell=True)
if result_structure.returncode != 0:
    print("导出表结构时出错，请检查命令或配置！")
    exit(1)

print("正在导出示例数据...")
result_sample = subprocess.run(cmd_sample, shell=True)
if result_sample.returncode != 0:
    print("导出示例数据时出错，请检查命令或配置！")
    exit(1)

# 合并两个 SQL 文件
with open(final_file, "wb") as outfile:
    for fname in [structure_file, sample_file]:
        if os.path.exists(fname):
            with open(fname, "rb") as infile:
                outfile.write(infile.read())

print(f"导出完成，生成文件：{final_file}")

