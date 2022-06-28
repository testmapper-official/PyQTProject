import sys
import sqlite3
import tempfile
import shutil
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


# глобальные переменные
con = None
filename = ''
temp_path = ''


# окно нахождения записи в таблице
class FindDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint)

        self.parent = parent

        self.initUI()

    # визуальная часть
    def initUI(self):
        global con
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle('Найти:')
        self.setFixedSize(200, 100)

        self.combobox = QComboBox(self)
        self.combobox.setGeometry(5, 5, 190, 20)

        info = con.cursor().execute(f'PRAGMA table_info({self.parent.tablename});').fetchall()
        headernames = [i[1] for i in info]

        self.combobox.addItems(headernames)
        self.combobox.setToolTip('Заголовок, в котором будут искать первое вхождение')

        self.text = QTextEdit('', self)
        self.text.setGeometry(5, 30, 190, 40)
        self.text.setLineWrapMode(QTextEdit.NoWrap)

        self.create = QPushButton('ОК', self)
        self.create.setGeometry(120, 75, 75, 20)
        self.create.clicked.connect(self.func_confirm)

        self.cancel = QPushButton('Отмена', self)
        self.cancel.setGeometry(5, 75, 75, 20)
        self.cancel.clicked.connect(self.func_cancel)

        self.show()

    # закрытие окна при нажатии "Отмена"
    def func_cancel(self):
        self.close()

    # нахождение записи и закрытие окна при нажатии "ОК"
    def func_confirm(self):
        column = 0
        isfound = False
        for i in range(self.parent.table_widget.columnCount()):
            if self.combobox.currentText() == self.parent.table_widget.horizontalHeaderItem(i).text():
                column = i
                break
        print(self.parent.table_widget.rowCount())
        for i in range(self.parent.table_widget.rowCount()):
            item = self.parent.table_widget.takeItem(i, column)
            self.parent.table_widget.setItem(i, column, item)
            if item and self.text.toPlainText() in item.text():
                self.parent.table_widget.scrollToItem(item)
                isfound = True
                break
        if not isfound:
            pass
        self.func_cancel()


# дополнительный диалог для параметра "Первичный ключ"
class PrimaryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint)

        self.parent = parent

        self.initUI()

    def initUI(self):
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle('Настройка ключа')
        self.setFixedSize(200, 200)
        if self.parent.combobox.currentText() == 'INTEGER':
            self.checkbox_auto = QCheckBox('AUTOINCREMENT', self)
            self.checkbox_auto.setGeometry(5, 5, 195, 25)
            self.checkbox_auto.setChecked(self.parent.autoincrement)

        self.create = QPushButton('ОК', self)
        self.create.setGeometry(120, 175, 75, 20)
        self.create.clicked.connect(self.func_confirm)

        self.cancel = QPushButton('Отмена', self)
        self.cancel.setGeometry(5, 175, 75, 20)
        self.cancel.clicked.connect(self.func_cancel)

        self.show()

    def func_cancel(self):
        self.close()


    def func_confirm(self):
        if self.parent.combobox.currentText() == 'INTEGER':
            self.parent.autoincrement = self.checkbox_auto.isChecked()
        self.func_cancel()


