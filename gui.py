from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QDialog, QLineEdit, QTabWidget, QScrollArea, QHBoxLayout, QMessageBox

from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QThread, QObject, QSize
from PyQt6.QtGui import QGuiApplication, QMovie
import sys
import os

from backend import Backend

class Worker(QObject):
    finished = pyqtSignal(str)
    progress = pyqtSignal(list)

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def run(self):
        print(self)
        self.backend.thread = self
        status = self.backend.get_data()
        self.finished.emit(status)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.mousePressFlag = False
        self.offset = QPoint() # Variable to store offset when dragging
        
        self.backend = Backend()

        # loading gif setup
        BASE_DIR = getattr(sys, '_MEIPASS', os.getcwd())
        loadingIcon = os.path.join(BASE_DIR, 'assets/loading.gif')
        self.loadingGIF = QMovie(loadingIcon)

        self.setupUI()
        self.setupWorkerThread()

        # on startup launch
        if self.backend.credentials_present():
            self.fetchInformation()

    def setupWorkerThread(self):
        self.thread = QThread()
        self.worker = Worker(self.backend)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.updateUIwithData)
        self.worker.progress.connect(self.updateUIwithprogress)
        self.worker.finished.connect(self.thread.quit) # quit thread afterwards

    def setupUI(self):
        self.setWindowTitle("ErpSnap2")
        self.setWindowFlags( Qt.WindowType.SplashScreen)

        # self.setFixedSize(400, 300)
        self.setStyleSheet( """
                background-color: rgba(0,0,0,100%);
            """)
        
        central_widget = QWidget()
        central_widget.setObjectName("mainContainer")
        central_widget.setStyleSheet( """
            QWidget{
                color: rgba(237,174,28,100%);
            }
            #mainContainer{
                text-align: center;
                border: 1px solid rgba(237,174,28,100%);
                border-radius: 5px;                
            }      
            """)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # self.title_label = QLabel("ErpSnap v2.2")
        # self.title_label.setStyleSheet("font-size: 18px;font-weight: bold;")
        # self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # layout.addWidget(self.title_label)

        refresh_button = QPushButton("⟳")
        refresh_button.setStyleSheet("color: black;background-color: rgba(237,174,28,100%);border:none;font-size: 13px;padding-bottom:3px;")
        refresh_button.clicked.connect(self.get_data)
        refresh_button.setFixedSize(13, 13)

        info_button = QPushButton("🛈")
        info_button.clicked.connect(self.show_info_dialog)
        info_button.setFixedSize(13,13)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(info_button)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)   

        self.status_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()  # Initially hide loading label
        layout.addWidget(self.status_label)      

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.South)
        layout.addWidget(self.tabs)
        tabsStyles = "border: none;padding: 0;"
        tabNames = ['Attendance','TimeTable','Notices']
        for tabNum in range(3):
            tab = QWidget()
            tab.setObjectName(tabNames[tabNum])
            tab.setStyleSheet(tabsStyles)
            tab_layout = QVBoxLayout()
            tab.setLayout(tab_layout)
            tab_label = QLabel()
            tab_label.setWordWrap(True)
            tab_label.setOpenExternalLinks(True)
            tab_layout.addWidget(tab_label)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(tab)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setStyleSheet("border: none")
            self.tabs.addTab(scroll_area,tabNames[tabNum])

        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border-bottom: 1px solid rgba(237,174,28,100%);
            }
            QTabBar::tab {
                background-color: rgba(0,0,0,100%);
                color: rgba(237,174,28,100%);
                padding: 3px;
                padding-left: 5px;
                padding-right: 5px;                
                
            }
            QTabBar::tab:selected {
                background-color: rgba(237,174,28,100%);
                color: rgba(0,0,0,100%);
            }
            /*QTabWidget::pane > QWidget {
                border: none;
            }*/
            """)

    #override: called when screen is rendered
    def showEvent(self, event): 
        super().showEvent(event)
        screen_gmtry = QGuiApplication.primaryScreen().geometry()
        margin = 30
        x = screen_gmtry.width() - self.width() - margin
        y = margin
        self.move(x,y)

    def show_info_dialog(self):
        dialog = QMessageBox()
        dialog.setWindowTitle("App Info")
        dialog.setTextFormat(Qt.TextFormat.RichText)
        dialog.setText(
            "<div style='text-align:center;margin: 0 auto'>"
            "<b>App Name:</b> ErpSnap<br>"
            "<b>Version:</b> 2.4<br>"
            "<b>Developer: <a href='https://www.github.com/AshishJii'>Ashish Verma</a><br>"
            "</div>"
        )
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.setWindowFlags(Qt.WindowType.SplashScreen)
        dialog.exec()

    # button click handler
    def get_data(self):
        if not self.backend.credentials_present():
            print("Credentials not present")
            self.prompt_login()
        print("Credentials present")
        self.fetchInformation()

    def fetchInformation(self):
        self.status_label.setText('')
        self.status_label.setMovie(self.loadingGIF)
        self.loadingGIF.setScaledSize(QSize(40,17))
        self.loadingGIF.start()
        self.status_label.show()
        self.thread.start()

    def updateUIwithprogress(self, data):
        print(data)
        self.findChild(QWidget,data[0]).findChild(QLabel).setText(data[1])

    def updateUIwithData(self, response):
        print(response)
        if response =='success':
            self.loadingGIF.stop()
            self.status_label.hide()
        else:
            self.status_label.setText(response)

    def prompt_login(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username, password = dialog.get_credentials()
            print("username",username)
            self.backend.save_credentials(username, password)
            print("Credentials have been saved")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # If left mouse button is pressed, set flag and store offset
            self.mousePressFlag = True
            self.offset = event.pos()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # If left mouse button is released, reset flag
            self.mousePressFlag = False
    
    def mouseMoveEvent(self, event):
        if self.mousePressFlag:
            # If mouse is being dragged, move the window
            self.move(self.pos() + event.pos() - self.offset)

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Enter Credentials")
        self.setWindowFlags(Qt.WindowType.SplashScreen)

        layout = QVBoxLayout()
        self.setObjectName("dialog")
        self.setStyleSheet("""
            QDialog {
                background-color: black;
                border: 1px solid rgba(237, 174, 28, 100%);
                border-radius: 10px;
                padding: 8px;
            }
            QLabel {
                color: rgba(237, 174, 28, 100%);
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #1E1E1E;
                border: 1px solid rgba(237, 174, 28, 100%);
                border-radius: 5px;
                color: rgba(237, 174, 28, 100%);
                padding: 5px;
                margin-bottom: 10px;
            }
            QPushButton {
                background-color: rgba(237, 174, 28, 100%);
                color: #2E2E2E;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 7px;
            }
            QPushButton:hover {
                background-color: rgba(237, 174, 28, 80%);
            }
        """)
        

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # Hide password input
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.accept)
        layout.addWidget(self.submit_button)


        # self.setStyleSheet("""
        #     QLabel {
        #         color: rgba(237, 174, 28, 100%);
        #         text-align: center;
        #     }
        #     QPushButton {
        #         color: rgba(237, 174, 28, 100%);
        #         border-bottom: rgba(237, 174, 28, 100%);
        #     }
        #     #dialog {
        #         border: 1px solid rgba(237, 174, 28, 100%);
        #         border-radius: 5px;                
        #     }
        #     """)

        self.setLayout(layout)

    def get_credentials(self):
        return self.username_input.text().strip(), self.password_input.text().strip()
