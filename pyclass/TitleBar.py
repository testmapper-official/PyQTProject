from PyQt5.QtCore import pyqtSignal, QPoint, Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QSpacerItem, QSizePolicy, QHBoxLayout


class TitleBar(QWidget):
    # Сигнал минимизации окна
    windowMinimumed = pyqtSignal()

    # увеличить максимальный сигнал окна
    windowMaximumed = pyqtSignal()

    # сигнал восстановления окна
    windowNormaled = pyqtSignal()

    # сигнал закрытия окна
    windowClosed = pyqtSignal()

    # Окно мобильных
    windowMoved = pyqtSignal(QPoint)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Поддержка настройки фона qss
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._old_pos = None

        # Размер значка по умолчанию
        self.iconSize = 20

        # Установите цвет фона по умолчанию, иначе он будет прозрачным из-за влияния родительского окна
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        self.setPalette(palette)

        # значок окна
        self.iconLabel = QLabel()
        # self.iconLabel.setScaledContents(True)

        # название окна
        self.titleLabel = QLabel()
        self.titleLabel.setMargin(2)
        self.titleLabel.setMinimumSize(150, 20)
        self.titleLabel.setStyleSheet("""
                text-align: left center;
                color: gray;
                font: 10pt "Britannic Bold";""")

        # Использовать шрифты Webdings для отображения значков
        font = self.font() or QFont()
        font.setFamily('Webdings')

        self.buttonMinimum = QPushButton('0', clicked=self.windowMinimumed.emit, font=font, objectName='buttonMinimum')
        self.buttonMaximum = QPushButton('1', clicked=self.showMaximized, font=font, objectName='buttonMaximum')
        self.buttonClose = QPushButton('r', clicked=self.windowClosed.emit, font=font, objectName='buttonClose')
        # макет
        layout = QHBoxLayout(spacing=0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.iconLabel)
        layout.addWidget(self.titleLabel)

        # Средний телескопический бар
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.layout_custom_widget = QHBoxLayout()
        self.layout_custom_widget.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(self.layout_custom_widget)
        layout.addWidget(self.buttonMinimum)
        layout.addWidget(self.buttonMaximum)
        layout.addWidget(self.buttonClose)

        self.setLayout(layout)

        # начальная высота
        self.setHeight()

    def addWidget(self, widget, width=20, height=20):
        self.layout_custom_widget.addWidget(widget)

        widget.setMinimumSize(width, height)
        widget.setMaximumSize(width, height)

    def showMaximized(self):
        if self.buttonMaximum.text() == '1':
            # Максимизировать
            self.buttonMaximum.setText('2')
            self.windowMaximumed.emit()
        else:  # Восстановить
            self.buttonMaximum.setText('1')
            self.windowNormaled.emit()

    def setHeight(self, height=20):
        """ Установка высоты строки заголовка """
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        # Задайте размер правой кнопки  ?
        self.buttonMinimum.setMinimumSize(height * 2, height)
        self.buttonMinimum.setMaximumSize(height * 2, height)
        self.buttonMaximum.setMinimumSize(height * 2, height)
        self.buttonMaximum.setMaximumSize(height * 2, height)
        self.buttonClose.setMinimumSize(height * 2, height)
        self.buttonClose.setMaximumSize(height * 2, height)

    def setTitle(self, title):
        """ Установить заголовок """
        self.titleLabel.setText(title)

    def setIcon(self, icon):
        """ настройки значокa """
        self.iconLabel.setPixmap(icon.pixmap(self.iconSize, self.iconSize))

    def setIconSize(self, size):
        """ Установить размер значка """
        self.iconSize = size

    def enterEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super().enterEvent(event)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.showMaximized()

    def mousePressEvent(self, event):
        """ Событие клика мыши """
        if event.button() == Qt.LeftButton:
            self._old_pos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        """ Событие отказов мыши """
        self._old_pos = None
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._old_pos:
            self.windowMoved.emit(self.mapToGlobal(event.pos() - self._old_pos))
        event.accept()