# Заголовок
class Header(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.initUI()
        self.autoincrement = False

    def initUI(self):
        self.setFixedSize(400, 40)

        self.tabletext = QLabel(self)
        self.tabletext.setText("ЗАГОЛОВОК")
        self.tabletext.setGeometry(15, 0, 100, 15)

        self.text = QTextEdit('', self)
        self.text.setGeometry(0, 15, 100, 25)
        self.text.setLineWrapMode(QTextEdit.NoWrap)

        self.combobox = QComboBox(self)
        self.combobox.setGeometry(105, 0, 80, 40)
        self.combobox.addItems(sorted(['INTEGER', 'TEXT', 'REAL']))
        self.combobox.currentTextChanged.connect(self.nullification)
        self.combobox.setToolTip('Определяет тип данных, который будет хранить заголовок')

        self.checkbox_null = QCheckBox('NOT NULL', self)
        self.checkbox_null.setGeometry(190, 0, 80, 20)

        self.checkbox_unique = QCheckBox('UNIQUE', self)
        self.checkbox_unique.setGeometry(190, 20, 100, 20)
        self.checkbox_unique.hide()

        self.checkbox_primary = QCheckBox('PRIMARY KEY', self)
        self.checkbox_primary.setGeometry(270, 0, 90, 20)
        self.checkbox_primary.stateChanged.connect(self.moreshow)

        self.primary_more = QPushButton('...', self)
        self.primary_more.setGeometry(360, 0, 20, 20)
        self.primary_more.clicked.connect(self.createprimarydialog)
        self.primary_more.hide()

    # нулифицирует все параметры при изменении типа данных
    def nullification(self):
        self.autoincrement = False

    # показывает доп. диалог при наличии "Первичный ключ"
    def moreshow(self):
        self.primary_more.show() if self.checkbox_primary.isChecked() else self.primary_more.hide()

    # открывает доп. диалог для "Первичный ключ"
    def createprimarydialog(self):
        PrimaryDialog(self)


# Страница с заголовками (настройка таблицы)
class HeaderWidget(QWidget):
    def __init__(self, parent, ishas=False):
        super().__init__(parent)

        self.headers = []
        self.parent = parent
        self.ishas = ishas
        self.initUI()

    def initUI(self):
        self.setFixedSize(300, 70)

        self.create = QPushButton('Создать', self)
        self.create.setGeometry(10, 10, 100, 20)
        self.create.clicked.connect(self.create_header)

        self.create = QPushButton('Обнулить', self)
        self.create.setGeometry(120, 10, 100, 20)
        self.create.clicked.connect(self.reverse_headers)

        if self.ishas:
            for header in con.cursor().execute(f'PRAGMA table_info({self.parent.parent.tablename});').fetchall():
                self.create_header(header)

    # обнуление заголовков
    def reverse_headers(self):
        for header in self.headers:
            header.close()
        self.headers.clear()
        self.setFixedSize(300, 90 + len(self.headers) * 50)

    # создание заголовка
    def create_header(self, subheader=None):
        header = Header(self)
        self.setFixedSize(400, 90 + len(self.headers) * 50)
        header.move(10, len(self.headers) * 50 + 40)
        header.show()
        self.headers.append(header)

        if subheader:
            header.text.setText(subheader[1])
            header.combobox.setCurrentText(subheader[2])
            header.checkbox_null.setChecked(subheader[3])
            header.checkbox_primary.setChecked(subheader[5])


# Диалог при создании новой таблицы
class CreateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint)

        self.parent = parent

        self.initUI()

    def initUI(self):
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle('Создание Таблицы Данных')
        self.setFixedSize(400, 300)

        self.tabletext = QLabel(self)
        self.tabletext.setText("Название таблицы:")
        self.tabletext.setGeometry(1, 0, 100, 25)

        self.tablename = QTextEdit('untitled', self)
        self.tablename.setGeometry(100, 0, 300, 25)
        self.tablename.setLineWrapMode(QTextEdit.NoWrap)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setGeometry(0, 30, 400, 225)
        self.tab_widget.currentChanged.connect(self.tabfunc)

        self.create = QPushButton('ОК', self)
        self.create.setGeometry(290, 270, 100, 20)
        self.create.clicked.connect(self.func_create)

        self.cancel = QPushButton('Отмена', self)
        self.cancel.setGeometry(10, 270, 100, 20)
        self.cancel.clicked.connect(self.func_cancel)

        self.headerwidget = QScrollArea(self)
        self.headerwidget.setWidgetResizable(True)
        self.headerwidget.setGeometry(0, 0, 400, 225)
        self.scrollAreaWidgetContents = HeaderWidget(self)
        self.headerwidget.setWidget(self.scrollAreaWidgetContents)

        self.textbrowser = QTextBrowser(self)
        self.textbrowser.setGeometry(10, 10, 350, 225)
        self.textbrowser.setLineWrapMode(QTextBrowser.NoWrap)
        self.textbrowser.horizontalScrollBar().setValue(0)
        self.textbrowser.setAutoFillBackground(False)
        self.textbrowser.setReadOnly(False)
        self.textbrowser.setPlainText("""CREATE TABLE untitled (
                                            id INTEGER  NOT NULL
                                                        PRIMARY KEY AUTOINCREMENT
                                                        UNIQUE
                                            );""")
        self.textbrowser.setStyleSheet("""
                    font: 75 8pt \"Times New Roman\"
                """)
        self.textbrowser.show()

        self.tab_widget.addTab(self.headerwidget, 'GUI')
        self.tab_widget.addTab(self.textbrowser, 'SQL')

        self.show()

    def tabfunc(self):
        if self.tab_widget.tabText(self.tab_widget.currentIndex()) == 'SQL':
            self.tablename.hide()
            self.tabletext.hide()
        else:
            self.tablename.show()
            self.tabletext.show()

    # Создает таблицу в БД
    def func_create(self):
        global con
        if self.tab_widget.tabText(self.tab_widget.currentIndex()) == 'SQL':
            try:
                con.cursor().execute(self.textbrowser.toPlainText())
                con.commit()
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Упс, что-то пошло не так!")
                msg.setInformativeText(f"{e}")
                msg.setWindowTitle("Ошибка")
                msg.exec_()
        else:
            request = """CREATE TABLE IF NOT EXISTS {} (
            {});"""
            data = {
                'tablename': '_'.join(self.tablename.toPlainText().split()),
                'headers': '',
            }
            for header in self.scrollAreaWidgetContents.headers:
                if header.text.toPlainText().isspace() or header.text.toPlainText() == '':
                    continue
                if data['headers'] != '':
                    data['headers'] += ',\n\t\t'
                data['headers'] += f"""{header.text.toPlainText()} {header.combobox.currentText()}
                        {'PRIMARY KEY' if header.checkbox_primary.isChecked() else ''}
                        {'NOT NULL' if header.checkbox_null.isChecked() else ''}
                        {'UNIQUE' if header.checkbox_unique.isChecked() else ''} """
            # создаем все таблицы
            try:
                con.cursor().execute(request.format(*data.values()))
                con.commit()
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Упс, что-то пошло не так!")
                msg.setInformativeText(f"{e}")
                msg.setWindowTitle("Ошибка")
                msg.exec_()

        # и загружаем все таблицы
        try:
            tables_name = con.cursor().execute(
                '''SELECT name from sqlite_master where type = "table"''').fetchall()
            self.parent.tab_widget.clear()
            for page in range(self.parent.tab_widget.count()):
                self.parent.tab_widget.widget(page).close()
            for table in tables_name:
                if table[0] != 'sqlite_sequence':
                    self.parent.load_table(table[0])
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Упс, что-то пошло не так!")
            msg.setInformativeText(f"{e}")
            msg.setWindowTitle("Ошибка")
            msg.exec_()
        self.func_cancel()

    def func_cancel(self):
        self.close()


