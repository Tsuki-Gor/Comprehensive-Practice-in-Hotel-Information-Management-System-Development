import pymysql
from service.config import localConfig  # 读取数据库配置

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=localConfig["host"],
        user=localConfig["user"],
        passwd=localConfig["passwd"],
        db=localConfig["db"],
        charset=localConfig["charset"],
        cursorclass=pymysql.cursors.DictCursor
    )
