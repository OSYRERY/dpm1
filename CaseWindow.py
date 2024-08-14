import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal

class CaseWindow(QMainWindow):
    case_selected = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.selected_form_factor = None

        # Установка названия и размеров главного окна
        self.setWindowTitle("Корпус")
        self.setGeometry(100, 100, 1200, 800)

        # Инициализация базы данных и интерфейса пользователя
        self.init_database()
        self.init_ui()

    # Создание или подключение к базе данных и создание таблиц, если они еще не созданы
    def init_database(self):
        self.connection = sqlite3.connect("components.db")
        self.cursor = self.connection.cursor()

        # Создание таблицы корпусов, если она отсутствует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                manufacturer TEXT,
                form_factor TEXT
                
            )
        ''')
        self.connection.commit()

    # Инициализация графического интерфейса пользователя (UI)
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        header_label = QLabel("Выберите корпус")
        main_layout.addWidget(header_label)

        search_name_layout = QHBoxLayout()
        self.search_name = QLineEdit(self)
        self.search_name.setPlaceholderText("Наименование")
        search_name_layout.addWidget(self.search_name)

        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_cases)
        search_name_layout.addWidget(search_button)

        main_layout.addLayout(search_name_layout)

        content_layout = QHBoxLayout()

        # Установка таблицы для отображения информации о корпусах
        self.case_table = QTableWidget()
        self.case_table.setColumnCount(5)
        self.case_table.setColumnWidth(0, 260)
        self.case_table.setHorizontalHeaderLabels([
            'Название', 'Производитель', 'Форм-фактор',  '',''
        ])
        self.load_cases()
        content_layout.addWidget(self.case_table)

        filter_group = QGroupBox("Фильтры")
        filter_group.setFixedSize(400, 250)  # Установить размер группы фильтров
        filter_layout = QGridLayout(filter_group)
        filter_layout.setContentsMargins(5, 5, 5, 5)

        self.search_manufacturer = QLineEdit(self)
        self.search_manufacturer.setPlaceholderText("Производитель")
        filter_layout.addWidget(QLabel("Производитель:"), 0, 0)
        filter_layout.addWidget(self.search_manufacturer, 0, 1)

        self.search_form_factor = QLineEdit(self)
        self.search_form_factor.setPlaceholderText("Форм-фактор")
        filter_layout.addWidget(QLabel("Форм-фактор:"), 1, 0)
        filter_layout.addWidget(self.search_form_factor, 1, 1)

        filter_button = QPushButton("Отфильтровать")
        filter_button.clicked.connect(self.search_cases)
        filter_layout.addWidget(filter_button, 2, 0, 1, 2)

        content_layout.addWidget(filter_group)
        main_layout.addLayout(content_layout)

        control_buttons_layout = QHBoxLayout()

        # Кнопка для добавления нового корпуса
        add_case_button = QPushButton("Добавить корпус")
        add_case_button.clicked.connect(self.add_case_dialog)
        control_buttons_layout.addWidget(add_case_button)

        edit_case_button = QPushButton("Редактировать корпус")
        edit_case_button.clicked.connect(self.edit_case_dialog)
        control_buttons_layout.addWidget(edit_case_button)

        delete_case_button = QPushButton("Удалить корпус")
        delete_case_button.clicked.connect(self.delete_case)
        control_buttons_layout.addWidget(delete_case_button)

        main_layout.addLayout(control_buttons_layout)

    # Загрузка данных о корпусах из базы данных в таблицу в UI
    def load_cases(self):
        self.case_table.setRowCount(0)
        query = "SELECT * FROM cases"
        params = []

        if self.selected_form_factor:
            query += " WHERE form_factor = ?"
            params.append(self.selected_form_factor)
        
        self.cursor.execute(query, params)
        print('load_cases', query, params)
        
        for row_data in self.cursor.fetchall():
            row = self.case_table.rowCount()
            self.case_table.insertRow(row)

            self.case_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))  # Name
            self.case_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))  # Form Factor
            self.case_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))  # Manufacturer

            # Сохраняем ID в скрытой колонке
            self.case_table.setItem(row, 3, QTableWidgetItem(str(row_data[0])))  # ID
            self.case_table.setColumnHidden(3, True)  # Скрываем колонку с ID
            
            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda checked, row=row: self.select_case(row))
            self.case_table.setCellWidget(row, 4, select_button)

    def search_cases(self):
        name = self.search_name.text()
        manufacturer = self.search_manufacturer.text()
        form_factor = self.search_form_factor.text() if self.search_form_factor.text() else self.selected_form_factor

        query = "SELECT * FROM cases WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if manufacturer:
            query += " AND manufacturer = ?"
            params.append(manufacturer)
        if form_factor:
            query += " AND (form_factor = ? OR form_factor = '-')"
            params.append(form_factor)

        self.case_table.setRowCount(0)
        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.case_table.rowCount()
            self.case_table.insertRow(row)

            self.case_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))  # Name
            self.case_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))  # Form Factor
            self.case_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))  # Manufacturer

            # Save ID in a hidden column
            self.case_table.setItem(row, 3, QTableWidgetItem(str(row_data[0])))  # ID
            self.case_table.setColumnHidden(3, True)  # Hide the ID column

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_case(row))
            self.case_table.setCellWidget(row, 4, select_button)

    # Отображение диалогового окна для добавления корпуса
    def add_case_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить корпус")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных о новом корпусе
        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        form_factor_edit = QLineEdit(dialog)

        # Добавление виджетов в форму
        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Форм-фактор:", form_factor_edit)


        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных о корпусе
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.add_case(
            name_edit.text(), manufacturer_edit.text(), 
            form_factor_edit.text(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    # Функция, добавляющая данные о новом корпусе в базу данных и обновляющая таблицу
    def add_case(self, name, manufacturer, form_factor, dialog):
        try:
            self.cursor.execute('''
                INSERT INTO cases (name, manufacturer, form_factor)
                VALUES (?, ?, ?)
            ''', (name, manufacturer, form_factor))
            self.connection.commit()
            dialog.accept()
            self.load_cases()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            dialog.reject()
        except Exception as e:
            print(f"Exception in add_case: {e}")
            dialog.reject()

    # Редактирование данных о корпусе
    def edit_case_dialog(self):
        current_row = self.case_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите корпус для редактирования")
            return

        case_id = int(self.case_table.item(current_row, 3).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать корпус")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных о корпусе для редактирования
        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        form_factor_edit = QLineEdit(dialog)

        # Заполняем форму данными из базы
        self.cursor.execute("SELECT name, manufacturer, form_factor FROM cases WHERE id=?", (case_id,))
        case_data = self.cursor.fetchone()
        name_edit.setText(case_data[0])
        manufacturer_edit.setText(case_data[1])
        form_factor_edit.setText(case_data[2])

        # Добавление виджетов в форму
        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Форм-фактор:", form_factor_edit)

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных о корпусе
        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(lambda: self.edit_case(
            case_id, name_edit.text(), manufacturer_edit.text(), 
            form_factor_edit.text(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    # Функция для редактирования информации о корпусе
    def edit_case(self, case_id, name, manufacturer, form_factor, dialog):
        try:
            self.cursor.execute('''
                UPDATE cases SET name=?, manufacturer=?, form_factor=? 
                WHERE id=?
            ''', (name, manufacturer, form_factor, case_id))
            self.connection.commit()
            dialog.accept()
            self.load_cases()
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при обновлении данных: {e}")
            dialog.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")
            dialog.reject()

    # Удаление корпуса
    def delete_case(self):
        current_row = self.case_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите корпус для удаления")
            return

        case_id = int(self.case_table.item(current_row, 3).text())
        reply = QMessageBox.question(
            self, 'Удаление записи', 'Вы действительно хотите удалить выбранный корпус?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM cases WHERE id=?", (case_id,))
                self.connection.commit()
                self.load_cases()
            except sqlite3.DatabaseError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при удалении данных: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")

    def select_case(self, row):
        name = self.case_table.item(row, 0).text()
        form_factor = self.case_table.item(row, 2).text()

        reply = QMessageBox.question(
            self, 'Подтверждение выбора',
            f"Вы уверены, что хотите выбрать корпус {name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.case_selected.emit(name, form_factor)
        else:
            QMessageBox.information(self, 'Выбор отменён', f"Выбор корпуса {name} отменён.")


    def set_form_factor_filter(self, form_factor):
        self.selected_form_factor = form_factor if form_factor is not None else self.selected_form_factor
        self.load_cases()

    def reset_filters(self):
        self.selected_form_factor = None
        self.load_cases()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    configurator = CaseWindow()
    configurator.show()
    sys.exit(app.exec_())