# Диалог при изменении существующей таблицы
class ChangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint)

        self.parent = parent

        self.initUI()

    def initUI(self):
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle('Настройка Таблицы Данных')
        self.setFixedSize(400, 300)

        self.tabletext = QLabel(self)
        self.tabletext.setText("Название таблицы:")
        self.tabletext.setGeometry(1, 0, 100, 25)

        self.tablename = QTextEdit(self.parent.tablename, self)
        self.tablename.setGeometry(100, 0, 300, 25)
        self.tablename.setLineWrapMode(QTextEdit.NoWrap)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setGeometry(0, 25, 400, 225)

        self.create = QPushButton('ОК', self)
        self.create.setGeometry(290, 270, 100, 20)
        self.create.clicked.connect(self.func_create)

        self.cancel = QPushButton('Отмена', self)
        self.cancel.setGeometry(10, 270, 100, 20)
        self.cancel.clicked.connect(self.func_cancel)

        self.headerwidget = QScrollArea(self)
        self.headerwidget.setWidgetResizable(True)
        self.headerwidget.setGeometry(0, 0, 400, 225)
        self.scrollAreaWidgetContents = HeaderWidget(self, True)
        self.headerwidget.setWidget(self.scrollAreaWidgetContents)

        self.tab_widget.addTab(self.headerwidget, 'GUI')

        self.show()

    # удаляет старую таблицу создает новую, забирая все данные из старой, если есть такая возможность
    def func_create(self):
        global con
        data = {
            'tablename': '_'.join(self.tablename.toPlainText().split()),
            'headers': '',
        }
        cur = con.cursor()

        info = cur.execute(f'PRAGMA table_info({self.parent.tablename});').fetchall()
        new_info = self.scrollAreaWidgetContents.headers
        headernames = []
        new_headernames = []

        for i in range(len(info)):
            if i < len(new_info):
                if info[i][2] == new_info[i].combobox.currentText():
                    new_headernames.append(new_info[i].text.toPlainText())
                    headernames.append(info[i][1])

        for header in self.scrollAreaWidgetContents.headers:
            if header.text.toPlainText().isspace() or header.text.toPlainText() == '':
                continue
            if data['headers'] != '':
                data['headers'] += ',\n\t\t'
            data['headers'] += f"""{header.text.toPlainText()} {header.combobox.currentText()}
                    {'NOT NULL' if header.checkbox_null.isChecked() else 'NULL'}
                    {'UNIQUE' if header.checkbox_unique.isChecked() else ''} 
                    {'PRIMARY KEY' if header.checkbox_primary.isChecked() else ''}"""

        # пересоздаем таблицу
        try:
            cur.execute('''CREATE TABLE bdreader_temp_table AS SELECT *
                                                      FROM {};'''.format(self.parent.tablename))
            cur.execute('DROP TABLE {};'.format(self.parent.tablename))
            cur.execute('''CREATE TABLE IF NOT EXISTS {} (
                                {} );'''.format(data['tablename'], data['headers']))
            cur.execute('''INSERT INTO {} (
                                 {}
                             )
                             SELECT {} FROM bdreader_temp_table;'''.format(data['tablename'], ','.join(
                new_headernames), ','.join(headernames)))
            cur.execute('DROP TABLE bdreader_temp_table;')

            con.commit()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Упс, что-то пошло не так!")
            msg.setInformativeText(f"{e}")
            msg.setWindowTitle("Ошибка")
            msg.exec_()

        try:
            self.parent.table_widget.clearContents()
            # получаем инфу по текущей таблице
            data = con.cursor().execute(f'''PRAGMA table_info({self.parent.tablename})''').fetchall()
            title = [i[1] for i in data]
            result = con.cursor().execute(f"""SELECT * FROM {self.parent.tablename}""").fetchall()

            # создаем и настраиваем страницу
            self.parent.table_widget.setColumnCount(len(title))
            self.parent.table_widget.setRowCount(len(result))
            self.parent.table_widget.setHorizontalHeaderLabels(title)

            for i, row in enumerate(result):
                for j, elem in enumerate(row):
                    item = QTableWidgetItem(str(elem))
                    self.parent.table_widget.setItem(i, j, item)

            self.parent.table_widget.resizeColumnsToContents()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Упс, что-то пошло не так!")
            msg.setInformativeText(f"{e}")
            msg.setWindowTitle("Ошибка")
            msg.exec_()
        self.func_cancel()

    def func_cancel(self):
        self.close()


