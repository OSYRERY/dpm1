import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QMessageBox
from ProcessorWindow import ProcessorWindow
from MatherboardWindow import MatherboardWindow
from CoolerWindow import CoolerWindow
from VideoCardWindow import VideoCardWindow
from RAMWindow import RAMWindow
from StorageWindow import StorageWindow
from PowerSupplyWindow import PowerSupplyWindow
from CaseWindow import CaseWindow
from OperatingSystemWindow import OperatingSystemWindow
from ConfigurationWindow import ConfigurationWindow


class ComputerConfigurator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.selected_socket = None
        self.selected_form_factor = None
        self.selected_ram_slots = None
        self.selected_ram_type = None

        self.setWindowTitle("Computer Configurator")
        self.setGeometry(100, 100, 500, 700)

        # Вертикальное расположение виджетов
        layout = QVBoxLayout()

        # Описание
        label = QLabel("Выберите компонент:")
        layout.addWidget(label)

        # Кнопка "Процессор"
        button_processor = QPushButton("Процессор")
        button_processor.clicked.connect(self.open_processor_window)
        layout.addWidget(button_processor)

        # Кнопка "Материнская плата"
        button_motherboard = QPushButton("Материнская плата")
        button_motherboard.clicked.connect(self.open_motherboard_window)
        layout.addWidget(button_motherboard)

        # Кнопка "Охлаждение"
        button_cooler = QPushButton("Охлаждение")
        button_cooler.clicked.connect(self.open_cooler_window)
        layout.addWidget(button_cooler)

        # Кнопка "Видеокарта"
        button_video_card = QPushButton("Видеокарта")
        button_video_card.clicked.connect(self.open_video_card_window)
        layout.addWidget(button_video_card)

        # Кнопка "Оперативная память"
        button_ram = QPushButton("Оперативная память")
        button_ram.clicked.connect(self.open_ram_window)
        layout.addWidget(button_ram)

        # Кнопка "Система хранения"
        button_storage = QPushButton("Накопитель")
        button_storage.clicked.connect(self.open_storage_window)
        layout.addWidget(button_storage)

        # Кнопка "Блок питания"
        button_power_supply = QPushButton("Блок питания")
        button_power_supply.clicked.connect(self.open_power_supply_window)
        layout.addWidget(button_power_supply)

        # Кнопка "Корпус"
        button_case = QPushButton("Корпус")
        button_case.clicked.connect(self.open_case_window)
        layout.addWidget(button_case)

        # Кнопка "Операционная система"
        button_os = QPushButton("Операционная система")
        button_os.clicked.connect(self.open_os_window)
        layout.addWidget(button_os)

        # Таблица для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setColumnWidth(0, 330)
        self.table.setHorizontalHeaderLabels(["Название", "Действие"])
        layout.addWidget(self.table)

        # Кнопка "Сброс конфигуратора"
        self.reset_button = QPushButton("Сброс конфигуратора")
        self.reset_button.clicked.connect(self.reset_configurator)
        layout.addWidget(self.reset_button)


        self.button_save = QPushButton("Сохранить конфигурацию")
        self.button_save.clicked.connect(self.save_current_configuration)
        layout.addWidget(self.button_save)

        # Кнопка "Сохраненные конфигурации"
        self.button_view_saved_configs = QPushButton("Сохраненные конфигурации")
        self.button_view_saved_configs.clicked.connect(self.open_configuration_window)
        layout.addWidget(self.button_view_saved_configs)

        # Основной виджет
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # создание экземпляра окон для каждого компонента и подключение сигнала
        self.processor_window = ProcessorWindow()
        self.processor_window.processor_selected.connect(self.add_processor_to_table)

        self.motherboard_window = MatherboardWindow()
        self.motherboard_window.motherboard_selected.connect(self.add_motherboard_to_table)
        

        self.cooler_window = CoolerWindow()
        self.cooler_window.cooler_selected.connect(self.add_cooler_to_table)

        self.video_card_window = VideoCardWindow()
        self.video_card_window.video_card_selected.connect(self.add_video_card_to_table)

        self.ram_window = RAMWindow()
        self.ram_window.ram_selected.connect(self.add_ram_to_table)

        self.storage_window = StorageWindow()
        self.storage_window.storage_selected.connect(self.add_storage_to_table)

        self.power_supply_window = PowerSupplyWindow()
        self.power_supply_window.power_supply_selected.connect(self.add_power_supply_to_table)

        self.case_window = CaseWindow()
        self.case_window.case_selected.connect(self.add_case_to_table)

        self.os_window = OperatingSystemWindow()
        self.os_window.operating_system_selected.connect(self.add_os_to_table)

        self.configuration_window = ConfigurationWindow()


        self.components = []  # список выбранных компонентов

    # процессор
    def add_processor_to_table(self, name, socket):
        row = self.table.rowCount()
        self.selected_socket = socket

        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))

        remove_button = QPushButton("Убрать")
        remove_button.clicked.connect(self.remove_component)
        self.table.setCellWidget(row, 1, remove_button)

        self.components.append((name, 'Процессор', socket))  # Указание типа компонента для дальнейшей работы

        self.motherboard_window.show_with_socket_filter(socket = socket)
        
    def open_processor_window(self): #\\
        if self.selected_socket:
            self.processor_window.show_with_socket_filter(self.selected_socket)
        self.processor_window.show()

    # мат плата
    def add_motherboard_to_table(self, name, socket, form_factor, ram_slots, ram_type):
        row = self.table.rowCount()
        self.selected_socket = socket
        self.selected_form_factor = form_factor  # Сохраняем форм-фактор
        self.selected_ram_slots = ram_slots
        self.selected_ram_type = ram_type
        
        print(f'add_motherboard_to_table {self.selected_socket, self.selected_form_factor, self.selected_ram_slots, self.selected_ram_type}')

        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))

        remove_button = QPushButton("Убрать")
        remove_button.clicked.connect(self.remove_component)
        self.table.setCellWidget(row, 1, remove_button)

        self.components.append((name, 'Материнская плата', socket, ram_slots, ram_type))

    def open_motherboard_window(self):
        if self.selected_socket or self.selected_form_factor or self.selected_ram_slots or self.selected_ram_type:
            self.motherboard_window.show_with_socket_filter(self.selected_socket, self.selected_form_factor, self.selected_ram_slots, self.selected_ram_type)
        self.motherboard_window.show()

    # кулер
    def add_cooler_to_table(self, name, socket):
        row = self.table.rowCount()
        self.selected_socket = socket

        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))

        remove_button = QPushButton("Убрать")
        remove_button.clicked.connect(self.remove_component)
        self.table.setCellWidget(row, 1, remove_button)

        self.components.append((name,'Охлаждение', socket))

    def open_cooler_window(self):
        if self.selected_socket:
            self.cooler_window.show_with_socket_filter(self.selected_socket)
        self.cooler_window.show()

    # видеокарта
    def add_video_card_to_table(self, name):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))

        remove_button = QPushButton("Убрать")
        remove_button.clicked.connect(self.remove_component)
        self.table.setCellWidget(row, 1, remove_button)

        self.components.append((name, 'Видеокарта'))

    def open_video_card_window(self):
        self.video_card_window.show()

    # оперативная память
    def add_ram_to_table(self, name, ram_slots, ram_type):
        row = self.table.rowCount()

        self.selected_ram_slots = ram_slots
        self.selected_ram_type = ram_type

        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))

        remove_button = QPushButton("Убрать")
        remove_button.clicked.connect(self.remove_component)
        self.table.setCellWidget(row, 1, remove_button)

        self.components.append((name, 'Оперативная память'))

    def open_ram_window(self):
        if self.selected_ram_slots and self.selected_ram_type:
            self.ram_window.show_with_ram_filters(self.selected_ram_slots, self.selected_ram_type)
        self.ram_window.show()

    # накопитель
    def add_storage_to_table(self, name):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))

        remove_button = QPushButton("Убрать")
        remove_button.clicked.connect(self.remove_component)
        self.table.setCellWidget(row, 1, remove_button)

        self.components.append((name, 'Накопитель'))

    def open_storage_window(self):
        self.storage_window.show()

    # блок питания
    def add_power_supply_to_table(self, name, form_factor):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))

        remove_button = QPushButton("Убрать")
        remove_button.clicked.connect(self.remove_component)
        self.table.setCellWidget(row, 1, remove_button)

        self.components.append((name, "Блок питания"))
        
        self.selected_form_factor = form_factor
        print('add_power_supply_to_table', form_factor)

    def open_power_supply_window(self):
        if self.selected_form_factor:
            self.power_supply_window.show_with_form_factor_filter(self.selected_form_factor)
        self.power_supply_window.show()

    # корпус
    def add_case_to_table(self, name, form_factor):  # Добавьте form_factor как параметр
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        

        remove_button = QPushButton("Убрать")
        remove_button.clicked.connect(self.remove_component)
        self.table.setCellWidget(row, 1, remove_button)

        self.components.append((name, 'Корпус'))
        
        self.selected_form_factor = form_factor  # Сохранить выбранный форм-фактор для фильтрации материнских плат
        print('add_case_to_table', form_factor)

    def open_case_window(self):
        if self.selected_form_factor:
            self.case_window.set_form_factor_filter(self.selected_form_factor)
        self.case_window.show()

    # операционная система
    def add_os_to_table(self, name):
        row = self.table.rowCount() #\\
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))

        remove_button = QPushButton("Убрать")
        remove_button.clicked.connect(self.remove_component)
        self.table.setCellWidget(row, 1, remove_button)

        self.components.append((name, "Операционная система"))

    def open_os_window(self):
        self.os_window.show()

    def open_configuration_window(self):
        self.configuration_window.load_configurations()
        self.configuration_window.show()

    def remove_component(self):
        button = self.sender()
        if button:
            row = self.table.indexAt(button.pos()).row()  # Получение индекса строки по позиции кнопки
            if row >= 0 and row < len(self.components):
                self.table.removeRow(row)
                del self.components[row]
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить компонент: недействительный индекс")

    # Сброс конфигуратора
    def reset_configurator(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        self.components = []
        self.selected_socket = None
        self.selected_form_factor = None
        self.selected_ram_slots = None
        self.selected_ram_type = None
        self.ram_window.reset_filters()
        self.motherboard_window.reset_filters()
        self.processor_window.reset_filters()
        self.case_window.reset_filters()
        self.cooler_window.reset_filters()


    def save_current_configuration(self):
        if not self.components:
            QMessageBox.warning(self, "Внимание", "Нет компонентов для сохранения")
            return
        config_str = '; '.join([f"{name} - {price}" for name, price, *_ in self.components])
        self.configuration_window.save_configuration(config_str)
        QMessageBox.information(self, "Сохранено", "Конфигурация успешно сохранена")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = ComputerConfigurator()
    main_window.show()
    sys.exit(app.exec_())

