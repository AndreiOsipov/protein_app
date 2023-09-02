
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QLineEdit, QWidget, QFileDialog, QLabel, QComboBox
from protein_script import write_to_file


#TODO LIST
#сделать возможность выбора папки++
#сделать возможность выбора расширения файла
#законтачить метод rkfccf MainWindow с методом записи в файл
#os.path.abspath vs os.getcwd()

class MainWindow(QMainWindow):
    def _init_input_fields(self):
        self.file_name_input_line = QLineEdit()
        self.domain_name_line_edit = QLineEdit()
        self.file_name_input_line.setPlaceholderText('input file name')  
        self.domain_name_line_edit.setPlaceholderText('input domain name')
    
    def _init_btns(self):
        self.choice_directory_btn = QPushButton("choice directory")
        self.complite_btn = QPushButton("generate table")
        self.choice_directory_btn.clicked.connect(self.set_dir_name)
        self.complite_btn.clicked.connect(self.print_fields_values)

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

    def print_fields_values(self):
        file_ext = self.ext_selector.itemText(self.ext_selector.currentIndex())
        full_path = os.path.join(self.dir_name, self.file_name_input_line.text()+file_ext)
        domain_name = self.domain_name_line_edit.text()
        self.download_state_label.setText('download in process')
        res = write_to_file(full_path, domain_name)
        if res == True:
            self.download_state_label.setText('download is complite')
        else:
            self.download_state_label.setText('ERROR, maybe domain name is wrong')
    def set_dir_name(self):
        self.dir_name = QFileDialog.getExistingDirectory(self, caption='choice a directory')
        self.dir_label.setText(f'dir name: {self.dir_name}')
app = QApplication(sys.argv)


main_window = MainWindow()
main_window.show()
app.exec()