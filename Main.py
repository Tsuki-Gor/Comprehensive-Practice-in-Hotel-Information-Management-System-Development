# 导入 sys 模块，用于与 Python 解释器进行交互，如获取命令行参数、退出程序等
import sys
# 从 PyQt5.QtWidgets 模块导入 QApplication、QMainWindow 和 QMessageBox 类，用于创建 GUI 应用程序、主窗口和消息框
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox
# 导入 pymysql 模块，用于与 MySQL 数据库进行交互
import pymysql
# 导入 cx_Oracle 模块，用于与 Oracle 数据库进行交互
try:
    import cx_Oracle
except ImportError:
    print("警告: cx_Oracle 模块未安装，Oracle数据库功能将不可用")
    print("请使用命令安装: pip install cx_Oracle")
# 从 PyQt5.Qt 模块导入所有内容，通常包含了 PyQt5 的核心功能
from PyQt5.Qt import *
# 从 PyQt5.QtCore 模块导入 Qt 类，用于访问 Qt 框架的核心常量和枚举
from PyQt5.QtCore import Qt
# 定义数据库配置字典 localConfig，包含数据库连接所需的各项参数
from decimal import Decimal
# 导入 xlwt 模块，用于创建和写入 Excel 文件
import xlwt
# 导入 matplotlib 库，用于绘制图表
import matplotlib
# 设置 matplotlib 使用 Qt5Agg 后端，以便与 PyQt5 集成
matplotlib.use("Qt5Agg")  # 声明使用QT5
# 从 matplotlib.backends.backend_qt5agg 模块导入 FigureCanvasQTAgg 类，并将其重命名为 FigureCanvas，用于在 PyQt5 中显示 matplotlib 图表
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# 从 matplotlib.figure 模块导入 Figure 类，用于创建图表对象
from matplotlib.figure import Figure
# 导入 datetime 模块，用于处理日期和时间
import datetime
# 导入 os 模块，用于与操作系统进行交互，如文件和目录操作
import os
# 将指定路径添加到 Python 模块搜索路径中，以便可以导入该路径下的模块
sys.path.append('D:\mysql\bin')
# 从 PyQt5 模块导入 QtCore、QtGui 和 QtWidgets 子模块
from PyQt5 import QtCore, QtGui, QtWidgets
# 导入 time 模块，用于处理时间相关的操作
import time
# 从 ui.ModifyPwd 模块导入 Ui_MpwdWindow 类，可能是用于修改密码的界面类
from ui.ModifyPwd import Ui_MpwdWindow
# 从 ui.report 模块导入 Ui_ReportWindow 类，可能是用于报表显示的界面类
from ui.report import Ui_ReportWindow
# 从 PyQt5.QtGui 模块导入 QPixmap 类，用于处理图像
from PyQt5.QtGui import QPixmap
# 从 PyQt5.QtWidgets 模块导入多个类，用于创建 GUI 组件，如主窗口、消息框、表格项、垂直布局、标签和按钮
from PyQt5.QtWidgets import QMainWindow,QMessageBox,QTableWidgetItem,QVBoxLayout, QLabel,QPushButton
# 从 ui.staff 模块导入 Ui_StaffWindow 类，可能是用于员工管理的界面类
from ui.staff import Ui_StaffWindow
# 从 ui.room 模块导入 Ui_RoomWindow 类，可能是用于房间管理的界面类
from ui.room import Ui_RoomWindow
# 注释掉的导入语句，可能是用于房间数据库操作的模块
# from dao.dbOpRoom import Room
# 重复导入 datetime 模块，建议删除重复导入
import datetime

from collections import defaultdict

import re

import service.config


localConfig = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'Tsuki',
    'db': 'dbdesign',
    'charset': 'utf8',
    'cursorclass' : pymysql.cursors.DictCursor    # 数据库操纵指针
}#数据库配置连接

localConfig=service.config.get_config()
def _initStaff():
    """
    初始化员工对象，创建一个全局的 Staff 类实例。
    :return: 返回初始化后的 Staff 类实例
    """
    global staff
    # 创建一个 Staff 类的实例并赋值给全局变量 staff
    staff = Staff()
    return staff

def get_staff():#员工账户
    """
    获取全局的员工对象。
    :return: 返回全局的 Staff 类实例
    """
    global staff
    return staff


class Database:
    """数据库操作类，支持MySQL和Oracle"""
    def __init__(self):
        self.db_type = service.config.DB_TYPE.upper()
        if self.db_type == "MYSQL":
            self.conn = pymysql.connect(**localConfig)
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        elif self.db_type == "ORACLE":
            try:
                # Oracle连接参数处理
                dsn = cx_Oracle.makedsn(
                    localConfig['host'],
                    localConfig['port'],
                    service_name=localConfig['service_name']
                )
                self.conn = cx_Oracle.connect(
                    user=localConfig['user'],
                    password=localConfig['passwd'],
                    dsn=dsn
                )
                # 创建游标
                self.cursor = self.conn.cursor()
                # 设置日期格式
                self.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")
                # 设置自动提交
                self.conn.autocommit = False
            except Exception as e:
                print(f"Oracle数据库连接错误: {e}")
                raise
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")

    def query(self, sql, params=None):
        """执行查询 SQL"""
        params = params or ()
        
        try:
            # 处理Oracle和MySQL的SQL语法差异
            if self.db_type == "ORACLE":
                # 为表名添加HR.前缀
                sql = re.sub(r'\b(FROM|JOIN|UPDATE|INTO|DELETE FROM)\s+(?!HR\.)([a-zA-Z_][a-zA-Z0-9_]*)', r'\1 HR.\2', sql, flags=re.IGNORECASE)
                # 处理Oracle特有的SQL语法
                # 替换LIMIT子句
                limit_match = re.search(r'LIMIT\s+(\d+)(\s*,\s*(\d+))?', sql, re.IGNORECASE)
                if limit_match:
                    if limit_match.group(3):  # LIMIT offset, count
                        offset = int(limit_match.group(1))
                        count = int(limit_match.group(3))
                        # 替换为Oracle的ROWNUM语法
                        rownum_clause = f"ROWNUM BETWEEN {offset+1} AND {offset+count}"
                        sql = re.sub(r'LIMIT\s+\d+\s*,\s*\d+', rownum_clause, sql, flags=re.IGNORECASE)
                    else:  # LIMIT count
                        count = int(limit_match.group(1))
                        # 替换为Oracle的ROWNUM语法
                        rownum_clause = f"ROWNUM <= {count}"
                        sql = re.sub(r'LIMIT\s+\d+', rownum_clause, sql, flags=re.IGNORECASE)
                
                # 将MySQL的占位符 %s 转换为Oracle的占位符 :n
                param_dict = None
                if params:
                    # 计算需要替换的占位符数量
                    param_count = sql.count('%s')
                    # 创建Oracle风格的占位符
                    for i in range(1, param_count + 1):
                        sql = sql.replace('%s', f':{i}', 1)
                    
                    # 将参数列表转换为字典形式
                    param_dict = {str(i+1): params[i] for i in range(len(params))}
                    
                    # 处理日期类型参数
                    for key, value in param_dict.items():
                        if isinstance(value, datetime.datetime):
                            param_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 添加调试信息
                    print(f"执行Oracle查询: {sql}")
                    print(f"参数: {param_dict}")
                    
                    self.cursor.execute(sql, param_dict)
                else:
                    print(f"执行Oracle查询(无参数): {sql}")
                    self.cursor.execute(sql)
            else:  # MySQL
                self.cursor.execute(sql, params)
            
            # 获取结果
            if self.db_type == "ORACLE":
                # 获取列名
                columns = [col[0].lower() for col in self.cursor.description] if self.cursor.description else []
                # 将结果转换为字典列表，模拟MySQL的DictCursor
                result = []
                
                # 检查是否有结果集
                if not self.cursor.description:
                    print("警告: 查询没有返回结果集描述信息")
                    return []
                    
                # 添加调试信息
                print(f"Oracle查询执行: {sql}")
                print(f"参数: {params}")
                
                try:
                    # 获取所有行前先检查游标状态
                    if hasattr(self.cursor, 'rowcount') and self.cursor.rowcount > 0:
                        print(f"游标显示有 {self.cursor.rowcount} 行数据")
                    
                    # 获取所有行 - 这是问题所在的第176行
                    # 在Oracle中，fetchall()可能返回空列表，即使数据库中有数据
                    # 这可能是由于游标状态或查询执行方式的问题
                    rows = self.cursor.fetchall()
                    print(f"查询结果行数: {len(rows) if rows else 0}")
                    
                    # 如果没有获取到数据但预期应该有数据，尝试其他方法
                    if not rows and self.cursor.description:
                        print("警告: fetchall()返回空结果，尝试逐行获取")
                        # 重置游标并重新执行查询
                        self.cursor.execute(sql, param_dict if params else None)
                        # 逐行获取结果
                        row = self.cursor.fetchone()
                        temp_rows = []
                        while row:
                            temp_rows.append(row)
                            row = self.cursor.fetchone()
                        rows = temp_rows
                        print(f"逐行获取结果行数: {len(rows)}")
                except Exception as fetch_error:
                    print(f"获取结果错误: {fetch_error}")
                    # 尝试重新执行查询
                    try:
                        self.cursor.execute(sql, param_dict if params else None)
                        rows = self.cursor.fetchall()
                        print(f"重新查询结果行数: {len(rows) if rows else 0}")
                    except Exception as retry_error:
                        print(f"重新查询错误: {retry_error}")
                        return []
                
                # 如果没有结果，直接返回空列表
                if not rows:
                    return []
                    
                for row in rows:
                    # 处理Oracle特殊类型转换
                    processed_row = {}
                    for i in range(len(columns)):
                        value = row[i]
                        # 处理Oracle的日期类型转换为Python datetime
                        if hasattr(value, 'isoformat'):
                            processed_row[columns[i]] = value
                        # 处理Oracle的CLOB类型
                        elif hasattr(value, 'read'):
                            try:
                                processed_row[columns[i]] = value.read()
                            except Exception as e:
                                print(f"读取CLOB错误: {e}")
                                processed_row[columns[i]] = str(value)
                        # 处理Oracle的NUMBER类型
                        elif isinstance(value, (int, float, Decimal)):
                            processed_row[columns[i]] = value
                        # 处理Oracle的BLOB类型
                        elif isinstance(value, cx_Oracle.LOB) and not hasattr(value, 'read'):
                            try:
                                processed_row[columns[i]] = value.read()
                            except Exception as e:
                                print(f"读取BLOB错误: {e}")
                                processed_row[columns[i]] = None
                        # 处理None值
                        elif value is None:
                            processed_row[columns[i]] = None
                        else:
                            processed_row[columns[i]] = value
                    result.append(processed_row)
                
                print(f"处理后结果数: {len(result)}")
                return result
            else:  # MySQL
                return self.cursor.fetchall()
        except Exception as e:
            print(f"查询执行错误: {e}")
            print(f"SQL: {sql}")
            print(f"参数: {params}")
            raise

    def execute(self, sql, params=None):
        """执行 INSERT、UPDATE、DELETE"""
        params = params or ()
        last_id = None
        
        try:
            if self.db_type == "ORACLE":
                # 处理Oracle的序列和返回值
                if sql.strip().upper().startswith("INSERT"):
                    # 提取表名，用于获取序列
                    table_match = re.search(r"INSERT\s+INTO\s+([^\s(]+)", sql, re.IGNORECASE)
                    if table_match:
                        table_name = table_match.group(1)
                        # 移除可能的模式名前缀
                        if '.' in table_name:
                            table_name = table_name.split('.')[-1]
                        
                        # 尝试从SQL中提取主键列名
                        id_column = "ID"  # 默认主键列名
                        column_match = re.search(r"INSERT\s+INTO\s+[^\s(]+\s*\(([^)]+)\)", sql, re.IGNORECASE)
                        if column_match:
                            columns = [col.strip() for col in column_match.group(1).split(',')]
                            # 假设第一列是主键
                            if columns and columns[0].upper().endswith('ID'):
                                id_column = columns[0].strip()
                        
                        # 检查是否需要使用序列
                        # 如果SQL中包含VALUES子句，并且第一个值是%s，则可能需要使用序列
                        values_match = re.search(r"VALUES\s*\(([^)]+)\)", sql, re.IGNORECASE)
                        if values_match:
                            values = [val.strip() for val in values_match.group(1).split(',')]
                            if values and values[0] == '%s' and len(params) > 0 and params[0] is None:
                                # 假设每个表有对应的序列: 表名_SEQ
                                seq_name = f"{table_name}_SEQ"
                                try:
                                    # 获取序列的下一个值
                                    self.cursor.execute(f"SELECT {seq_name}.NEXTVAL FROM DUAL")
                                    seq_value = self.cursor.fetchone()[0]
                                    # 替换第一个参数为序列值
                                    params_list = list(params)
                                    params_list[0] = seq_value
                                    params = tuple(params_list)
                                except Exception as seq_error:
                                    print(f"序列获取错误: {seq_error}，尝试使用RETURNING子句")
                        
                        # 修改SQL以返回生成的ID
                        returning_sql = sql + f" RETURNING {id_column} INTO :new_id"
                        
                        # 准备接收返回值的变量
                        new_id_var = self.cursor.var(cx_Oracle.NUMBER)
                        
                        # 处理参数绑定
                        if params:
                            param_count = sql.count('%s')
                            for i in range(1, param_count + 1):
                                returning_sql = returning_sql.replace('%s', f':{i}', 1)
                            
                            param_dict = {str(i+1): params[i] for i in range(len(params))}
                            # 处理日期类型参数
                            for key, value in param_dict.items():
                                if isinstance(value, datetime.datetime):
                                    param_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                            
                            param_dict['new_id'] = new_id_var
                            
                            try:
                                self.cursor.execute(returning_sql, param_dict)
                                # 获取生成的ID
                                last_id = new_id_var.getvalue()
                            except Exception as returning_error:
                                print(f"RETURNING子句执行错误: {returning_error}，尝试普通执行")
                                # 如果RETURNING子句失败，回退到普通执行
                                sql_normal = sql
                                for i in range(1, param_count + 1):
                                    sql_normal = sql_normal.replace('%s', f':{i}', 1)
                                self.cursor.execute(sql_normal, param_dict)
                        else:
                            try:
                                param_dict = {'new_id': new_id_var}
                                self.cursor.execute(returning_sql, param_dict)
                                # 获取生成的ID
                                last_id = new_id_var.getvalue()
                            except Exception as returning_error:
                                print(f"RETURNING子句执行错误: {returning_error}，尝试普通执行")
                                # 如果RETURNING子句失败，回退到普通执行
                                self.cursor.execute(sql)
                    else:
                        # 如果无法提取表名，则正常执行
                        if params:
                            param_count = sql.count('%s')
                            for i in range(1, param_count + 1):
                                sql = sql.replace('%s', f':{i}', 1)
                            
                            param_dict = {str(i+1): params[i] for i in range(len(params))}
                            # 处理日期类型参数
                            for key, value in param_dict.items():
                                if isinstance(value, datetime.datetime):
                                    param_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                            
                            self.cursor.execute(sql, param_dict)
                        else:
                            self.cursor.execute(sql)
                else:  # UPDATE, DELETE等
                    if params:
                        param_count = sql.count('%s')
                        for i in range(1, param_count + 1):
                            sql = sql.replace('%s', f':{i}', 1)
                        
                        param_dict = {str(i+1): params[i] for i in range(len(params))}
                        # 处理日期类型参数
                        for key, value in param_dict.items():
                            if isinstance(value, datetime.datetime):
                                param_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                        
                        self.cursor.execute(sql, param_dict)
                    else:
                        self.cursor.execute(sql)
            else:  # MySQL
                self.cursor.execute(sql, params)
                last_id = self.cursor.lastrowid
            
            self.conn.commit()
            return last_id
        except Exception as e:
            self.conn.rollback()
            print(f"执行SQL错误: {e}")
            print(f"SQL: {sql}")
            print(f"参数: {params}")
            raise

    def close(self):
        """关闭数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(f"关闭数据库连接错误: {e}")
            
    def __enter__(self):
        """支持with语句的上下文管理"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句的上下文管理，确保连接关闭"""
        self.close()
        
    def fetchone(self):
        """获取单条记录，兼容两种数据库"""
        if self.db_type == "ORACLE":
            row = self.cursor.fetchone()
            if row:
                # 获取列名
                columns = [col[0].lower() for col in self.cursor.description]
                # 处理Oracle特殊类型转换
                processed_row = {}
                for i in range(len(columns)):
                    value = row[i]
                    # 处理Oracle的日期类型转换为Python datetime
                    if hasattr(value, 'isoformat'):
                        processed_row[columns[i]] = value
                    # 处理Oracle的CLOB类型
                    elif hasattr(value, 'read'):
                        processed_row[columns[i]] = value.read()
                    # 处理Oracle的NUMBER类型
                    elif isinstance(value, (int, float, Decimal)):
                        processed_row[columns[i]] = value
                    # 处理Oracle的BLOB类型
                    elif isinstance(value, cx_Oracle.LOB) and not hasattr(value, 'read'):
                        processed_row[columns[i]] = value.read()
                    # 处理None值
                    elif value is None:
                        processed_row[columns[i]] = None
                    else:
                        processed_row[columns[i]] = value
                return processed_row
            return None
        else:  # MySQL
            return self.cursor.fetchone()
            
    def adapt_sql_for_oracle(self, sql):
        """将MySQL风格的SQL适配为Oracle风格"""
        if self.db_type != "ORACLE":
            return sql
            
        # 替换MySQL特有的函数
        sql = sql.replace('NOW()', 'SYSDATE')
        sql = sql.replace('CURDATE()', 'TRUNC(SYSDATE)')
        
        # 替换自增ID语法
        sql = re.sub(r'AUTO_INCREMENT', '', sql, flags=re.IGNORECASE)
        
        # 替换LIMIT子句
        limit_match = re.search(r'LIMIT\s+(\d+)(\s*,\s*(\d+))?', sql, re.IGNORECASE)
        if limit_match:
            if limit_match.group(3):  # LIMIT offset, count
                offset = int(limit_match.group(1))
                count = int(limit_match.group(3))
                # 替换为Oracle的ROWNUM语法
                rownum_clause = f"ROWNUM BETWEEN {offset+1} AND {offset+count}"
                sql = re.sub(r'LIMIT\s+\d+\s*,\s*\d+', rownum_clause, sql, flags=re.IGNORECASE)
            else:  # LIMIT count
                count = int(limit_match.group(1))
                # 替换为Oracle的ROWNUM语法
                rownum_clause = f"ROWNUM <= {count}"
                sql = re.sub(r'LIMIT\s+\d+', rownum_clause, sql, flags=re.IGNORECASE)
        
        return sql

