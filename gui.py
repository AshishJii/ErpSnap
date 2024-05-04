from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QApplication, QDialog, QLineEdit, QTabWidget
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QThread, QObject, QSize
from PyQt6.QtGui import QGuiApplication, QMovie

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
        self.loadingGIF = QMovie('loading.gif')
        self.setupUI()
        self.setupWorkerThread()

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
                color: rgba(237,174,28,100%);
                background-color: rgba(0,0,0,100%);
                text-align: center;
                border-radius: 150px;
                border: 1px solid rgba(237,174,28,100%);
                padding: 5px;
                """)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.title_label = QLabel("ErpSnap v2.1")
        self.title_label.setStyleSheet("font-size: 18px;font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        self.status_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()  # Initially hide loading label
        layout.addWidget(self.status_label)      

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.South)
        layout.addWidget(self.tabs)
        tabsStyles = "border: none;padding: 0;"

        tabNames = ['AttenTab','TtTab','NtcTab']
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
            self.tabs.addTab(tab,tabNames[tabNum])

        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                /*border: none;*/
            }
            QTabBar::tab {
                background-color: rgba(0,0,0,100%);
                color: rgba(237,174,28,100%);
            }
            QTabBar::tab:selected {
                background-color: rgba(237,174,28,100%);
                color: rgba(0,0,0,100%);
            }
            /*QTabWidget::pane > QWidget {
                border: none;
            }*/
            """)
        
        self.fetch_button = QPushButton("Refresh")
        self.fetch_button.clicked.connect(self.fetch_data)
        layout.addWidget(self.fetch_button)

    #override: called when screen is rendered
    def showEvent(self, event): 
        super().showEvent(event)
        screen_gmtry = QGuiApplication.primaryScreen().geometry()
        margin = 30
        x = screen_gmtry.width() - self.width() - margin
        y = margin
        self.move(x,y)

    def fetch_data(self):
        self.status_label.setMovie(self.loadingGIF)
        self.loadingGIF.setScaledSize(QSize(40,17))
        self.loadingGIF.start()
        self.status_label.show()
        QApplication.processEvents()

        if not self.backend.credentials_present():
            print("Credentials not present")
            self.prompt_login()

        print("Credentials present")
        self.thread.start()

    def updateUIwithprogress(self, data):
        print(data)
        self.findChild(QWidget,data[0]).findChild(QLabel).setText(data[1])
        QApplication.processEvents()

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

        self.setLayout(layout)

    def get_credentials(self):
        return self.username_input.text().strip(), self.password_input.text().strip()
