# 导入 sys 模块，用于与 Python 解释器进行交互，如获取命令行参数、退出程序等
import sys
# 从 PyQt5.QtWidgets 模块导入 QApplication、QMainWindow 和 QMessageBox 类，用于创建 GUI 应用程序、主窗口和消息框
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox
# 导入 pymysql 模块，用于与 MySQL 数据库进行交互
import pymysql
# 从 PyQt5.Qt 模块导入所有内容，通常包含了 PyQt5 的核心功能
from PyQt5.Qt import *
# 从 PyQt5.QtCore 模块导入 Qt 类，用于访问 Qt 框架的核心常量和枚举
from PyQt5.QtCore import Qt
# 定义数据库配置字典 localConfig，包含数据库连接所需的各项参数
localConfig = {
    'host': 'localhost',
    # 数据库主机地址
    'port': 3306,
    # 数据库端口号
    'user': 'root',
    # 数据库用户名
    'passwd': 'Tsuki',
    # 数据库密码
    'db': 'dbdesign',
    # 要连接的数据库名称
    'charset': 'utf8',
    # 字符编码
    'cursorclass' : pymysql.cursors.DictCursor    # 数据库操纵指针，使用字典形式返回查询结果
}#数据库配置连接
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

import re

localConfig = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'Tsuki',
    'db': 'dbdesign',
    'charset': 'utf8',
    'cursorclass' : pymysql.cursors.DictCursor    # 数据库操纵指针
}#数据库配置连接
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