class InvoiceManager:
    """发票管理类"""

    @staticmethod
    def fetch_invoice_summary(invoice_id=None, order_id=None, client_or_team_id=None, ordertype=None):
        """查询发票信息"""
        db = Database()
        sql = "SELECT * FROM v_invoice_summary WHERE 1=1"
        params = []
        if invoice_id:
            sql += " AND invoice_id = %s"
            params.append(invoice_id)
        if order_id:
            sql += " AND order_id = %s"
            params.append(order_id)
        if client_or_team_id:
            sql += " AND client_or_team_id = %s"
            params.append(client_or_team_id)
        if ordertype:
            sql += " AND ordertype = %s"
            params.append(ordertype)

        result = db.query(sql, params)
        db.close()
        return result

    @staticmethod
    def create_invoice(order_id, invoice_title, invoice_amount, invoice_type='Electronic', tax_number=None, remark=None):
        """创建新发票"""
        db = Database()
        sql = """
            INSERT INTO invoice (order_id, invoice_title, invoice_type, invoice_amount, tax_number, invoice_status, remark)
            VALUES (%s, %s, %s, %s, %s, 'pending', %s)
        """
        new_invoice_id = db.execute(sql, (order_id, invoice_title, invoice_type, invoice_amount, tax_number, remark))
        db.close()
        return new_invoice_id

    @staticmethod
    def update_invoice_status(invoice_id, status):
        """更新发票状态"""
        if status not in ['issued', 'cancelled']:
            return {"error": "无效的状态"}

        db = Database()
        sql = "UPDATE invoice SET invoice_status = %s, issue_time = %s WHERE invoice_id = %s"
        db.execute(sql, (status, datetime.utcnow(), invoice_id))
        db.close()
        return {"message": f"发票状态已更新为 {status}"}


class Payment:
    """
    支付记录模型，对应表 payment
    """
    def __init__(self, payment_id: int = None, order_id: int = None,
                 pay_amount: Decimal = Decimal("0.00"), pay_method: str = "",
                 payment_status: str = "pending", transaction_id: str = None,
                 pay_time: datetime = None, remark: str = None):
        self.payment_id = payment_id
        self.order_id = order_id
        self.pay_amount = pay_amount
        self.pay_method = pay_method
        self.payment_status = payment_status
        self.transaction_id = transaction_id
        self.pay_time = pay_time if pay_time else datetime.now()
        self.remark = remark

    def __repr__(self):
        return (f"Payment(payment_id={self.payment_id}, order_id={self.order_id}, "
                f"pay_amount={self.pay_amount}, pay_method='{self.pay_method}', "
                f"payment_status='{self.payment_status}', transaction_id='{self.transaction_id}', "
                f"pay_time='{self.pay_time}', remark='{self.remark}')")


class PaymentDetail:
    """
    支付详情模型，对应视图 v_payment_details
    视图字段：payment_id, order_id, client_or_team_id, ordertype, pay_amount,
            pay_method, payment_status, transaction_id, pay_time
    """
    def __init__(self, payment_id: int, order_id: int, client_or_team_id: str,
                 ordertype: str, pay_amount: Decimal, pay_method: str,
                 payment_status: str, transaction_id: str, pay_time: datetime):
        self.payment_id = payment_id
        self.order_id = order_id
        self.client_or_team_id = client_or_team_id
        self.ordertype = ordertype
        self.pay_amount = pay_amount
        self.pay_method = pay_method
        self.payment_status = payment_status
        self.transaction_id = transaction_id
        self.pay_time = pay_time

    def __repr__(self):
        return (f"PaymentDetail(payment_id={self.payment_id}, order_id={self.order_id}, "
                f"client_or_team_id='{self.client_or_team_id}', ordertype='{self.ordertype}', "
                f"pay_amount={self.pay_amount}, pay_method='{self.pay_method}', "
                f"payment_status='{self.payment_status}', transaction_id='{self.transaction_id}', "
                f"pay_time='{self.pay_time}')")


# -------------------------------
# 2. 数据访问层（PaymentRepository）
# -------------------------------

class PaymentRepository:
    """
    封装支付记录的所有数据库操作
    """
    def __init__(self, db: Database):
        self.db = db

    def get_payment_by_id(self, payment_id: int) -> Payment:
        sql = "SELECT * FROM payment WHERE payment_id = %s"
        result = self.db.query(sql, (payment_id,))
        if result:
            row = result[0]
            return Payment(
                payment_id=row['payment_id'],
                order_id=row['order_id'],
                pay_amount=row['pay_amount'],
                pay_method=row['pay_method'],
                payment_status=row['payment_status'],
                transaction_id=row['transaction_id'],
                pay_time=row['pay_time'],
                remark=row['remark']
            )
        return None

    def get_all_payments(self) -> list:
        sql = "SELECT * FROM payment"
        results = self.db.query(sql)
        payments = []
        for row in results:
            payments.append(Payment(
                payment_id=row['payment_id'],
                order_id=row['order_id'],
                pay_amount=row['pay_amount'],
                pay_method=row['pay_method'],
                payment_status=row['payment_status'],
                transaction_id=row['transaction_id'],
                pay_time=row['pay_time'],
                remark=row['remark']
            ))
        return payments

    def insert_payment(self, payment: Payment) -> int:
        sql = ("INSERT INTO payment (order_id, pay_amount, pay_method, payment_status, "
               "transaction_id, pay_time, remark) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        params = (payment.order_id, payment.pay_amount, payment.pay_method, payment.payment_status,
                  payment.transaction_id, payment.pay_time, payment.remark)
        payment_id = self.db.execute(sql, params)
        payment.payment_id = payment_id
        return payment_id

    def update_payment(self, payment: Payment) -> bool:
        sql = ("UPDATE payment SET order_id=%s, pay_amount=%s, pay_method=%s, payment_status=%s, "
               "transaction_id=%s, pay_time=%s, remark=%s WHERE payment_id=%s")
        params = (payment.order_id, payment.pay_amount, payment.pay_method, payment.payment_status,
                  payment.transaction_id, payment.pay_time, payment.remark, payment.payment_id)
        self.db.execute(sql, params)
        return True

    def delete_payment(self, payment_id: int) -> bool:
        sql = "DELETE FROM payment WHERE payment_id = %s"
        self.db.execute(sql, (payment_id,))
        return True

    def get_payment_details_by_order_id(self, order_id: int) -> list:
        """
        从视图中查询指定订单的支付详情
        """
        sql = "SELECT * FROM v_payment_details WHERE order_id = %s"
        results = self.db.query(sql, (order_id,))
        details = []
        for row in results:
            details.append(PaymentDetail(
                payment_id=row['payment_id'],
                order_id=row['order_id'],
                client_or_team_id=row['client_or_team_id'],
                ordertype=row['ordertype'],
                pay_amount=row['pay_amount'],
                pay_method=row['pay_method'],
                payment_status=row['payment_status'],
                transaction_id=row['transaction_id'],
                pay_time=row['pay_time']
            ))
        return details


# -------------------------------
# 3. 业务逻辑层（PaymentService）
# -------------------------------

class PaymentService:
    """
    处理支付记录的业务逻辑，例如数据校验、异常处理等
    """
    def __init__(self, repository: PaymentRepository):
        self.repository = repository

    def create_payment(self, payment: Payment) -> Payment:
        # 简单的校验：支付金额必须大于0
        if payment.pay_amount <= 0:
            raise ValueError("支付金额必须大于0")
        payment_id = self.repository.insert_payment(payment)
        payment.payment_id = payment_id
        return payment

    def update_payment(self, payment: Payment) -> Payment:
        if not payment.payment_id or payment.payment_id <= 0:
            raise ValueError("支付记录ID无效")
        self.repository.update_payment(payment)
        return payment

    def remove_payment(self, payment_id: int) -> bool:
        if payment_id <= 0:
            raise ValueError("支付记录ID无效")
        return self.repository.delete_payment(payment_id)

    def find_payment_by_id(self, payment_id: int) -> Payment:
        return self.repository.get_payment_by_id(payment_id)

    def list_payments(self) -> list:
        return self.repository.get_all_payments()

    def get_payment_details(self, order_id: int) -> list:
        """
        查询指定订单的支付详情（来自视图）
        """
        return self.repository.get_payment_details_by_order_id(order_id)

