import subprocess
import sys
from datetime import datetime
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, \
     QWidget, QPlainTextEdit, QPushButton, QDesktopWidget

SCRIPT = "test.bash"
LOGFILE = "tunnel.log"


class Controller:

    def switch_on(self) -> bool:
        result = self.run_shell_script(SCRIPT, "on")
        print("Tunnel switched ON")
        return result

    def switch_off(self) -> bool:
        result = self.run_shell_script(SCRIPT, "off")
        print("Tunnel switched OFF")
        return result

    @staticmethod
    def get_log(lines=100) -> str:
        with open(LOGFILE) as f:
            data = f.readlines()
        return ''.join(data[-lines:])

    @staticmethod
    def run_shell_script(script: str, param: str) -> bool:
        cmd = f"./{script} {param}"
        with open(LOGFILE, "a") as logfile:
            logfile.write(f"\n-------{datetime.now().strftime('%Y%m%d %H:%M:%S')}--------\n")
            logfile.write(f"Executing: {cmd}\n")
            logfile.flush()
            process = subprocess.Popen(
                cmd, shell=True, executable="/bin/bash", encoding="utf-8",
                stdout=logfile)
            process.communicate()
            if process.returncode != 0:
                print(f"ERROR: {process.returncode}")
                return False
            return True


class LogWindow:

    def __init__(self, width: int = 640, height: int = 800):
        self.window = QWidget()
        self.window.resize(width, height)
        self.move_center()
        # Text box
        self.text_box = QPlainTextEdit(self.window)
        self.text_box.setWindowTitle("Log")
        self.text_box.resize(width - 10, height - 50)
        self.text_box.move(5, 40)
        # Button
        self.button = QPushButton("Close", self.window)
        self.button.clicked.connect(self.window.close)
        self.button.move(5, 5)

    def move_center(self):
        qr = self.window.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.window.move(qr.topLeft())

    def set_text(self, text: str):
        self.text_box.setPlainText(text)
        self.text_box.moveCursor(QTextCursor.End)

    def show(self):
        self.window.show()


class View:

    def __init__(self, application: QApplication, controller: Controller):
        self.app = application
        self.tray = QSystemTrayIcon()
        self.menu = QMenu()
        self.controller = controller
        self.actions = []
        self.log_window = LogWindow()
        self._setup()

    def _setup(self):
        self.app.setQuitOnLastWindowClosed(False)

        # Adding a system tray and menu
        self.tray.setIcon(QIcon("icons/off.png"))
        self.tray.setVisible(True)
        self.tray.setContextMenu(self.menu)

        # ON Tunnel menu
        menu_on = QAction("Tunnel ON")
        menu_on.triggered.connect(self.switch_on)
        self.menu.addAction(menu_on)
        self.actions.append(menu_on)

        # OFF Tunnel menu
        menu_off = QAction("Tunnel OFF")
        menu_off.triggered.connect(self.switch_off)
        self.menu.addAction(menu_off)
        self.actions.append(menu_off)

        # Log menu
        menu_log = QAction("Show log")
        menu_log.triggered.connect(self.show_log)
        self.menu.addAction(menu_log)
        self.actions.append(menu_log)

        # Quit menu
        menu_quit = QAction("Quit")
        menu_quit.triggered.connect(self.app.quit)
        self.menu.addSeparator()
        self.menu.addAction(menu_quit)
        self.actions.append(menu_quit)

    def switch_on(self):
        self.tray.setIcon(QIcon("icons/wait.png"))
        if self.controller.switch_on():
            self.tray.setIcon(QIcon("icons/on.png"))
        else:
            self.tray.setIcon(QIcon("icons/error.png"))

    def switch_off(self):
        self.tray.setIcon(QIcon("icons/wait.png"))
        if self.controller.switch_off():
            self.tray.setIcon(QIcon("icons/off.png"))
        else:
            self.tray.setIcon(QIcon("icons/error.png"))

    def show_log(self):
        data = self.controller.get_log()
        self.log_window.set_text(data)
        self.log_window.show()


if __name__ == "__main__":
    app = QApplication([])
    ctrl = Controller()
    view = View(app, ctrl)
    sys.exit(app.exec_())
