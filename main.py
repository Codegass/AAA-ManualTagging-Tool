import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
                               QTreeView, QTableWidget, QHBoxLayout, QSplitter, QTableWidgetItem)
from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtCore import QDir, Qt
from PySide6.QtWidgets import QFileDialog
import csv
from PySide6.QtCore import QItemSelectionModel, QItemSelection
from PySide6.QtCore import QModelIndex

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSV File Viewer")
        self.setGeometry(100, 100, 800, 600)

        # 主布局
        main_layout = QVBoxLayout()

        # 水平布局用于文件树和表格
        h_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        # 文件树
        self.treeView = QTreeView()
        splitter.addWidget(self.treeView)

        # 表格视图
        self.tableView = QTableWidget()
        splitter.addWidget(self.tableView)

        h_layout.addWidget(splitter)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 选择文件夹的按钮
        self.button = QPushButton("Select Folder")
        self.button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.button)

        # 下一个文件按钮
        self.nextButton = QPushButton("Next File")
        self.nextButton.clicked.connect(self.load_next_file)
        button_layout.addWidget(self.nextButton)

        # 上一个文件按钮
        self.prevButton = QPushButton("Previous File")
        self.prevButton.clicked.connect(self.load_prev_file)
        button_layout.addWidget(self.prevButton)

        # 将布局添加到主布局
        main_layout.addLayout(h_layout)
        main_layout.addLayout(button_layout)

        # 设置中央小部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 文件系统模型
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.treeView.setModel(self.model)

        # 设置文件树的点击事件
        # self.treeView.selectionModel().selectionChanged.connect(self.on_file_selected)
        self.treeView.selectionModel().selectionChanged.connect(self.on_file_selected)


    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.model.setRootPath(folder_path)
            self.treeView.setRootIndex(self.model.index(folder_path))

    def get_file_index(self, step):
        current_index = self.treeView.currentIndex()
        if not current_index.isValid():
            return QModelIndex()

        row = current_index.row() + step
        parent = current_index.parent()
        return self.model.index(row, 0, parent)

    def load_next_file(self):
        self.save_current_csv()  # 保存当前 CSV
        next_index = self.get_file_index(1)
        if next_index.isValid():
            self.treeView.setCurrentIndex(next_index)
            selection = QItemSelection(next_index, next_index)
            self.on_file_selected(selection, QItemSelection())

    def load_prev_file(self):
        self.save_current_csv()  # 保存当前 CSV
        prev_index = self.get_file_index(-1)
        if prev_index.isValid():
            self.treeView.setCurrentIndex(prev_index)
            selection = QItemSelection(prev_index, prev_index)
            self.on_file_selected(selection, QItemSelection())

    def on_file_selected(self, selected, deselected):
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            if index.isValid():
                file_path = self.model.filePath(index)
                if file_path.endswith('.csv'):
                    self.current_csv_path = file_path  # 保存当前 CSV 文件路径
                    self.load_csv(file_path)
                else:
                    self.current_csv_path = None  # 清除当前 CSV 文件路径
                    self.display_not_csv_message()

    def display_not_csv_message(self):
        self.tableView.setRowCount(1)
        self.tableView.setColumnCount(1)
        self.tableView.setItem(0, 0, QTableWidgetItem("NOT CSV"))

    def load_csv(self, file_path):
        self.current_csv_path = file_path
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = list(reader)
            self.populate_table(data)

    def populate_table(self, data):
        self.tableView.clear()
        if not data:
            return

        self.tableView.setRowCount(len(data))
        self.tableView.setColumnCount(len(data[0]))

        for row_idx, row in enumerate(data):
            for col_idx, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                self.tableView.setItem(row_idx, col_idx, item)

    def save_current_csv(self):
        if not hasattr(self, 'current_csv_path') or not self.current_csv_path:
            return  # 如果没有当前文件路径，则不执行保存操作

        with open(self.current_csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in range(self.tableView.rowCount()):
                row_data = []
                for column in range(self.tableView.columnCount()):
                    item = self.tableView.item(row, column)
                    row_data.append(item.text() if item else '')
                writer.writerow(row_data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