class Staff:
    """
    员工操作类
    """
    def __init__(self, config=localConfig):
        # 使用Database类连接数据库，自动适配MySQL和Oracle
        self.db_type = service.config.DB_TYPE.upper()
        self.database = Database()
        self.cursor = self.database.cursor
        self.conn = self.database.conn
        
        # 获取数据库版本信息
        try:
            if self.db_type == "MYSQL":
                self.cursor.execute("SELECT VERSION()")
                data = self.cursor.fetchone()
                print("Database version : %s " % data['version()'])
            elif self.db_type == "ORACLE":
                self.cursor.execute("SELECT BANNER FROM V$VERSION WHERE BANNER LIKE 'Oracle%'")
                data = self.cursor.fetchone()
                print("Database version : %s " % data['banner'])
        except Exception as e:
            print(f"获取数据库版本信息失败: {e}")
            
        self.username = None
        self.password = None
        self.srole = None
        self.sid = None
        self.sname = None
        self.ssex = None
        self.stime = None
        self.sidcard = None
        self.sphone = None
        self.image=None

    def userLogin(self, username, password):
        """
        员工登录方法，检查用户名和密码是否匹配。

        参数：
            username (str): 用户名
            password (str): 密码

        返回：
            str: 返回员工的角色（管理员/前台），如果登录失败返回 False
        """

        try:
            # 使用Database类的query方法执行查询，自动适配MySQL和Oracle
            sql = "SELECT * FROM staff"
            data = self.database.query(sql)
            
            # 在数据库中查找用户名与密码，如果匹配则读入相关信息
            for row in data:
                # Oracle返回的列名可能是大写，所以使用大小写不敏感的方式获取
                username_col = 'susername' if 'susername' in row else 'SUSERNAME'
                password_col = 'spassword' if 'spassword' in row else 'SPASSWORD'
                
                if row[username_col] == username and row[password_col] == password:
                    self.username = username
                    self.password = password
                    
                    # 处理不同数据库返回的列名大小写差异
                    self.sid = row['sid'] if 'sid' in row else row['SID']
                    self.sname = row['sname'] if 'sname' in row else row['SNAME']
                    self.ssex = row['ssex'] if 'ssex' in row else row['SSEX']
                    self.stime = row['stime'] if 'stime' in row else row['STIME']
                    self.srole = row['srole'] if 'srole' in row else row['SROLE']
                    self.sidcard = row['sidcard'] if 'sidcard' in row else row['SIDCARD']
                    self.sphone = row['sphone'] if 'sphone' in row else row['SPHONE']
                    self.image = row['image'] if 'image' in row else row['IMAGE']
                    
                    return self.srole
            return False
        except Exception as e:
            print(f"登录错误: {e}")
            return False

    def modifyPasswd(self, sid, newPasswd, oldPasswd):
        """
        修改员工密码，验证旧密码后进行更新。

        参数：
            sid (str): 员工ID
            newPasswd (str): 新密码
            oldPasswd (str): 旧密码

        返回：
            bool: 修改成功返回 True，失败返回 False
        """
        try:
            # 使用Database类的query方法执行查询，自动适配MySQL和Oracle
            sql = "SELECT * FROM staff WHERE sid = %s"
            data = self.database.query(sql, (sid,))
            
            if not data:
                return False
                
            # 处理不同数据库返回的列名大小写差异
            password_col = 'spassword' if 'spassword' in data[0] else 'SPASSWORD'
            
            if data[0][password_col] == oldPasswd:
                # 使用Database类的execute方法执行更新，自动适配MySQL和Oracle
                update_sql = "UPDATE staff SET spassword = %s WHERE sid = %s"
                self.database.execute(update_sql, (newPasswd, sid))
                self.password = newPasswd
                print("密码修改成功")
                return True
            else:
                print("旧密码不正确")
                return False
        except Exception as e:
            print(f"修改密码错误: {e}")
            return False

    def forgetPasswd(self, newPasswd, sid, sidcard):
        """
        通过员工身份证号重置密码。

        参数：
            newPasswd (str): 新密码
            sid (str): 员工ID
            sidcard (str): 员工身份证号

        返回：
            bool: 重置成功返回 True，失败返回 False
        """
        try:
            # 使用Database类的query方法执行查询，自动适配MySQL和Oracle
            sql = "SELECT * FROM staff WHERE sid = %s"
            data = self.database.query(sql, (sid,))
            
            if not data:
                return False
                
            # 处理不同数据库返回的列名大小写差异
            sidcard_col = 'sidcard' if 'sidcard' in data[0] else 'SIDCARD'
            
            if data[0][sidcard_col] == sidcard:
                # 使用Database类的execute方法执行更新，自动适配MySQL和Oracle
                update_sql = "UPDATE staff SET spassword = %s WHERE sid = %s"
                self.database.execute(update_sql, (newPasswd, sid))
                self.password = newPasswd
                return True
            else:
                return False
        except Exception as e:
            print(f"重置密码错误: {e}")
            return False

    def addStaff(self,sid,sname,ssex,stime,susername,spassword,srole,sidcard,sphone):
        """
        添加新员工到数据库。

        参数：
            sid (str): 员工ID
            sname (str): 员工姓名
            ssex (str): 性别
            stime (str): 入职时间
            susername (str): 登录用户名
            spassword (str): 登录密码
            srole (str): 角色（管理员/前台）
            sidcard (str): 身份证号
            sphone (str): 手机号

        返回：
            bool: 添加成功返回 True，失败返回 False
        """
        try:
            sql = "insert into staff values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            self.database.execute(sql, (sid,sname,ssex,stime,susername,spassword,srole,sidcard,sphone))
            return True
        except Exception as e:
            print(e)
            QMessageBox().information(None, "提示", "该员工已存在！", QMessageBox.Yes)
            return False

    def showAllStaff(self,sname):
        """
        按姓名查询员工信息（支持模糊查询）。

        参数：
            sname (str): 员工姓名（支持模糊匹配）

        返回：
            list: 查询到的员工信息列表，失败返回 False

        支持模糊查询，可用于搜索类似 张%（张开头的员工）。
        """
        try:
            # like %s 支持模糊查询，可用于搜索类似 张%（张开头的员工）。
            sql = "select * from staff where sname like %s"
            data = self.database.query(sql, (sname,))
            return data
        except Exception as e:
            print(e)
            return False

    def deleteStaff(self,sid,sname,sidcard):
        """
        删除指定员工，需要提供员工ID、姓名和身份证号进行验证。

        参数：
            sid (str): 员工ID
            sname (str): 员工姓名
            sidcard (str): 员工身份证号

        返回：
            bool: 删除成功返回 True，失败返回 False
        """
        try:
            # %s 是 占位符，防止 SQL 注入攻击。
            sql = "delete from staff where sid=%s and sname=%s and sidcard=%s"
            self.database.execute(sql, (sid,sname,sidcard))
            return True
        except Exception as e:
            print(e)
            QMessageBox().information(None, "提示", "没有相关员工信息！", QMessageBox.Yes)
            return False

    def delStaff(self,sid):
        """
        根据员工ID删除员工。

        参数：
            sid (str): 员工ID

        返回：
            bool: 删除成功返回 True，失败返回 False
        """
        try:
            sql = "delete from staff where sid=%s"
            self.database.execute(sql, (sid,))
            return True
        except Exception as e:
            print(e)
            return False

    # def modifyStaff(self, row, column, value):
    #     """
    #     修改员工信息。
    #
    #     参数：
    #         row (int): 需要修改的员工在查询结果中的行索引
    #         column (int): 需要修改的列索引
    #         value (str): 新值
    #
    #     返回：
    #         bool: 修改成功返回 True，失败返回 False
    #
    #     说明：
    #         - 该方法通过 SQL_COLUMN 列表定位数据库字段
    #         - row 表示要修改的员工位置
    #         - column 对应需要修改的字段索引
    #     """
    #     # 这个列表存储了 staff 表的列名，用于匹配 column 参数。
    #     SQL_COLUMN = ['sid','sname','ssex','stime','susername','spassword','srole','sidcard','sphone']
    #     try:
    #         self.cursor.execute("select * from staff")
    #         data = self.cursor.fetchall()
    #
    #
    #         # 这里有严重错误
    #         # rid_selected = data[row]['rid']
    #         # sql = "update room set " + SQL_COLUMN[column] + "='" + value + "'where rid='" + rid_selected +"'"
    #         # self.cursor.execute(sql)
    #
    #         sid_selected =  data[row]['sid']
    #         sql = "update staff set " + SQL_COLUMN[column] + " = %s where sid = %s"
    #         self.cursor.execute(sql,(value,sid_selected))
    #
    #
    #
    #         self.db.commit()
    #         return True
    #     except Exception as e:
    #         print(e)
    #         return False

    def modifyStaff_2(self, sid, column, value):
        """
        修改员工信息,新版,根据sid而不是row。

        参数：
            sid (str): 员工ID
            column (int): 需要修改的列索引
            value (str): 新值

        返回：
            bool: 修改成功返回 True，失败返回 False

        说明：
            - 该方法通过 SQL_COLUMN 列表定位数据库字段
            - row 表示要修改的员工位置
            - column 对应需要修改的字段索引
        """
        # 这个列表存储了 staff 表的列名，用于匹配 column 参数。
        SQL_COLUMN = ['sid','sname','ssex','stime','susername','spassword','srole','sidcard','sphone']
        try:
            # 使用Database类的query方法执行查询，自动适配MySQL和Oracle
            sql = "select * from staff"
            data = self.database.query(sql)

            # 这里有严重错误
            # rid_selected = data[row]['rid']
            # sql = "update room set " + SQL_COLUMN[column] + "='" + value + "'where rid='" + rid_selected +"'"
            # self.cursor.execute(sql)

            # sid_selected =  data[row]['sid']
            sid_selected = sid
            sql = "update staff set " + SQL_COLUMN[column] + " = %s where sid = %s"
            self.database.execute(sql, (value, sid_selected))

            return True
        except Exception as e:
            print(e)
            return False