class Staff:
    """
    员工操作类
    """
    def __init__(self, config=localConfig):
        self.db = pymysql.connect(host=config['host'],port=config['port'],user=config['user'],
                                      passwd=config['passwd'],db=config['db'],charset=config['charset'],
                                      cursorclass=config['cursorclass'])
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT VERSION()")
        data = self.cursor.fetchone()
        print("Database version : %s " % data['VERSION()'])
        self.username = None
        self.password = None
        self.srole = None
        self.sid = None
        self.sname = None
        self.ssex = None
        self.stime = None
        self.sidcard = None
        self.sphone = None

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
            self.cursor.execute("select * from staff")
            data = self.cursor.fetchall()
            for row in data:
                if row['susername'] == username and row['spassword'] == password:
                    self.username = username
                    self.password = password
                    self.sid = row['sid']
                    self.sname = row['sname']
                    self.ssex = row['ssex']
                    self.stime = row['stime']
                    self.srole = row['srole']
                    self.sidcard = row['sidcard']
                    self.sphone = row['sphone']
                    return row['srole']
        except Exception as e:
            print(e)
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
            self.cursor.execute("select * from staff where sid=%s ", (sid))
            data = self.cursor.fetchall()[0]
            if data['spassword'] == oldPasswd:
                self.cursor.execute("update staff set spassword=%s where sid=%s ",(newPasswd, sid))
                self.db.commit()
                self.password = newPasswd
                print("ok")
                return True
            else:
                print("no")
                return False
        except Exception as e:
            print(e)
            return False

    def forgetPasswd(self, newPasswd,sid,sidcard):
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
            self.cursor.execute("select * from staff where sid=%s",sid)
            data = self.cursor.fetchall()[0]
            print(data)
            if data['sidcard'] == sidcard:
                self.cursor.execute("update staff set spassword=%s where sid=%s",(newPasswd,sid))
                self.db.commit()
                self.password = newPasswd
                return True
            else:
                return False
        except Exception as e:
            print(e)
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
            self.cursor.execute("insert into staff values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sid,sname,ssex,stime,susername,spassword,srole,sidcard,sphone))
            self.db.commit()
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
            self.cursor.execute("select * from staff where sname like %s",(sname))
            data = self.cursor.fetchall()
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
            # sid, 注意这里的逗号，因为 Python 传入单个值时必须是元组 (sid,)，否则 pymysql 会报错。
            self.cursor.execute("delete from staff where sid=%s and sname=%s and sidcard=%s",(sid,sname,sidcard))
            self.db.commit()
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
            self.cursor.execute("delete from staff where sid=%s",(sid))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def modifyStaff(self, row, column, value):
        """
        修改员工信息。

        参数：
            row (int): 需要修改的员工在查询结果中的行索引
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
            self.cursor.execute("select * from staff")
            data = self.cursor.fetchall()


            # 这里有严重错误
            # rid_selected = data[row]['rid']
            # sql = "update room set " + SQL_COLUMN[column] + "='" + value + "'where rid='" + rid_selected +"'"
            # self.cursor.execute(sql)

            sid_selected =  data[row]['sid']
            sql = "update staff set " + SQL_COLUMN[column] + " = %s where sid = %s"
            self.cursor.execute(sql,(value,sid_selected))



            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False
class Room:
    """客房信息操作类"""
    def __init__(self,config=localConfig):
        self.db = pymysql.connect(host=config['host'],port=config['port'],user=config['user'],
                                      passwd=config['passwd'],db=config['db'],charset=config['charset'],
                                      cursorclass=config['cursorclass'])
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT VERSION()")
        data = self.cursor.fetchone()
        print("Database version : %s " % data['VERSION()'])
        self.staff = get_staff()

    def showAllRoom(self):
        self.cursor.execute("select * from room")
        data = self.cursor.fetchall()
        return data

    def showRoom(self,rtype,rstate,rstorey,rstarttime,rendtime,price_bottom,price_up):
        """根据条件检索房间"""
        print(rstarttime, rendtime)
        if rstate == 0:
            self.cursor.execute("select * from room where rtype like %s and rstorey like %s and rprice between %s and %s",
                            (rtype,rstorey,int(price_bottom),int(price_up)))
            data1 = self.cursor.fetchall()
            return data1
        elif rstate == 1:
            self.cursor.execute(
                "select rid from room where rtype like %s and rstorey like %s and rprice between %s and %s",
                (rtype, rstorey, int(price_bottom), int(price_up)))
            data = self.cursor.fetchall()
            list_data = []
            for i in range(len(data)):
                crid = data[i]['rid']
                self.cursor.execute(
                    "select * from checkin_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                    "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)"
                    , (crid, rstarttime, rstarttime, rendtime, rendtime, rstarttime, rendtime,rstarttime,rendtime))
                data1 = self.cursor.fetchall()
                self.cursor.execute(
                    "select * from checkin_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                    "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)"
                    , (crid, rstarttime, rstarttime, rendtime, rendtime, rstarttime, rendtime,rstarttime,rendtime))
                data2 = self.cursor.fetchall()
                self.cursor.execute(
                    "select * from booking_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                    "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)"
                    , (crid, rstarttime, rstarttime, rendtime, rendtime, rstarttime, rendtime,rstarttime,rendtime))
                data3 = self.cursor.fetchall()
                self.cursor.execute(
                    "select * from booking_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                    "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)"
                    , (crid, rstarttime, rstarttime, rendtime, rendtime, rstarttime, rendtime,rstarttime,rendtime))
                data4 = self.cursor.fetchall()
                if data1 == () and data2 == () and data3 == () and data4 == ():
                    list_data.append(crid)
            ret = []
            for i in range(len(list_data)):
                rid_ret = list_data[i]
                self.cursor.execute("select * from room where rid=%s",(rid_ret))
                ret = ret + self.cursor.fetchall()
            return ret

    def addRoom(self,rid,rtype,rstorey,rprice,rdesc,rpic):
        """增加房间"""
        try:
            self.cursor.execute("insert into room values(%s,%s,%s,%s,%s,%s)",(rid,rtype,rstorey,rprice,rdesc,rpic))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            QMessageBox().information(None, "提示", "房间号已存在！", QMessageBox.Yes)
            return False

    def delRoom(self,rid):
        """表格上直接删除"""
        try:
            self.cursor.execute("delete from room where rid=%s",(rid))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def modifyRoom(self, row, column, value):
        """表格上直接修改"""
        # 字典方法得到要修改的列
        SQL_COLUMN = ['rid','rtype','rstorey','rprice','rdesc']
        try:
            self.cursor.execute("select * from room")
            data = self.cursor.fetchall()
            rid_selected = data[row]['rid']
            sql = "update room set " + SQL_COLUMN[column] + "='" + value + "'where rid='" + rid_selected +"'"
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def singleCheckinDB(self,cname,cid,cphone,cage,csex,crid,cendtime,remark):
        """个人入住"""
        # 查询预定表和入住表，判断该房间是否能租出去
        starttime = datetime.date.today()
        self.cursor.execute("select * from checkin_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                            "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)"
                            ,(crid,starttime,starttime,cendtime,cendtime,starttime,cendtime,starttime,cendtime))
        data1 = self.cursor.fetchall()
        self.cursor.execute("select * from checkin_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                            "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)"
                            , (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime,starttime,cendtime))
        data2 = self.cursor.fetchall()
        self.cursor.execute("select * from booking_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                            "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)"
                            , (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime,starttime,cendtime))
        data3 = self.cursor.fetchall()
        self.cursor.execute("select * from booking_team as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                            "or A.end_time>%s and A.start_time<%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)"
                            , (crid, starttime, starttime, cendtime, cendtime, starttime, cendtime,starttime,cendtime))
        data4 = self.cursor.fetchall()
        if data1 != () or data2 != () or data3 != () or data4 != ():
            QMessageBox().information(None, "提示", "该时间段对应房间被占用（入住/预约）！", QMessageBox.Yes)
            return False
        self.cursor.execute("select * from client where cid=%s",(cid))
        data = self.cursor.fetchall()
        if data == ():
            self.cursor.execute("insert into client(cname,cid,cphone,cage,csex,register_sid,accomodation_times) "
                                "values(%s,%s,%s,%s,%s,%s,%s)",(cname,cid,cphone,cage,csex,self.staff.sid,0))
        self.cursor.execute("select * from room where rid=%s",(crid))
        data = self.cursor.fetchall()
        if data == ():
            QMessageBox().information(None, "提示", "没有对应房间号！", QMessageBox.Yes)
            return False
        perPrice = data[0]['rprice']
        totalPrice = int(perPrice) * int((cendtime-starttime).days)
        try:
            self.cursor.execute("insert into checkin_client values(%s,%s,%s,%s,%s,%s,%s)",
                                (crid,cid,starttime,cendtime,totalPrice,self.staff.sid,remark))
            self.db.commit()
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
            self.cursor.execute(
                "select * from checkin_client as A where (A.rid=%s) and (A.end_time>%s and A.start_time<%s "
                "or A.end_time>%s and A.start_time<=%s or A.start_time<=%s and A.end_time>=%s or A.start_time>=%s and A.end_time<=%s)"
                , (trid, tstarttime, tstarttime, tendtime, tendtime, tstarttime, tendtime, tstarttime, tendtime))
            data1 = self.cursor.fetchall()
            print(data1)
            self.cursor.execute("select * from checkin_team as A where (A.rid=%s) and ((A.end_time>%s and A.start_time<%s) "
                                "or (A.end_time>%s and A.start_time<%s) or (A.start_time<=%s and A.end_time>=%s) or (A.start_time>=%s and A.end_time<=%s))"
                                , (trid, tstarttime, tstarttime, tendtime, tendtime, tstarttime, tendtime, tstarttime, tendtime))
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

    def checkoutDB(self,flag, id,rid,payType,remark):
        """两种方式退房"""
        try:
            if flag == '个人':
                self.cursor.execute("select * from checkin_client where rid=%s and cid=%s",(rid,id))
                data = self.cursor.fetchall()
                if data == ():
                    QMessageBox().information(None, "提示", "没有相关入住信息！", QMessageBox.Yes)
                    return False
                else:
                    rid_out = data[0]['rid']
                    cid_out = data[0]['cid']
                    stime_out = data[0]['start_time']
                    etime_out = data[0]['end_time']
                    money = data[0]['total_price']
                    self.cursor.execute("insert into hotelorder(id,ordertype,start_time,end_time,rid,pay_type,money,remark,register_sid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                        (cid_out,flag,stime_out,etime_out,rid_out,payType,money,remark,self.staff.sid))
                    self.cursor.execute("delete from checkin_client where rid=%s and cid=%s",(rid_out,cid_out))
                    self.db.commit()
                    QMessageBox().information(None, "提示", "本次需要支付%s" %money, QMessageBox.Yes)
            elif flag == '团队':
                sum = 0
                for r in re.split(',|，| ',rid):
                    self.cursor.execute(
                        "select * from checkin_team where rid=%s and tid=%s", (r, id))
                    data = self.cursor.fetchall()
                    if data == ():
                        QMessageBox().information(None, "提示", "没有相关入住信息！", QMessageBox.Yes)
                        return False
                    else:
                        rid_out = data[0]['rid']
                        tid_out = data[0]['tid']
                        stime_out = data[0]['start_time']
                        etime_out = data[0]['end_time']
                        money = data[0]['total_price']
                        self.cursor.execute(
                            "insert into hotelorder(id,ordertype,start_time,end_time,rid,pay_type,money,remark,register_sid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                            , (tid_out, flag, stime_out, etime_out, rid_out, payType, money, remark,self.staff.sid))
                        self.cursor.execute("delete from checkin_team where rid=%s and tid=%s", (rid_out, tid_out))
                        self.db.commit()
                        sum = sum + int(money)
                QMessageBox().information(None, "提示", "本次需要支付%s" %str(sum), QMessageBox.Yes)
            return True
        except Exception as e:
            print(e)
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

    def getRevenue(self):
        """
        获取营业额
        """
        list_revenue = []
        list_date = []
        for i in range(7):
            data = ()
            sum = 0
            delta = datetime.timedelta(days=i)
            date = datetime.date.today()
            date_selected = date - delta
            str_date = str(date_selected)
            list_date.append(str_date[5:])
            self.cursor.execute("select money from hotelorder where end_time=%s",(date_selected))
            data = self.cursor.fetchall()
            if data != ():
                for i in range(len(data)):
                    sum = sum + int(data[i]['money'])
            list_revenue.append(sum)
        print(list_revenue)
        print(list_date)
        list_date.reverse()
        return list_date, list_revenue

    def getOccupy(self):
        """
        获取入住率/出租率
        """
        list_occupy = []
        list_date = []
        self.cursor.execute("select count(*) from room")
        totalRoomCount = self.cursor.fetchall()[0]['count(*)']
        print(totalRoomCount)
        for i in range(7):
            data = ()
            occupyRate = 0.0
            delta = datetime.timedelta(days=i)
            date = datetime.date.today()
            date_selected = date - delta
            str_date = str(date_selected)
            list_date.append(str_date[5:])
            self.cursor.execute("select distinct rid from hotelorder where end_time>=%s and start_time<=%s",
                                (date_selected,date_selected))
            data = self.cursor.fetchall()
            print(data)
            if data != ():
                occupyRate = float(len(data) / totalRoomCount)
            list_occupy.append(occupyRate)
        print(list_occupy)
        list_date.reverse()
        return list_date, list_occupy


    def getClientStatics(self):
        """
        获取客户相关数据
        """
        list_clientStatics = []
        self.cursor.execute("select * from hotelorder where ordertype='个人'")
        num_client = len(self.cursor.fetchall())
        self.cursor.execute("select distinct id from hotelorder where ordertype='团队'")
        num_team = len(self.cursor.fetchall())
        list_ret = []
        list_ret.append(num_client)
        list_ret.append(num_team)
        return list_ret


    def getStaffStatics(self):
        """
        获取员工相关数据
        """
        self.cursor.execute("select register_sid,count(*) from hotelorder group by register_sid")
        data = self.cursor.fetchall()
        list_clientNum = []
        list_clientSta = []
        for i in range(len(data)):
            list_clientNum.append(data[i]['register_sid'])
            list_clientSta.append(data[i]['count(*)'])
        print(list_clientNum)
        print(list_clientSta)
        return list_clientNum, list_clientSta
class Figure_Canvas(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # 在父类中激活Figure窗口
        super(Figure_Canvas, self).__init__(self.fig)
        # 第三步：创建一个子图，用于绘制图形用，111表示子图编号
        self.axes = self.fig.add_subplot(111)

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

class Ui_LoginWindow(object):
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
        self.forgetPasswd.setText(_translate("MainWindow", "忘记密码？"))


class Ui_HomeWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("浙商大招待所")
        MainWindow.resize(800, 600)
        MainWindow.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../pictures/酒店.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        icon1.addPixmap(QtGui.QPixmap("../../../../pictures/chart.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        icon2.addPixmap(QtGui.QPixmap("../../../../pictures/coffee.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        icon3.addPixmap(QtGui.QPixmap("../../../../pictures/staff.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        icon4.addPixmap(QtGui.QPixmap("../../../../pictures/hotel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_7.setIcon(icon4)
        self.toolButton_7.setIconSize(QtCore.QSize(100, 100))
        self.toolButton_7.setObjectName("toolButton_7")
        self.modifyPwd = QtWidgets.QToolButton(self.frame)
        self.modifyPwd.setGeometry(QtCore.QRect(710, 150, 81, 21))
        self.modifyPwd.setStyleSheet("background:#e1e9ed")
        self.modifyPwd.setObjectName("modifyPwd")
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
        self.label.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        self.label.setFont(font)
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "浙商大招待所"))
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


    def forgetPwd(self):
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
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget_4.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget_4.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
        QMessageBox().information(None, "提示", "client -- 客户表\nteam -- 团队表\nstaff -- 员工表\nroom -- 房间表"
                                              "\ncheckin_client -- 入住个人客户表"
                                              "\ncheckin_team -- 入住团体表\nbooking_client -- 个人预约表\n"
                                              "booking_team -- 团体预约表\nhotelorder -- 完成订单表", QMessageBox.Yes)

    def figureOrder(self):
        self.plotRevenue()
        self.plotOccupy()


    def plotRevenue(self):
        c = Chart()
        x, y = c.getRevenue()
        F = Figure_Canvas(width=6, height=2, dpi=100)
        F.axes.plot(x, y)

        F.fig.suptitle("revenue in 7 days")
        self.gridlayout.addWidget(F, 1, 0)

    def plotOccupy(self):
        F1 = Figure_Canvas(width=6, height=2, dpi=100)
        F1.fig.suptitle("occupancy rate in 7 days")
        c = Chart()
        x, y = c.getOccupy()
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
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
        lb = QLabel(self)
        lb.setFixedSize(150,80)
        lb.setPixmap(QPixmap(rpic))
        lb.setStyleSheet("border:1px solid white")
        lb.setScaledContents(True)
        self.flayout.addWidget(lb)
        self.flayout.addWidget(QLabel("房间号:"+rid + "    楼层:"+rstorey,self, styleSheet="color: #990066;"))
        self.flayout.addWidget(QLabel("类型:"+rtype, self, styleSheet="color: #990066;", openExternalLinks=True))
        self.flayout.addWidget(QLabel("描述:"+rdesc+" 价格:"+rprice, self, styleSheet="color: #990066;", openExternalLinks=True))
        pb = QPushButton(self)
        pb.setFixedSize(80,25)
        pb.setText("立即订购")
        pb.setStyleSheet("background:#CCFFCC;border-radius:8px;\n")
        self.flayout.addWidget(pb)
        pb.clicked.connect(lambda: self.pbSwitch(rid,endtime))

    def reOpen(self):
        self.close()
        self.tmp = RoomOp()
        self.tmp.show()

    def findRoom(self):
        rtype = self.inputType.currentText()
        if rtype == '请选择...':
            rtype = '%%'
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

        self.name.setText(self.staff.sname)
        self.sname.setText(self.staff.sname)
        self.ssex.setText(self.staff.ssex)
        self.srole.setText(self.staff.srole)
        self.stime.setText(str(self.staff.stime))
        self.sphone.setText(self.staff.sphone)
        self.sidcard.setText(self.staff.sidcard)
        self.sidcard_2.setText(self.staff.sid)

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
        # 获取 用户输入的新值。
        value = self.modifyvalue.text()
        # 调用 modifyStaff() 更新数据库中的员工信息。
        self.staff.modifyStaff(row,column,value)
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