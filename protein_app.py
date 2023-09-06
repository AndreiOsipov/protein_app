
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QLineEdit, QWidget, QFileDialog, QLabel, QComboBox
from protein_script import UnionAPI
from PyQt6.QtCore import QObject, QThread, pyqtSignal

#TODO LIST
#сделать возможность выбора папки++
#сделать возможность выбора расширения файла


class DownloadHandler(QThread):
    def __init__(self, api: UnionAPI, file_name) -> None:
        super().__init__()
        self.api = api
        self.file_name = file_name

    def run(self):
        self.api.write_to_file(self.file_name)

class DownloadInfoHandler(QThread):
    persent_signal = pyqtSignal(float)
    def __init__(self, api: UnionAPI) -> None:
        super().__init__()
        self.api = api

    def run(self):
        while self.api.is_starting:
            self.persent_signal.emit(self.api.proteins_downloaded_persent)

class MainWindow(QMainWindow):
    def _init_handlers(self, domain_name, file_name):
        self.api = UnionAPI(domain_name)
        self.download_handler = DownloadHandler(self.api, file_name)
        self.download_progress_handler = DownloadInfoHandler(self.api)
        self.download_progress_handler.persent_signal.connect(self.change_progres)

    def _init_input_fields(self):
        self.file_name_input_line = QLineEdit()
        self.domain_name_line_edit = QLineEdit()
        self.file_name_input_line.setPlaceholderText('input file name')  
        self.domain_name_line_edit.setPlaceholderText('input domain name')
    
    def _init_btns(self):
        self.choice_directory_btn = QPushButton("choice directory")
        self.complite_btn = QPushButton("generate table")
        self.choice_directory_btn.clicked.connect(self.set_dir_name)
        self.complite_btn.clicked.connect(self.download_table)

    def _init_labels(self):
        self.dir_label = QLabel(text=f'dir name: {self.dir_name}')
        self.download_state_label = QLabel(f'state: {self.downloader_state}')

    def _init_states(self):
        self.file_name = ""
        self.domain_name = ""
        self.downloader_state = ""

        self.dir_name = os.path.dirname(os.path.abspath(__file__))
    
    def _init_ext_combo_box(self):
        self.ext_selector = QComboBox()
        self.ext_selector.addItems(['.tsv'])

    def __init__(self) -> None:

        super().__init__()
        self.api = None
        
        self.setWindowTitle("Proteins info getter")

        self._init_states()
        self._init_labels()
        self._init_input_fields()
        self._init_btns()
        self._init_ext_combo_box()

        self.main_layout = QGridLayout()

        self.main_layout.addWidget(self.choice_directory_btn, 0,0)
        self.main_layout.addWidget(self.dir_label, 0, 1)
        self.main_layout.addWidget(self.file_name_input_line, 1, 0)
        self.main_layout.addWidget(self.ext_selector, 1, 1)
        self.main_layout.addWidget(self.domain_name_line_edit, 2, 0)
        self.main_layout.addWidget(self.download_state_label, 2, 1)
        self.main_layout.addWidget(self.complite_btn, 3, 0)

        self.main_container = QWidget()
        self.main_container.setLayout(self.main_layout)

        self.setCentralWidget(self.main_container)
    
    def change_progres(self, progress: float):
        self.download_state_label.setText(f'state: downloaded on {self.download_handler.api.proteins_downloaded_persent}%')

    def download_table(self):
        
        file_ext = self.ext_selector.itemText(self.ext_selector.currentIndex())
        full_path = os.path.join(self.dir_name, self.file_name_input_line.text()+file_ext)
        
        domain_name = self.domain_name_line_edit.text()
        #создание api и потоков
        if self.api is None or (not self.api.is_starting):
            self._init_handlers(domain_name, full_path)
        
        if not self.api.is_starting:        
            self.download_handler.start()
            self.download_progress_handler.start()

    def set_dir_name(self):
        self.dir_name = QFileDialog.getExistingDirectory(self, caption='choice a directory')
        self.dir_label.setText(f'dir name: {self.dir_name}')

app = QApplication(sys.argv)


main_window = MainWindow()
main_window.show()
app.exec()