class Room:
    """客房信息操作类"""
    def __init__(self,config=localConfig):
        # 使用Database类连接数据库，自动适配MySQL和Oracle
        self.db_type = service.config.DB_TYPE.upper()
        self.database = Database()
        self.cursor = self.database.cursor
        self.conn = self.database.conn
        
        # 获取数据库版本信息
        if self.db_type == "MYSQL":
            self.cursor.execute("SELECT VERSION()")
            data = self.cursor.fetchone()
            print("Database version : %s " % data['version()'])
        elif self.db_type == "ORACLE":
            self.cursor.execute("SELECT BANNER FROM V$VERSION WHERE BANNER LIKE 'Oracle%'")
            data = self.cursor.fetchone()
            print("Database version : %s " % data['banner'])
            
        # 获取全局的staff对象
        self.staff = get_staff()

    def showAllRoom(self):
        """
        显示所有房间信息。
        返回：
            list: 查询到的房间信息列表
        """
        sql = "SELECT * FROM room"
        data = self.database.query(sql)
        return data

    def showRoom(self,rtype,rstate,rstorey,rstarttime,rendtime,price_bottom,price_up):
        """
        根据条件检索房间

        LIKE %s 是 SQL 模糊查询，用于匹配部分字符串。
        BETWEEN %s AND %s 用于指定价格范围，查询 rprice 介于 price_bottom 和 price_up 之间的房间。

        检查 rstate

        rstate == 0：查询所有符合条件的房间（无入住约束）。
        rstate == 1：进一步过滤掉已被入住或预订的房间。
        SQL 语句

        rtype LIKE %s：匹配房间类型，如 "豪华双人间"。
        rstorey LIKE %s：匹配楼层，如 "3楼" 。
        rprice BETWEEN %s AND %s：匹配价格区间。
        """
        print(rstarttime, rendtime)
        if rstate == 0:
            sql = "select * from room where rtype like %s and rstorey like %s and rprice between %s and %s"
            data1 = self.database.query(sql, (rtype, rstorey, int(price_bottom), int(price_up)))
            return data1
        elif rstate == 1:
            # 查找符合条件的房间 rid。查找 rtype、rstorey 和 rprice 符合的房间 ID。
            sql = "select rid from room where rtype like %s and rstorey like %s and rprice between %s and %s"
            data = self.database.query(sql, (rtype, rstorey, int(price_bottom), int(price_up)))
            list_data = []
            for i in range(len(data)):
                # 过滤掉已被入住的房间
                crid = data[i]['rid']
                # 检查入住客户
                sql = ("select * from checkin_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                       "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)")
                data1 = self.database.query(sql, (crid, rstarttime, rstarttime, rendtime, rendtime, rstarttime, rendtime, rstarttime, rendtime))
                
                # 检查入住团队
                sql = ("select * from checkin_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                       "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)")
                data2 = self.database.query(sql, (crid, rstarttime, rstarttime, rendtime, rendtime, rstarttime, rendtime, rstarttime, rendtime))
                
                # 检查预订客户
                sql = ("select * from booking_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                       "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)")
                data3 = self.database.query(sql, (crid, rstarttime, rstarttime, rendtime, rendtime, rstarttime, rendtime, rstarttime, rendtime))
                
                # 检查预订团队
                sql = ("select * from booking_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                       "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)")
                data4 = self.database.query(sql, (crid, rstarttime, rstarttime, rendtime, rendtime, rstarttime, rendtime, rstarttime, rendtime))
                
                # 如果所有 data1, data2, data3, data4 为空，说明房间没有被占用，则添加到 list_data。
                if data1 == () and data2 == () and data3 == () and data4 == ():
                    list_data.append(crid)
            
            ret = []
            # 查询符合条件的房间详细信息：
            # 逐个查询 room 表，获取完整房间信息。最终返回 ret 结果。
            for i in range(len(list_data)):
                rid_ret = list_data[i]
                sql = "select * from room where rid=%s"
                room_data = self.database.query(sql, (rid_ret,))
                ret = ret + room_data
            return ret

    def addRoom(self,rid,rtype,rstorey,rprice,rdesc,rpic):
        """
        增加房间

        避免主键冲突：如果 rid 已存在，插入会失败，提示 "房间号已存在"。
        改进建议
        增加字段校验（确保 rprice 为数值）。
        增加事务回滚（rollback()）防止数据库异常后部分写入。
        """
        try:
            sql = "insert into room values(%s,%s,%s,%s,%s,%s)"
            self.database.execute(sql, (rid, rtype, rstorey, rprice, rdesc, rpic))
            return True
        except Exception as e:
            print(e)
            QMessageBox().information(None, "提示", "房间号已存在！", QMessageBox.Yes)
            return False

    def delRoom(self,rid):
        """
        表格上直接删除

        改进建议
        检查是否有入住或预订记录
        """
        try:
            sql = "delete from room where rid=%s"
            self.database.execute(sql, (rid,))
            return True
        except Exception as e:
            print(e)
            return False

    def modifyRoom(self, row, column, value):
        """
        表格上直接修改

        改进建议
        增加字段校验，例如价格必须是数字
        """
        # 字典方法得到要修改的列
        SQL_COLUMN = ['rid','rtype','rstorey','rprice','rdesc']
        try:
            # 获取所有房间数据
            sql = "select * from room"
            data = self.database.query(sql)
            rid_selected = data[row]['rid']
            
            # 使用参数化查询，避免SQL注入
            sql = "update room set " + SQL_COLUMN[column] + "=%s where rid=%s"
            self.database.execute(sql, (value, rid_selected))
            return True
        except Exception as e:
            print(e)
            return False

    def singleCheckinDB(self,cname,cid,cphone,cage,csex,crid,cendtime,remark):
        """
        个人入住

        1.预订信息检测：检查 checkin_client、checkin_team、booking_client、booking_team 是否有冲突。如果有冲突，提示房间已被占用。
        2.计算入住费用：查询房间价格，计算总价，int((cendtime - starttime).days) 计算入住天数。

        改进建议
        使用 EXISTS 提高查询性能
        使用 ON DUPLICATE KEY UPDATE 避免重复入住

        """
        # 查询预定表和入住表，判断该房间是否能租出去
        starttime = datetime.date.today()
        
        # 检查入住客户冲突
        sql = ("select * from checkin_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
               "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)")
        data1 = self.database.query(sql, (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime, starttime, cendtime))
        
        # 检查入住团队冲突
        sql = ("select * from checkin_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
               "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)")
        data2 = self.database.query(sql, (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime, starttime, cendtime))
        
        # 检查预订客户冲突
        sql = ("select * from booking_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
               "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)")
        data3 = self.database.query(sql, (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime, starttime, cendtime))
        
        # 检查预订团队冲突
        sql = ("select * from booking_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
               "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)")
        data4 = self.database.query(sql, (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime, starttime, cendtime))
        
        if data1 != () or data2 != () or data3 != () or data4 != ():
            QMessageBox().information(None, "提示", "该时间段对应房间被占用（入住/预约）！", QMessageBox.Yes)
            return False
        
        # 检查客户是否存在
        sql = "select * from client where cid=%s"
        data = self.database.query(sql, (cid,))
        
        if data == ():
            # 插入新客户
            sql = ("insert into client(cname,cid,cphone,cage,csex,register_sid,accomodation_times) "
                   "values(%s,%s,%s,%s,%s,%s,%s)")
            self.database.execute(sql, (cname, cid, cphone, cage, csex, self.staff.sid, 0))
        
        # 检查房间是否存在
        sql = "select * from room where rid=%s"
        data = self.database.query(sql, (crid,))
        
        if data == ():
            QMessageBox().information(None, "提示", "没有对应房间号！", QMessageBox.Yes)
            return False
        
        perPrice = data[0]['rprice']
        totalPrice = int(perPrice) * int((cendtime-starttime).days)
        
        try:
            # 插入入住记录
            sql = "insert into checkin_client values(%s,%s,%s,%s,%s,%s,%s)"
            self.database.execute(sql, (crid, cid, starttime, cendtime, totalPrice, self.staff.sid, remark))
            return True
        except Exception as e:
            print(e)
            QMessageBox().information(None, "提示", "相关客户已入住，请勿重复插入", QMessageBox.Yes)
            return False

    def teamCheckinDB(self,tname,tid,tphone,ttrid,tendtime,tremark):
        """团体入住"""
        tstarttime = datetime.date.today()
        for trid in re.split(',|，| ', ttrid):
            print(trid)
            # 检查入住客户冲突
            sql = ("select * from checkin_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                   "or A.end_time>%s and A.start_time<=%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)")
            data1 = self.database.query(sql, (trid, tstarttime, tstarttime, tendtime, tendtime, tstarttime, tendtime, tstarttime, tendtime))
            print(data1)
            
            # 检查入住团队冲突
            sql = ("select * from checkin_team as A where (A.rid=%s) and ((A.end_time>%s and A.start_time<%s) "
                   "or (A.end_time>%s and A.start_time<%s) or (A.start_time<=%s and A.end_time>=%s) or (A.start_time>=%s and A.end_time<=%s))")
            data2 = self.database.query(sql, (trid, tstarttime, tstarttime, tendtime, tendtime, tstarttime, tendtime, tstarttime, tendtime))
            data2 = self.cursor.fetchall()
            print(data2)
            self.cursor.execute(
                "select * from booking_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)"
                , (trid, tstarttime, tstarttime, tendtime, tendtime, tstarttime, tendtime, tstarttime, tendtime))
            data3 = self.cursor.fetchall()
            print(data3)
            self.cursor.execute("select * from booking_team as A where (A.rid=%s) and ((A.end_time>%s and A.start_time<%s) "
                                "or (A.end_time>%s and A.start_time<%s) or (A.start_time<=%s and A.end_time>=%s) or (A.start_time>=%s and A.end_time<=%s))"
                                , (trid, tstarttime, tstarttime, tendtime, tendtime, tstarttime, tendtime, tstarttime, tendtime))
            data4 = self.cursor.fetchall()
            print(data4)
            if data1 != () or data2 != () or data3 != () or data4 != ():
                QMessageBox().information(None, "提示", "该时间段对应房间被占用（入住/预约）！", QMessageBox.Yes)
                return False
        try:
            for i in re.split(',|，| ', ttrid):
                self.cursor.execute("select * from team where tid=%s", (tid))
                data = self.cursor.fetchall()
                if data == ():
                    self.cursor.execute("insert into team(tname,tid,tphone,check_in_sid,accomodation_times) values(%s,%s,%s,%s,%s)",
                                        (tname, tid, tphone, self.staff.sid, 0))

                self.cursor.execute("select * from room where rid=%s",(i))
                perPrice = self.cursor.fetchall()[0]['rprice']
                starttime = datetime.date.today()
                totalPrice = int(perPrice) * int((tendtime - starttime).days)
                self.cursor.execute("insert into checkin_team values(%s,%s,%s,%s,%s,%s,%s)",
                                    (i, tid, starttime, tendtime, totalPrice, self.staff.sid, tremark))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def reserveToCheckinC(self,cid,rid):
        """个人预约订单入住"""
        # 先查找预约表
        starttime = datetime.date.today()
        self.cursor.execute("select * from booking_client where cid=%s and rid=%s and start_time=%s",(cid,rid,starttime))
        data = self.cursor.fetchall()
        if data == ():
            QMessageBox().information(None, "提示", "没有对应预约或者预约入住时间未到！", QMessageBox.Yes)
            return False
        # 再从预约表中获取相关信息
        endtime = data[0]['end_time']
        remark = data[0]['remark']
        # 下面计算房价
        self.cursor.execute("select * from room where rid=%s",(rid))
        data = self.cursor.fetchall()
        if data == ():
            QMessageBox().information(None, "提示", "没有对应房间号！", QMessageBox.Yes)
            return False
        perPrice = data[0]['rprice']
        totalPrice = int(perPrice) * int((endtime-starttime).days)
        try:
            self.cursor.execute("insert into checkin_client values(%s,%s,%s,%s,%s,%s,%s)",
                                (rid,cid,starttime,endtime,totalPrice,self.staff.sid,remark))
            self.cursor.execute("delete from booking_client where cid=%s and rid=%s and start_time=%s",(cid,rid,starttime))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False


    def reserveToCheckinT(self,tid,rrid):
        """团队预定入住"""
        starttime = datetime.date.today()
        for rid in re.split(',|，| ', rrid):
            print(rid)
            self.cursor.execute("select * from booking_team where tid=%s and rid=%s and start_time=%s",
                                (tid, rid, starttime))
            data = self.cursor.fetchall()
            print(data)
            if data == ():
                QMessageBox().information(None, "提示", "%s房间没有对应预约或者预约入住时间未到！"%rid, QMessageBox.Yes)
                return False
            # 再从预约表中获取相关信息
            endtime = data[0]['end_time']
            remark = data[0]['remark']
            # 下面计算房价
            self.cursor.execute("select * from room where rid=%s", (rid))
            data = self.cursor.fetchall()
            if data == ():
                QMessageBox().information(None, "提示", "没有%s房间号！"%rid, QMessageBox.Yes)
                return False
            perPrice = data[0]['rprice']
            totalPrice = int(perPrice) * int((endtime - starttime).days)
            try:
                self.cursor.execute("insert into checkin_team values(%s,%s,%s,%s,%s,%s,%s)",
                                    (rid, tid, starttime, endtime, totalPrice, self.staff.sid, remark))
                self.cursor.execute("delete from booking_team where tid=%s and rid=%s and start_time=%s",
                                    (tid, rid, starttime))
                self.db.commit()
            except Exception as e:
                print(e)
                return False
        return True

    def reserveCDB(self,cname,cid,cphone,cage,csex,crid,cstarttime,cendtime,cremark):
        """个人预约"""
        starttime = datetime.date.today()
        self.cursor.execute("select * from checkin_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                            "or A.end_time>%s and A.start_time<%s A.start_time<=%s and A.end_time>%s or A.start_time>=%s and A.end_time<=%s)"
                            , (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime, starttime, cendtime))
        data1 = self.cursor.fetchall()
        self.cursor.execute("select * from checkin_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                            "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>%s or A.start_time>=%s and A.end_time<=%s)"
                            , (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime, starttime, cendtime))
        data2 = self.cursor.fetchall()
        self.cursor.execute("select * from booking_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                            "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>%s or A.start_time>=%s and A.end_time<=%s)"
                            , (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime, starttime, cendtime))
        data3 = self.cursor.fetchall()
        self.cursor.execute("select * from booking_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                            "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>%s or A.start_time>=%s and A.end_time<=%s)"
                            , (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime, starttime, cendtime))
        data4 = self.cursor.fetchall()
        if data1 != () or data2 != () or data3 != () or data4 != ():
            QMessageBox().information(None, "提示", "该时间段对应房间被占用（入住/预约）！", QMessageBox.Yes)
            return False
        self.cursor.execute("select * from client where cid=%s",(cid))
        data = self.cursor.fetchall()
        if data == ():
            self.cursor.execute(
                "insert into client(cname,cid,cphone,cage,csex,register_sid,accomodation_times) values(%s,%s,%s,%s,%s,%s,%s)",
                (cname, cid, cphone, cage, csex, self.staff.sid, 0))
        try:
            self.cursor.execute("insert into booking_client(cid,rid,start_time,end_time,remark) values(%s,%s,%s,%s,%s)",
                                (cid,crid,cstarttime,cendtime,cremark))
            self.db.commit()
            return  True
        except Exception as e:
            print(e)
            QMessageBox().information(None, "提示", "相关预约信息已存在！", QMessageBox.Yes)
            return False

    def reserveTDB(self,tname,tid,tphone,ttrid,tstarttime,tendtime,tremark):
        """团体预约"""
        for trid in re.split(',|，| ', ttrid):
            self.cursor.execute(
                "select * from checkin_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>%s or A.start_time>=%s and A.end_time<=%s)"
                , (trid, tstarttime, tstarttime, tendtime, tendtime, tstarttime, tendtime, tstarttime, tendtime))
            data1 = self.cursor.fetchall()
            self.cursor.execute("select * from checkin_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                                "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>%s or A.start_time>=%s and A.end_time<=%s)"
                                , (trid, tstarttime, tstarttime, tendtime, tendtime, tstarttime, tendtime, tstarttime, tendtime))
            data2 = self.cursor.fetchall()
            self.cursor.execute(
                "select * from booking_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>%s or A.start_time>=%s and A.end_time<=%s)"
                , (trid, tstarttime, tstarttime, tendtime, tendtime, tstarttime, tendtime, tstarttime, tendtime))
            data3 = self.cursor.fetchall()
            self.cursor.execute("select * from booking_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                                "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>%s or A.start_time>=%s and A.end_time<=%s)"
                                , (trid, tstarttime, tstarttime, tendtime, tendtime, tstarttime, tendtime, tstarttime, tendtime))
            data4 = self.cursor.fetchall()
            if data1 != () or data2 != () or data3 != () or data4 != ():
                QMessageBox().information(None, "提示", "该时间段对应房间被占用（入住/预约）！", QMessageBox.Yes)
                return False
            self.cursor.execute("select * from team where tid=%s", (tid))
            data = self.cursor.fetchall()
            if data == ():
                self.cursor.execute(
                    "insert into team(tname,tid,tphone,check_in_sid,accomodation_times) values(%s,%s,%s,%s,%s)",
                    (tname, tid, tphone, self.staff.sid, 0))
            try:
                self.cursor.execute("insert into booking_team(tid,rid,start_time,end_time,remark) values(%s,%s,%s,%s,%s)",
                                    (tid, trid, tstarttime, tendtime, tremark))
                self.db.commit()
            except Exception as e:
                print(e)
                QMessageBox().information(None, "提示", "相关预约信息已存在！", QMessageBox.Yes)
                return False
        return True

    def cancelReserveCDB(self,cancel_cid,cancel_rid):
        """个人取消预约"""
        self.cursor.execute("select * from booking_client where cid=%s and rid=%s",(cancel_cid,cancel_rid))
        if self.cursor.fetchall() == ():
            QMessageBox().information(None, "提示", "没有相关预约信息！", QMessageBox.Yes)
            return False
        try:
            self.cursor.execute("delete from booking_client where cid=%s and rid=%s",(cancel_cid,cancel_rid))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            QMessageBox().information(None, "提示", "没有相关预约信息！", QMessageBox.Yes)
            return False

    def cancelReserveTDB(self,cancel_tid,cancel_rid):
        """团体取消预约"""
        try:
            for r in re.split(',|，| ', cancel_rid):
                self.cursor.execute("select * from booking_team where tid=%s and rid=%s", (cancel_tid, r))
                if self.cursor.fetchall() == ():
                    QMessageBox().information(None, "提示", "%s房间没有预约！"%r, QMessageBox.Yes)
                    return False
                self.cursor.execute("delete from booking_team where tid=%s and rid=%s",(cancel_tid,r))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    # def checkoutDB(self,flag, id,rid,payType,remark):
    #     """两种方式退房"""
    #     try:
    #         if flag == '个人':
    #             self.cursor.execute("select * from checkin_client where rid=%s and cid=%s",(rid,id))
    #             data = self.cursor.fetchall()
    #             if data == ():
    #                 QMessageBox().information(None, "提示", "没有相关入住信息！", QMessageBox.Yes)
    #                 return False
    #             else:
    #                 rid_out = data[0]['rid']
    #                 cid_out = data[0]['cid']
    #                 stime_out = data[0]['start_time']
    #                 etime_out = data[0]['end_time']
    #                 money = data[0]['total_price']
    #                 self.cursor.execute("insert into hotelorder(id,ordertype,start_time,end_time,rid,pay_type,money,remark,register_sid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
    #                                     (cid_out,flag,stime_out,etime_out,rid_out,payType,money,remark,self.staff.sid))
    #                 self.cursor.execute("delete from checkin_client where rid=%s and cid=%s",(rid_out,cid_out))
    #                 self.db.commit()
    #                 QMessageBox().information(None, "提示", "本次需要支付%s" %money, QMessageBox.Yes)
    #         elif flag == '团队':
    #             sum = 0
    #             for r in re.split(',|，| ',rid):
    #                 self.cursor.execute(
    #                     "select * from checkin_team where rid=%s and tid=%s", (r, id))
    #                 data = self.cursor.fetchall()
    #                 if data == ():
    #                     QMessageBox().information(None, "提示", "没有相关入住信息！", QMessageBox.Yes)
    #                     return False
    #                 else:
    #                     rid_out = data[0]['rid']
    #                     tid_out = data[0]['tid']
    #                     stime_out = data[0]['start_time']
    #                     etime_out = data[0]['end_time']
    #                     money = data[0]['total_price']
    #                     self.cursor.execute(
    #                         "insert into hotelorder(id,ordertype,start_time,end_time,rid,pay_type,money,remark,register_sid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    #                         , (tid_out, flag, stime_out, etime_out, rid_out, payType, money, remark,self.staff.sid))
    #                     self.cursor.execute("delete from checkin_team where rid=%s and tid=%s", (rid_out, tid_out))
    #                     self.db.commit()
    #                     sum = sum + int(money)
    #             QMessageBox().information(None, "提示", "本次需要支付%s" %str(sum), QMessageBox.Yes)
    #         return True
    #     except Exception as e:
    #         print(e)
    #         return False

    def checkoutDB(self, flag, id, rid, payType, remark):
        """
        退房操作（个人 / 团队）修改版

        回滚事务 (rollback())：
        避免数据损坏：如果插入订单失败但删除入住记录成功，数据会不一致（订单丢失但客户已退房）。
        遇到 数据库异常（如外键约束失败、断网）时，数据回滚到 操作前的状态。

        """
        try:
            if flag == '个人':
                # 查询入住信息
                self.cursor.execute("SELECT * FROM checkin_client WHERE rid=%s AND cid=%s", (rid, id))
                data = self.cursor.fetchone()

                if not data:
                    QMessageBox().information(None, "提示", "没有相关入住信息！", QMessageBox.Yes)
                    return False

                # 提取数据
                rid_out, cid_out, stime_out, etime_out, money = data['rid'], data['cid'], data['start_time'], data[
                    'end_time'], data['total_price']

                # 插入新订单到 hotelorder_v1
                self.cursor.execute("""
                    INSERT INTO hotelorder_v1 (id, ordertype, start_time, end_time, rid, pay_type, money, remark, register_sid, order_status, pay_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 'pending')
                """, (cid_out, flag, stime_out, etime_out, rid_out, payType, money, remark, self.staff.sid))

                # 删除入住记录
                self.cursor.execute("DELETE FROM checkin_client WHERE rid=%s AND cid=%s", (rid_out, cid_out))

                # 提交事务
                self.db.commit()

                QMessageBox().information(None, "提示", f"本次需要支付 {money}，订单已生成！", QMessageBox.Yes)

            elif flag == '团队':
                total_sum = 0
                rooms = rid.split(",")  # 支持多个房间退房

                for room_id in rooms:
                    # 查询入住信息
                    self.cursor.execute("SELECT * FROM checkin_team WHERE rid=%s AND tid=%s", (room_id.strip(), id))
                    data = self.cursor.fetchone()

                    if not data:
                        QMessageBox().information(None, "提示", f"房间 {room_id} 没有相关入住信息！", QMessageBox.Yes)
                        return False

                    # 提取数据
                    rid_out, tid_out, stime_out, etime_out, money = data['rid'], data['tid'], data['start_time'], data[
                        'end_time'], data['total_price']
                    total_sum += int(money)

                    # 插入新订单到 hotelorder_v1
                    self.cursor.execute("""
                        INSERT INTO hotelorder_v1 (id, ordertype, start_time, end_time, rid, pay_type, money, remark, register_sid, order_status, pay_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 'pending')
                    """, (tid_out, flag, stime_out, etime_out, rid_out, payType, money, remark, self.staff.sid))

                    # 删除入住记录
                    self.cursor.execute("DELETE FROM checkin_team WHERE rid=%s AND tid=%s", (rid_out, tid_out))

                # 提交事务
                self.db.commit()

                QMessageBox().information(None, "提示", f"本次团队订单总计支付 {total_sum}，订单已生成！",
                                          QMessageBox.Yes)

            return True
        except Exception as e:
            self.db.rollback()  # 遇到异常时回滚，确保数据一致性
            print(f"退房错误: {e}")
            return False

