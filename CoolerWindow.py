import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal

class CoolerWindow(QMainWindow):
    cooler_selected = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.selected_socket = None

        self.setWindowTitle("Система охлаждения")
        self.setGeometry(100, 100, 1600, 800)

        self.init_database()
        self.init_ui()

    def init_database(self):
        self.connection = sqlite3.connect("components.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS coolers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                manufacturer TEXT,
                socket TEXT,
                power_dissipation INTEGER,
                noise_level TEXT
            )
        ''')
        self.connection.commit()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        header_label = QLabel("Выберите систему охлаждения")
        main_layout.addWidget(header_label)

        # Name search field and search button on top
        search_name_layout = QHBoxLayout()
        self.search_name = QLineEdit(self)
        self.search_name.setPlaceholderText("Наименование")
        search_name_layout.addWidget(self.search_name)

        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_coolers)
        search_name_layout.addWidget(search_button)

        main_layout.addLayout(search_name_layout)

        content_layout = QHBoxLayout()

        self.cooler_table = QTableWidget()
        self.cooler_table.setColumnCount(7)
        self.cooler_table.setColumnWidth(0, 280)
        self.cooler_table.setColumnWidth(3, 220)
        self.cooler_table.setColumnWidth(4, 200)
        self.cooler_table.setHorizontalHeaderLabels([
            'Название', 'Производитель', 'Сокет', 'Рассеиваемая мощность (Вт)',
            'Уровень шума (дБ)', '', ''
        ])
        self.load_coolers()
        content_layout.addWidget(self.cooler_table)

        filter_group = QGroupBox("Фильтры")
        filter_group.setFixedSize(400, 250)
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

        self.search_power = QLineEdit(self)
        self.search_power.setPlaceholderText("Рассеиваемая мощность")
        filter_layout.addWidget(QLabel("Рассеиваемая мощность (Вт):"), 2, 0)
        filter_layout.addWidget(self.search_power, 2, 1)

        self.search_noise = QLineEdit(self)
        self.search_noise.setPlaceholderText("Уровень шума")
        filter_layout.addWidget(QLabel("Уровень шума (дБ):"), 3, 0)
        filter_layout.addWidget(self.search_noise, 3, 1)

        filter_button = QPushButton("Отфильтровать")
        filter_button.clicked.connect(self.search_coolers)
        filter_layout.addWidget(filter_button, 4, 0, 1, 2)

        content_layout.addWidget(filter_group)
        main_layout.addLayout(content_layout)

        # Control buttons below the table
        control_buttons_layout = QHBoxLayout()

        add_cooler_button = QPushButton("Добавить охладитель")
        add_cooler_button.clicked.connect(self.add_cooler_dialog)
        control_buttons_layout.addWidget(add_cooler_button)

        edit_cooler_button = QPushButton("Редактировать охладитель")
        edit_cooler_button.clicked.connect(self.edit_cooler_dialog)
        control_buttons_layout.addWidget(edit_cooler_button)

        delete_cooler_button = QPushButton("Удалить охладитель")
        delete_cooler_button.clicked.connect(self.delete_cooler)
        control_buttons_layout.addWidget(delete_cooler_button)

        main_layout.addLayout(control_buttons_layout)

    def show_with_socket_filter(self, socket=None):
        if socket is not None:
            self.selected_socket = socket
        self.load_coolers()

    def load_coolers(self):
        self.cooler_table.setRowCount(0)
        if self.selected_socket:
            query = "SELECT * FROM coolers WHERE socket = ? OR socket = '-'"
            self.cursor.execute(query, (self.selected_socket,))
        else:
            query = "SELECT * FROM coolers"
            self.cursor.execute(query)

        for row_data in self.cursor.fetchall():
            row = self.cooler_table.rowCount()
            self.cooler_table.insertRow(row)

            self.cooler_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.cooler_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.cooler_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.cooler_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))
            self.cooler_table.setItem(row, 4, QTableWidgetItem(str(row_data[5])))

            self.cooler_table.setItem(row, 5, QTableWidgetItem(str(row_data[0])))
            self.cooler_table.setColumnHidden(5, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_cooler(row))
            self.cooler_table.setCellWidget(row, 6, select_button)

    def search_coolers(self):
        name = self.search_name.text()
        manufacturer = self.search_manufacturer.text()
        socket = self.search_socket.text() if self.search_socket.text() else self.selected_socket
        power = self.search_power.text()
        noise = self.search_noise.text()

        query = "SELECT * FROM coolers WHERE 1=1"
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
        if power:
            query += " AND power_dissipation = ?"
            params.append(power)
        if noise:
            query += " AND noise_level = ?"
            params.append(noise)

        self.cooler_table.setRowCount(0)
        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.cooler_table.rowCount()
            self.cooler_table.insertRow(row)

            self.cooler_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.cooler_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.cooler_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.cooler_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))
            self.cooler_table.setItem(row, 4, QTableWidgetItem(str(row_data[5])))

            self.cooler_table.setItem(row, 5, QTableWidgetItem(str(row_data[0])))
            self.cooler_table.setColumnHidden(5, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_cooler(row))
            self.cooler_table.setCellWidget(row, 6, select_button)

    def add_cooler_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить охладитель")
        dialog_layout = QGridLayout(dialog)

        form_layout = QFormLayout()
        name = QLineEdit(dialog)
        manufacturer = QLineEdit(dialog)
        socket = QLineEdit(dialog)
        power_dissipation = QSpinBox(dialog)
        noise_level = QSpinBox(dialog)
        power_dissipation.setMaximum(1000000)
        noise_level.setMaximum(1000000)

        form_layout.addRow("Название:", name)
        form_layout.addRow("Производитель:", manufacturer)
        form_layout.addRow("Сокет:", socket)
        form_layout.addRow("Рассеиваемая мощность (Вт):", power_dissipation)
        form_layout.addRow("Уровень шума (дБ):", noise_level)

        dialog_layout.addLayout(form_layout, 0, 0)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.add_cooler(
            name.text(), manufacturer.text(), socket.text(),
            power_dissipation.value(), noise_level.value(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    def add_cooler(self, name, manufacturer, socket, power_dissipation, noise_level, dialog):
        try:
            self.cursor.execute('''
                        INSERT INTO coolers (name, manufacturer, socket, power_dissipation, noise_level)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, manufacturer, socket, power_dissipation, noise_level))
            self.connection.commit
            dialog.accept()
            self.load_coolers()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            dialog.reject()
        except Exception as e:
            print(f"Exception in add_cooler: {e}")
            dialog.reject()

    def edit_cooler_dialog(self):
        current_row = self.cooler_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите охладитель для редактирования")
            return

        cooler_id = int(self.cooler_table.item(current_row, 5).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать охладитель")

        dialog_layout = QGridLayout(dialog)

        form_layout = QFormLayout()
        name_edit = QLineEdit(dialog)
        manufacturer_edit = QLineEdit(dialog)
        socket_edit = QLineEdit(dialog)
        power_dissipation_spin = QSpinBox(dialog)
        power_dissipation_spin.setMaximum(1000000)
        noise_level_spin = QSpinBox(dialog)
        noise_level_spin.setMaximum(1000000)

        self.cursor.execute(
            "SELECT name, manufacturer, socket, power_dissipation, noise_level FROM coolers WHERE id=?",
            (cooler_id,))
        cooler_data = self.cursor.fetchone()
        name_edit.setText(cooler_data[0])
        manufacturer_edit.setText(cooler_data[1])
        socket_edit.setText(cooler_data[2])
        power_dissipation_spin.setValue(cooler_data[3])
        noise_level_spin.setValue(cooler_data[4])

        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Сокет:", socket_edit)
        form_layout.addRow("Рассеиваемая мощность (Вт):", power_dissipation_spin)
        form_layout.addRow("Уровень шума (дБ):", noise_level_spin)

        dialog_layout.addLayout(form_layout, 0, 0)

        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(lambda: self.edit_cooler(
            cooler_id, name_edit.text(), manufacturer_edit.text(), socket_edit.text(), power_dissipation_spin.value(), noise_level_spin.value(), dialog))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    def edit_cooler(self, cooler_id, name, manufacturer, socket, power_dissipation, noise_level, dialog):
        try:
            self.cursor.execute('''
                UPDATE coolers SET name=?, manufacturer=?, socket=?,
                power_dissipation=?, noise_level=?
                WHERE id=?
            ''', (name, manufacturer, socket, power_dissipation, noise_level, cooler_id))
            self.connection.commit()
            dialog.accept()
            self.load_coolers()
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при обновлении данных: {e}")
            dialog.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")
            dialog.reject()

    def delete_cooler(self):
        current_row = self.cooler_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите охладитель для удаления")
            return

        cooler_id = int(self.cooler_table.item(current_row, 5).text())
        reply = QMessageBox.question(self, 'Удаление записи', 'Вы действительно хотите удалить выбранный охладитель?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM coolers WHERE id=?", (cooler_id,))
                self.connection.commit()
                self.load_coolers()
            except sqlite3.DatabaseError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при удалении данных: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")

    def select_cooler(self, row):
        name = self.cooler_table.item(row, 0).text()
        socket = self.cooler_table.item(row, 2).text()

        reply = QMessageBox.question(self, 'Подтверждение выбора', f"Вы уверены, что хотите выбрать охладитель {name}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.cooler_selected.emit(name, socket)
        else:
            QMessageBox.information(self, 'Выбор отменён', f"Выбор охладителя {name} отменён.")

    def reset_filters(self):
        self.selected_socket = None
        self.load_coolers()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    configurator = CoolerWindow()
    configurator.show()
    sys.exit(app.exec_())