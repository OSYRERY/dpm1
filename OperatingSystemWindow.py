import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal

class OperatingSystemWindow(QMainWindow):
    operating_system_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Установка названия и размеров главного окна
        self.setWindowTitle("Операционная система")
        self.setGeometry(100, 100, 1200, 800)

        # Инициализация базы данных и интерфейса пользователя
        self.init_database()
        self.init_ui()

    # Создание или подключение к базе данных и создание таблиц, если они еще не созданы
    def init_database(self):
        self.connection = sqlite3.connect("components.db")
        self.cursor = self.connection.cursor()

        # Создание таблицы операционных систем, если она отсутствует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS operating_systems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                manufacturer TEXT
            )
        ''')
        self.connection.commit()

    # Инициализация графического интерфейса пользователя (UI)
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        header_label = QLabel("Выберите операционную систему")
        main_layout.addWidget(header_label)

        search_name_layout = QHBoxLayout()
        self.search_name = QLineEdit(self)
        self.search_name.setPlaceholderText("Наименование")
        search_name_layout.addWidget(self.search_name)

        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_os)
        search_name_layout.addWidget(search_button)

        main_layout.addLayout(search_name_layout)

        content_layout = QHBoxLayout()

        # Установка таблицы для отображения информации об операционных системах
        self.os_table = QTableWidget()
        self.os_table.setColumnCount(4)
        self.os_table.setColumnWidth(0, 180)# Указываем 6 столбцов, включая кнопки
        self.os_table.setHorizontalHeaderLabels([
            'Название', 'Производитель', '', ''  # Пустой заголовок для кнопок выбора
        ])
        # Загрузка списка операционных систем в таблицу
        self.load_os()
        content_layout.addWidget(self.os_table)

        main_layout.addLayout(content_layout)

        # Control buttons below the table
        control_buttons_layout = QHBoxLayout()

        # Кнопка для добавления новой операционной системы
        add_os_button = QPushButton("Добавить операционную систему")
        # Связывание клика по кнопке с функцией открытия диалогового окна
        add_os_button.clicked.connect(self.add_os_dialog)
        control_buttons_layout.addWidget(add_os_button)

        edit_os_button = QPushButton("Редактировать операционную систему")
        edit_os_button.clicked.connect(self.edit_os_dialog)
        control_buttons_layout.addWidget(edit_os_button)

        delete_os_button = QPushButton("Удалить операционную систему")
        delete_os_button.clicked.connect(self.delete_os)
        control_buttons_layout.addWidget(delete_os_button)

        main_layout.addLayout(control_buttons_layout)

    # Загрузка данных об операционных системах из базы данных в таблицу в UI
    def load_os(self):
        self.os_table.setRowCount(0)
        self.cursor.execute("SELECT * FROM operating_systems")
        for row_data in self.cursor.fetchall():
            row = self.os_table.rowCount()
            self.os_table.insertRow(row)
            # for column, data in enumerate(row_data):
            #     self.os_table.setItem(row, column, QTableWidgetItem(str(data)))

            self.os_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.os_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))

            self.os_table.setItem(row, 2, QTableWidgetItem(str(row_data[0])))  # ID
            self.os_table.setColumnHidden(2, True)  # Скрываем колонку с ID
            
            # Сдвигаем кнопку "Выбрать" на столбец вправо
            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda checked, row=row: self.select_os(row))
            self.os_table.setCellWidget(row, 3, select_button)

    def search_os(self):
        name = self.search_name.text()

        query = "SELECT * FROM operating_systems WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")

        self.os_table.setRowCount(0)
        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.os_table.rowCount()
            self.os_table.insertRow(row)

            self.os_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.os_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))

            self.os_table.setItem(row, 2, QTableWidgetItem(str(row_data[0])) ) # ID
            self.os_table.setColumnHidden(2, True)  # Скрываем колонку с ID

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_os(row))
            self.os_table.setCellWidget(row, 3, select_button)
    # Отображение диалогового окна для добавления операционной системы
    def add_os_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить операционную систему")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных о новой операционной системе
        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)

        # Добавление виджетов в форму
        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных об операционной системе
        save_button = QPushButton("Сохранить")
        # Сохранение операционной системы и закрытие диалога по клику
        save_button.clicked.connect(lambda: self.add_os(
            name_edit.text(), manufacturer_edit.text(), dialog
        ))

        close_button = QPushButton("Отмена")
        # Закрытие диалогового окна без сохранения
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    # Функция, добавляющая данные о новой операционной системе в базу данных и обновляющая таблицу
    def add_os(self, name, manufacturer, dialog):
        try:
            self.cursor.execute('''
                INSERT INTO operating_systems (name, manufacturer)
                VALUES (?, ?)''',
                                (name, manufacturer))
            self.connection.commit()
            dialog.accept()
            self.load_os()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            dialog.reject()
        except Exception as e:
            print(f"Exception in add_os: {e}")
            dialog.reject()

    def edit_os_dialog(self):
        # Получаем текущую выбранную строку
        current_row = self.os_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите операционную систему для редактирования")
            return

        # Получаем ID операционной системы из строки для последующей выборки данных
        os_id = int(self.os_table.item(current_row, 2).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать операционную систему")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных об операционной системе для редактирования
        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)

        # Заполняем форму данными из базы
        self.cursor.execute(
            "SELECT name, manufacturer FROM operating_systems WHERE id=?",
            (os_id,))
        os_data = self.cursor.fetchone()
        name_edit.setText(os_data[0])
        manufacturer_edit.setText(os_data[1])

        # Добавление виджетов в форму
        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных об операционной системе
        save_button = QPushButton("Сохранить изменения")
        # Сохранение изменений операционной системы и закрытие диалога по клику
        save_button.clicked.connect(lambda: self.edit_os(
            os_id, name_edit.text(), manufacturer_edit.text(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    # Функция для редактирования информации об операционной системе
    def edit_os(self, os_id, name, manufacturer, dialog):
        try:
            self.cursor.execute('''
                   UPDATE operating_systems SET name=?, manufacturer=?
                   WHERE id=?''',
                                (name, manufacturer, os_id))
            self.connection.commit()
            dialog.accept()
            self.load_os()
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при обновлении данных: {e}")
            dialog.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")
            dialog.reject()

    # Функция для удаления операционной системы
    def delete_os(self):
        current_row = self.os_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите операционную систему для удаления")
            return

        os_id = int(self.os_table.item(current_row, 2).text())
        reply = QMessageBox.question(self, 'Удаление записи',
                                     'Вы действительно хотите удалить выбранную операционную систему?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM operating_systems WHERE id=?", (os_id,))
                self.connection.commit()
                self.load_os()
            except sqlite3.DatabaseError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при удалении данных: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")

    def select_os(self, row):
        name = self.os_table.item(row, 0).text()

        # Создание всплывающего окна подтверждения
        reply = QMessageBox.question(
            self, 'Подтверждение выбора',
            f"Вы уверены, что хотите выбрать операционную систему {name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.operating_system_selected.emit(name)
        else:
            QMessageBox.information(self, 'Выбор отменён', f"Выбор операционной системы {name} отменён.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    configurator = OperatingSystemWindow()
    configurator.show()
    sys.exit(app.exec_())
