from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton
from PyQt5 import QtCore

class Ui_fpWindow(object):
    def setupUi(self, fpWindow):
        fpWindow.setObjectName("fpWindow")
        fpWindow.resize(400, 300)

        self.centralwidget = QWidget(fpWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 标题
        self.labelTitle = QLabel("忘记密码", self.centralwidget)
        self.labelTitle.setGeometry(150, 20, 100, 30)

        # 输入框
        self.labelSid = QLabel("员工编号:", self.centralwidget)
        self.labelSid.setGeometry(50, 60, 80, 30)
        self.inputSid = QLineEdit(self.centralwidget)
        self.inputSid.setGeometry(150, 60, 200, 30)

        self.labelSidcard = QLabel("身份证号:", self.centralwidget)
        self.labelSidcard.setGeometry(50, 100, 80, 30)
        self.inputSidcard = QLineEdit(self.centralwidget)
        self.inputSidcard.setGeometry(150, 100, 200, 30)

        self.labelNewPasswd = QLabel("新密码:", self.centralwidget)
        self.labelNewPasswd.setGeometry(50, 140, 80, 30)
        self.inputNewPasswd = QLineEdit(self.centralwidget)
        self.inputNewPasswd.setGeometry(150, 140, 200, 30)
        self.inputNewPasswd.setEchoMode(QLineEdit.Password)

        # 按钮
        self.btnSubmit = QPushButton("确认修改", self.centralwidget)
        self.btnSubmit.setGeometry(50, 200, 120, 40)

        self.btnBack = QPushButton("返回", self.centralwidget)
        self.btnBack.setGeometry(230, 200, 120, 40)

        fpWindow.setCentralWidget(self.centralwidget)

        _translate = QtCore.QCoreApplication.translate
        fpWindow.setWindowTitle(_translate("fpWindow", "忘记密码"))