class Chart:
    def __init__(self,config=localConfig):
        self.db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'],
                                  passwd=config['passwd'], db=config['db'], charset=config['charset'],
                                  cursorclass=config['cursorclass'])
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT VERSION()")
        data = self.cursor.fetchone()
        print("Database version : %s " % data['VERSION()'])


    def toExcel(self,path, table_name):
        """
        导出到excel表
        """
        sql = "select * from " + table_name
        self.cursor.execute(sql)
        path = str(path)
        fields = [field[0] for field in self.cursor.description]
        all_data = self.cursor.fetchall()
        # 写入excel
        book = xlwt.Workbook()
        sheet = book.add_sheet('sheet1')
        for col, field in enumerate(fields):
            sheet.write(0, col, field)
        row = 1
        for i in range(len(all_data)):
            data = all_data[i].values()
            for col, field in enumerate(data):
                sheet.write(row, col, field)
            row += 1
        book.save(path+"/%s.xls" % table_name)

    # def getRevenue(self):
    #     """
    #     获取营业额
    #     """
    #     list_revenue = []
    #     list_date = []
    #     for i in range(7):
    #         data = ()
    #         sum = 0
    #         delta = datetime.timedelta(days=i)
    #         date = datetime.date.today()
    #         date_selected = date - delta
    #         str_date = str(date_selected)
    #         list_date.append(str_date[5:])
    #         self.cursor.execute("select money from hotelorder where end_time=%s",(date_selected))
    #         data = self.cursor.fetchall()
    #         if data != ():
    #             for i in range(len(data)):
    #                 sum = sum + int(data[i]['money'])
    #         list_revenue.append(sum)
    #     print(list_revenue)
    #     print(list_date)
    #     list_date.reverse()
    #     return list_date, list_revenue

    # def getRevenue(self):
    #     """
    #     获取最近 7 天的营业额，新版
    #     """
    #     list_revenue = []
    #     list_date = []
    #     today = datetime.date.today()
    #
    #     query = """
    #     SELECT DATE_FORMAT(end_time, '%%m-%%d') AS order_date, SUM(total_amount) AS revenue
    #     FROM v_order_summary
    #     WHERE end_time BETWEEN DATE_SUB(%s, INTERVAL 6 DAY) AND %s
    #     GROUP BY order_date
    #     ORDER BY order_date;
    #     """
    #     self.cursor.execute(query, (today, today))
    #     data = self.cursor.fetchall()
    #
    #     for row in data:
    #         list_date.append(row['order_date'])
    #         list_revenue.append(float(row['revenue']) if row['revenue'] else 0)
    #
    #     return list_date, list_revenue

    def getRevenue(self):
        """
        获取最近 7 天的营业额，新版
        确保即使某天无记录，仍然在图表中显示
        """
        list_revenue = []
        list_date = []

        today = datetime.date.today()
        past_7_days = [(today - datetime.timedelta(days=i)).strftime('%m-%d') for i in
                       range(6, -1, -1)]  # 生成完整的 7 天日期列表

        if self.db_type == "ORACLE":
            query = """
            SELECT TO_CHAR(end_time, 'MM-DD') AS order_date, SUM(total_amount) AS revenue
            FROM v_order_summary
            WHERE end_time BETWEEN %s - INTERVAL '6' DAY AND %s
            GROUP BY TO_CHAR(end_time, 'MM-DD')
            ORDER BY order_date
            """
        else:
            query = """
            SELECT DATE_FORMAT(end_time, '%%m-%%d') AS order_date, SUM(total_amount) AS revenue
            FROM v_order_summary
            WHERE end_time BETWEEN DATE_SUB(%s, INTERVAL 6 DAY) AND %s
            GROUP BY order_date
            ORDER BY order_date;
            """
        self.cursor.execute(query, (today, today))
        if self.db_type == "ORACLE":
            data = self.fetchall()
        else:
            data = self.cursor.fetchall()

        # 将 SQL 结果映射到 {日期: 营业额}
        revenue_dict = defaultdict(lambda: 0)  # 默认值 0
        for row in data:
            revenue_dict[row['order_date']] = float(row['revenue']) if row['revenue'] else 0

        # 生成完整的日期和营业额列表
        list_date = past_7_days  # 确保 x 轴包含所有日期
        list_revenue = [revenue_dict[date] for date in past_7_days]  # 确保 y 轴值与 x 轴对应

        return list_date, list_revenue

    # def getOccupy(self):
    #     """
    #     获取入住率/出租率
    #     """
    #     list_occupy = []
    #     list_date = []
    #     self.cursor.execute("select count(*) from room")
    #     totalRoomCount = self.cursor.fetchall()[0]['count(*)']
    #     print(totalRoomCount)
    #     for i in range(7):
    #         data = ()
    #         occupyRate = 0.0
    #         delta = datetime.timedelta(days=i)
    #         date = datetime.date.today()
    #         date_selected = date - delta
    #         str_date = str(date_selected)
    #         list_date.append(str_date[5:])
    #         self.cursor.execute("select distinct rid from hotelorder where end_time>=%s and start_time<=%s",
    #                             (date_selected,date_selected))
    #         data = self.cursor.fetchall()
    #         print(data)
    #         if data != ():
    #             occupyRate = float(len(data) / totalRoomCount)
    #         list_occupy.append(occupyRate)
    #     print(list_occupy)
    #     list_date.reverse()
    #     return list_date, list_occupy

    # def getOccupy(self):
    #     """
    #     获取最近 7 天的入住率，新版本
    #     """
    #     list_occupy = []
    #     list_date = []
    #     today = datetime.date.today()
    #
    #     # 获取总房间数
    #     self.cursor.execute("SELECT COUNT(*) AS total_rooms FROM room")
    #     total_room_count = self.cursor.fetchone()['total_rooms']
    #
    #     query = """
    #     SELECT DATE_FORMAT(start_time, '%%m-%%d') AS checkin_date, COUNT(DISTINCT rid) AS occupied_rooms
    #     FROM v_order_summary
    #     WHERE start_time BETWEEN DATE_SUB(%s, INTERVAL 6 DAY) AND %s
    #     GROUP BY checkin_date
    #     ORDER BY checkin_date;
    #     """
    #     self.cursor.execute(query, (today, today))
    #     data = self.cursor.fetchall()
    #
    #     for row in data:
    #         list_date.append(row['checkin_date'])
    #         occupy_rate = (row['occupied_rooms'] / total_room_count) if total_room_count > 0 else 0
    #         list_occupy.append(round(occupy_rate, 2))
    #
    #     return list_date, list_occupy

    def getOccupy(self):
        """
        获取最近 7 天的入住率（确保所有日期都有数据）
        """
        list_occupy = []
        list_date = []

        today = datetime.date.today()

        # 生成过去 7 天的完整日期列表
        past_7_days = [(today - datetime.timedelta(days=i)).strftime('%m-%d') for i in range(6, -1, -1)]

        # 获取总房间数
        self.cursor.execute("SELECT COUNT(*) AS total_rooms FROM room")
        if self.db_type == "ORACLE":
            total_room_count = self.fetchone()['total_rooms']
        else:
            total_room_count = self.cursor.fetchone()['total_rooms']

        # 查询入住数据
        if self.db_type == "ORACLE":
            query = """
            SELECT TO_CHAR(start_time, 'MM-DD') AS checkin_date, COUNT(DISTINCT rid) AS occupied_rooms
            FROM v_order_summary
            WHERE start_time BETWEEN %s - INTERVAL '6' DAY AND %s
            GROUP BY TO_CHAR(start_time, 'MM-DD')
            ORDER BY checkin_date
            """
        else:
            query = """
            SELECT DATE_FORMAT(start_time, '%%m-%%d') AS checkin_date, COUNT(DISTINCT rid) AS occupied_rooms
            FROM v_order_summary
            WHERE start_time BETWEEN DATE_SUB(%s, INTERVAL 6 DAY) AND %s
            GROUP BY checkin_date
            ORDER BY checkin_date;
            """
        self.cursor.execute(query, (today, today))
        data = self.cursor.fetchall()

        # 结果映射到 {日期: 入住房间数}
        occupy_dict = defaultdict(lambda: 0)  # 默认值 0
        for row in data:
            occupy_dict[row['checkin_date']] = row['occupied_rooms']

        # 生成完整的日期和入住率列表
        list_date = past_7_days
        list_occupy = [
            round((occupy_dict[date] / total_room_count), 2) if total_room_count > 0 else 0
            for date in past_7_days
        ]

        return list_date, list_occupy

    # def getClientStatics(self):
    #     """
    #     获取客户相关数据
    #     """
    #     list_clientStatics = []
    #     self.cursor.execute("select * from hotelorder where ordertype='个人'")
    #     num_client = len(self.cursor.fetchall())
    #     self.cursor.execute("select distinct id from hotelorder where ordertype='团队'")
    #     num_team = len(self.cursor.fetchall())
    #     list_ret = []
    #     list_ret.append(num_client)
    #     list_ret.append(num_team)
    #     return list_ret

    def getClientStatics(self):
        """
        获取个人和团队订单数量，新版本
        """
        query = """
        SELECT 
            SUM(CASE WHEN ordertype = '个人' THEN 1 ELSE 0 END) AS num_client,
            SUM(CASE WHEN ordertype = '团队' THEN 1 ELSE 0 END) AS num_team
        FROM v_client_team_order;
        """
        self.cursor.execute(query)
        data = self.cursor.fetchone()
        return [data['num_client'], data['num_team']]


    # def getStaffStatics(self):
    #     """
    #     获取员工相关数据
    #     """
    #     self.cursor.execute("select register_sid,count(*) from hotelorder group by register_sid")
    #     data = self.cursor.fetchall()
    #     list_clientNum = []
    #     list_clientSta = []
    #     for i in range(len(data)):
    #         list_clientNum.append(data[i]['register_sid'])
    #         list_clientSta.append(data[i]['count(*)'])
    #     print(list_clientNum)
    #     print(list_clientSta)
    #     return list_clientNum, list_clientSta

    def getStaffStatics(self):
        """
        获取员工订单处理情况
        """
        query = """
        SELECT register_sid, COUNT(*) AS order_count
        FROM v_order_summary
        GROUP BY register_sid
        ORDER BY order_count DESC;
        """
        self.cursor.execute(query)
        data = self.cursor.fetchall()

        list_staff_id = []
        list_order_count = []
        for row in data:
            list_staff_id.append(row['register_sid'])
            list_order_count.append(row['order_count'])

        return list_staff_id, list_order_count

