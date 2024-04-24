from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QApplication, QDialog, QLineEdit
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QThread, QObject
from backend import Backend

class Worker(QObject):
    finished = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def run(self):
        print(self)
        self.backend.thread = self
        data = self.backend.handle_button_click() 
        self.finished.emit(data)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.mousePressFlag = False
        self.offset = QPoint() # Variable to store offset when dragging
        
        self.backend = Backend(login_callback=self.prompt_login)
        self.setupUI()

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

        self.title_label = QLabel("ErpSnap v2.0")
        self.title_label.setStyleSheet("font-size: 18px;font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        self.status_label = QLabel("Loading...", alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()  # Initially hide loading label
        layout.addWidget(self.status_label)
        
        self.data_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.data_label)        
        
        self.fetch_button = QPushButton("Refresh")
        self.fetch_button.clicked.connect(self.fetch_data)
        layout.addWidget(self.fetch_button)
        
        self.setCentralWidget(central_widget)

    def fetch_data(self):
        self.status_label.show()
        self.data_label.hide()
        QApplication.processEvents()

        self.thread = QThread()
        self.worker = Worker(self.backend)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.updateUIwithData)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.updateUIwithprogress)
        self.thread.start()

    def updateUIwithprogress(self, data):
        print(data)
        self.status_label.setText(data)
        self.status_label.show()

    def updateUIwithData(self, data):
        print(data)
        self.status_label.hide()
        self.data_label.show()
        if data is not None:
            self.data_label.setText(str(data))
        else:
            self.data_label.setText("ERror Occured. Try again:")

    def prompt_login(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username, password = dialog.get_credentials()
            print("username",username)
            self.backend.save_credentials(username, password)
            self.fetch_data()

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
