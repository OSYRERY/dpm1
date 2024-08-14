import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal


class RAMWindow(QMainWindow):
    ram_selected = pyqtSignal(str, str, str)
    def __init__(self):
        super().__init__()
        
        self.selected_ram_slots = None
        self.selected_ram_type = None

        # Установка названия и размеров главного окна
        self.setWindowTitle("Оперативная память")
        self.setGeometry(100, 100, 1700, 800)

        # Инициализация базы данных и интерфейса пользователя
        self.init_database()
        self.init_ui()

    # Создание или подключение к базе данных и создание таблиц, если они еще не созданы
    def init_database(self):
        self.connection = sqlite3.connect("components.db")
        self.cursor = self.connection.cursor()

        # Создание таблицы оперативной памяти, если она отсутствует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ram (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                manufacturer TEXT,
                typeRAM TEXT,
                num_modules INTEGER,
                module_size INTEGER,
                total_size INTEGER
            )
        ''')
        self.connection.commit()

    # Инициализация графического интерфейса пользователя (UI)
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        header_label = QLabel("Выберите оперативную память")
        main_layout.addWidget(header_label)

        # Name search field and search button on top
        search_name_layout = QHBoxLayout()
        self.search_name = QLineEdit(self)
        self.search_name.setPlaceholderText("Наименование")
        search_name_layout.addWidget(self.search_name)

        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_ram)
        search_name_layout.addWidget(search_button)

        main_layout.addLayout(search_name_layout)

        content_layout = QHBoxLayout()

        # Установка таблицы для отображения информации об оперативной памяти
        self.ram_table = QTableWidget()
        self.ram_table.setColumnCount(8)
        self.ram_table.setColumnWidth(0, 260)
        self.ram_table.setColumnWidth(4, 180)
        self.ram_table.setColumnWidth(5, 180)
        self.ram_table.setHorizontalHeaderLabels([
            'Название', 'Производитель', 'Тип памяти', 'Кол-во плашек', 'Объем плашки (Гб)', 'Суммарный объем (Гб)', '' , '' # Пустой заголовок для кнопок выбора
        ])
        # Загрузка списка оперативной памяти в таблицу
        self.load_ram()
        content_layout.addWidget(self.ram_table)

        filter_group = QGroupBox("Фильтры")
        filter_group.setFixedSize(400, 250)
        filter_layout = QGridLayout(filter_group)
        filter_layout.setContentsMargins(5, 5, 5, 5)

        self.search_manufacturer = QLineEdit(self)
        self.search_manufacturer.setPlaceholderText("Производитель")
        filter_layout.addWidget(QLabel("Производитель:"), 0, 0)
        filter_layout.addWidget(self.search_manufacturer, 0, 1)

        self.search_type = QLineEdit(self)
        self.search_type.setPlaceholderText("Тип памяти")
        filter_layout.addWidget(QLabel("Тип памяти:"), 1, 0)
        filter_layout.addWidget(self.search_type, 1, 1)

        self.search_modules = QLineEdit(self)
        self.search_modules.setPlaceholderText("Кол-во плашек")
        filter_layout.addWidget(QLabel("Кол-во плашек:"), 2, 0)
        filter_layout.addWidget(self.search_modules, 2, 1)

        self.search_module_size = QLineEdit(self)
        self.search_module_size.setPlaceholderText("Объем плашки (Гб)")
        filter_layout.addWidget(QLabel("Объем плашки (Гб):"), 3, 0)
        filter_layout.addWidget(self.search_module_size, 3, 1)

        self.search_total_size = QLineEdit(self)
        self.search_total_size.setPlaceholderText("Суммарный объем (Гб)")
        filter_layout.addWidget(QLabel("Суммарный объем (Гб):"), 4, 0)
        filter_layout.addWidget(self.search_total_size, 4, 1)

        filter_button = QPushButton("Отфильтровать")
        filter_button.clicked.connect(self.search_ram)
        filter_layout.addWidget(filter_button, 5, 0, 1, 2)

        content_layout.addWidget(filter_group)
        main_layout.addLayout(content_layout)

        control_buttons_layout = QHBoxLayout()

        add_ram_button = QPushButton("Добавить оперативную память")
        add_ram_button.clicked.connect(self.add_ram_dialog)
        control_buttons_layout.addWidget(add_ram_button)

        edit_ram_button = QPushButton("Редактировать оперативную память")
        edit_ram_button.clicked.connect(self.edit_ram_dialog)
        control_buttons_layout.addWidget(edit_ram_button)

        delete_ram_button = QPushButton("Удалить оперативную память")
        delete_ram_button.clicked.connect(self.delete_ram)
        control_buttons_layout.addWidget(delete_ram_button)

        main_layout.addLayout(control_buttons_layout)

    def show_with_ram_filters(self, ram_slots=None, ram_type=None):
        if ram_slots is not None:
            self.selected_ram_slots = ram_slots
        if ram_type is not None:
            self.selected_ram_type = ram_type
        self.load_ram()

    def load_ram(self):
        self.ram_table.setRowCount(0)
        query = "SELECT * FROM ram WHERE 1=1"
        params = []
        if self.selected_ram_type:
            query += " AND typeRAM = ?"
            params.append(self.selected_ram_type)
        if self.selected_ram_slots:
            query += " AND num_modules <= ?"
            params.append(self.selected_ram_slots)

        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.ram_table.rowCount()
            self.ram_table.insertRow(row)

            self.ram_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.ram_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.ram_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.ram_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))
            self.ram_table.setItem(row, 4, QTableWidgetItem(str(row_data[5])))
            self.ram_table.setItem(row, 5, QTableWidgetItem(str(row_data[6])))

            self.ram_table.setItem(row, 6, QTableWidgetItem(str(row_data[0])))
            self.ram_table.setColumnHidden(6, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda checked, row=row: self.select_ram(row))
            self.ram_table.setCellWidget(row, 7, select_button)

    def search_ram(self):
        name = self.search_name.text()
        manufacturer = self.search_manufacturer.text()
        typeRAM = self.search_type.text() if self.search_type.text() else self.selected_ram_type
        num_modules = self.search_modules.text() if self.search_modules.text() else self.selected_ram_slots
        module_size = self.search_module_size.text()
        total_size = self.search_total_size.text()

        query = "SELECT * FROM ram WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if manufacturer:
            query += " AND manufacturer = ?"
            params.append(manufacturer)
        if typeRAM:
            query += " AND typeRAM = ?"
            params.append(typeRAM)
        if num_modules and num_modules.isdigit():
            query += " AND num_modules = ?"
            params.append(int(num_modules))
        if module_size and module_size.isdigit():
            query += " AND module_size = ?"
            params.append(int(module_size))
        if total_size and total_size.isdigit():
            query += " AND total_size = ?"
            params.append(int(total_size))

        self.ram_table.setRowCount(0)
        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.ram_table.rowCount()
            self.ram_table.insertRow(row)

            self.ram_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.ram_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.ram_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.ram_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))
            self.ram_table.setItem(row, 4, QTableWidgetItem(str(row_data[5])))
            self.ram_table.setItem(row, 5, QTableWidgetItem(str(row_data[6])))

            self.ram_table.setItem(row, 6, QTableWidgetItem(str(row_data[0])))
            self.ram_table.setColumnHidden(6, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda checked, row=row: self.select_ram(row))
            self.ram_table.setCellWidget(row, 7, select_button)

    # Отображение диалогового окна для добавления оперативной памяти
    def add_ram_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить оперативную память")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных о новой оперативной памяти
        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        type_edit = QLineEdit(dialog)
        num_modules_spin = QSpinBox(dialog)
        module_size_spin = QSpinBox(dialog)
        total_size_spin = QSpinBox(dialog)  # Можно автоматически рассчитать, умножив количество на размер модуля
        num_modules_spin.setMaximum(1000000)
        module_size_spin.setMaximum(1000000)
        total_size_spin.setMaximum(1000000)


        # Добавление виджетов в форму
        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Тип памяти:", type_edit)
        form_layout.addRow("Кол-во плашек:", num_modules_spin)
        form_layout.addRow("Объем плашки (Гб):", module_size_spin)
        form_layout.addRow("Суммарный объем (Гб):", total_size_spin)  # этот параметр можно вычислять на лету или скрыть

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных об оперативной памяти
        save_button = QPushButton("Сохранить")
        # Сохранение оперативной памяти и закрытие диалога по клику
        save_button.clicked.connect(lambda: self.add_ram(
            name_edit.text(), manufacturer_edit.text(), type_edit.text(),
            num_modules_spin.value(), module_size_spin.value(), total_size_spin.value(), dialog
        ))

        close_button = QPushButton("Отмена")
        # Закрытие диалогового окна без сохранения
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    # Функция, добавляющая данные о новой оперативной памяти в базу данных и обновляющая таблицу
    def add_ram(self, name, manufacturer, typeRAM, num_modules, module_size, total_size, dialog):
        try:
            self.cursor.execute('''
                INSERT INTO ram (name, manufacturer, typeRAM, num_modules, module_size, total_size)
                VALUES (?, ?, ?, ?, ?, ?)''',
                                (name, manufacturer, typeRAM, num_modules, module_size, total_size))
            self.connection.commit()
            dialog.accept()
            self.load_ram()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            dialog.reject()
        except Exception as e:
            print(f"Exception in add_ram: {e}")
            dialog.reject()

    def edit_ram_dialog(self):
        # Получаем текущую выбранную строку
        current_row = self.ram_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите оперативную память для редактирования")
            return

        # Получаем ID оперативной памяти из строки для последующей выборки данных
        ram_id = int(self.ram_table.item(current_row, 6).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать оперативную память")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных об оперативной памяти для редактирования
        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        type_edit = QLineEdit(dialog)
        num_modules_spin = QSpinBox(dialog)
        module_size_spin = QSpinBox(dialog)
        total_size_spin = QSpinBox(dialog)  # Можно автоматически рассчитать, умножив количество на размер модуля
        num_modules_spin.setMaximum(1000000)
        module_size_spin.setMaximum(1000000)
        total_size_spin.setMaximum(1000000)

        # Заполняем форму данными из базы
        self.cursor.execute(
            "SELECT name, manufacturer, typeRAM, num_modules, module_size, total_size FROM ram WHERE id=?",
            (ram_id,))
        ram_data = self.cursor.fetchone()
        name_edit.setText(ram_data[0])
        manufacturer_edit.setText(ram_data[1])
        type_edit.setText(ram_data[2])
        num_modules_spin.setValue(int(ram_data[3]))
        module_size_spin.setValue(int(ram_data[4]))
        total_size_spin.setValue(int(ram_data[5]))




        # Добавление виджетов в форму
        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Тип памяти:", type_edit)
        form_layout.addRow("Кол-во плашек:", num_modules_spin)
        form_layout.addRow("Объем плашки (Гб):", module_size_spin)
        form_layout.addRow("Суммарный объем (Гб):", total_size_spin)  # этот параметр можно вычислять на лету или скрыть

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных об оперативной памяти
        save_button = QPushButton("Сохранить изменения")
        # Сохранение изменений оперативной памяти и закрытие диалога по клику
        save_button.clicked.connect(lambda: self.edit_ram(
            ram_id, name_edit.text(), manufacturer_edit.text(), type_edit.text(),
            num_modules_spin.value(), module_size_spin.value(), total_size_spin.value(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    # Функция для редактирования информации об оперативной памяти
    def edit_ram(self, ram_id, name, manufacturer, typeRAM, num_modules, module_size, total_size, dialog):
        try:
            self.cursor.execute('''UPDATE ram SET name=?, manufacturer=?, typeRAM=?,
                   num_modules=?, module_size=?, total_size=? WHERE id=?''',
                                (name, manufacturer, typeRAM, num_modules, module_size, total_size, ram_id))
            self.connection.commit()
            dialog.accept()
            self.load_ram()
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при обновлении данных: {e}")
            dialog.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")
            dialog.reject()

    # Функция для удаления оперативной памяти
    def delete_ram(self):
        current_row = self.ram_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите оперативную память для удаления")
            return

        ram_id = int(self.ram_table.item(current_row, 6).text())
        reply = QMessageBox.question(self, 'Удаление записи', 'Вы действительно хотите удалить выбранную оперативную память?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM ram WHERE id=?", (ram_id,))
                self.connection.commit()
                self.load_ram()
            except sqlite3.DatabaseError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при удалении данных: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")

    def select_ram(self, row):
        name = self.ram_table.item(row, 0).text()
        typeRAM = self.ram_table.item(row, 2).text()
        num_modules = self.ram_table.item(row, 3).text()

        reply = QMessageBox.question(
            self, 'Подтверждение выбора',
            f"Вы уверены, что хотите выбрать оперативную память {name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.ram_selected.emit(name, typeRAM, num_modules)
            QMessageBox.information(self, 'Выбор сделан', f"Выбор оперативной памяти {name} подтвержден.")
        else:
            QMessageBox.information(self, 'Выбор отменен', f"Выбор оперативной памяти {name} отменен.")

    

    def reset_filters(self):
        self.selected_ram_slots = None
        self.selected_ram_type = None
        self.load_ram()

# Точка входа в приложение
if __name__ == '__main__':
    app = QApplication(sys.argv)
    configurator = RAMWindow()
    configurator.show()
    sys.exit(app.exec_())