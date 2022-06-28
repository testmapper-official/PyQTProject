from PyQt5.QtCore import Qt
from os import path

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QGridLayout, QTreeView, \
    QTabWidget
import json

from pyclass.PythonEditor import QSimplePythonEditor


class App(QWidget):
    dark = open('themes/dark.qss', 'r').read()
    light = open('themes/light.qss', 'r').read()

    def __init__(self, frameless_window):
        super().__init__()

        self.isBarHidden = True

        self.widgets = []

        self.readOnly = True
        self.isDark = True

        self.setStyleSheet(self.dark)

        # Использовать шрифты Webdings для отображения значков
        self.win = frameless_window
        self.titleBar = frameless_window.titleBar

        ButtonWidget = QWidget(objectName="ButtonWidget")

        #self.createButton = QPushButton('Create file', clicked=self.createFile, objectName="CreateButton")
        self.openButton = QPushButton('Open file', clicked=self.openFile, objectName="OpenButton")
        self.modeButton = QPushButton('Read-Only', clicked=self.modeFile, objectName="ModeButton")
        self.themeButton = QPushButton('Change Theme', clicked=self.changeTheme, objectName="ThemeButton")
        #self.saveButton = QPushButton('Save file', clicked=self.saveFile, objectName="SaveButton")
        #self.indexTree = QTreeView(objectName="IndexTree")
        #self.indexTree.setMaximumWidth(115)

        #self.createButton.hide()
        self.openButton.hide()
        self.modeButton.hide()
        self.themeButton.hide()
        #self.saveButton.hide()
        #self.indexTree.hide()


        self.toggle = QPushButton('8', clicked=self.slideinfo, objectName="ToggleBar")
        self.toggle.setFixedWidth(30)
        self.toggle.setMaximumHeight(1500)

        self.tabWidget = QTabWidget()
        self.tabWidget.setStyleSheet('background-color: rgb(39, 40, 34);')
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setAutoFillBackground(True)
        self.tabWidget.tabCloseRequested.connect(lambda index: self.onTabClose(index))

        # Загрузка файлов из сохраненного кэша программы
        with open('static/res.json') as res:
            data = json.load(res)
            for name in data['PATHS']: # перебирает сохраненные пути файлов
                if path.isfile(name): # если существует файл, то открывает
                    f = open(name, 'r', encoding='utf-8').read()
                    Page = QSimplePythonEditor()
                    Page.setText(f)
                    self.tabWidget.addTab(Page, name)
                else: # если нет, то удаляет его из кэша с последующим сохранением изменений.
                    data['PATHS'].remove(name)
        with open('static/res.json', 'w') as res:
            json.dump(data, res)

        # вспомогательный лэйаут, выдвижная панель
        toggleLayout = QGridLayout()
        toggleLayout.setContentsMargins(0, 0, 0, 0)
        toggleLayout.setSpacing(0)
        #toggleLayout.addWidget(self.createButton, 0, 0)
        toggleLayout.addWidget(self.openButton, 7, 0)
        toggleLayout.addWidget(self.modeButton, 8, 0)
        toggleLayout.addWidget(self.themeButton, 9, 0)
        #toggleLayout.addWidget(self.saveButton, 2, 0)
        #toggleLayout.addWidget(self.indexTree, 3, 0, 15, 0)
        toggleLayout.addWidget(self.toggle, 0, 1, 15, 1)

        # лэйаут с текстовым редактором
        workLayout = QVBoxLayout()
        workLayout.setContentsMargins(0, 0, 0, 0)
        workLayout.setSpacing(0)
        workLayout.addWidget(self.tabWidget)

        # создание основного лэйаута
        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addLayout(toggleLayout)
        mainLayout.addLayout(workLayout)

        self.setLayout(mainLayout)

        self.widgets.append(self)
        self.widgets.append(self.openButton)
        self.widgets.append(self.modeButton)
        self.widgets.append(self.themeButton)
        self.widgets.append(self.tabWidget)
        self.widgets.append(self.toggle)
        self.widgets.append(self.titleBar)

    def changeTheme(self):
        if self.isDark:
            for widget in self.widgets:
                widget.setStyleSheet(self.light)
            self.tabWidget.setStyleSheet('background-color: rgb(255, 255, 255);')
            self.win.setWidget(self, dark=False)
            self.titleBar.titleLabel.setStyleSheet("""
                            text-align: left center;
                            color: white;
                            font: 10pt "Britannic Bold";""")
            self.titleBar.buttonMaximum.setStyleSheet(self.light)
            self.titleBar.buttonMinimum.setStyleSheet(self.light)
            self.titleBar.buttonClose.setStyleSheet(self.light)
            for index in range(self.tabWidget.count()):
                self.tabWidget.widget(index).setTheme(False)

        else:
            for widget in self.widgets:
                widget.setStyleSheet(self.dark)
            self.tabWidget.setStyleSheet('background-color: rgb(39, 40, 34);')
            self.win.setWidget(self, dark=True)
            self.titleBar.titleLabel.setStyleSheet("""
                text-align: left center;
                color: gray;
                font: 10pt "Britannic Bold";""")
            self.titleBar.buttonMaximum.setStyleSheet(self.dark)
            self.titleBar.buttonMinimum.setStyleSheet(self.dark)
            self.titleBar.buttonClose.setStyleSheet(self.dark)
            for index in range(self.tabWidget.count()):
                self.tabWidget.widget(index).setTheme(True)
        self.isDark = not(self.isDark)


    def modeFile(self):
        self.readOnly = not (self.readOnly)
        for index in range(self.tabWidget.count()):
            self.tabWidget.widget(index).setReadOnly(self.readOnly)
        if self.readOnly:
            self.modeButton.setText('Read-Only')
        else:
            self.modeButton.setText('Write Mode')


    def onTabClose(self, index):
        name = self.tabWidget.tabText(index)
        with open('static/res.json') as res:
            data = json.load(res)
        data['PATHS'].remove(name)
        with open('static/res.json', 'w') as res:
            json.dump(data, res)

        self.tabWidget.removeTab(index)

    """def createFile(self):
        self.tabWidget.addTab(QSimplePythonEditor(), "untitled")"""

    """def saveFile(self):
        if path.isfile(self.tabWidget.tabText(self.tabWidget.currentIndex())):
            with open(self.tabWidget.tabText(self.tabWidget.currentIndex()), 'w', encoding='utf-8') as f:
                f.write(self.tabWidget.widget(self.tabWidget.currentIndex()).text())
        else:
            # пользователь выбирает произвольный файл
            name = QFileDialog.getSaveFileName(self, 'Выбрать файл', '',
                                               'Python file (*.py)')[0]
            formats = ['py']
            if name != '' and name.split('.')[-1] in formats:
                with open(name, 'w', encoding='utf-8') as f:
                    f.write(self.tabWidget.widget(self.tabWidget.currentIndex()).text())
                    self.tabWidget.setTabText(self.tabWidget.currentIndex(), name)"""


    def openFile(self):
        # пользователь выбирает произвольный файл
        name = QFileDialog.getOpenFileName(self, 'Выбрать файл', '',
                                           'Python file (*.py)')[0]
        formats = ['py']
        if name != '' and name.split('.')[-1] in formats:
            f = open(name, 'r', encoding='utf-8').read()
            Page = QSimplePythonEditor()
            Page.setText(f)
            Page.setTheme(self.isDark)
            print(1)
            # сохранение пути файла в кэш
            with open('static/res.json') as res:
                data = json.load(res)
            if name in data['PATHS']: # если файл повторно открывают, операция прерывается
                return
            data['PATHS'].append(name)
            with open('static/res.json', 'w') as res:
                json.dump(data, res)

            #self.titleBar.setTitle(f'TEXT EDITOR v0.2a - {name}')
            self.tabWidget.addTab(Page, name)
            Page.setReadOnly(self.readOnly)

    def slideinfo(self):
        # переключает видимость содержимого панели
        if not self.isBarHidden:
            self.toggle.setText('8')
        else:
            self.toggle.setText('7')
        #self.createButton.setVisible(self.isBarHidden)
        self.openButton.setVisible(self.isBarHidden)
        self.modeButton.setVisible(self.isBarHidden)
        self.themeButton.setVisible(self.isBarHidden)
        #self.saveButton.setVisible(self.isBarHidden)
        #self.indexTree.setVisible(self.isBarHidden)
        self.isBarHidden = not(self.isBarHidden)
