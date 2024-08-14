import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal


class ProcessorWindow(QMainWindow):
    processor_selected = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.selected_socket = None

        self.setWindowTitle("Процессор")
        self.setGeometry(100, 100, 1600, 800)

        self.init_database()
        self.init_ui()

    def init_database(self):
        self.connection = sqlite3.connect("components.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS processors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                manufacturer TEXT,
                socket TEXT,
                core_count INTEGER,
                thread_count INTEGER,
                frequency INTEGER
            )
        ''')
        self.connection.commit()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        header_label = QLabel("Выберите процессор")
        main_layout.addWidget(header_label)

        # Name search field and search button on top
        search_name_layout = QHBoxLayout()
        self.search_name = QLineEdit(self)
        self.search_name.setPlaceholderText("Наименование")
        search_name_layout.addWidget(self.search_name)

        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_processors)
        search_name_layout.addWidget(search_button)

        main_layout.addLayout(search_name_layout)

        content_layout = QHBoxLayout()

        # Processor table in the main content area
        self.processor_table = QTableWidget()
        self.processor_table.setColumnCount(8)
        self.processor_table.setColumnWidth(0, 220)
        self.processor_table.setColumnWidth(3, 150)
        self.processor_table.setColumnWidth(4, 160)
        self.processor_table.setHorizontalHeaderLabels([
            'Наименование', 'Производитель', 'Сокет', 'Количество ядер',
            'Количество потоков', 'Частота работы', '', ''
        ])
        self.load_processors()
        content_layout.addWidget(self.processor_table)


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

        self.search_core_count = QLineEdit(self)
        self.search_core_count.setPlaceholderText("Количество ядер")
        filter_layout.addWidget(QLabel("Количество ядер:"), 2, 0)
        filter_layout.addWidget(self.search_core_count, 2, 1)

        self.search_thread_count = QLineEdit(self)
        self.search_thread_count.setPlaceholderText("Количество потоков")
        filter_layout.addWidget(QLabel("Количество потоков:"), 3, 0)
        filter_layout.addWidget(self.search_thread_count, 3, 1)

        self.search_frequency = QLineEdit(self)
        self.search_frequency.setPlaceholderText("Частота работы")
        filter_layout.addWidget(QLabel("Частота работы:"), 4, 0)
        filter_layout.addWidget(self.search_frequency, 4, 1)

        filter_button = QPushButton("Отфильтровать")
        filter_button.clicked.connect(self.search_processors)
        filter_layout.addWidget(filter_button, 5, 0, 1, 2)

        content_layout.addWidget(filter_group)
        main_layout.addLayout(content_layout)

        # Control buttons below the table
        control_buttons_layout = QHBoxLayout()

        add_processor_button = QPushButton("Добавить процессор")
        add_processor_button.clicked.connect(self.add_processor_dialog)
        control_buttons_layout.addWidget(add_processor_button)

        edit_processor_button = QPushButton("Редактировать процессор")
        edit_processor_button.clicked.connect(self.edit_processor_dialog)
        control_buttons_layout.addWidget(edit_processor_button)

        delete_processor_button = QPushButton("Удалить процессор")
        delete_processor_button.clicked.connect(self.delete_processor)
        control_buttons_layout.addWidget(delete_processor_button)

        main_layout.addLayout(control_buttons_layout)

    def show_with_socket_filter(self, socket=None):
        if socket is not None:
            self.selected_socket = socket
        self.load_processors()

    def load_processors(self):
        self.processor_table.setRowCount(0)
        if self.selected_socket:
            self.cursor.execute("SELECT * FROM processors WHERE socket = ?", (self.selected_socket,))
        else:
            self.cursor.execute("SELECT * FROM processors")

        for row_data in self.cursor.fetchall():
            row = self.processor_table.rowCount()
            self.processor_table.insertRow(row)

            self.processor_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.processor_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.processor_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.processor_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))
            self.processor_table.setItem(row, 4, QTableWidgetItem(str(row_data[5])))
            self.processor_table.setItem(row, 5, QTableWidgetItem(str(row_data[6])))

            self.processor_table.setItem(row, 6, QTableWidgetItem(str(row_data[0])))
            self.processor_table.setColumnHidden(6, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_processor(row))
            self.processor_table.setCellWidget(row, 7, select_button)

    def search_processors(self):
        name = self.search_name.text()
        manufacturer = self.search_manufacturer.text()
        socket = self.search_socket.text() if self.search_socket.text() else self.selected_socket
        core_count = self.search_core_count.text()
        thread_count = self.search_thread_count.text()
        frequency = self.search_frequency.text()

        query = "SELECT * FROM processors WHERE 1=1"
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
        if core_count:
            query += " AND core_count = ?"
            params.append(core_count)
        if thread_count:
            query += " AND thread_count = ?"
            params.append(thread_count)
        if frequency:
            query += " AND frequency = ?"
            params.append(frequency)

        self.processor_table.setRowCount(0)
        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.processor_table.rowCount()
            self.processor_table.insertRow(row)

            self.processor_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.processor_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.processor_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.processor_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))
            self.processor_table.setItem(row, 4, QTableWidgetItem(str(row_data[5])))
            self.processor_table.setItem(row, 5, QTableWidgetItem(str(row_data[6])))

            self.processor_table.setItem(row, 6, QTableWidgetItem(str(row_data[0])))
            self.processor_table.setColumnHidden(6, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_processor(row))
            self.processor_table.setCellWidget(row, 7, select_button)

    def add_processor_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить процессор")

        dialog_layout = QGridLayout(dialog)

        form_layout = QFormLayout()
        name = QLineEdit(dialog)
        manufacturer = QLineEdit(dialog)
        socket = QLineEdit(dialog)
        core_count = QSpinBox(dialog)
        thread_count = QSpinBox(dialog)
        frequency = QSpinBox(dialog)
        core_count.setMaximum(1000000)
        thread_count.setMaximum(1000000)
        frequency.setMaximum(1000000)

        form_layout.addRow("Наименование:", name)
        form_layout.addRow("Производитель:", manufacturer)
        form_layout.addRow("Сокет:", socket)
        form_layout.addRow("Количество ядер:", core_count)
        form_layout.addRow("Количество потоков:", thread_count)
        form_layout.addRow("Частота работы:", frequency)

        dialog_layout.addLayout(form_layout, 0, 0)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.add_processor(
            name.text(), manufacturer.text(), socket.text(),
            core_count.value(), thread_count.value(), frequency.value(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    def add_processor(self, name, manufacturer, socket, core_count, thread_count, frequency, dialog):
        try:
            self.cursor.execute('''
                INSERT INTO processors (name, manufacturer, socket, core_count,
                thread_count, frequency)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, manufacturer, socket, core_count, thread_count, frequency))
            self.connection.commit()
            dialog.accept()
            self.load_processors()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            dialog.reject()
        except Exception as e:
            print(f"Exception in add_processor: {e}")
            dialog.reject()

    def edit_processor_dialog(self):
        current_row = self.processor_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите процессор для редактирования")
            return

        # Получаем ID процессора из строки для последующей выборки данных
        id = int(self.processor_table.item(current_row, 6).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать процессор")

        dialog_layout = QGridLayout(dialog)

        # Форма для ввода данных о процессоре для редактирования
        form_layout = QFormLayout()
        name = QLineEdit(dialog)
        manufacturer = QLineEdit(dialog)
        socket = QLineEdit(dialog)
        core_count = QSpinBox(dialog)
        thread_count = QSpinBox(dialog)
        frequency = QSpinBox(dialog)
        core_count.setMaximum(1000000)
        thread_count.setMaximum(1000000)        
        frequency.setMaximum(1000000)

        # Заполняем форму данными из базы
        self.cursor.execute(
            "SELECT name, manufacturer, socket, core_count, thread_count, frequency FROM processors WHERE id=?",
            (id,))
        proc_data = self.cursor.fetchone()
        name.setText(proc_data[0])
        manufacturer.setText(proc_data[1])
        socket.setText(proc_data[2])
        core_count.setValue(proc_data[3])
        thread_count.setValue(proc_data[4])
        frequency.setValue(proc_data[5])

        # Добавление виджетов в форму
        form_layout.addRow("Наименование :", name)
        form_layout.addRow("Производитель:", manufacturer)
        form_layout.addRow("Сокет:", socket)
        form_layout.addRow("Количество ядер:", core_count)
        form_layout.addRow("Количество потоков:", thread_count)
        form_layout.addRow("Частота работы:", frequency)

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных о процессоре
        save_button = QPushButton("Сохранить изменения")
        # Сохранение изменений процессора и закрытие диалога по клику
        save_button.clicked.connect(lambda: self.edit_processor(
            id, name.text(), manufacturer.text(),
            socket.text(), core_count.value(),
            thread_count.value(), frequency.value(),
            dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

        # Функция для редактирования информации о процессоре

    def edit_processor(self, id, name, manufacturer, socket, core_count, thread_count, frequency,
                       dialog):
        try:
            self.cursor.execute('''
                   UPDATE processors SET name=?, manufacturer=?, socket=?,
                   core_count=?, thread_count=?, frequency=?
                   WHERE id=?''',
                                (name, manufacturer, socket, core_count, thread_count, frequency, id))
            self.connection.commit()
            dialog.accept()
            self.load_processors()
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при обновлении данных: {e}")
            dialog.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")
            dialog.reject()

        # Функция для удаления процессора

    def delete_processor(self):
        current_row = self.processor_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите процессор для удаления")
            return

        id = int(self.processor_table.item(current_row, 6).text())
        reply = QMessageBox.question(self, 'Удаление записи', 'Вы действительно хотите удалить выбранный процессор?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM processors WHERE id=?", (id,))
                self.connection.commit()
                self.load_processors()
            except sqlite3.DatabaseError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при удалении данных: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")

    def select_processor(self, row):
        name = self.processor_table.item(row, 0).text()

        # Создание всплывающего окна подтверждения
        reply = QMessageBox.question(
            self, 'Подтверждение выбора',
            f"Вы уверены, что хотите выбрать процессор {name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        socket = self.processor_table.item(row, 2).text()
        if reply == QMessageBox.Yes:
            self.processor_selected.emit(name, socket)
        else:
            QMessageBox.information(self, 'Выбор отменён', f"Выбор процессора {name} отменён.")

    def reset_filters(self):
        self.selected_socket = None
        self.load_processors()


# Точка входа в приложение
if __name__ == '__main__':
    app = QApplication(sys.argv)
    configurator = ProcessorWindow()
    configurator.show()
    sys.exit(app.exec_())
