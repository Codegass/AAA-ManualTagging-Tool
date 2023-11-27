import sys, csv, json  # noqa: E401
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTreeView,
    QTableWidget,
    QHBoxLayout,
    QSplitter,
    QTableWidgetItem,
    QFileSystemModel,
    QFileDialog,
    QMenu
)
from PySide6.QtCore import QDir, Qt, QItemSelection, QModelIndex
from PySide6.QtGui import QAction
from utils import read_config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 默认配置
        self.config_path = 'config.json'
        self.default_config = {
            'splitter_ratio': [1, 3],
            'column_widths': {},
        }
        self.config = read_config(self.config_path, self.default_config)

        self.setWindowTitle("CSV File Viewer")
        self.setGeometry(100, 100, 800, 600)

        # 加载窗口大小
        if 'window_size' in self.config:
            self.resize(*self.config['window_size'])

        # 主布局
        main_layout = QVBoxLayout()

        # 水平布局用于文件树和表格
        h_layout = QHBoxLayout()
        self.splitter = QSplitter(Qt.Horizontal)

        # 设置分割器的初始位置
        self.splitter.setSizes([self.config['splitter_ratio'][0], self.config['splitter_ratio'][1]])

        # 连接分割器位置改变的信号
        self.splitter.splitterMoved.connect(self.on_splitter_moved)

        # 文件树
        self.treeView = QTreeView()
        self.splitter.addWidget(self.treeView)

        # 表格视图
        self.tableView = QTableWidget()
        self.splitter.addWidget(self.tableView)

        h_layout.addWidget(self.splitter)

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
                if file_path.endswith(".csv"):
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
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            data = list(reader)
            self.populate_table(data)

        # 应用列宽度设置
        for i in range(self.tableView.columnCount()):
            header = self.tableView.horizontalHeader().model().headerData(i, Qt.Horizontal)
            if header in self.config['column_widths']:
                self.tableView.setColumnWidth(i, self.config['column_widths'][header])


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

        # 添加上下文菜单
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.on_context_menu)

        # 连接列宽度改变的信号
        self.tableView.horizontalHeader().sectionResized.connect(self.on_column_resized)

        # 应用列宽度设置
        for i in range(self.tableView.columnCount()):
            header = self.tableView.horizontalHeader().model().headerData(i, Qt.Horizontal)
            if header in self.config['column_widths']:
                self.tableView.setColumnWidth(i, self.config['column_widths'][header])


    def on_column_resized(self, index, oldWidth, newWidth):
        header = self.tableView.horizontalHeader().model().headerData(index, Qt.Horizontal)
        self.config['column_widths'][header] = newWidth
        self.save_config()


    def on_context_menu(self, point):
        # 创建上下文菜单
        context_menu = QMenu(self.tableView)

        # 添加菜单项
        for i in range(self.tableView.model().columnCount()):
            action = QAction(self.tableView.model().headerData(i, Qt.Horizontal))
            action.setCheckable(True)
            action.setChecked(not self.tableView.isColumnHidden(i))
            action.setData(i)
            action.triggered.connect(self.toggle_column_visibility)
            context_menu.addAction(action)

        # 显示菜单
        context_menu.exec(self.tableView.mapToGlobal(point))

    def toggle_column_visibility(self):
        action = self.sender()
        column = action.data()
        self.tableView.setColumnHidden(column, not action.isChecked())

    def save_current_csv(self):
        if not hasattr(self, "current_csv_path") or not self.current_csv_path:
            return  # 如果没有当前文件路径，则不执行保存操作

        with open(
            self.current_csv_path, mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            for row in range(self.tableView.rowCount()):
                row_data = []
                for column in range(self.tableView.columnCount()):
                    item = self.tableView.item(row, column)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)

    def on_splitter_moved(self, pos, index):
        sizes = self.splitter.sizes()
        total = sum(sizes)
        self.config['splitter_ratio'] = [sizes[0] / total, sizes[1] / total]
        with open(self.config_path, 'w') as config_file:
            json.dump(self.config, config_file)

    def save_config(self):
        with open(self.config_path, 'w') as config_file:
            json.dump(self.config, config_file)

    def closeEvent(self, event):
        # 保存窗口大小
        self.config['window_size'] = [self.width(), self.height()]
        self.save_config()
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        totalSize = self.splitter.size().width()
        leftSize = totalSize * self.config['splitter_ratio'][0] / sum(self.config['splitter_ratio'])
        rightSize = totalSize * self.config['splitter_ratio'][1] / sum(self.config['splitter_ratio'])
        self.splitter.setSizes([leftSize, rightSize])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
