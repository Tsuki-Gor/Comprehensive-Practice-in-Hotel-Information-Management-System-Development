import os

# MySQL 配置
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "passwd": "Tsuki",
    "db": "dbdesign",
    "charset": "utf8",
    "cursorclass": "pymysql.cursors.DictCursor"
}

# Oracle 配置（未来切换时使用）
ORACLE_CONFIG = {
    "host": "localhost",
    "port": 1521,
    "user": "oracle_user",
    "passwd": "oracle_password",
    "service_name": "orclpdb1"  # Oracle 使用 service_name 而非 db
}

# 选择数据库类型（未来切换 Oracle 只需修改这里）
DB_TYPE = os.getenv("DB_TYPE", "MYSQL")  # 读取环境变量，默认使用 MySQL
# 切换示例：
# set DB_TYPE=ORACLE  # Windows CMD


# 获取当前数据库配置
def get_config():
    if DB_TYPE.upper() == "MYSQL":
        return MYSQL_CONFIG
    elif DB_TYPE.upper() == "ORACLE":
        return ORACLE_CONFIG
    else:
        raise ValueError("Unsupported database type: {}".format(DB_TYPE))

# 供外部模块使用
localConfig = get_config()