class Figure_Canvas(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # 在父类中激活Figure窗口
        super(Figure_Canvas, self).__init__(self.fig)
        # 第三步：创建一个子图，用于绘制图形用，111表示子图编号
        self.axes = self.fig.add_subplot(111)

#----------------------------------------------------------
#经过pyuic生成的python文件会生成一个类，并具有以下方法：
#setupUi（self,Widget）:该方法将ui元素应用到给定的窗口，将ui中定义的所有控件添加到（widget）中，之后都可以通过self.xxx进行调用
#retranslateui(self,widget):用于设置界面的文本
#(不过只有setupUi是重要的）
#----------------------------------------------------------
# class Ui_LoginWindow(object):
#     def setupUi(self, MainWindow):
#         MainWindow.setObjectName("浙商大招待所")
#         MainWindow.resize(800, 600)
#         font = QtGui.QFont()
#         font.setFamily("Century Gothic")
#         font.setPointSize(-1)
#         MainWindow.setFont(font)
#         icon = QtGui.QIcon()
#         icon.addPixmap(QtGui.QPixmap("../../../../../../../../pictures/酒店.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#         MainWindow.setWindowIcon(icon)
#         MainWindow.setStyleSheet("\n"
# "*{\n"
# "font-size:24px;\n"
# "font-family:Century Gothic;\n"
# "}\n"
# "QFrame{\n"
# "background:rgba(0,0,0,0.8);\n"
# "border-radius:15px;\n"
# "}\n"
# "#centralwidget{\n"
# "border-image:url(D:/pictures/login4.jpg) strectch；\n"
# "}\n"
# "\n"
# "#toolButton{\n"
# "background:red;\n"
# "border-radius:60px;\n"
# "}\n"
# "QLabel{\n"
# "color:white;\n"
# "background:transparent;\n"
# "}\n"
# "QPushButton{\n"
# "background:red;;\n"
# "border-radius:15px;\n"
# "}\n"
# "QPushButton:hover{\n"
# "background:#333;\n"
# "border-radius:15px;\n"
# "background:#49ebff;\n"
# "}\n"
# "QLineEdit{\n"
# "background:transparent;\n"
# "border:none;\n"
# "color:#717072;\n"
# "border-bottom:1px solid #717072;\n"
# "}")
#         self.centralwidget = QtWidgets.QWidget(MainWindow)
#         font = QtGui.QFont()
#         font.setFamily("Century Gothic")
#         font.setPointSize(-1)
#         self.centralwidget.setFont(font)
#         self.centralwidget.setFocusPolicy(QtCore.Qt.WheelFocus)
#         self.centralwidget.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
#         self.centralwidget.setObjectName("centralwidget")
#         self.frame = QtWidgets.QFrame(self.centralwidget)
#         self.frame.setGeometry(QtCore.QRect(140, 80, 491, 461))
#         font = QtGui.QFont()
#         font.setFamily("Century Gothic")
#         font.setPointSize(-1)
#         self.frame.setFont(font)
#         self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
#         self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
#         self.frame.setObjectName("frame")
#         self.label = QtWidgets.QLabel(self.frame)
#         self.label.setGeometry(QtCore.QRect(180, 70, 151, 41))
#         font = QtGui.QFont()
#         font.setFamily("Century Gothic")
#         font.setPointSize(-1)
#         self.label.setFont(font)
#         self.label.setObjectName("label")
#         self.lineEdit_user = QtWidgets.QLineEdit(self.frame)
#         self.lineEdit_user.setGeometry(QtCore.QRect(70, 160, 361, 31))
#         self.lineEdit_user.setText("")
#         self.lineEdit_user.setObjectName("lineEdit_user")
#         self.lineEdit_password = QtWidgets.QLineEdit(self.frame)
#         self.lineEdit_password.setGeometry(QtCore.QRect(70, 260, 361, 31))
#         font = QtGui.QFont()
#         font.setFamily("Century Gothic")
#         font.setPointSize(-1)
#         self.lineEdit_password.setFont(font)
#         self.lineEdit_password.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
#         self.lineEdit_password.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
#         self.lineEdit_password.setText("")
#         self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
#         self.lineEdit_password.setObjectName("lineEdit_password")
#         self.pushButton = QtWidgets.QPushButton(self.frame)
#         self.pushButton.setGeometry(QtCore.QRect(30, 370, 421, 51))
#         palette = QtGui.QPalette()
#         brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
#         brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
#         brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
#         brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
#         brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
#         brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
#         brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
#         brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
#         brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
#         self.pushButton.setPalette(palette)
#         self.pushButton.setStyleSheet("background-color: rgb(81, 182, 255);\n"
# "QPalette pal = startBtn.palette(); \n"
# "pal.setColor(QPalette::ButtonText, Qt::red);\n"
# "startBtn.setPalette(pal); \n"
# "startBtn.setStyleSheet(\"background-color:green\"); ")
#         self.pushButton.setObjectName("pushButton")
#         self.label_2 = QtWidgets.QLabel(self.frame)
#         self.label_2.setGeometry(QtCore.QRect(70, 120, 121, 31))
#         font = QtGui.QFont()
#         font.setFamily("Century Gothic")
#         font.setPointSize(-1)
#         self.label_2.setFont(font)
#         self.label_2.setObjectName("label_2")
#         self.label_3 = QtWidgets.QLabel(self.frame)
#         self.label_3.setGeometry(QtCore.QRect(70, 220, 121, 31))
#         self.label_3.setObjectName("label_3")
#         self.toolButton = QtWidgets.QToolButton(self.centralwidget)
#         self.toolButton.setGeometry(QtCore.QRect(330, 20, 121, 121))
#         palette = QtGui.QPalette()
#         brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
#         brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
#         brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
#         brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
#         brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
#         brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
#         brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
#         brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
#         brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
#         self.toolButton.setPalette(palette)
#         self.toolButton.setStyleSheet("background-color: rgb(116, 197, 255);")
#         self.toolButton.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
#         self.toolButton.setText("")
#         icon1 = QtGui.QIcon()
#         icon1.addPixmap(QtGui.QPixmap("../../../../../../pictures/院徽.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#         self.toolButton.setIcon(icon1)
#         self.toolButton.setIconSize(QtCore.QSize(150, 150))
#         self.toolButton.setObjectName("toolButton")
#         self.forgetPasswd = QtWidgets.QToolButton(self.centralwidget)
#         self.forgetPasswd.setGeometry(QtCore.QRect(660, 560, 111, 31))
#         font = QtGui.QFont()
#         font.setFamily("Century Gothic")
#         font.setPointSize(-1)
#         self.forgetPasswd.setFont(font)
#         self.forgetPasswd.setStyleSheet("border:none;\n"
# "background:rgba(0,0,0,0.8)\n"
# "")
#         self.forgetPasswd.setObjectName("forgetPasswd")
#         self.label_4 = QtWidgets.QLabel(self.centralwidget)
#         self.label_4.setGeometry(QtCore.QRect(660, 560, 121, 31))
#         palette = QtGui.QPalette()
#         brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
#         brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
#         brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
#         brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
#         brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
#         brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
#         brush = QtGui.QBrush(QtGui.QColor(57, 209, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.LinkVisited, brush)
#         brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
#         brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
#         brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
#         brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
#         brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
#         brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
#         brush = QtGui.QBrush(QtGui.QColor(57, 209, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.LinkVisited, brush)
#         brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
#         brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
#         brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
#         brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
#         brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
#         brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
#         brush = QtGui.QBrush(QtGui.QColor(57, 209, 255))
#         brush.setStyle(QtCore.Qt.SolidPattern)
#         palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.LinkVisited, brush)
#         self.label_4.setPalette(palette)
#         self.label_4.setObjectName("label_4")
#         MainWindow.setCentralWidget(self.centralwidget)
#
#         self.retranslateUi(MainWindow)
#         QtCore.QMetaObject.connectSlotsByName(MainWindow)
#
#     def retranslateUi(self, MainWindow):
#         _translate = QtCore.QCoreApplication.translate
#         MainWindow.setWindowTitle(_translate("MainWindow", "浙商大招待所"))
#         self.label.setText(_translate("MainWindow", "Now Login！"))
#         self.lineEdit_user.setPlaceholderText(_translate("MainWindow", "username"))
#         self.lineEdit_password.setPlaceholderText(_translate("MainWindow", "password"))
#         self.pushButton.setText(_translate("MainWindow", "登 录"))
#         self.label_2.setText(_translate("MainWindow", "账户名"))
#         self.label_3.setText(_translate("MainWindow", "密码"))
#         self.forgetPasswd.setText(_translate("MainWindow", "忘记密码"))
#         self.label_4.setText(_translate("MainWindow", "忘记密码？"))#登录页

'''class Ui_LoginWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        MainWindow.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../../pictures/酒店.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("\n"
"*{\n"
"font-size:24px;\n"
"font-family:Century Gothic;\n"
"}\n"
"QFrame{\n"
"background:rgba(0,0,0,0.8);\n"
"border-radius:15px;\n"
"}\n"
"#centralwidget{\n"
"border-image:url(D:/pictures/login4.jpg) strectch；\n"
"}\n"
"\n"
"#toolButton{\n"
"background:red;\n"
"border-radius:60px;\n"
"}\n"
"QLabel{\n"
"color:white;\n"
"background:transparent;\n"
"}\n"
"QPushButton{\n"
"background:red;;\n"
"border-radius:15px;\n"
"}\n"
"QPushButton:hover{\n"
"background:#333;\n"
"border-radius:15px;\n"
"background:#49ebff;\n"
"}\n"
"QLineEdit{\n"
"background:transparent;\n"
"border:none;\n"
"color:#717072;\n"
"border-bottom:1px solid #717072;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        self.centralwidget.setFont(font)
        self.centralwidget.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.centralwidget.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(140, 80, 491, 461))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        self.frame.setFont(font)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(180, 70, 151, 41))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.lineEdit_user = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_user.setGeometry(QtCore.QRect(70, 160, 361, 31))
        self.lineEdit_user.setText("")
        self.lineEdit_user.setObjectName("lineEdit_user")
        self.lineEdit_password = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_password.setGeometry(QtCore.QRect(70, 260, 361, 31))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        self.lineEdit_password.setFont(font)
        self.lineEdit_password.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.lineEdit_password.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.lineEdit_password.setText("")
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(30, 370, 421, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(81, 182, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.pushButton.setPalette(palette)
        self.pushButton.setStyleSheet("background-color: rgb(81, 182, 255);\n"
"QPalette pal = startBtn.palette(); \n"
"pal.setColor(QPalette::ButtonText, Qt::red);\n"
"startBtn.setPalette(pal); \n"
"startBtn.setStyleSheet(\"background-color:green\"); ")
        self.pushButton.setObjectName("pushButton")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(70, 120, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(70, 220, 121, 31))
        self.label_3.setObjectName("label_3")
        self.toolButton = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton.setGeometry(QtCore.QRect(330, 20, 121, 121))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(116, 197, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.toolButton.setPalette(palette)
        self.toolButton.setStyleSheet("background-color: rgb(116, 197, 255);")
        self.toolButton.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.toolButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../../../../../../pictures/院徽.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon1)
        self.toolButton.setIconSize(QtCore.QSize(150, 150))
        self.toolButton.setObjectName("toolButton")
        self.forgetPasswd = QtWidgets.QPushButton(self.centralwidget)
        self.forgetPasswd.setGeometry(QtCore.QRect(660, 550, 121, 31))
        self.forgetPasswd.setObjectName("forgetPasswd")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "浙商大招待所"))
        self.label.setText(_translate("MainWindow", "Now Login！"))
        self.lineEdit_user.setPlaceholderText(_translate("MainWindow", "username"))
        self.lineEdit_password.setPlaceholderText(_translate("MainWindow", "password"))
        self.pushButton.setText(_translate("MainWindow", "登 录"))
        self.label_2.setText(_translate("MainWindow", "账户名"))
        self.label_3.setText(_translate("MainWindow", "密码"))
        self.forgetPasswd.setText(_translate("MainWindow", "忘记密码？"))'''






class Ui_LoginWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        MainWindow.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("references/pictures/酒店.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("\n"
"*{\n"
"font-size:24px;\n"
"font-family:Century Gothic;\n"
"}\n"
"QFrame{\n"
"background:rgba(0,0,0,0.8);\n"
"border-radius:15px;\n"
"}\n"
"#centralwidget{\n"
"border-image:url(D:/pictures/login4.jpg) strectch；\n"
"}\n"
"\n"
"#toolButton{\n"
"background:red;\n"
"border-radius:60px;\n"
"}\n"
"QLabel{\n"
"color:white;\n"
"background:transparent;\n"
"}\n"
"QPushButton{\n"
"background:red;;\n"
"border-radius:15px;\n"
"}\n"
"QPushButton:hover{\n"
"background:#333;\n"
"border-radius:15px;\n"
"background:#49ebff;\n"
"}\n"
"QLineEdit{\n"
"background:transparent;\n"
"border:none;\n"
"color:#717072;\n"
"border-bottom:1px solid #717072;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        self.centralwidget.setFont(font)
        self.centralwidget.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.centralwidget.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(130, 80, 501, 461))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        self.frame.setFont(font)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(180, 70, 151, 41))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.lineEdit_user = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_user.setGeometry(QtCore.QRect(70, 160, 361, 31))
        self.lineEdit_user.setText("")
        self.lineEdit_user.setObjectName("lineEdit_user")
        self.lineEdit_password = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_password.setGeometry(QtCore.QRect(70, 260, 361, 31))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        self.lineEdit_password.setFont(font)
        self.lineEdit_password.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.lineEdit_password.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.lineEdit_password.setText("")
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(30, 370, 421, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.pushButton.setPalette(palette)
        self.pushButton.setStyleSheet("background-color: rgb(85, 170, 255);\n"
"QPalette pal = startBtn.palette(); \n"
"pal.setColor(QPalette::ButtonText, Qt::red);\n"
"startBtn.setPalette(pal); \n"
"startBtn.setStyleSheet(\"background-color:rgb(85, 255, 127)en\"); ")
        self.pushButton.setObjectName("pushButton")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(70, 120, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(-1)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(70, 220, 121, 31))
        self.label_3.setObjectName("label_3")
        self.toolButton = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton.setGeometry(QtCore.QRect(310, 20, 121, 121))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.toolButton.setPalette(palette)
        self.toolButton.setStyleSheet("background-color: rgb(85, 170, 255);")
        self.toolButton.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.toolButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("references/pictures/ii.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon1)
        self.toolButton.setIconSize(QtCore.QSize(150, 150))
        self.toolButton.setObjectName("toolButton")
        self.forgetPasswd = QtWidgets.QPushButton(self.centralwidget)
        self.forgetPasswd.setGeometry(QtCore.QRect(660, 550, 121, 31))
        self.forgetPasswd.setObjectName("forgetPasswd")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(0, 0, 801, 601))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap("references/pictures/bg.png"))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        self.label_4.raise_()
        self.frame.raise_()
        self.toolButton.raise_()
        self.forgetPasswd.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "友谊会馆"))
        self.label.setText(_translate("MainWindow", "Now Login！"))
        self.lineEdit_user.setPlaceholderText(_translate("MainWindow", "username"))
        self.lineEdit_password.setPlaceholderText(_translate("MainWindow", "password"))
        self.pushButton.setText(_translate("MainWindow", "登 录"))
        self.label_2.setText(_translate("MainWindow", "账户名"))
        self.label_3.setText(_translate("MainWindow", "密码"))
        self.forgetPasswd.setText(_translate("MainWindow", "忘记密码？"))





class Ui_HomeWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../pictures/酒店.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("QMainWindow{\n"
"border-radius:15px\n"
"}\n"
"QWidget{\n"
"border-radius:15px;\n"
"}\n"
"#frame{\n"
"background: #e1e9ed;}\n"
"QToolButton{\n"
"background:#EAF7FF;\n"
"border-radius:15px;\n"
"}\n"
"QToolButton:hover{\n"
"background:#EAF7FF;\n"
"border-radius:15px;\n"
"background:#49ebff;\n"
"}\n"
"#label{\n"
"text-align:center;\n"
"}\n"
"#welcome{\n"
"text-align:center;\n"
"}\n"
"#toolButton_7\n"
"{\n"
"background:#e1e9ed;\n"
"}")
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.chartbutton = QtWidgets.QToolButton(self.centralwidget)
        self.chartbutton.setGeometry(QtCore.QRect(530, 340, 200, 120))
        self.chartbutton.setMinimumSize(QtCore.QSize(200, 120))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setBold(True)
        font.setWeight(75)
        self.chartbutton.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("references/pictures/chart.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.chartbutton.setIcon(icon1)
        self.chartbutton.setIconSize(QtCore.QSize(70, 70))
        self.chartbutton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.chartbutton.setObjectName("chartbutton")
        self.roombutton = QtWidgets.QToolButton(self.centralwidget)
        self.roombutton.setGeometry(QtCore.QRect(40, 340, 200, 120))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setBold(True)
        font.setWeight(75)
        self.roombutton.setFont(font)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("references/pictures/room.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.roombutton.setIcon(icon2)
        self.roombutton.setIconSize(QtCore.QSize(80, 80))
        self.roombutton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.roombutton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.roombutton.setObjectName("roombutton")
        self.staffbutton = QtWidgets.QToolButton(self.centralwidget)
        self.staffbutton.setGeometry(QtCore.QRect(290, 340, 200, 120))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setBold(True)
        font.setWeight(75)
        self.staffbutton.setFont(font)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("references/pictures/employee.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.staffbutton.setIcon(icon3)
        self.staffbutton.setIconSize(QtCore.QSize(80, 80))
        self.staffbutton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.staffbutton.setObjectName("staffbutton")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(0, 0, 800, 180))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.welcome = QtWidgets.QLabel(self.frame)
        self.welcome.setGeometry(QtCore.QRect(40, 10, 751, 51))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(12)
        self.welcome.setFont(font)
        self.welcome.setText("")
        self.welcome.setAlignment(QtCore.Qt.AlignCenter)
        self.welcome.setObjectName("welcome")
        self.toolButton_7 = QtWidgets.QToolButton(self.frame)
        self.toolButton_7.setGeometry(QtCore.QRect(370, 70, 71, 71))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.toolButton_7.setFont(font)
        self.toolButton_7.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("../../../pictures/hotel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_7.setIcon(icon4)
        self.toolButton_7.setIconSize(QtCore.QSize(100, 100))
        self.toolButton_7.setObjectName("toolButton_7")
        self.modifyPwd = QtWidgets.QToolButton(self.frame)
        self.modifyPwd.setGeometry(QtCore.QRect(710, 150, 81, 21))
        self.modifyPwd.setStyleSheet("background:#e1e9ed")
        self.modifyPwd.setObjectName("modifyPwd")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(0, 0, 771, 451))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap("references/pictures/bg.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.toolButton_7.raise_()
        self.label_3.raise_()
        self.welcome.raise_()
        self.modifyPwd.raise_()
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(310, 540, 181, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(195, 210, 217))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(225, 232, 236))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(97, 105, 108))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(130, 140, 145))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(225, 232, 236))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(195, 210, 217))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(225, 232, 236))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(97, 105, 108))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(130, 140, 145))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(225, 232, 236))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(97, 105, 108))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(225, 232, 236))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(97, 105, 108))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(130, 140, 145))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(97, 105, 108))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(97, 105, 108))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(195, 210, 217))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.label.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(-7, 181, 791, 431))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("references/pictures/bg.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.label_2.raise_()
        self.chartbutton.raise_()
        self.roombutton.raise_()
        self.staffbutton.raise_()
        self.frame.raise_()
        self.label.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "友谊会馆"))
        self.chartbutton.setText(_translate("MainWindow", "维护与报表"))
        self.roombutton.setText(_translate("MainWindow", "客房管理"))
        self.staffbutton.setText(_translate("MainWindow", "员工管理"))
        self.modifyPwd.setText(_translate("MainWindow", "修改密码"))
        self.label.setText(_translate("MainWindow", "酒店管理系统--冉熙"))

class LoginPage(QMainWindow, Ui_LoginWindow):#我将其设置为 main control 页面跳转
    def __init__(self, parent=None):
        super(LoginPage, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.display)
        self.forgetPasswd.clicked.connect(self.forgetPwd)


    def display(self):
        username = self.lineEdit_user.text()
        password = self.lineEdit_password.text()
        global staff
        staff = _initStaff()
        role = staff.userLogin(username,password)
        # 登录成功，返回权限，1为前台,2为管理员
        if role:
            # from mainControl import Homepage
            self.Mainwindow = HomePage()
            self.close()
            self.Mainwindow.show()
        else:
            QMessageBox().information(None, "提示", "账号或密码错误！", QMessageBox.Yes)


    def forgetPwd(self):#未实现
        from service.forgetPwd import fpWindow
        self.fpWindow = fpWindow()
        self.close()
        self.fpWindow.show()
class HomePage(QMainWindow, Ui_HomeWindow):
    def __init__(self,parent=None):
        """
        传入staff全局变量
        :param parent:
        """
        super(HomePage, self).__init__(parent)
        self.setupUi(self)
        # get_staff() 是一个 全局函数，返回当前登录的 Staff 对象。
        # self.staff.sname[0]：获取 员工名字的第一个字符，用于显示欢迎信息。
        self.staff = get_staff()
        print(self.staff.sname[0])
        self.welcome.setText(self.staff.sname + ',你好。你的权限为：' + self.staff.srole + '。今天是' + time.strftime("%Y-%m-%d", time.localtime()))
        #绑定按钮，括号内都是跳转的方法
        # 多个按钮都 绑定了槽函数
        self.staffbutton.clicked.connect(self.gotoStaff)
        self.roombutton.clicked.connect(self.gotoRoom)
        # self.clientbutton.clicked.connect(self.gotoClient)
        # self.orderbutton.clicked.connect(self.gotoOrder)
        self.chartbutton.clicked.connect(self.gotoChart)
        self.modifyPwd.clicked.connect(self.modifyPasswd)

    def modifyPasswd(self):

        self.mpWindow = mpWindow()
        self.close()
        self.mpWindow.show()

    def gotoChart(self):

        self.ChartOp = ChartOp()
        self.ChartOp.show()

    # def gotoOrder(self):
    #     from service.orderOp import OrderOp
    #     self.OrderOp = OrderOp()
    #     self.OrderOp.show()

    # def gotoClient(self):
    #     from service.clientOp import ClientOp
    #     self.ClientOp = ClientOp()
    #     self.ClientOp.show()

    def gotoRoom(self):

        self.RoomOp = RoomOp()
        self.RoomOp.show()

    def gotoStaff(self):

        self.StaffOP = StaffOP()
        self.StaffOP.show()
