
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QLineEdit, QWidget, QFileDialog, QLabel, QComboBox, QStackedLayout
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from proteins_scripts.union_protein_script import ProteinsSquenceDownloader, UnionAPI
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
        
        while self.api.proteins_downloaded_persent < 101:
            self.persent_signal.emit(self.api.proteins_downloaded_persent)
            self.sleep(1)

class MainWindow(QMainWindow):
    
    def _init_handlers(self, domain_name, file_name):
        self.api = UnionAPI(domain_name)
        self.download_handler = DownloadHandler(self.api, file_name)
        self.download_progress_handler = DownloadInfoHandler(self.api)

    def _init_input_fields(self):
        self.file_name_input_line = QLineEdit()
        self.domain_name_line_edit = QLineEdit()
        self.file_name_input_line.setPlaceholderText('input file name')  
        self.domain_name_line_edit.setPlaceholderText('input domain name')

        self.protein_name_input_line = QLineEdit()
        self.protein_name_input_line.setPlaceholderText('input protein sequence name, example: RB1_human')


    def _init_btns(self):
        self.choice_directory_btn = QPushButton("choice directory")
        self.complite_btn = QPushButton("generate table")
        self.protein_complite_btn = QPushButton("Start downloading (long)")
        self.protein_choice_directory_btn = QPushButton('choice directory for proteins downlodads')
        self.choice_directory_btn.clicked.connect(self.set_dir_name)
        self.complite_btn.clicked.connect(self.download_table)

    def _init_labels(self):
        self.dir_label = QLabel(text=f'dir name: {self.dir_name}')
        self.protein_dir_label = QLabel(text=f'dir name: {self.protein_dir_name}')
        self.download_state_label = QLabel(f'state: {self.downloader_state}')
        self.protein_download_state_label = QLabel(f'state: {self.download_proteins_state}')
    
    def _init_states(self):
        self.file_name = ""
        self.domain_name = ""
        self.downloader_state = ""
        self.download_proteins_state = ""

        self.dir_name = os.path.dirname(os.path.abspath(__file__))
        self.protein_dir_name = os.path.dirname(os.path.abspath(__file__))
        
    def _init_ext_combo_box(self):
        self.ext_selector = QComboBox()
        self.ext_selector.addItems(['.tsv'])
    
    def _init_domain_grid(self):
        self.domain_layout = QGridLayout()

        self.domain_layout.addWidget(self.choice_directory_btn, 0,0)
        self.domain_layout.addWidget(self.dir_label, 0, 1)
        self.domain_layout.addWidget(self.file_name_input_line, 1, 0)
        self.domain_layout.addWidget(self.ext_selector, 1, 1)
        self.domain_layout.addWidget(self.domain_name_line_edit, 2, 0)
        self.domain_layout.addWidget(self.download_state_label, 2, 1)
        self.domain_layout.addWidget(self.complite_btn, 3, 0)
    
    def _init_protein_grid(self):
        self.protein_layout = QGridLayout()
        
        self.protein_layout.addWidget(self.protein_choice_directory_btn, 0,0)
        self.protein_layout.addWidget(self.protein_dir_label, 0,1)
        self.protein_layout.addWidget(self.protein_name_input_line, 1,0)
        self.protein_layout.addWidget(self.protein_download_state_label, 1,1)

        self.domain_layout.addWidget(self.protein_complite_btn, 2, 0)

    def _init_stack(self):
        self.stack_layout = QStackedLayout()
        self.stack_layout.addWidget(self.domain_mode_container)
        self.stack_layout.addWidget(self.protein_mode_container)
        self.stack_layout.setCurrentWidget(self.domain_mode_container)

    def __init__(self) -> None:

        super().__init__()
        self.api = None
        
        self.setWindowTitle("Proteins info getter")

        self._init_states()
        self._init_labels()
        self._init_input_fields()
        self._init_btns()
        self._init_ext_combo_box()
        
        self._init_domain_grid()
        self._init_protein_grid()

        self.domain_mode_container = QWidget()
        self.protein_mode_container = QWidget()
        self.main_widget = QWidget()

        
        self.domain_mode_container.setLayout(self.domain_layout)
        self._init_stack()
        
        self.main_widget.setLayout(self.stack_layout)
        self.setCentralWidget(self.main_widget)

    def change_progres(self, progress: float):
        self.download_state_label.setText(f'state: downloaded on {self.download_handler.api.proteins_downloaded_persent}%')

    def download_table(self):
        
        file_ext = self.ext_selector.itemText(self.ext_selector.currentIndex())
        full_path = os.path.join(self.dir_name, self.file_name_input_line.text()+file_ext)
        
        domain_name = self.domain_name_line_edit.text()
        #создание api и потоков
        if self.api is None or (not self.api.is_starting):
            
            # self.download_progress_handler = None
            # self.download_handler = None

            self._init_handlers(domain_name, full_path)

            self.download_progress_handler.persent_signal.connect(self.change_progres)
            self.download_progress_handler.start(priority=QThread.Priority(2))
            self.download_handler.start(priority=QThread.Priority(1))

    def set_dir_name(self):
        self.dir_name = QFileDialog.getExistingDirectory(self, caption='choice a directory')
        self.dir_label.setText(f'dir name: {self.dir_name}')

app = QApplication(sys.argv)


main_window = MainWindow()
main_window.show()
app.exec()