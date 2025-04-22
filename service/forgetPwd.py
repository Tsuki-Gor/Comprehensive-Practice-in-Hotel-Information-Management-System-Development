from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from ui.forgetPwdUI import Ui_fpWindow  # 这里我们稍后会创建这个 UI 文件
from Main import Database  # 导入Database类

class fpWindow(QMainWindow, Ui_fpWindow):
    def __init__(self, parent=None):
        super(fpWindow, self).__init__(parent)
        self.setupUi(self)

        # 绑定按钮事件
        self.btnSubmit.clicked.connect(self.resetPassword)
        self.btnBack.clicked.connect(self.goBack)

    def resetPassword(self):
        """重置密码"""
        sid = self.inputSid.text()
        sidcard = self.inputSidcard.text()
        newPasswd = self.inputNewPasswd.text()

        if not sid or not sidcard or not newPasswd:
            QMessageBox.warning(self, "警告", "所有字段都不能为空！", QMessageBox.Yes)
            return

        try:
            database = Database()
            # 查询员工信息
            data = database.query("SELECT * FROM staff WHERE sid=%s", (sid,))

            if not data:
                QMessageBox.warning(self, "警告", "员工编号不存在！", QMessageBox.Yes)
                return

            # 处理不同数据库返回的列名大小写差异
            sidcard_col = 'sidcard' if 'sidcard' in data[0] else 'SIDCARD'

            if data[0][sidcard_col] != sidcard:
                QMessageBox.warning(self, "警告", "身份证号错误！", QMessageBox.Yes)
                return

            # 更新密码
            database.execute("UPDATE staff SET spassword=%s WHERE sid=%s", (newPasswd, sid))
            QMessageBox.information(self, "成功", "密码已重置！请重新登录。", QMessageBox.Yes)
            self.goBack()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库操作失败：{str(e)}", QMessageBox.Yes)

    def goBack(self):
        """返回登录界面"""
        from Main import LoginPage
        self.loginWindow = LoginPage()
        self.close()
        self.loginWindow.show()