# страница с таблицей
class Page(QWidget):
    def __init__(self, parent=None, table='', title=[]):
        super().__init__()

        self.parent = parent
        self.tablename = table
        self.headers = title
        self.last_pb_text = ''

        print(self.tablename, self.headers)

        self.initUI()

    def initUI(self):
        self.add = QPushButton('Добавить', self)
        self.add.setGeometry(5, 10, 90, 20)
        self.add.clicked.connect(self.func_add)
        self.add.setToolTip('Добавляет запись в таблицу')

        self.change = QPushButton('Найти', self)
        self.change.setGeometry(100, 10, 90, 20)
        self.change.clicked.connect(self.func_find)
        self.change.setToolTip('Функция, позволяющая найти существующие запись(и) по запросу в таблице')

        self.delete = QPushButton('Удалить', self)
        self.delete.setGeometry(195, 10, 90, 20)
        self.delete.clicked.connect(self.func_remove)
        self.delete.setToolTip('Удаляет выделенную запись в таблице')

        self.confirm = QPushButton('Подтвердить', self)
        self.confirm.setGeometry(290, 10, 90, 20)
        self.confirm.clicked.connect(self.func_confirm)
        self.confirm.setToolTip('Подтверждает все внесенные изменения в таблице, занося в временный БД SQL')

        self.delete = QPushButton('Настройки', self)
        self.delete.setGeometry(385, 10, 90, 20)
        self.delete.clicked.connect(self.func_settings)
        self.delete.setToolTip('Изменить структуру таблицы')

        self.reverse = QPushButton('Отменить', self)
        self.reverse.setGeometry(480, 10, 90, 20)
        self.reverse.clicked.connect(self.func_reverse)
        self.reverse.setToolTip('Отменяет все внесенные изменения до последнего подтверждения')

        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(10, 40, 580, 480)
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)

        self.table_widget.setEditTriggers(QAbstractItemView.SelectedClicked)

    # добавить запись
    def func_add(self):
        row = self.table_widget.rowCount()
        self.table_widget.setRowCount(row + 1)
        columns = self.table_widget.columnCount()
        for i in range(columns):
            string = 'null'
            item = QTableWidgetItem(string)
            self.table_widget.setItem(row, i, item)

    # удалить запись
    def func_remove(self):
        self.table_widget.removeRow(self.table_widget.currentRow())

    # найти запись
    def func_find(self):
        FindDialog(self).exec()

    # изменение структуры таблицы
    def func_settings(self):
        ChangeDialog(self).exec()

    # подтверждение данных и перенос в БД
    def func_confirm(self):
        global con
        self.table_widget.resizeColumnsToContents()
        try:
            data = ''

            cur = con.cursor()

            info = cur.execute(f'PRAGMA table_info({self.tablename});').fetchall()
            headernames = [i[1] for i in info]

            for header in info:
                if data != '':
                    data += ',\n\t\t'
                data += f"""{header[1]} {header[2]}
                                {'NOT NULL' if header[3] else 'NULL'}
                                {'UNIQUE' if False else ''} 
                                {'PRIMARY KEY' if header[5] else ''}"""

            request = ''
            for i in range(self.table_widget.rowCount()):
                if request != '':
                    request += ', '
                s = '('
                for j in range(self.table_widget.columnCount()):
                    if s != '(':
                        s += ', '
                    if info[j][2] == 'TEXT':
                        s += "'" + self.table_widget.item(i, j).text() + "'"
                    else:
                        s += self.table_widget.item(i, j).text()
                request += s + ')'
            print(request)
            # создаем все таблицы
            cur.execute('DROP TABLE {};'.format(self.tablename))
            cur.execute('''CREATE TABLE {} (
                                {} );'''.format(self.tablename, data))
            request_code = '''INSERT INTO {} (
                                 {}
                             )
                             VALUES
                              {};'''
            # print(request_code.format(self.tablename, ', '.join(headernames), request))
            cur.execute(request_code.format(self.tablename, ', '.join(headernames), request))

            con.commit()
            print('успешно')
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Упс, что-то пошло не так!")
            msg.setInformativeText(f"{e}")
            msg.setWindowTitle("Ошибка")
            msg.exec_()

    # отменение всех внесенных данных в таблицу
    def func_reverse(self):
        global con
        try:
            self.table_widget.clearContents()
            # получаем инфу по текущей таблице
            data = con.cursor().execute(f'''PRAGMA table_info({self.tablename})''').fetchall()
            title = [i[1] for i in data]
            result = con.cursor().execute(f"""SELECT * FROM {self.tablename}""").fetchall()

            # создаем и настраиваем страницу
            self.table_widget.setColumnCount(len(title))
            self.table_widget.setRowCount(len(result))
            self.table_widget.setHorizontalHeaderLabels(title)

            for i, row in enumerate(result):
                for j, elem in enumerate(row):
                    item = QTableWidgetItem(str(elem))
                    self.table_widget.setItem(i, j, item)

            self.table_widget.resizeColumnsToContents()
        except Exception as e:
            QErrorMessage(self).showMessage(f"Произошла ошибка:\n {e}")


