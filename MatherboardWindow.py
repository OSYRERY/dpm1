import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QMainWindow, QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
    QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox
)
from PyQt5.QtCore import pyqtSignal

class MatherboardWindow(QMainWindow):
    motherboard_selected = pyqtSignal(str, str, str, str, str)

    def __init__(self):
        super().__init__()

        self.selected_socket = None
        self.selected_form_factor = None
        self.selected_ram_slots = None
        self.selected_ram_type = None

        self.setWindowTitle("Материнская плата")
        self.setGeometry(100, 100, 1700, 800)

        self.init_database()
        self.init_ui()

    def init_database(self):
        self.connection = sqlite3.connect("components.db")
        self.cursor = self.connection.cursor()

        # Обновленная таблица для материнских плат
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS motherboards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                manufacturer TEXT,
                socket TEXT,
                form_factor TEXT,
                ram_slots INTEGER,
                ram_type TEXT
            )
        ''')
        self.connection.commit()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        header_label = QLabel("Выберите материнскую плату")
        main_layout.addWidget(header_label)

        # Name search field and search button on top
        search_name_layout = QHBoxLayout()
        self.search_name = QLineEdit(self)
        self.search_name.setPlaceholderText("Наименование")
        search_name_layout.addWidget(self.search_name)

        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_motherboards)
        search_name_layout.addWidget(search_button)

        main_layout.addLayout(search_name_layout)

        content_layout = QHBoxLayout()

        # Motherboard table in the main content area
        self.motherboard_table = QTableWidget()
        self.motherboard_table.setColumnCount(8)
        self.motherboard_table.setColumnWidth(0, 280)
        self.motherboard_table.setColumnWidth(3, 180)
        self.motherboard_table.setColumnWidth(4, 180)
        self.motherboard_table.setHorizontalHeaderLabels([
            'Название', 'Производитель', 'Сокет', 'Форм-фактор',
            'Количество слотов ОЗУ', 'Тип памяти', '', ''
        ])
        self.load_motherboards()
        content_layout.addWidget(self.motherboard_table)

        # Filter fields and filter button on the right
        filter_group = QGroupBox("Фильтры")
        filter_group.setFixedSize(400, 250)  # Установить размер группы фильтров
        filter_layout = QGridLayout(filter_group)
        filter_layout.setContentsMargins(5, 5, 5, 5)

        self.search_manufacturer = QLineEdit(self)
        self.search_manufacturer.setPlaceholderText("Производитель")
        filter_layout.addWidget(QLabel("Производитель:"), 0, 0)
        filter_layout.addWidget(self.search_manufacturer, 0, 1)

        self.search_socket = QLineEdit(self)
        self.search_socket.setPlaceholderText("Сокет")
        filter_layout.addWidget(QLabel("Сокет:"), 1, 0)
        filter_layout.addWidget(self.search_socket, 1, 1)

        self.search_form_factor = QLineEdit(self)
        self.search_form_factor.setPlaceholderText("Форм-фактор")
        filter_layout.addWidget(QLabel("Форм-фактор:"), 2, 0)
        filter_layout.addWidget(self.search_form_factor, 2, 1)

        self.search_ram_slots = QLineEdit(self)
        self.search_ram_slots.setPlaceholderText("Количество слотов ОЗУ")
        filter_layout.addWidget(QLabel("Количество слотов ОЗУ:"), 3, 0)
        filter_layout.addWidget(self.search_ram_slots, 3, 1)

        self.search_ram_type = QLineEdit(self)
        self.search_ram_type.setPlaceholderText("Тип памяти")
        filter_layout.addWidget(QLabel("Тип памяти:"), 4, 0)
        filter_layout.addWidget(self.search_ram_type, 4, 1)

        filter_button = QPushButton("Отфильтровать")
        filter_button.clicked.connect(self.search_motherboards)
        filter_layout.addWidget(filter_button, 5, 0, 1, 2)

        content_layout.addWidget(filter_group)
        main_layout.addLayout(content_layout)

        # Control buttons below the table
        control_buttons_layout = QHBoxLayout()

        add_motherboard_button = QPushButton("Добавить материнскую плату")
        add_motherboard_button.clicked.connect(self.add_motherboard_dialog)
        control_buttons_layout.addWidget(add_motherboard_button)

        edit_motherboard_button = QPushButton("Редактировать материнскую плату")
        edit_motherboard_button.clicked.connect(self.edit_motherboard_dialog)
        control_buttons_layout.addWidget(edit_motherboard_button)

        delete_motherboard_button = QPushButton("Удалить материнскую плату")
        delete_motherboard_button.clicked.connect(self.delete_motherboard)
        control_buttons_layout.addWidget(delete_motherboard_button)

        main_layout.addLayout(control_buttons_layout)

    def show_with_socket_filter(self, socket=None, form_factor=None, ram_slots=None, ram_type=None):
        if socket is not None:
            self.selected_socket = socket
        if form_factor is not None:
            self.selected_form_factor = form_factor
        if ram_slots is not None:
            self.selected_ram_slots = ram_slots
        if ram_type is not None:
            self.selected_ram_type = ram_type
        self.load_motherboards()

    def load_motherboards(self):
        self.motherboard_table.setRowCount(0)
        query = "SELECT * FROM motherboards WHERE 1=1"
        params = []
        if self.selected_socket:
            query += " AND socket = ?"
            params.append(self.selected_socket)
        if self.selected_form_factor:
            query += " AND form_factor = ?"
            params.append(self.selected_form_factor)
        if self.selected_ram_slots:
            query += " AND ram_slots >= ?"
            params.append(self.selected_ram_slots)
        if self.selected_ram_type:
            query += " AND ram_type = ?"
            params.append(self.selected_ram_type)

        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.motherboard_table.rowCount()
            self.motherboard_table.insertRow(row)

            self.motherboard_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.motherboard_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.motherboard_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.motherboard_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))
            self.motherboard_table.setItem(row, 4, QTableWidgetItem(str(row_data[5])))
            self.motherboard_table.setItem(row, 5, QTableWidgetItem(str(row_data[6])))

            self.motherboard_table.setItem(row, 6, QTableWidgetItem(str(row_data[0])))  # ID
            self.motherboard_table.setColumnHidden(6, True)  # Скрываем колонку с ID

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_motherboard(row))
            self.motherboard_table.setCellWidget(row, 7, select_button)

    def search_motherboards(self):
        name = self.search_name.text()
        manufacturer = self.search_manufacturer.text()
        socket = self.search_socket.text() if self.search_socket.text() else self.selected_socket
        form_factor = self.search_form_factor.text() if self.search_form_factor.text() else self.selected_form_factor
        ram_slots = self.search_ram_slots.text() if self.search_ram_slots.text() else self.selected_ram_slots
        ram_type = self.search_ram_type.text() if self.search_ram_type.text() else self.selected_ram_type

        query = "SELECT * FROM motherboards WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if manufacturer:
            query += " AND manufacturer = ?"
            params.append(manufacturer)
        if socket:
            query += " AND (socket = ? OR socket = '-')"
            params.append(socket)
        if form_factor:
            query += " AND (form_factor = ? OR form_factor = '-')"
            params.append(form_factor)
        if ram_slots:
            query += " AND (ram_slots >= ? OR ram_slots = '-')"
            params.append(ram_slots)
        if ram_type:
            query += " AND (ram_type = ? OR ram_type = '-')"
            params.append(ram_type)

        self.motherboard_table.setRowCount(0)
        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.motherboard_table.rowCount()
            self.motherboard_table.insertRow(row)

            self.motherboard_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.motherboard_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.motherboard_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.motherboard_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))
            self.motherboard_table.setItem(row, 4, QTableWidgetItem(str(row_data[5])))
            self.motherboard_table.setItem(row, 5, QTableWidgetItem(str(row_data[6])))
            
            self.motherboard_table.setItem(row, 6, QTableWidgetItem(str(row_data[0])))  # ID
            self.motherboard_table.setColumnHidden(6, True)  # Скрываем колонку с ID
            
            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_motherboard(row))
            self.motherboard_table.setCellWidget(row, 7, select_button)

    def add_motherboard_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить материнскую плату")
        dialog_layout = QGridLayout(dialog)

        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        socket_edit = QLineEdit(dialog)
        form_factor_edit = QLineEdit(dialog)
        ram_slots_spin = QSpinBox(dialog)
        ram_slots_spin.setMaximum(1000000)
        ram_type_edit = QLineEdit(dialog)

        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Сокет:", socket_edit)
        form_layout.addRow("Форм-фактор:", form_factor_edit)
        form_layout.addRow("Количество слотов ОЗУ:", ram_slots_spin)
        form_layout.addRow("Тип памяти:", ram_type_edit)

        dialog_layout.addLayout(form_layout, 0, 0)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.add_motherboard(
            name_edit.text(), manufacturer_edit.text(), socket_edit.text(), form_factor_edit.text(),
            ram_slots_spin.value(), ram_type_edit.text(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()


    def add_motherboard(self, name, manufacturer, socket, form_factor, ram_slots, ram_type, dialog):
        try:
            self.cursor.execute('''
                INSERT INTO motherboards (name, manufacturer, socket, form_factor, ram_slots, ram_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, manufacturer, socket, form_factor, ram_slots, ram_type))
            self.connection.commit()
            dialog.accept()
            self.load_motherboards()
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при добавлении данных: {e}")
            dialog.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")
            dialog.reject()


    def edit_motherboard_dialog(self):
        current_row = self.motherboard_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите материнскую плату для редактирования")
            return

        motherboard_id = int(self.motherboard_table.item(current_row, 6).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать материнскую плату")

        dialog_layout = QGridLayout(dialog)

        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        socket_edit = QLineEdit(dialog)
        form_factor_edit = QLineEdit(dialog)
        ram_slots_spin = QSpinBox(dialog)
        ram_slots_spin.setMaximum(1000000)
        ram_type_edit = QLineEdit(dialog)

        # Загрузка текущих значений из базы данных
        self.cursor.execute(
            "SELECT name, manufacturer, socket, form_factor, ram_slots, ram_type FROM motherboards WHERE id=?",
            (motherboard_id,))
        motherboard_data = self.cursor.fetchone()
        name_edit.setText(motherboard_data[0])
        manufacturer_edit.setText(motherboard_data[1])
        socket_edit.setText(motherboard_data[2])
        form_factor_edit.setText(motherboard_data[3])
        ram_slots_spin.setValue(motherboard_data[4])
        ram_type_edit.setText(motherboard_data[5])

        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Сокет:", socket_edit)
        form_layout.addRow("Форм-фактор:", form_factor_edit)
        form_layout.addRow("Количество слотов ОЗУ:", ram_slots_spin)
        form_layout.addRow("Тип памяти:", ram_type_edit)

        dialog_layout.addLayout(form_layout, 0, 0)

        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(lambda: self.edit_motherboard(
            motherboard_id, name_edit.text(), manufacturer_edit.text(),socket_edit.text(),
            form_factor_edit.text(),  ram_slots_spin.value(),
            ram_type_edit.text(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()


    def edit_motherboard(self, motherboard_id, name, manufacturer, socket, form_factor, ram_slots, ram_type, dialog):
        try:
            self.cursor.execute('''
                UPDATE motherboards SET name=?, manufacturer=?, socket=?, form_factor = ?,  ram_slots=?, ram_type = ?
                WHERE id=?
            ''', (name, manufacturer, socket, form_factor,  ram_slots, ram_type, motherboard_id))
            self.connection.commit()
            dialog.accept()
            self.load_motherboards()
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при обновлении данных: {e}")
            dialog.reject()
        except Exception as e:

            QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")
            dialog.reject()

    def delete_motherboard(self):
        current_row = self.motherboard_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите материнскую плату для удаления")
            return

        motherboard_id = int(self.motherboard_table.item(current_row, 6).text())

        confirmation = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить выбранную материнскую плату?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
    )

        if confirmation == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM motherboards WHERE id=?", (motherboard_id,))
                self.connection.commit()
                self.load_motherboards()
            except sqlite3.DatabaseError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при удалении данных: {e}")

    def select_motherboard(self, row):
        current_row = self.motherboard_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите материнскую плату для выбора")
            return

        motherboard_name = self.motherboard_table.item(row, 0).text()  # Название
        socket = self.motherboard_table.item(row, 2).text()
        form_factor = self.motherboard_table.item(row, 3).text()
        ram_slots = self.motherboard_table.item(row, 4).text()
        ram_type = self.motherboard_table.item(row, 5).text()
        id = int(self.motherboard_table.item(row, 6).text())  # Получение ID из скрытой колонки

        confirmation = QMessageBox.question(
            self,
            "Подтверждение выбора",
            f"Вы уверены, что хотите выбрать материнскую плату '{motherboard_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            # Записываем выбранную материнскую плату в промежуточный файл
            try:
                with open('selected_motherboard.txt', 'w') as f:
                    f.write(f"{motherboard_name};")
                # Вместо сообщения через QMessageBox, вызываем сигнал
                self.motherboard_selected.emit(motherboard_name, socket, form_factor, ram_slots, ram_type)

                QMessageBox.information(self, "Выбор сделан", "Выбор материнской платы сохранен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошло исключение при сохранении выбора: {e}")

    def reset_filters(self):
        self.selected_socket = None
        self.selected_form_factor = None
        self.selected_ram_slots = None
        self.selected_ram_type = None
        self.load_motherboards()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MatherboardWindow()
    main_window.show()
    sys.exit(app.exec_())