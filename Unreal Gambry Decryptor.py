import sys
import os
import requests
import ctypes
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QFileDialog, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

LICENSE_URL = "https://raw.githubusercontent.com/SuperNoopXD/decrypt-server/main/licenses.json"
API_URL = "https://SuperNoopXD.pythonanywhere.com/decrypt"

USER_FILE = os.path.join(
    os.getenv("APPDATA"),
    "DecryptTool_user.txt"
)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

myappid = "unreal.gambry.decryptor"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
class DecryptApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unreal Gambry Decryptor")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setFixedSize(520, 320)

        self.setStyleSheet("""
            QWidget {
                background-color: #2B2D31;
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #5865F2;
                color: white;
                border: none;
                padding: 14px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 10px;
            }
        """)

        self.label = QLabel("اختر الملف المشفر لفك التشفير")
        self.label.setAlignment(Qt.AlignCenter)

        self.button = QPushButton("Choose File")
        self.button.clicked.connect(self.decrypt_file)

        self.change_user_btn = QPushButton("Change User")
        self.change_user_btn.clicked.connect(self.change_user)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.change_user_btn)
        layout.addStretch()

        self.setLayout(layout)

    def get_user(self):
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()

        user, ok = QInputDialog.getText(
            self,
            "اسم المستخدم",
            "اكتب اسم المستخدم:"
        )

        if ok and user:
            with open(USER_FILE, "w", encoding="utf-8") as f:
                f.write(user)
            return user

        return None

    def change_user(self):
        if os.path.exists(USER_FILE):
            os.remove(USER_FILE)

        QMessageBox.information(
            self,
            "Done",
            "تم حذف المستخدم الحالي، سيتم طلب يوزر جديد"
        )

    def check_license(self):
        user = self.get_user()
        if not user:
            return False

        try:
            r = requests.get(LICENSE_URL, timeout=10)
            data = r.json()

            expiry = data.get(user)
            if not expiry:
                return False

            return datetime.now().date() <= datetime.strptime(
                expiry, "%Y-%m-%d"
            ).date()

        except:
            return False

    def decrypt_file(self):
        if not self.check_license():
            QMessageBox.critical(
                self,
                "Expired",
                "الاشتراك منتهي أو اليوزر غير موجود"
            )
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "اختار الملف"
        )

        if not file_path:
            return

        try:
            with open(file_path, "rb") as f:
                r = requests.post(API_URL, files={"file": f}, timeout=60)

            folder = os.path.dirname(file_path)
            save_path = os.path.join(folder, "gambry_result.txt")

            with open(save_path, "w", encoding="utf-8") as out:
                out.write(r.text)

            QMessageBox.information(
                self,
                "Done",
                f"تم الحفظ في:\n{save_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DecryptApp()
    window.show()
    sys.exit(app.exec())