# основное окно
class Main(QMainWindow):
    qss = open('themes/menacing.qss', 'r').read()

    def __init__(self):
        super().__init__()
        self.initUI()

    # настройка окна
    def initUI(self):
        #self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setStyleSheet(self.qss)

        self.setGeometry(300, 100, 800, 600)
        self.setWindowTitle('Data Editor')

        self.centralwidget = QWidget(self)
        self.tab_widget = QTabWidget(self.centralwidget)
        self.tab_widget.setGeometry(200, 0, 600, 560)
        self.setCentralWidget(self.centralwidget)

        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(0, 0, 600, 20)
        self.menu = QMenu('Файл', self.menubar)
        self.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.NEW_FILE_BUTTON = QAction('Создать...\tCtrl+N', self)
        self.NEW_FILE_BUTTON.triggered.connect(self.create_db)
        self.menu.addAction(self.NEW_FILE_BUTTON)
        self.OPEN_FILE_BUTTON = QAction('Открыть...\tCtrl+O', self)
        self.OPEN_FILE_BUTTON.triggered.connect(self.open_db)
        self.menu.addAction(self.OPEN_FILE_BUTTON)
        self.SAVE_FILE_BUTTON = QAction('Сохранить\tCtrl+S', self)
        self.SAVE_FILE_BUTTON.triggered.connect(self.save_db)
        self.menu.addAction(self.SAVE_FILE_BUTTON)
        self.SAVE_AS_FILE_BUTTON = QAction('Сохранить как...\tCtrl+Shift+S', self)
        self.SAVE_AS_FILE_BUTTON.triggered.connect(self.save_as_db)
        self.menu.addAction(self.SAVE_AS_FILE_BUTTON)
        self.menubar.addAction(self.menu.menuAction())

        self.tablebutton = QPushButton('Создать таблицу', self)
        self.tablebutton.setGeometry(0, 20, 200, 50)
        self.tablebutton.clicked.connect(self.create_table)
        #self.tablebutton.hide()

        self.tablebutton2 = QPushButton('Удалить таблицу', self)
        self.tablebutton2.setGeometry(0, 70, 200, 50)
        self.tablebutton2.clicked.connect(self.delete_table)
        self.tablebutton2.hide()

        self.tab_widget.setCurrentIndex(0)

    # реализация нажатий горячих клавиш
    def keyPressEvent(self, event):
        # print(event.nativeScanCode())
        # print(int(event.modifiers()))
        if int(event.modifiers()) == 67108864:  # Ctrl
            if event.nativeScanCode() == 49:  # + N
                self.create_db()
                pass
            elif event.nativeScanCode() == 19 and self.FILE_NAME != '':  # + R
                # self.function_Close_File()
                pass
            elif event.nativeScanCode() == 31 and self.FILE_NAME != '':  # + S
                # self.function_Save_File()
                pass
            elif event.nativeScanCode() == 24:  # + O
                self.open_db()
        elif int(event.modifiers()) == 67108864 + 33554432:  # Ctrl + Shift
            if event.nativeScanCode() == 31 and self.FILE_NAME != '':  # + S
                # self.function_Save_As_File()
                pass
        elif int(event.nativeScanCode()) == 339:  # Delete
            pass

    # удаление таблицы из БД
    def delete_table(self):
        global con
        if self.tab_widget.count():
            con.cursor().execute('DROP TABLE {};'.format(self.tab_widget.currentWidget().tablename))
            self.tab_widget.currentWidget().close()
            self.tab_widget.removeTab(self.tab_widget.currentIndex())
            con.commit()

    # содание таблицы в БД
    def create_table(self):
        CreateDialog(self).exec()

    # сохранение БД
    def save_db(self):
        global filename
        global temp_path
        shutil.copyfile(temp_path, filename)

    # сохранение БД как новый файл
    def save_as_db(self):
        global filename
        global con
        global temp_path
        name = QFileDialog.getSaveFileName(self, 'Создать базу данных', '',
                                           'db (*.db);;sqlite3 (*.sqlite)')[0]
        if name != '':
            filename = name

            shutil.copyfile(temp_path, filename)

    # создание БД
    def create_db(self):
        global filename
        global con
        global temp_path
        name = QFileDialog.getSaveFileName(self, 'Создать базу данных', '',
                                           'db (*.db);;sqlite3 (*.sqlite)')[0]
        if name != '':
            with open(name, 'w') as f:
                f.write('')

            if con:
                con.close()
                con = None
            filename = name

            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, 'temp_file_name.' + filename.split('.')[-1])
            shutil.copy2(filename, temp_path)
            con = sqlite3.connect(temp_path)

            print(filename)
            print(temp_path)

            self.tab_widget.clear()
            self.tablebutton.show()
            self.tablebutton2.show()

            self.setWindowTitle(f'Data Editor - {filename}')

    # открытие БД
    def open_db(self):
        global filename
        global con
        global temp_path
        # пользователь выбирает произвольную базу данных
        name = QFileDialog.getOpenFileName(self, 'Выбрать базу данных', '',
                                           'База данных (*)')[0]
        formats = ['sqlite', 'db']
        if name != '' and name.split('.')[-1] in formats:
            if con:
                con.close()
                con = None

            filename = name

            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, 'temp_file_name.' + filename.split('.')[-1])
            shutil.copy2(filename, temp_path)
            con = sqlite3.connect(temp_path)

            self.tablebutton.show()
            self.tablebutton2.show()
            # и загружаем все таблицы
            tables_name = con.cursor().execute(
                '''SELECT name from sqlite_master where type = "table"''').fetchall()
            self.tab_widget.clear()
            for page in range(self.tab_widget.count()):
                self.tab_widget.widget(page).close()
            for table in tables_name:
                if table[0] != 'sqlite_sequence':
                    self.load_table(table[0])

            self.setWindowTitle(f'Data Editor - {filename}')

    # загрузка таблицы БД
    def load_table(self, table):
        global con
        # получаем инфу по текущей таблице
        data = con.cursor().execute(f'''PRAGMA table_info({table})''').fetchall()
        title = [i[1] for i in data]
        result = con.cursor().execute(f"""SELECT * FROM {table}""").fetchall()

        # создаем и настраиваем страницу
        ex = Page(self, table, title)
        ex.table_widget.setColumnCount(len(title))
        ex.table_widget.setRowCount(len(result))
        ex.table_widget.setHorizontalHeaderLabels(title)

        for i, row in enumerate(result):
            for j, elem in enumerate(row):
                item = QTableWidgetItem(str(elem))
                # item.setFlags(Qt.ItemIsEnabled)
                ex.table_widget.setItem(i, j, item)

        ex.table_widget.resizeColumnsToContents()
        # добавляем на главный экран
        self.tab_widget.addTab(ex, table)

    # завершение прграммы
    def closeEvent(self, event):
        global con
        if con is not None:
            con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = Main()
    m.show()
    sys.exit(app.exec())
