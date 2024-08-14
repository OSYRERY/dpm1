import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QSpinBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal

class VideoCardWindow(QMainWindow):
    video_card_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Видеокарта")
        self.setGeometry(100, 100, 1600, 800)
        self.init_database()
        self.init_ui()

    def init_database(self):
        self.connection = sqlite3.connect("components.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                manufacturer TEXT,
                memory_size INTEGER,
                clock_speed INTEGER
            )
        ''')
        self.connection.commit()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        header_label = QLabel("Выберите видеокарту")
        main_layout.addWidget(header_label)

        # Name search field and search button on top
        search_name_layout = QHBoxLayout()
        self.search_name = QLineEdit(self)
        self.search_name.setPlaceholderText("Наименование")
        search_name_layout.addWidget(self.search_name)

        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_video_cards)
        search_name_layout.addWidget(search_button)

        main_layout.addLayout(search_name_layout)

        content_layout = QHBoxLayout()

        self.video_card_table = QTableWidget()
        self.video_card_table.setColumnCount(6)
        self.video_card_table.setColumnWidth(0, 400)
        self.video_card_table.setColumnWidth(2, 200)
        self.video_card_table.setColumnWidth(3, 180)
        self.video_card_table.setHorizontalHeaderLabels([
            'Название', 'Производитель', 'Объем видеопамяти (Гб)', 'Частота работы(МгЦ)', '', ''
        ])
        self.load_video_cards()
        content_layout.addWidget(self.video_card_table)

        filter_group = QGroupBox("Фильтры")
        filter_group.setFixedSize(400, 250)
        filter_layout = QGridLayout(filter_group)
        filter_layout.setContentsMargins(5, 5, 5, 5)

        self.search_manufacturer = QLineEdit(self)
        self.search_manufacturer.setPlaceholderText("Производитель")
        filter_layout.addWidget(QLabel("Производитель:"), 0, 0)
        filter_layout.addWidget(self.search_manufacturer, 0, 1)

        self.search_memory_size = QLineEdit(self)
        self.search_memory_size.setPlaceholderText("Объем памяти (Гб)")
        filter_layout.addWidget(QLabel("Объем памяти (Гб):"), 1, 0)
        filter_layout.addWidget(self.search_memory_size, 1, 1)

        self.search_clock_speed = QLineEdit(self)
        self.search_clock_speed.setPlaceholderText("Частота работы (МгЦ)")
        filter_layout.addWidget(QLabel("Частота работы (МгЦ):"), 2, 0)
        filter_layout.addWidget(self.search_clock_speed, 2, 1)

        filter_button = QPushButton("Отфильтровать")
        filter_button.clicked.connect(self.search_video_cards)
        filter_layout.addWidget(filter_button, 3, 0, 1, 2)

        content_layout.addWidget(filter_group)
        main_layout.addLayout(content_layout)

        # Control buttons below the table
        control_buttons_layout = QHBoxLayout()

        add_video_card_button = QPushButton("Добавить видеокарту")
        add_video_card_button.clicked.connect(self.add_video_card_dialog)
        control_buttons_layout.addWidget(add_video_card_button)

        edit_video_card_button = QPushButton("Редактировать видеокарту")
        edit_video_card_button.clicked.connect(self.edit_video_card_dialog)
        control_buttons_layout.addWidget(edit_video_card_button)

        delete_video_card_button = QPushButton("Удалить видеокарту")
        delete_video_card_button.clicked.connect(self.delete_video_card)
        control_buttons_layout.addWidget(delete_video_card_button)

        main_layout.addLayout(control_buttons_layout)

    def load_video_cards(self):
        self.video_card_table.setRowCount(0)
        self.cursor.execute("SELECT * FROM video_cards")
        for row_data in self.cursor.fetchall():
            row = self.video_card_table.rowCount()
            self.video_card_table.insertRow(row)
            self.video_card_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.video_card_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.video_card_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.video_card_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))
            self.video_card_table.setItem(row, 4, QTableWidgetItem(str(row_data[0])))
            self.video_card_table.setColumnHidden(4, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_video_card(row))
            self.video_card_table.setCellWidget(row, 5, select_button)

    def search_video_cards(self):
        name = self.search_name.text()
        manufacturer = self.search_manufacturer.text()
        memory_size = self.search_memory_size.text()
        clock_speed = self.search_clock_speed.text()

        query = "SELECT * FROM video_cards WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if manufacturer:
            query += " AND manufacturer = ?"
            params.append(manufacturer)
        if memory_size:
            query += " AND memory_size = ?"
            params.append(memory_size)
        if clock_speed:
            query += " AND clock_speed = ?"
            params.append(clock_speed)

        self.video_card_table.setRowCount(0)
        self.cursor.execute(query, params)
        for row_data in self.cursor.fetchall():
            row = self.video_card_table.rowCount()
            self.video_card_table.insertRow(row)
            self.video_card_table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
            self.video_card_table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
            self.video_card_table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
            self.video_card_table.setItem(row, 3, QTableWidgetItem(str(row_data[4])))
            self.video_card_table.setItem(row, 4, QTableWidgetItem(str(row_data[0])))
            self.video_card_table.setColumnHidden(4, True)

            select_button = QPushButton("Выбрать")
            select_button.clicked.connect(lambda _, row=row: self.select_video_card(row))
            self.video_card_table.setCellWidget(row, 5, select_button)
    def add_video_card_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить видеокарту")

        dialog_layout = QGridLayout(dialog)

        form_layout = QFormLayout()
        name_edit = QLineEdit()
        manufacturer_edit = QLineEdit()
        memory_size_spin = QSpinBox()
        memory_size_spin.setMaximum(1000000) # предположим, максимальный размер памяти 32 Гб
        clock_speed_spin = QSpinBox()
        clock_speed_spin.setMaximum(1000000) # максимальная частота 5000 МгЦ


        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Объем видеопамяти (Гб):", memory_size_spin)
        form_layout.addRow("Частота работы (МгЦ):", clock_speed_spin)

        dialog_layout.addLayout(form_layout, 0, 0)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.add_video_card(
            name_edit.text(), manufacturer_edit.text(), memory_size_spin.value(),
            clock_speed_spin.value(), dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    def add_video_card(self, name, manufacturer, memory_size, clock_speed, dialog):
        try:
            self.cursor.execute('''
                INSERT INTO video_cards (name, manufacturer, memory_size, clock_speed)
                VALUES (?, ?, ?, ?)''',
                (name, manufacturer, memory_size, clock_speed))
            self.connection.commit()
            dialog.accept()
            self.load_video_cards()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            dialog.reject()
        except Exception as e:
            print(f"Exception in add_video_card: {e}")
            dialog.reject()

    def edit_video_card_dialog(self):
        current_row = self.video_card_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите видеокарту для редактирования")
            return

        video_card_id = int(self.video_card_table.item(current_row, 4).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать видеокарту")

        dialog_layout = QGridLayout(dialog)

        form_layout = QFormLayout()
        name_edit = QLineEdit()
        manufacturer_edit = QLineEdit()
        memory_size_spin = QSpinBox()
        memory_size_spin.setMaximum(1000000)  # предположим, максимальный размер памяти 32 Гб
        clock_speed_spin = QSpinBox()
        clock_speed_spin.setMaximum(1000000)  # максимальная частота 5000 МгЦ


        self.cursor.execute(
            "SELECT name, manufacturer, memory_size, clock_speed FROM video_cards WHERE id=?",
            (video_card_id,))
        video_card_data = self.cursor.fetchone()
        name_edit.setText(video_card_data[0])
        manufacturer_edit.setText(video_card_data[1])
        memory_size_spin.setValue(int(video_card_data[2]))
        clock_speed_spin.setValue(int(video_card_data[3]))

        # Добавление виджетов в форму
        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Производитель:", manufacturer_edit)
        form_layout.addRow("Объем видеопамяти (Гб):", memory_size_spin)
        form_layout.addRow("Частота работы (МгЦ):", clock_speed_spin)

        dialog_layout.addLayout(form_layout, 0, 0)

        # Кнопки управления сохранением данных о видеокарте
        save_button = QPushButton("Сохранить изменения")
        # Сохранение изменений видеокарты и закрытие диалога по клику
        save_button.clicked.connect(lambda: self.edit_video_card(
            video_card_id, name_edit.text(), manufacturer_edit.text(),
            memory_size_spin.value(), clock_speed_spin.value(),
            dialog
        ))

        close_button = QPushButton("Отмена")
        close_button.clicked.connect(dialog.reject)

        dialog_layout.addWidget(save_button, 1, 0)
        dialog_layout.addWidget(close_button, 1, 1)

        dialog.exec_()

    def edit_video_card(self, video_card_id, name, manufacturer, memory_size, clock_speed, dialog):
        try:
            self.cursor.execute('''
                UPDATE video_cards SET name=?, manufacturer=?, memory_size=?,
                clock_speed=?
                WHERE id=?''',
                (name, manufacturer, memory_size, clock_speed, video_card_id))
            self.connection.commit()
            dialog.accept()
            self.load_video_cards()
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при обновлении данных: {e}")
            dialog.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")
            dialog.reject()

    def delete_video_card(self):
        current_row = self.video_card_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите видеокарту для удаления")
            return

        video_card_id = int(self.video_card_table.item(current_row, 4).text())
        reply = QMessageBox.question(self, 'Удаление записи', 'Вы действительно хотите удалить выбранную видеокарту?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM video_cards WHERE id=?", (video_card_id,))
                self.connection.commit()
                self.load_video_cards()
            except sqlite3.DatabaseError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при удалении данных: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошло исключение: {e}")

    def select_video_card(self, row):
        name = self.video_card_table.item(row, 0).text()

        reply = QMessageBox.question(
            self, 'Подтверждение выбора',
            f"Вы уверены, что хотите выбрать видеокарту {name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.video_card_selected.emit(name)
        else:
            QMessageBox.information(self, 'Выбор отменён', f"Выбор видеокарты {name} отменён.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    configurator = VideoCardWindow()
    configurator.show()
    sys.exit(app.exec_())