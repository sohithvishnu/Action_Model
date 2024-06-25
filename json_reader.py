import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem

class ActionLabeler(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Action Labeler')
        self.setGeometry(100, 100, 800, 600)

        # Widgets
        self.label_file = QLabel('JSON File:', self)
        self.text_file = QLineEdit(self)
        self.btn_load = QPushButton('Load Actions', self)
        self.btn_load.clicked.connect(self.load_actions)

        self.table_actions = QTableWidget(self)
        self.table_actions.setColumnCount(3)
        self.table_actions.setHorizontalHeaderLabels(['Timestamp', 'Action', 'Details'])

        self.label_add_label = QLabel('Add Label:', self)
        self.text_label = QLineEdit(self)
        self.btn_add_label = QPushButton('Add Label', self)
        self.btn_add_label.clicked.connect(self.add_label)

        # Layout
        layout_top = QHBoxLayout()
        layout_top.addWidget(self.label_file)
        layout_top.addWidget(self.text_file)
        layout_top.addWidget(self.btn_load)

        layout_table = QVBoxLayout()
        layout_table.addWidget(self.table_actions)

        layout_bottom = QHBoxLayout()
        layout_bottom.addWidget(self.label_add_label)
        layout_bottom.addWidget(self.text_label)
        layout_bottom.addWidget(self.btn_add_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_top)
        main_layout.addLayout(layout_table)
        main_layout.addLayout(layout_bottom)

        self.setLayout(main_layout)

    def load_actions(self):
        file_name = self.text_file.text()
        try:
            with open(file_name, 'r') as f:
                actions = json.load(f)
                self.populate_table(actions)
        except FileNotFoundError:
            print(f"File '{file_name}' not found.")

    def populate_table(self, actions):
        self.table_actions.setRowCount(len(actions))
        row = 0
        for action in actions:
            timestamp = str(action.get('timestamp', ''))
            action_name = action.get('action', '')
            details = action.get('details', '')

            self.table_actions.setItem(row, 0, QTableWidgetItem(timestamp))
            self.table_actions.setItem(row, 1, QTableWidgetItem(action_name))
            self.table_actions.setItem(row, 2, QTableWidgetItem(details))
            row += 1

    def add_label(self):
        selected_row = self.table_actions.currentRow()
        if selected_row >= 0:
            label = self.text_label.text()
            self.table_actions.setItem(selected_row, 3, QTableWidgetItem(label))
            # Optionally save the label back to your data structure or file

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ActionLabeler()
    ex.show()
    sys.exit(app.exec_())
