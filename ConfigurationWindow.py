import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QMainWindow, QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
    QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QDateTimeEdit
)
from PyQt5.QtCore import pyqtSignal, QDateTime

class ConfigurationWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сохраненные конфигурации")
        self.setGeometry(100, 100, 800, 600)
        self.connection = sqlite3.connect("components.db")
        self.init_ui()
        self.init_db()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.config_table = QTableWidget(self)
        self.config_table.setColumnCount(3)  # ID, Конфигурация, Дата сохранения
        self.config_table.setHorizontalHeaderLabels(['', 'Конфигурация', 'Дата'])
        layout.addWidget(self.config_table)
        
        #self.load_button = QPushButton("Загрузить конфигурации")
        #self.load_button.clicked.connect(self.load_configurations)
        #layout.addWidget(self.load_button)
        
        self.delete_button = QPushButton("Удалить конфигурацию")
        self.delete_button.clicked.connect(self.delete_configuration)
        layout.addWidget(self.delete_button)
        
        self.setLayout(layout)
    
    def init_db(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                configuration TEXT,
                save_date TEXT
            )
        ''')
        self.connection.commit()

    def load_configurations(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM configurations")
        rows = cursor.fetchall()
        self.config_table.setRowCount(0)
        for row_data in rows:
            row = self.config_table.rowCount()
            self.config_table.insertRow(row)

            self.config_table.setItem(row, 1, QTableWidgetItem(str(row_data[1])))
            self.config_table.setItem(row, 2, QTableWidgetItem(str(row_data[2])))

            # Сохраняем ID в скрытой колонке
            self.config_table.setItem(row, 0, QTableWidgetItem(str(row_data[0])))  # ID
            self.config_table.setColumnHidden(0, True)  # Скрываем колонку с ID
 
    def delete_configuration(self):
        current_row = self.config_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите конфигурацию для удаления")
            return
        config_id = int(self.config_table.item(current_row, 0).text())
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM configurations WHERE id=?", (config_id,))
        self.connection.commit()
        self.load_configurations()

    def save_configuration(self, configuration):
        cursor = self.connection.cursor()
        current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        cursor.execute("INSERT INTO configurations (configuration, save_date) VALUES (?, ?)", (configuration, current_datetime))
        self.connection.commit()