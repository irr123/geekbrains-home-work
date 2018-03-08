import time
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtWidgets
from . import log


class Ui_MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.send_callback = parent.s_handler
        self.stop_callback = parent.stop
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setGeometry(QtCore.QRect(30, 410, 621, 131))
        self.textEdit.setObjectName('textEdit')
        self.textBrowser = QtWidgets.QTextBrowser(self)
        self.textBrowser.setGeometry(QtCore.QRect(30, 10, 741, 371))
        self.textBrowser.setObjectName('textBrowser')
        self.pushButton = QtWidgets.QPushButton('Send', self)
        self.pushButton.setGeometry(QtCore.QRect(670, 440, 111, 61))
        self.pushButton.setObjectName('pushButton')
        self.pushButton.clicked.connect(self.sendHandler)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.stop_callback()

    def sendHandler(self):
        current_txt = self.textEdit.toPlainText()
        if not current_txt:
            return

        self.textEdit.clear()
        log.LOGGER.debug(
            'sendHandler called, {}'.format(current_txt))
        self.textBrowser.append(
            '[{}] {} said: {}'.format(time.time(), 'I', current_txt))
        self.send_callback(current_txt)

    def receiveHandler(self, who, msg):
        self.textBrowser.append('{} said: {}'.format(who, msg))


class Gui(object):
    def __init__(self, s_callback, r_callback, stop_callback=None):
        self.s_callback = s_callback
        self.r_callback = r_callback
        self.stop_callback = stop_callback
        self.app = QApplication([])
        self.main_widget = Ui_MainWindow(self)
        self.main_widget.setGeometry(QtCore.QRect(50, 50, 800, 550))

    def start(self):
        self.main_widget.show()
        try:
            self.app.exec_()
        except Exception:
            self.stop()

    @property
    def r_handler(self):
        return self.main_widget.receiveHandler

    def s_handler(self, msg):
        self.s_callback(msg)

    def stop(self):
        if callable(self.stop_callback):
            self.stop_callback()
        self.app.quit()


def main():
    gui = Gui(
        lambda x: print('Call send-callback', x),
        lambda: print('Call receive-callback'),
        lambda: print('Call stop-callback'))
    gui.start()


if __name__ == '__main__':
    log.setup_logger('debug')
    main()
