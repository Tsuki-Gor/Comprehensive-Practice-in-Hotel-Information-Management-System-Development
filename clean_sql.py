import os


def clean_sql_file(input_file, output_file):
    """
    读取 SQL 文件，去除注释（-- 开头的行）、MySQL 特殊语法（/*! ... */）以及空行，
    并将清理后的内容写入新的 SQL 文件。

    :param input_file: 原始 SQL 文件路径
    :param output_file: 处理后的 SQL 文件路径
    """
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            line = line.strip()

            # 过滤掉注释（-- 开头）和 MySQL 特殊语法（/*! ... */）
            if line.startswith("--") or line.startswith("/*!") or not line:
                continue

            # 写入清理后的 SQL 语句
            outfile.write(line + "\n")

    print(f"清理完成，生成文件：{output_file}")


# # 让用户手动输入 SQL 文件所在目录
# input_dir = input("请输入 SQL 文件所在目录（例如 C:/mysql_backup）：").strip()
# output_dir = input("请输入清理后 SQL 文件的输出目录：").strip()

input_dir="C:/Users/mircocrift/Desktop/mysql_backup"
output_dir="C:/Users/mircocrift/Desktop/mysql_backup"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 获取 SQL 文件路径
input_file = os.path.join(input_dir, "final_dump.sql")  # 你的原始 SQL 文件
output_file = os.path.join(output_dir, "cleaned_final_dump.sql")  # 清理后的 SQL 文件

# 运行 SQL 清理
clean_sql_file(input_file, output_file)
