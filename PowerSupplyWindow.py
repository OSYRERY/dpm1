import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal

class PowerSupplyWindow(QMainWindow):
    power_supply_selected = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

        self.selected_form_factor = None

        # Установка названия и размеров главного окна
        self.setWindowTitle("Блок питания")
        self.setGeometry(100, 100, 1600, 800)

        # Инициализация базы данных и интерфейса пользователя
        self.init_database()
        self.init_ui()

    # Создание или подключение к базе данных и создание таблиц, если они еще не созданы
    def init_database(self):
        self.connection = sqlite3.connect("components.db")
        self.cursor = self.connection.cursor()

        # Создание таблицы блоков питания, если она отсутствует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS power_supplies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                manufacturer TEXT,
                wattage TEXT,
                form_factor TEXT
            )
        ''')
        self.connection.commit()

    # Инициализация графического интерфейса пользователя (UI)
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        header_label = QLabel("Выберите блок питания")
        main_layout.addWidget(header_label)


        # Name search field and search button on top
        search_name_layout = QHBoxLayout()
        self.search_name = QLineEdit(self)
        self.search_name.setPlaceholderText("Наименование")
        search_name_layout.addWidget(self.search_name)

        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_power_supplies)
        search_name_layout.addWidget(search_button)

        main_layout.addLayout(search_name_layout)

        content_layout = QHBoxLayout()

        self.ps_table = QTableWidget()
        self.ps_table.setColumnCount(6)
        self.ps_table.setColumnWidth(0, 240)
        self.ps_table.setHorizontalHeaderLabels([
            'Наименование', 'Производитель', 'Мощность', 'Форм-фактор', '', ''
        ])
        self.load_power_supplies()
        content_layout.addWidget(self.ps_table)

        filter_group = QGroupBox("Фильтры")
        filter_group.setFixedSize(400, 250)  # Установить размер группы фильтров
        filter_layout = QGridLayout(filter_group)
        filter_layout.setContentsMargins(5, 5, 5, 5)

        self.search_manufacturer = QLineEdit(self)
        self.search_manufacturer.setPlaceholderText("Производитель")
        filter_layout.addWidget(QLabel("Производитель:"), 0, 0)
        filter_layout.addWidget(self.search_manufacturer, 0, 1)

        self.search_wattage = QLineEdit(self)
        self.search_wattage.setPlaceholderText("Мощность")
        filter_layout.addWidget(QLabel("Мощность (в Вт):"), 1, 0)
        filter_layout.addWidget(self.search_wattage, 1, 1)

        self.search_form_factor = QLineEdit(self)
        self.search_form_factor.setPlaceholderText("Форм-фактор")
        filter_layout.addWidget(QLabel("Форм-фактор:"), 2, 0)
        filter_layout.addWidget(self.search_form_factor, 2, 1)

        filter_button = QPushButton("Отфильтровать")
        filter_button.clicked.connect(self.search_power_supplies)
        filter_layout.addWidget(filter_button, 3, 0, 1, 2)

        content_layout.addWidget(filter_group)
        main_layout.addLayout(content_layout)

        # Control buttons below the table
        control_buttons_layout = QHBoxLayout()

        # Кнопка для добавления нового блока питания
        add_ps_button = QPushButton("Добавить блок питания")
        # Связывание клика по кнопке с функцией открытия диалогового окна
        add_ps_button.clicked.connect(self.add_ps_dialog)
        control_buttons_layout.addWidget(add_ps_button)

        edit_ps_button = QPushButton("Редактировать блок питания")
        edit_ps_button.clicked.connect(self.edit_ps_dialog)
        control_buttons_layout.addWidget(edit_ps_button)

        delete_ps_button = QPushButton("Удалить блок питания")
        delete_ps_button.clicked.connect(self.delete_ps)
        control_buttons_layout.addWidget(delete_ps_button)

        main_layout.addLayout(control_buttons_layout)

    def show_with_form_factor_filter(self, form_factor=None):
        if form_factor is not None: self.selected_form_factor = form_factor
        self.load_power_supplies()  # Загрузить список компонентов с фильтрацией по сокету
    
    # Загрузка данных о блоках питания из базы данных в таблицу в UI
    def load_power_supplies(self):
        self.ps_table.setRowCount(0)
        if self.selected_form_factor:
            self.cursor.execute("SELECT * FROM power_supplies WHERE form_factor = ?", (self.selected_form_factor,))
        else:
            self.cursor.execute("SELECT * FROM power_supplies")

        for row_data in self.cursor.fetchall():
            row = self.ps_table.rowCount()
            self.ps_table.insertRow(row)

            self.ps_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.ps_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.ps_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.ps_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))

            self.ps_table.setItem(row, 4, QTableWidgetItem(str(row_data[0])))
            self.ps_table.setColumnHidden(4, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda checked, row=row: self.select_ps(row))
            self.ps_table.setCellWidget(row, 5, select_button)

    def search_power_supplies(self):
        name = self.search_name.text()
        manufacturer = self.search_manufacturer.text()
        wattage = self.search_wattage.text()
        form_factor = self.search_form_factor.text() if self.search_form_factor.text() else self.selected_form_factor

        query = "SELECT * FROM power_supplies WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if manufacturer:
            query += " AND manufacturer = ?"
            params.append(manufacturer)
        if wattage:
            query += " AND wattage = ?"
            params.append(wattage)
        if form_factor:
            query += " AND (form_factor = ? OR form_factor = '-')"
            params.append(form_factor)

        self.ps_table.setRowCount(0)
        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.ps_table.rowCount()
            self.ps_table.insertRow(row)

            self.ps_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.ps_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.ps_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.ps_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))

            self.ps_table.setItem(row, 4, QTableWidgetItem(str(row_data[0])))
            self.ps_table.setColumnHidden(4, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda checked, row=row: self.select_ps(row))
            self.ps_table.setCellWidget(row, 5, select_button)

    # Отображение диалогового окна для добавления блока питания
    def add_ps_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить блок питания")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных о новом блоке питания
        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        wattage_spin = QLineEdit(dialog)
        form_factor_edit = QLineEdit(dialog)

        # Добавление виджетов в форму
        form_layout.addRow("Наименование:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Мощность (в Вт):", wattage_spin)
        form_layout.addRow("Форм-фактор:", form_factor_edit)

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных о блоке питания
        save_button = QPushButton("Сохранить")
        # Сохранение блока питания и закрытие диалога по клику
        save_button.clicked.connect(lambda: self.add_ps(
            name_edit.text(), manufacturer_edit.text(), wattage_spin.text(), form_factor_edit.text(), dialog
        ))

        close_button = QPushButton("Отмена")
        # Закрытие диалогового окна без сохранения
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    # Функция, добавляющая данные о новом блоке питания в базу данных и обновляющая таблицу
    def add_ps(self, name, manufacturer, wattage, form_factor, dialog):
        try:
            self.cursor.execute('''
                INSERT INTO power_supplies (name, manufacturer, wattage, form_factor)
                VALUES (?, ?, ?, ?)''',
                                (name, manufacturer, wattage, form_factor))
            self.connection.commit()
            dialog.accept()
            self.load_power_supplies()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            dialog.reject()
        except Exception as e:
            print(f"Exception in add_ps: {e}")
            dialog.reject()

    def edit_ps_dialog(self):
        # Получаем текущую выбранную строку
        current_row = self.ps_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите блок питания для редактирования")
            return

        # Получаем ID блока питания из строки для последующей выборки данных
        ps_id = int(self.ps_table.item(current_row, 4).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать блок питания")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных о блоке питания для редактирования
        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        wattage_spin = QLineEdit(dialog)
        form_factor_edit = QLineEdit(dialog)

        # Заполняем форму данными из базы
        self.cursor.execute(
            "SELECT name, manufacturer, wattage, form_factor FROM power_supplies WHERE id=?",
            (ps_id,))
        ps_data = self.cursor.fetchone()
        name_edit.setText(ps_data[0])
        manufacturer_edit.setText(ps_data[1])
        wattage_spin.setText(ps_data[2])
        form_factor_edit.setText(ps_data[3])

        # Добавление виджетов в форму
        form_layout.addRow("Наименование:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Мощность (в Вт):", wattage_spin)
        form_layout.addRow("Форм-фактор:", form_factor_edit)

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных о блоке питания
        save_button = QPushButton("Сохранить изменения")
        # Сохранение изменений блока питания и закрытие диалога по клику
        save_button.clicked.connect(lambda: self.edit_ps(
            ps_id, name_edit.text(), manufacturer_edit.text(), wattage_spin.text(),  form_factor_edit.text(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    # Функция для редактирования информации о блоке питания
    def edit_ps(self, ps_id, name, manufacturer, wattage,  form_factor, dialog):
        try:
            self.cursor.execute('''
                   UPDATE power_supplies SET name=?, manufacturer=?, wattage=?, form_factor=?
                   WHERE id=?''',
                                (name, manufacturer, wattage,  form_factor, ps_id))
            self.connection.commit()
            dialog.accept()
            self.load_power_supplies()
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при обновлении данных: {e}")
            dialog.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")
            dialog.reject()

    # Функция для удаления блока питания
    def delete_ps(self):
        current_row = self.ps_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите блок питания для удаления")
            return

        ps_id = int(self.ps_table.item(current_row, 4).text())
        reply = QMessageBox.question(self, 'Удаление записи', 'Вы действительно хотите удалить выбранный блок питания?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM power_supplies WHERE id=?", (ps_id,))
                self.connection.commit()
                self.load_power_supplies()
            except sqlite3.DatabaseError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при удалении данных: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")

    def select_ps(self, row):
        name = self.ps_table.item(row, 0).text()
        form_factor = self.ps_table.item(row, 3).text()

        # Создание всплывающего окна подтверждения
        reply = QMessageBox.question(
            self, 'Подтверждение выбора',
            f"Вы уверены, что хотите выбрать блок питания {name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.power_supply_selected.emit(name, form_factor)
        else:
            QMessageBox.information(self, 'Выбор отменён', f"Выбор блока питания {name} отменён.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    configurator = PowerSupplyWindow()
    configurator.show()
    sys.exit(app.exec_())