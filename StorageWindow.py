import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QMainWindow, QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
    QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox
)
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal

class StorageWindow(QMainWindow):
    storage_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Установка названия и размеров главного окна
        self.setWindowTitle("Накопитель")
        self.setGeometry(100, 100, 1200, 800)

        self.init_database()
        self.init_ui()

    # Создание или подключение к базе данных и создание таблиц, если они еще не созданы
    def init_database(self):
        self.connection = sqlite3.connect("components.db")
        self.cursor = self.connection.cursor()

        # Создание таблицы накопителей, если она отсутствует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS storages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                manufacturer TEXT,
                capacity INTEGER,
                form_factor TEXT
                
            )
        ''')
        self.connection.commit()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        header_label = QLabel("Выберите накопитель")
        main_layout.addWidget(header_label)

        # Name search field and search button on top
        search_name_layout = QHBoxLayout()
        self.search_name = QLineEdit(self)
        self.search_name.setPlaceholderText("Наименование")
        search_name_layout.addWidget(self.search_name)

        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_storages)
        search_name_layout.addWidget(search_button)

        main_layout.addLayout(search_name_layout)

        content_layout = QHBoxLayout()

        self.storage_table = QTableWidget()
        self.storage_table.setColumnCount(6)
        self.storage_table.setColumnWidth(0, 220)
        self.storage_table.setHorizontalHeaderLabels([
            'Название', 'Производитель', 'Объем(Гб)', 'Интерфейс', '', ''
        ])
        self.load_storages()
        content_layout.addWidget(self.storage_table)

        filter_group = QGroupBox("Фильтры")
        filter_group.setFixedSize(400, 250)
        filter_layout = QGridLayout(filter_group)
        filter_layout.setContentsMargins(5, 5, 5, 5)

        self.search_manufacturer = QLineEdit(self)
        self.search_manufacturer.setPlaceholderText("Производитель")
        filter_layout.addWidget(QLabel("Производитель:"), 0, 0)
        filter_layout.addWidget(self.search_manufacturer, 0, 1)

        self.search_capacity = QLineEdit(self)
        self.search_capacity.setPlaceholderText("Объем (ГБ)")
        filter_layout.addWidget(QLabel("Объем (ГБ):"), 1, 0)
        filter_layout.addWidget(self.search_capacity, 1, 1)

        self.search_form_factor = QLineEdit(self)
        self.search_form_factor.setPlaceholderText("Интерфейс")
        filter_layout.addWidget(QLabel("Интерфейс:"), 2, 0)
        filter_layout.addWidget(self.search_form_factor, 2, 1)

        filter_button = QPushButton("Отфильтровать")
        filter_button.clicked.connect(self.search_storages)
        filter_layout.addWidget(filter_button, 3, 0, 1, 2)

        content_layout.addWidget(filter_group)
        main_layout.addLayout(content_layout)

        # Control buttons below the table
        control_buttons_layout = QHBoxLayout()

        # Кнопка для добавления нового накопителя
        add_storage_button = QPushButton("Добавить накопитель")
        add_storage_button.clicked.connect(self.add_storage_dialog)
        control_buttons_layout.addWidget(add_storage_button)

        edit_storage_button = QPushButton("Редактировать накопитель")
        edit_storage_button.clicked.connect(self.edit_storage_dialog)
        control_buttons_layout.addWidget(edit_storage_button)

        delete_storage_button = QPushButton("Удалить накопитель")
        delete_storage_button.clicked.connect(self.delete_storage)
        control_buttons_layout.addWidget(delete_storage_button)

        main_layout.addLayout(control_buttons_layout)

    # Загрузка данных о накопителях из базы данных в таблицу в UI
    def load_storages(self):
        self.storage_table.setRowCount(0)
        self.cursor.execute("SELECT * FROM storages")
        for row_data in self.cursor.fetchall():
            row = self.storage_table.rowCount()
            self.storage_table.insertRow(row)

            self.storage_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.storage_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.storage_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.storage_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))

            self.storage_table.setItem(row, 4, QTableWidgetItem(str(row_data[0])))
            self.storage_table.setColumnHidden(4, True)

            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(0, 0, 0, 0)
            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_storage(row))
            button_layout.addWidget(select_button)
            button_widget.setLayout(button_layout)
            self.storage_table.setCellWidget(row, 5, button_widget)

    def search_storages(self):
        name = self.search_name.text()
        manufacturer = self.search_manufacturer.text()
        capacity = self.search_capacity.text()
        form_factor = self.search_form_factor.text()

        query = "SELECT * FROM storages WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if manufacturer:
            query += " AND manufacturer = ?"
            params.append(manufacturer)
        if capacity:
            query += " AND capacity = ?"
            params.append(capacity)
        if form_factor:
            query += " AND form_factor = ?"
            params.append(form_factor)

        self.storage_table.setRowCount(0)
        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.storage_table.rowCount()
            self.storage_table.insertRow(row)

            self.storage_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.storage_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.storage_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.storage_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))

            self.storage_table.setItem(row, 4, QTableWidgetItem(str(row_data[0])))
            self.storage_table.setColumnHidden(4, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_storage(row))
            self.storage_table.setCellWidget(row, 5, select_button)

    # Отображение диалогового окна для добавления накопителя
    def add_storage_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить накопитель")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных о новом накопителе
        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        capacity_spin = QSpinBox(dialog)
        capacity_spin.setMaximum(1000000000)
        form_factor_edit = QLineEdit(dialog)
        

        # Добавление виджетов в форму
        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Объем (ГБ):", capacity_spin)
        form_layout.addRow("Интерфейс:", form_factor_edit)
        

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных о накопителе
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.add_storage(
            name_edit.text(), manufacturer_edit.text(), capacity_spin.value(), 
            form_factor_edit.text(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    # Функция, добавляющая данные о новом накопителе в базу данных и обновляющая таблицу
    def add_storage(self, name, manufacturer, capacity, form_factor,  dialog):
        try:
            self.cursor.execute('''
                INSERT INTO storages (name, manufacturer, capacity, form_factor)
                VALUES (?, ?, ?, ?)
            ''', (name, manufacturer, capacity, form_factor, ))
            self.connection.commit()
            dialog.accept()
            self.load_storages()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            dialog.reject()
        except Exception as e:
            print(f"Exception in add_storage: {e}")
            dialog.reject()

    # Редактирование данных о накопителе
    def edit_storage_dialog(self):
        current_row = self.storage_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите накопитель для редактирования")
            return

        storage_id = int(self.storage_table.item(current_row, 4).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать накопитель")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных о накопителе для редактирования
        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        capacity_spin = QSpinBox(dialog)
        capacity_spin.setMaximum(1000000000)
        form_factor_edit = QLineEdit(dialog)
        

        # Заполняем форму данными из базы
        self.cursor.execute("SELECT name, manufacturer, capacity, form_factor FROM storages WHERE id=?",
                            (storage_id,))
        storage_data = self.cursor.fetchone()
        name_edit.setText(storage_data[0])
        manufacturer_edit.setText(storage_data[1])
        capacity_spin.setValue(int(storage_data[2]))
        form_factor_edit.setText(storage_data[3])
        

        # Добавление виджетов в форму
        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Объем (ГБ):", capacity_spin)
        form_layout.addRow("Интерфейс:", form_factor_edit)
        

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных о накопителе
        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(lambda: self.edit_storage(
            storage_id, name_edit.text(), manufacturer_edit.text(), 
            capacity_spin.value(), form_factor_edit.text(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    # Функция для редактирования информации о накопителе
    def edit_storage(self, storage_id, name, manufacturer, capacity, form_factor, dialog):
        try:
            self.cursor.execute('''
                UPDATE storages SET name=?, manufacturer=?, capacity=?, form_factor=? 
                WHERE id=?
            ''', (name, manufacturer, capacity, form_factor, storage_id))
            self.connection.commit()
            dialog.accept()
            self.load_storages()
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при обновлении данных: {e}")
            dialog.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")
            dialog.reject()

    # Удаление накопителя
    def delete_storage(self):
        current_row = self.storage_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите накопитель для удаления")
            return

        storage_id = int(self.storage_table.item(current_row, 4).text())
        reply = QMessageBox.question(
            self, 'Удаление записи', 'Вы действительно хотите удалить выбранный накопитель?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM storages WHERE id=?", (storage_id,))
                self.connection.commit()
                self.load_storages()
            except sqlite3.DatabaseError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при удалении данных: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")

    def select_storage(self, row):
        name = self.storage_table.item(row, 0).text()

        reply = QMessageBox.question(
            self, 'Подтверждение выбора',
            f"Вы уверены, что хотите выбрать накопитель {name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.storage_selected.emit(name)
        else:
            QMessageBox.information(self, 'Выбор отменён', f"Выбор накопителя {name} отменён.")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    configurator = StorageWindow()
    configurator.show()
    sys.exit(app.exec_())