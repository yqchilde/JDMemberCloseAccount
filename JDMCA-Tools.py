import os
import sys
import yaml
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from JDMCA_Form import Ui_JDMCA
from utils.config import get_config
import subprocess
from utils.getchromedriver import check_driver_version

mirror_dic = {
    "清华": "https://pypi.tuna.tsinghua.edu.cn/simple/",
    "豆瓣": "https://pypi.douban.com/simple/",
    "阿里": "https://mirrors.aliyun.com/pypi/simple/",
    "腾讯": "https://mirrors.cloud.tencent.com/pypi/simple"
}


def excuteCommand(com):
    ex = subprocess.Popen(com, stdout=subprocess.PIPE, shell=True)
    out, err = ex.communicate()
    status = ex.wait()
    print("cmd in:", com)
    print("cmd out: ", out.decode())
    return out.decode()


class JDMCA_Tools(QtWidgets.QWidget, Ui_JDMCA):
    def Log_info(self, log):
        self.logbox.setPlainText(self.logbox.toPlainText() + log + "\n")

    def __init__(self):
        super(JDMCA_Tools, self).__init__()
        self.setupUi(self)
        self.resize(self.width(), self.height())
        self.setMaximumSize(self.width(), self.height())
        self.setMinimumSize(self.width(), self.height())
        self.form_max_height = self.height()
        self.KeyTable.setColumnWidth(0, 80)
        self.KeyTable.setColumnWidth(1, 550)
        row_cnt = self.KeyTable.rowCount()
        for i in range(12):
            self.KeyTable.insertRow(row_cnt)
        self.Chk_Muilt.clicked.connect(self.Chk_Muilt_Clicked)
        self.Btn_Run.clicked.connect(self.Btn_Run_Clicked)
        self.Btn_InstallPip.clicked.connect(self.Btn_InstallPip_Clicked)
        self.Btn_unInstallPip.clicked.connect(self.Btn_unInstallPip_Clicked)
        self.Btn_InstallPip_One.clicked.connect(self.Btn_InstallPip_One_Clicked)
        self.Btn_downchromedriver.clicked.connect(self.Btn_downchromedriver_Clicked)
        self.setWindowTitle("退会辅助工具 V0.0.3")
        self.init()

    def Btn_downchromedriver_Clicked(self):
        check_driver_version(".\drivers\chromedriver.exe")

    def Btn_InstallPip_One_Clicked(self):
        cmd = '' + self.pipcmd + ' install -i ' + mirror_dic[self.Combox_mirror.currentText()] + " " +\
              self.Txt_ModuleName.text() + "\r\npause"
        excuteCommand(cmd)
        res = excuteCommand(self.pipcmd + " list")
        modulename = self.Txt_ModuleName.text().split("=")[0].replace("~", "").replace(">", "").replace("<", "").upper()
        if modulename in res.upper():
            QMessageBox.information(self, '提示', "安装{}成功".format(self.Txt_ModuleName.text()))
        else:
            if modulename.replace("_","-") in res.upper():
                QMessageBox.information(self, '提示', "安装{}成功".format(self.Txt_ModuleName.text()))
            else:
                QMessageBox.warning(self, '提示', "依赖安装好像有问题。。。")
        pass

    def CheckModuleState(self):
        print('判断依赖安装情况')
        res = excuteCommand(self.pipcmd + " list")
        return 'opencv-python'.upper() in res.upper()

    def Btn_InstallPip_Clicked(self):
        print('升级pip')
        excuteCommand('' + self.pythoncmd + ' -m pip install --upgrade pip')
        print('安装依赖')
        print("选择源:" + self.Combox_mirror.currentText())
        cmd = ('' + self.pipcmd + ' install  -i ' + mirror_dic[self.Combox_mirror.currentText()] +
               ' torch requests~=2.25.1 PyYAML~=5.4.1 psutil~=5.8.0 selenium~=3.141.0 easyocr~=1.3.2 Pillow~=8.2.0 '
               'urllib3~=1.26.5 baidu-aip==2.2.18.0 websockets~=9.1 opencv_python~=4.5.2.54 '
               'func-timeout~=4.3.5 msedge-selenium-tools~=3.141.3 numpy~=1.19.5')
        excuteCommand(cmd)
        if self.CheckModuleState():
            QMessageBox.information(self, '提示', "安装opencv-python成功，其他依赖应该也OK了")
        else:
            QMessageBox.warning(self, '提示', "依赖安装好像有问题。。。")

    def Btn_unInstallPip_Clicked(self):
        cmd = ('' + self.pipcmd + ' uninstall -y opencv_python')
        res = excuteCommand(cmd)
        res = excuteCommand(self.pipcmd + " list")
        if 'opencv_python'.upper() not in res.upper():
            QMessageBox.information(self, '提示', "卸载opencv-python成功")
        else:
            QMessageBox.warning(self, '提示', "好像卸载失败了。。。")

    def Chk_Muilt_Clicked(self):
        if self.Chk_Muilt.isChecked():
            self.Chk_LocalMsg.setChecked(True)
            self.Chk_LocalMsg.setEnabled(False)
            self.Txt_Cookie.setEnabled(False)
            self.KeyTable.setEnabled(True)
        else:
            self.Chk_LocalMsg.setEnabled(True)
            self.Txt_Cookie.setEnabled(True)
            self.KeyTable.setEnabled(False)

    def init(self):
        config = yaml.safe_load(open(get_file("config.yaml"), 'r', encoding='utf-8'))
        try:
            self.Chk_Auto.setChecked(config["main"]["cron_enable"])
            self.Chk_Muilt.setChecked(config["multi"]["multi_enable"])

            row_idx = 0
            for i in range(1, 10):
                try:
                    self.KeyTable.setItem(row_idx, 0, QTableWidgetItem(str(config["multi"]["port" + str(i)])))
                    self.KeyTable.setItem(row_idx, 1, QTableWidgetItem(config["multi"]["key" + str(i)]))
                    row_idx += 1
                except Exception as e:
                    print(str(e))
        except:
            self.Chk_Auto.setEnabled(False)
            self.Chk_Muilt.setEnabled(False)
            self.KeyTable.setEnabled(False)

        self.Txt_Cookie.setPlainText(config["cookie"])
        self.Chk_LocalMsg.setChecked(1 - config["sms_captcha"]["jd_wstool"])
        self.Chk_CloudID.setChecked(config["shop"]["add_remote_shop_data"])
        self.Chk_Headless.setChecked(config["selenium"]["headless"])

        self.Chk_Muilt_Clicked()
        self.GetPythonCmd()
        pass

    def GetPythonCmd(self):
        """
        检测系统python环境
        :return:
        """
        self.pythoncmd = ''
        self.pipcmd = ''

        res = os.popen("python --version")
        res = res.read()
        if 'python 3'.upper() in res.upper():
            self.pythoncmd = 'python'
        else:
            res = os.popen("python3 --version")
            res = res.read()
            if 'python 3'.upper() in res.upper():
                self.pythoncmd = 'python3'

        res = os.popen("pip --version")
        res = res.read()
        if 'python 3'.upper() in res.upper():
            self.pipcmd = 'pip'
        else:
            res = os.popen("pip3 --version")
            res = res.read()
            if 'python 3'.upper() in res.upper():
                self.pipcmd = 'pip3'

        errmsg = ''
        if self.pythoncmd == '':
            errmsg += '请安装python3.6~3.9版本\n'
        if self.pipcmd == '':
            errmsg += '请安装pip3\n'
        if errmsg != '':
            QMessageBox.warning(self, '错误', errmsg)
            sys.exit()

    def saveconfig(self):
        """
        保存配置文件
        :return:
        """
        config = yaml.safe_load(open(get_file("config.yaml"), 'r', encoding='utf-8'))
        try:
            config["main"]["cron_enable"] = self.Chk_Auto.isChecked()
            config["multi"]["multi_enable"] = self.Chk_Muilt.isChecked()
            row_idx = 1
            for i in range(0, 10):
                try:
                    if self.KeyTable.item(i, 0).text() != '' or self.KeyTable.item(i, 1).text() != '':
                        config["multi"]["port" + str(row_idx)] = int(self.KeyTable.item(i, 0).text())
                        config["multi"]["key" + str(row_idx)] = self.KeyTable.item(i, 1).text()
                        row_idx += 1
                except Exception as e:
                    print(str(e))
        except:
            pass

        config["cookie"] = self.Txt_Cookie.toPlainText()
        config["sms_captcha"]["jd_wstool"] = bool(1 - self.Chk_LocalMsg.isChecked())
        config["shop"]["add_remote_shop_data"] = self.Chk_CloudID.isChecked()
        config["selenium"]["headless"] = self.Chk_Headless.isChecked()

        with open(get_file("config.yaml"), "w", encoding="utf-8") as f:
            yaml.dump(config, f)

    def Btn_Run_Clicked(self):
        """
        跑啊~~~~
        :return:
        """
        # 备份配置文件
        print(os.path.exists("./config.yaml.bak1"))
        if os.path.exists("./config.yaml.bak1") == False:
            from shutil import copy
            copy("./config.yaml", "./config.yaml.bak1")
        # 保存配置
        self.saveconfig()

        if not self.CheckModuleState():
            self.Btn_InstallPip_Clicked()

        # 检测并下载chromedriver
        check_driver_version(".\drivers\chromedriver.exe")
        import threading
        threading.Thread(target=self.run_cmd_thread).start()



    def run_cmd_thread(self):
        # 启动进程
        if self.Chk_Muilt.isEnabled():
            pyscript = 'Multi_Close.py'
        else:
            pyscript = 'main.py'
        excuteCommand(self.pythoncmd + ' ' + pyscript)


def get_file(file_name=""):
    """
    获取文件绝对路径, 防止在某些情况下报错
    :param file_name: 文件名
    :return:
    """
    return os.path.join(os.path.split(sys.argv[0])[0], file_name)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = JDMCA_Tools()
    myshow.show()
    sys.exit(app.exec_())