class ChartOp(QMainWindow, Ui_ReportWindow):
    def __init__(self,parent=None):
        super(ChartOp, self).__init__(parent)
        self.setupUi(self)
        self.staff = get_staff()
        self.welcome.setText(self.staff.sname)
        self.role.setText('权限：'+ self.staff.srole)
        #禁用listwidgeet的滚动条
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget_4.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget_4.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #绑定listwidget与stackedwidget，（实现同步变化，当listwidget的选中行变化时，stackedwidget的页面索引也改变）
        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
        self.listWidget_4.currentRowChanged.connect(self.stackedWidget_2.setCurrentIndex)
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(0)
        self.gridlayout = QGridLayout(self.groupBox)  # 继承容器groupBox
        self.gridlayout2 = QGridLayout(self.groupBox_2) # 同上
        # lineedit1 = self.path1
        # lineedit2 = self.path2
        # lineedit3 = self.path3
        # self.scan.clicked.connect(lambda: self.setBrowerPath(lineedit1))
        # self.scan_2.clicked.connect(lambda: self.setBrowerPath(lineedit2))
        # self.scan_3.clicked.connect(lambda: self.setBrowerPath(lineedit3))
        # self.tosql1.clicked.connect(self.toSQLDB)
        # self.tosql2.clicked.connect(self.toSQLTable)
        # self.toexcel.clicked.connect(self.toExcel)
        # self.ask.clicked.connect(self.help)
        self.showfigure1.clicked.connect(self.figureOrder)
        self.showfigure2.clicked.connect(self.figureCS)

    def setBrowerPath(self,lineedit):
        download_path = QtWidgets.QFileDialog.getExistingDirectory(self,"选择导出目录","D:\pictures")
        lineedit.setText(download_path)

    def toSQLDB(self):
        """导出整个库"""
        key = localConfig['passwd']
        path = self.path1.text()
        os.system("mysqldump -uroot -p%s dbdesign > %s/dbdesign.sql" % (key,path))
        QMessageBox().information(None, "提示", "导出数据库完成！", QMessageBox.Yes)

    def toSQLTable(self):
        """导出某个表"""
        key = localConfig['passwd']
        path = self.path2.text()
        table_name = self.name1.currentText()
        if table_name == '请选择...':
            QMessageBox.information(None,'提示','必须选择一个表',QMessageBox.Yes)
            return False
        os.system("mysqldump -uroot -p%s dbdesign %s > %s/%s.sql" %(key,table_name,path,table_name))
        QMessageBox().information(None, "提示", "导出数据库表完成！", QMessageBox.Yes)

    def toExcel(self):
        """导出某个表到excel"""
        key = localConfig['passwd']
        c = Chart()
        path = self.path3.text()
        table_name = self.name2.currentText()
        if table_name == '请选择...':
            QMessageBox.information(None,'提示','必须选择一个表',QMessageBox.Yes)
            return False
        c.toExcel(path,table_name)
        QMessageBox().information(None, "提示", "导出表格完成！", QMessageBox.Yes)

    def help(self):
        # QMessageBox().information(None, "提示", "client -- 客户表\nteam -- 团队表\nstaff -- 员工表\nroom -- 房间表"
        #                                       "\ncheckin_client -- 入住个人客户表"
        #                                       "\ncheckin_team -- 入住团体表\nbooking_client -- 个人预约表\n"
        #                                       "booking_team -- 团体预约表\nhotelorder -- 完成订单表", QMessageBox.Yes)

        QMessageBox().information(None, "提示", "client -- 客户表\nteam -- 团队表\nstaff -- 员工表\nroom -- 房间表"
                                                "\ncheckin_client -- 入住个人客户表"
                                                "\ncheckin_team -- 入住团体表\nbooking_client -- 个人预约表\n"
                                                "booking_team -- 团体预约表\nhotelorder_v1 -- 完成订单表", QMessageBox.Yes)

    def figureOrder(self):
        self.plotRevenue()
        self.plotOccupy()

    #绘图相关
    def plotRevenue(self):
        c = Chart()
        x, y = c.getRevenue()
        F = Figure_Canvas(width=6, height=2, dpi=100)
        F.axes.plot(x, y)

        F.fig.suptitle("revenue in 7 days")
        F.axes.plot(x, y, marker='o')  # 添加点标记，确保即使某天营业额为 0 也能清晰显示
        F.axes.set_xticks(range(len(x)))  # 设置 x 轴刻度
        # F.axes.set_xticklabels(x, rotation=45)  # 旋转 x 轴标签，避免重叠
        F.axes.set_ylabel("Revenue")  # y 轴添加单位

        # 设置 y 轴范围
        # F.axes.set_ylim(0, 1)  # 强制 y 轴范围为 [0, 1]
        # F.axes.set_ylim(bottom=0)  # 确保 y 轴起点为 0


        self.gridlayout.addWidget(F, 1, 0)

    def plotOccupy(self):
        F1 = Figure_Canvas(width=6, height=2, dpi=100)
        F1.fig.suptitle("occupancy rate in 7 days")
        c = Chart()
        x, y = c.getOccupy()

        F1.axes.plot(x, y, marker='o')  # 画点，防止数据缺失时线段断裂
        F1.axes.set_xticks(range(len(x)))  # 设置 x 轴刻度
        F1.axes.set_ylabel("Occupancy Rate (%)")  # y 轴添加单位

        F1.axes.set_ylim(0, 1)  # 确保 y 轴在 0 到 1 之间（百分比）

        F1.axes.plot(x, y)
        self.gridlayout.addWidget(F1, 2, 0)


    def figureCS(self):
        self.plotClient()
        self.plotStaff()


    def plotStaff(self):
        F1 = Figure_Canvas(width=6, height=2, dpi=100)
        F1.fig.suptitle("components of client")
        c = Chart()
        component = c.getClientStatics()
        content = ['individual', 'team']
        cols = ['r','m']
        F1.axes.pie(component,labels=content,startangle=90,shadow=True,explode=(0,0.1),colors=cols,autopct='%1.1f%%')
        self.gridlayout2.addWidget(F1, 1, 0)

    def plotClient(self):
        c = Chart()
        x, y = c.getStaffStatics()
        F = Figure_Canvas(width=6, height=2, dpi=100)
        F.axes.bar(x, y)
        F.fig.suptitle("  staff performance: the order number they address")
        self.gridlayout2.addWidget(F, 2, 0)
class RoomOp(QMainWindow, Ui_RoomWindow):
    def __init__(self,parent=None):
        super(RoomOp, self).__init__(parent)
        self.setupUi(self)

        self.staff = get_staff()
        self.welcome.setText(self.staff.sname)
        self.role.setText('权限：'+ self.staff.srole)
        #加载头像
        if self.staff.image:  # 确保 staff.image 不是 None
            pixmap = QPixmap()
            if pixmap.loadFromData(self.staff.image):  # 从数据库的 BLOB 加载数据
                # 确保 head 是 QToolButton
                if isinstance(self.head, QToolButton):
                    icon = QIcon(pixmap)
                    self.head.setIcon(icon)

                    # 调整按钮的 iconSize，使其适配头像
                    button_size = self.head.size()  # 获取按钮大小
                    self.head.setIconSize(button_size)  # 让头像匹配按钮尺寸
                else:
                    print("head 组件类型未知，无法设置图片")
            else:
                print("头像加载失败：数据格式错误")
        else:
            print("未找到头像数据")


        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #非常好的时间选择器
        self.inputStartTime.setCalendarPopup(True)
        self.inputEndTime.setCalendarPopup(True)
        self.endtime.setCalendarPopup(True)
        self.tendtime.setCalendarPopup(True)
        self.starttime_booking.setCalendarPopup(True)
        self.endtime_booking.setCalendarPopup(True)
        self.tstarttime_booking.setCalendarPopup(True)
        self.tendtime_booking.setCalendarPopup(True)
        self.starttime_checkout.setCalendarPopup(True)
        self.endtime_checkout.setCalendarPopup(True)

        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_sub.setCurrentIndex(0)
        self.stackedWidget_sub_2.setCurrentIndex(0)
        self.stackedWidget_sub_3.setCurrentIndex(0)
        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
        self.listWidget_2.currentRowChanged.connect(self.stackedWidget_sub.setCurrentIndex)
        self.listWidget_3.currentRowChanged.connect(self.stackedWidget_sub_2.setCurrentIndex)
        self.listWidget_4.currentRowChanged.connect(self.stackedWidget_sub_3.setCurrentIndex)
        #绑定按钮
        self.commitCheckin.clicked.connect(self.singleCheckin)
        self.commitCheckinTeam.clicked.connect(self.teamCheckin)
        self.commitBookingClient.clicked.connect(self.reserveClient)
        self.commitBookingTeam.clicked.connect(self.reserveTeam)
        self.commitDeBookC.clicked.connect(self.cancelReserveC)
        self.commitDeBookT.clicked.connect(self.cancelReserveT)
        self.commitCheckout.clicked.connect(self.checkout)
        self.searchNB.clicked.connect(self.showRoomInfo)
        self.commitTableDel.clicked.connect(self.tableDel)
        self.commitTableModify.clicked.connect(self.tableModify)
        self.commitAddRoom.clicked.connect(self.addRoom)
        self.commitrtcC.clicked.connect(self.reverseToCheckC)
        self.commitrtcT.clicked.connect(self.reverseToCheckT)
        self.commitSearch.clicked.connect(self.findRoom)
        self.scan.clicked.connect(self.setBrowerPath)
        self.reset.clicked.connect(self.reOpen)

    # 下面用布局的方式显示房间
    def showRoom(self,rid,rtype,rstorey,rprice,rdesc,rpic,endtime,i,j):
        self.glayout = self.gridLayout
        self.glayout.setContentsMargins(10,3,10,3)
        # 下面展示信息
        self.flayout = QVBoxLayout()
        self.glayout.addLayout(self.flayout,i,j)
        # QLabel 用于显示图片
        lb = QLabel(self)
        lb.setFixedSize(150, 80)  # 设置图片的固定大小
        lb.setPixmap(QPixmap(rpic))  # 加载图片
        lb.setStyleSheet("border:1px solid white")  # 设置白色边框
        lb.setScaledContents(True)  # 让图片自动适应 QLabel 的大小
        self.flayout.addWidget(lb)  # 添加到布局中

        self.flayout.addWidget(QLabel("房间号:"+rid + "    楼层:"+rstorey,self, styleSheet="color: #990066;"))
        self.flayout.addWidget(QLabel("类型:"+rtype, self, styleSheet="color: #990066;", openExternalLinks=True))
        self.flayout.addWidget(QLabel("描述:"+rdesc+" 价格:"+rprice, self, styleSheet="color: #990066;", openExternalLinks=True))
        pb = QPushButton(self)
        pb.setFixedSize(80,25)
        pb.setText("立即订购")
        pb.setStyleSheet("background:#CCFFCC;border-radius:8px;\n")
        self.flayout.addWidget(pb)
        pb.clicked.connect(lambda: self.pbSwitch(rid,endtime))

    def get_image_from_db(self, rid):
        """
        从数据库中获取房间的图片 (BLOB)
        """
        try:
            r=Room()
            r.cursor.execute("SELECT rpic FROM rooms WHERE room_id=?", (rid,))
            result = r.cursor.fetchone()

            if result:
                return result[0]  # 返回 BLOB 数据
            else:
                return None
        except Exception as e:
            print(f"数据库读取错误: {e}")
            return None

    def reOpen(self):
        self.close()
        self.tmp = RoomOp()
        self.tmp.show()

    def findRoom(self):
        rtype = self.inputType.currentText()
        if rtype == '请选择...':
            rtype = '%%'#如果用户不选择房间类型，则查询全部类型
        print(rtype)
        if self.inputFree.isChecked():
            rstate = 1
        else:
            rstate = 0
        rstorey = self.inputstorey.currentText()
        if rstorey == '请选择...':
            rstorey = '%%'
        rstarttime = self.inputStartTime.date().toPyDate()
        rendtime = self.inputEndTime.date().toPyDate()
        if rendtime <= rstarttime:
            QMessageBox().information(None, "提示", "结束时间必须大于开始时间！", QMessageBox.Yes)
            return False
        price_bottom = self.inputprice1.text()
        if price_bottom == '':
            price_bottom = 0
        price_up = self.inputprice2.text()
        if price_up == '':
            price_up = 10000
        r = Room()
        da = r.showRoom(rtype,rstate,rstorey,rstarttime,rendtime,price_bottom,price_up)
        length = len(da)
        if length == 0:
            QMessageBox().information(None, "提示", "没有符合要求的记录！", QMessageBox.Yes)
            return False
        k = 0
        for i in range(1 + int(length / 3)):
            for j in range(3):
                if k == length:
                    break
                print(k)
                self.showRoom(da[k]['rid'],da[k]['rtype'],da[k]['rstorey'],da[k]['rprice'],da[k]['rdesc'],da[k]['rpic'],rendtime,i,j)
                k = k + 1
        return True




    def pbSwitch(self,rid,endtime):
        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget_sub.setCurrentIndex(0)
        self.crid.setText(rid)
        self.endtime.setDate(endtime)

    def singleCheckin(self):
        cname = self.cname.text()
        cid = self.cid.text()
        cphone = self.cphone.text()
        cage = self.cage.text()
        if self.male.isChecked():
            csex = '男'
        elif self.female.isChecked():
            csex = '女'
        else:
            csex = ''
        crid = self.crid.text()
        endtime = self.endtime.date().toPyDate()
        if endtime <= datetime.date.today():
            QMessageBox().information(None, "提示", "结束时间必须大于今天！", QMessageBox.Yes)
            return False
        remark = self.remark.text()
        r = Room()
        ret = r.singleCheckinDB(cname,cid,cphone,cage,csex,crid,endtime,remark)
        if ret:
            QMessageBox().information(None, "提示", "入住信息登记完成！", QMessageBox.Yes)

    def teamCheckin(self):
        tname = self.tname.text()
        tid = self.tid.text()
        tphone = self.tphone.text()
        trid = self.trid.text()
        tendtime = self.tendtime.date().toPyDate()
        if tendtime <= datetime.date.today():
            QMessageBox().information(None, "提示", "结束时间必须大于今天！", QMessageBox.Yes)
            return False
        tremark = self.tremark.text()
        r = Room()
        print(tid)
        ret = r.teamCheckinDB(tname, tid, tphone,trid,tendtime,tremark)
        if ret:
            QMessageBox().information(None, "提示", "入住信息登记完成！", QMessageBox.Yes)

    def reverseToCheckC(self):
        cid = self.cid_rtc.text()
        rid = self.crid_rtc.text()
        r = Room()
        ret = r.reserveToCheckinC(cid,rid)
        if ret == True:
            QMessageBox().information(None, "提示", "预约入住完成！", QMessageBox.Yes)


    def reverseToCheckT(self):
        tid = self.tid_rtc.text()
        rid = self.trid_rtc.text()
        print(tid,rid)
        r = Room()
        ret = r.reserveToCheckinT(tid, rid)
        if ret:
            QMessageBox().information(None, "提示", "预约入住完成！", QMessageBox.Yes)

    def reserveClient(self):
        cname = self.cname_booking.text()
        cid = self.cid_booking.text()
        cphone = self.cphone_booking.text()
        cage = self.cage_booking.text()
        if self.male_booking.isChecked():
            csex = '男'
        elif self.female_booking.isChecked():
            csex = '女'
        else:
            csex = ''
        crid = self.crid_booking.text()
        cstarttime = self.starttime_booking.date().toPyDate()
        cendtime = self.endtime_booking.date().toPyDate()
        if cendtime <= cstarttime:
            QMessageBox().information(None, "提示", "结束时间必须大于开始时间！", QMessageBox.Yes)
            return False
        cremark = self.remark_booking.text()
        r = Room()
        ret = r.reserveCDB(cname,cid,cphone,cage,csex,crid,cstarttime,cendtime,cremark)
        if ret:
            QMessageBox().information(None, "提示", "预约信息登记完成！", QMessageBox.Yes)

    def reserveTeam(self):
        tname = self.tname_booking.text()
        tid = self.tid_booking.text()
        tphone = self.tphone_booking.text()
        trid = self.trid_booking.text()
        tstarttime = self.tstarttime_booking.date().toPyDate()
        tendtime = self.tendtime_booking.date().toPyDate()
        if tendtime <= tstarttime:
            QMessageBox().information(None, "提示", "结束时间必须大于开始时间！", QMessageBox.Yes)
            return False
        tremark = self.tremark_booking.text()
        r = Room()
        ret = r.reserveTDB(tname,tid,tphone,trid,tstarttime,tendtime,tremark)
        if ret:
            QMessageBox().information(None, "提示", "预约信息登记完成！", QMessageBox.Yes)

    def cancelReserveC(self):
        cancel_cid = self.cid_deb.text()
        cancel_rid = self.crid_deb.text()
        r = Room()
        ret = r.cancelReserveCDB(cancel_cid,cancel_rid)
        if ret:
            QMessageBox().information(None, "提示", "取消预约成功！", QMessageBox.Yes)

    def cancelReserveT(self):
        cancel_tid = self.tid_deb.text()
        cancel_rid = self.trid_deb.text()
        r = Room()
        ret = r.cancelReserveTDB(cancel_tid,cancel_rid)
        if ret:
            QMessageBox().information(None, "提示", "取消预约成功！", QMessageBox.Yes)

    def checkout(self):
        id = self.id_checkout.text()
        if self.single_flag.isChecked():
            check_type = '个人'
        elif self.team_flag.isChecked():
            check_type = '团队'
        else:
            messageBox = QMessageBox()
            messageBox.setWindowTitle('错误')
            messageBox.setText('必须选择个人/团队')
            messageBox.exec_()
            return
        stime = self.starttime_checkout.date().toPyDate()
        etime = self.endtime_checkout.date().toPyDate()
        if etime <= stime:
            QMessageBox().information(None, "提示", "结束时间必须大于开始时间！", QMessageBox.Yes)
            return False
        rid = self.rid_checkout.text()
        pay_type = self.paytype_checkout.text()
        remark = self.remark_checkout.text()
        r = Room()
        ret = r.checkoutDB(check_type,id,rid,pay_type,remark)
        if ret:
            QMessageBox().information(None, "提示", "退房成功！", QMessageBox.Yes)

    def showRoomInfo(self):
        r = Room()
        if int(self.staff.srole) > 1:
            data = r.showAllRoom()
            print(data)
            rowNum = len(data)
            columnNum = len(data[0])
            self.roomTable.setRowCount(rowNum)
            self.roomTable.setColumnCount(columnNum)
            for i,da in enumerate(data):
                da = list(da.values())
                for j in range(columnNum):
                    self.itemContent = QTableWidgetItem(( '%s' )  % (da[j]))
                    self.roomTable.setItem(i, j, self.itemContent)
        else:
            QMessageBox().information(None, "提示", "权限要求不符合！", QMessageBox.Yes)

    def tableDel(self):
        row_selected = self.roomTable.selectedItems()
        if len(row_selected) == 0:
            return
        row = row_selected[0].text()
        r = Room()
        r.delRoom(row)
        row = row_selected[0].row()
        self.roomTable.removeRow(row)
        QMessageBox().information(None, "提示", "删除成功！", QMessageBox.Yes)

    def tableModify(self):
        row_selected = self.roomTable.selectedItems()
        if len(row_selected) == 0:
            return
        row = row_selected[0].row()
        column  = row_selected[0].column()
        value = self.modifyvalue.text()
        r = Room()
        r.modifyRoom(row,column,value)
        tvalue = QTableWidgetItem(('%s') % (value))
        self.roomTable.setItem(row,column, tvalue)
        QMessageBox().information(None, "提示", "修改成功！", QMessageBox.Yes)

    def addRoom(self):
        if int(self.staff.srole) > 1:
            rid = self.rid_add.text()
            rtype = self.rtype_add.currentText()
            rstorey = self.rstorey_add.currentText()
            rprice = self.rprice_add.text()
            rdesc = self.rdesc_add.text()
            rpic = self.path.text()
            r = Room()
            ret = r.addRoom(rid,rtype,rstorey,rprice,rdesc,rpic)
            if ret == True:
                QMessageBox().information(None, "提示", "添加房源成功！", QMessageBox.Yes)
        else:
            QMessageBox().information(None, "提示", "权限不符合要求！", QMessageBox.Yes)

    def setBrowerPath(self):
        download_path = QtWidgets.QFileDialog.getExistingDirectory(self,"选择图片路径","D:\pictures")
        self.path.setText(download_path)
class StaffOP(QMainWindow, Ui_StaffWindow):
    def __init__(self, parent=None):
        super(StaffOP, self).__init__(parent)
        self.setupUi(self)
        # 让日期选择器弹出一个日历窗口，让用户可以方便地选择日期
        self.inputdate.setCalendarPopup(True)
        # 默认显示第一个子页面
        self.stackedWidget.setCurrentIndex(0)
        # 绑定用户信息
        self.staff = get_staff()
        self.welcome.setText(self.staff.sname)
        self.role.setText('权限：'+ self.staff.srole)

        # 加载头像
        if self.staff.image:  # 确保 staff.image 不是 None
            pixmap = QPixmap()
            if pixmap.loadFromData(self.staff.image):  # 从数据库的 BLOB 加载数据
                # 确保 head 是 QToolButton
                if isinstance(self.head, QToolButton):
                    icon = QIcon(pixmap)
                    self.head.setIcon(icon)

                    # 调整按钮的 iconSize，使其适配头像
                    button_size = self.head.size()  # 获取按钮大小
                    self.head.setIconSize(button_size)  # 让头像匹配按钮尺寸
                else:
                    print("head 组件类型未知，无法设置图片")
            else:
                print("头像加载失败：数据格式错误")
        else:
            print("未找到头像数据")



        self.name.setText(self.staff.sname)
        self.sname.setText(self.staff.sname)
        self.ssex.setText(self.staff.ssex)
        self.srole.setText(self.staff.srole)
        self.stime.setText(str(self.staff.stime))
        self.sphone.setText(self.staff.sphone)
        self.sidcard.setText(self.staff.sidcard)
        self.sidcard_2.setText(self.staff.sid)

        # 加载头像
        if self.staff.image:  # 确保 staff.image 不是 None
            pixmap = QPixmap()
            if pixmap.loadFromData(self.staff.image):  # 从数据库的 BLOB 加载数据
                # 确保 head 是 QToolButton
                if isinstance(self.head_2, QToolButton):
                    icon = QIcon(pixmap)
                    self.head_2.setIcon(icon)

                    # 调整按钮的 iconSize，使其适配头像
                    button_size = self.head_2.size()  # 获取按钮大小
                    self.head_2.setIconSize(button_size)  # 让头像匹配按钮尺寸
                else:
                    print("head 组件类型未知，无法设置图片")
            else:
                print("头像加载失败：数据格式错误")
        else:
            print("未找到头像数据")

        # 列表组件设置
        # listWidget 允许 点击不同选项，切换到不同的页面（通常结合 QStackedWidget 使用）。
        # currentRowChanged 信号：当用户点击 listWidget 里的某一项时，会触发这个信号，返回当前选中的行索引。
        # setCurrentIndex()：这个方法用于 切换 QStackedWidget 的页面。
        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 绑定事件
        self.searchNB.clicked.connect(self.searchStaff)
        self.commitAdd.clicked.connect(self.addStaff)
        self.commitDe.clicked.connect(self.deleteStaff)
        self.commitTableDel.clicked.connect(self.tableDel)
        self.commitTableModify.clicked.connect(self.tableModify)

    def searchStaff(self):
        sname = str(self.searchName.text())
        s_sname = '%' + sname + '%'
        # self.staff.srole 代表 当前用户的权限：
        # 1 代表普通员工，无权查询。
        # 2 代表管理员，允许查询。
        if int(self.staff.srole) > 1:
            self.data = self.staff.showAllStaff(s_sname)
            # print(self.data)
            self.rowNum = len(self.data)
            self.columnNum = len(self.data[0])
            print(self.rowNum)
            print(self.columnNum)
            # 更新 QTableWidget
            self.searchTable.setRowCount(self.rowNum)
            self.searchTable.setColumnCount(self.columnNum)
            for i, da in enumerate(self.data):
                # 字典转列表
                da = list(da.values())
                for j in range(self.columnNum):
                    self.itemContent = QTableWidgetItem(( '%s' )  % (da[j]))
                    self.searchTable.setItem(i, j, self.itemContent)
        else:
            QMessageBox().information(None, "提示", "权限不符合要求！", QMessageBox.Yes)

    def addStaff(self):
        sid = self.inputsid.text().split()
        sname = self.inputname.text().split()
        # self.inputmale.isChecked() 检测 性别选择按钮是否被选中。
        if self.inputmale.isChecked():
            ssex = '男'
        elif self.inputfemale.isChecked():
            ssex = '女'
        else:
            ssex = ''
        stime = self.inputdate.date().toPyDate()
        susername = self.inputuser.text().split()
        spwd = self.inputpwd.text().split()
        srole = self.inputrole.text().split()
        sidcard = self.inputidcard.text().split()
        sphone = self.inputphone.text().split()
        if sid == '' or ssex == '' or sname == '' or stime == '' or susername == '' or spwd == '' \
                or srole == '' or sidcard == '' or sphone == '':
            QMessageBox().information(None, "提示", "信息不能为空！", QMessageBox.Yes)
            return False
        if int(self.staff.srole) > 1:
            # 调用Staff类实例的方法
            ret = self.staff.addStaff(sid,sname,ssex,stime,susername,spwd,srole,sidcard,sphone)
            if ret:
                QMessageBox().information(None, "提示", "添加成功！", QMessageBox.Yes)
        else:
            QMessageBox().information(None, "提示", "权限不符合要求！", QMessageBox.Yes)

    def deleteStaff(self):
        """
        根据用户在输入框中的输入，来删除员工。
        """
        sid = self.desid.text()
        sname = self.dename.text()
        sidcard = self.deidcard.text()
        # 数据校验：检验是否有空值
        if sid == '' or sname == '' or sidcard == '':
            # 参数1： None 代表没有指定父窗口（可以改为 self）。
            # 参数2： "提示" 是消息框标题。
            # 参数3： "信息不能为空！" 是提示内容。
            # 参数4： QMessageBox.Yes 代表 确定按钮。
            QMessageBox().information(None, "提示", "信息不能为空！", QMessageBox.Yes)
            return False
        if int(self.staff.srole) > 1:
            self.staff.deleteStaff(sid,sname,sidcard)
            # showAllStaff('%%') 查询所有员工信息，'%%' 是 SQL LIKE 语法的通配符，代表 查询所有员工。
            self.data = self.staff.showAllStaff('%%')
            print(self.data)
            self.rowNum = len(self.data)
            self.columnNum = len(self.data[0])
            self.deleteTable.setRowCount(self.rowNum)
            self.deleteTable.setColumnCount(self.columnNum)
            # data可能是一个列表，每个值是一个员工的字典。
            # enumerate(self.data) 让 i 代表 行索引，da 代表 员工数据（字典）。
            for i, da in enumerate(self.data):
                # 字典转列表
                da = list(da.values())
                # 遍历一个员工数据字典的每个字段。
                for j in range(self.columnNum):
                    self.itemContent = QTableWidgetItem(( '%s' )  % (da[j]))
                    self.deleteTable.setItem(i, j, self.itemContent)
            QMessageBox().information(None, "提示", "删除成功！", QMessageBox.Yes)
        else:
            QMessageBox().information(None, "提示", "权限不符合要求！", QMessageBox.Yes)

    def tableDel(self):
        """
        从表格中获取要删除的员工，并删除

        ![](https://raw.githubusercontent.com/Tsuki-Gor/Pic_Bed_Ob/main/Mixed/M2025/03/2025_03_07__23_24_36_130b54.png)

        """
        # 获取选中的表格行
        row_selected = self.searchTable.selectedItems()
        if len(row_selected) == 0:
            return
        # 获取选中行的 第一个单元格的内容（通常是 员工ID）。
        row = row_selected[0].text()
        # 调用 delStaff() 方法，删除该员工。
        self.staff.delStaff(row)
        # 获取选中行的索引。
        row = row_selected[0].row()
        # 从 QTableWidget 中删除该行。
        self.searchTable.removeRow(row)
        QMessageBox().information(None, "提示", "删除成功！", QMessageBox.Yes)

    def tableModify(self):
        """

        """
        row_selected = self.searchTable.selectedItems()
        if len(row_selected) == 0:
            return
        # 获取当前选中的行索引。这里的行索引是什么？
        row = row_selected[0].row()
        column  = row_selected[0].column()

        # 获取第一列的 sid（当前行第 0 列的值）
        sid_item = self.searchTable.item(row, 0)
        if sid_item is None:
            QMessageBox().information(None, "提示", "无法获取员工ID！", QMessageBox.Yes)
            return

        sid = sid_item.text()  # 提取 sid 值

        # 获取 用户输入的新值。
        value = self.modifyvalue.text()
        # # 调用 modifyStaff() 更新数据库中的员工信息。
        # self.staff.modifyStaff(row,column,value)

        self.staff.modifyStaff_2(sid, column, value)

        tvalue = QTableWidgetItem(('%s') % (value))
        self.searchTable.setItem(row,column, tvalue)
        QMessageBox().information(None, "提示", "修改成功！", QMessageBox.Yes)
class mpWindow(QMainWindow, Ui_MpwdWindow):
    def __init__(self, parent=None):
        super(mpWindow, self).__init__(parent)
        self.setupUi(self)
        # self.retLogin.clicked.connect(self.returnToMain)
        self.commitButton.clicked.connect(self.commit)

    # def returnToMain(self):
    #     from service.mainControl import MainWindow
    #     self.Mainwindow = Ui_LoginWindow()
    #     self.close()
    #     self.Mainwindow.show()

    def commit(self):
        newPwd = self.lineEdit_newpwd.text()
        oldPwd = self.lineEdit_oldpasswd.text()
        sid = self.lineEdit_sid.text()
        if newPwd == '' or oldPwd == '' or sid == '':
            QMessageBox().information(None, "提示", "信息不能为空！", QMessageBox.Yes)
            return False
        s = Staff()
        ret = s.modifyPasswd(sid, newPwd, oldPwd)
        if ret == True:
            QMessageBox().information(None, "提示", "修改密码成功，进入登录页面！", QMessageBox.Yes)
            # from Homepage import HomePage
            self.tmpWindow = LoginPage()
            self.close()
            self.tmpWindow.show()
        else:
            QMessageBox().information(None, "提示", "修改密码失败！", QMessageBox.Yes)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = LoginPage()
    widget.show()
    sys.exit(app.exec_())