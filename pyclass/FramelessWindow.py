from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QEnterEvent, QPainter, QPen
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from pyclass.Direction import Direction
from pyclass.TitleBar import TitleBar


class FramelessWindow(QWidget):
    qss = open('themes/dark.qss', 'r').read()
    # Четыре периметра
    MARGINS = 7

    def __init__(self):
        super().__init__()

        self.setStyleSheet(self.qss)

        self._old_pos = None
        self._direction = None

        self._widget = None

        # Фон прозрачный
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Нет границы
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        # Отслеживание мыши
        self.setMouseTracking(True)

        # макет
        layout = QVBoxLayout(spacing=0)

        # Зарезервировать границы для изменения размера окна без полей
        layout.setContentsMargins(self.MARGINS, self.MARGINS, self.MARGINS, self.MARGINS)

        # Панель заголовка
        self.titleBar = TitleBar(self)
        layout.addWidget(self.titleBar)

        self.setLayout(layout)

        # слот сигнала
        self.titleBar.windowMinimumed.connect(self.showMinimized)
        self.titleBar.windowMaximumed.connect(self.showMaximized)
        self.titleBar.windowNormaled.connect(self.showNormal)
        self.titleBar.windowClosed.connect(self.close)
        self.titleBar.windowMoved.connect(self.move)
        self.windowTitleChanged.connect(self.titleBar.setTitle)
        self.windowIconChanged.connect(self.titleBar.setIcon)

    def setTitleBarHeight(self, height=38):
        """ Установка высоты строки заголовка """
        self.titleBar.setHeight(height)

    def setIconSize(self, size):
        """ Установка размера значка """
        self.titleBar.setIconSize(size)

    def setWidget(self, widget, dark=True):
        """ Настройте свои собственные элементы управления """

        self._widget = widget

        # Установите цвет фона по умолчанию, иначе он будет прозрачным из-за влияния родительского окна
        self._widget.setAutoFillBackground(True)
        if dark:
            palette = self._widget.palette()
            palette.setColor(palette.Window, QColor(37, 37, 37))
            self._widget.setPalette(palette)
        else:
            palette = self._widget.palette()
            palette.setColor(palette.Window, QColor('#afdafc'))
            self._widget.setPalette(palette)
        self._widget.installEventFilter(self)
        self.layout().addWidget(self._widget)

    def move(self, pos):
        if self.windowState() == Qt.WindowMaximized or self.windowState() == Qt.WindowFullScreen:
            # Максимизировать или полноэкранный режим не допускается
            return

        super().move(pos)

    def showMaximized(self):
        """ Чтобы максимизировать, удалите верхнюю, нижнюю, левую и правую границы.
            Если вы не удалите его, в пограничной области будут пробелы. """
        super().showMaximized()

        self.layout().setContentsMargins(0, 0, 0, 0)

    def showNormal(self):
        """ Восстановить, сохранить верхнюю и нижнюю левую и правую границы,
            иначе нет границы, которую нельзя отрегулировать """
        super().showNormal()

        self.layout().setContentsMargins(self.MARGINS, self.MARGINS, self.MARGINS, self.MARGINS)

    def eventFilter(self, obj, event):
        """ Фильтр событий, используемый для решения мыши в других элементах
            управления и восстановления стандартного стиля мыши """
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)

        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        """ Поскольку это полностью прозрачное фоновое окно, жесткая для поиска
            граница с прозрачностью 1 рисуется в событии перерисовывания, чтобы отрегулировать размер окна. """
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 255, 255, 1), 2 * self.MARGINS))
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        """ Событие клика мыши """
        super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            self._old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        """ Событие отказов мыши """
        super().mouseReleaseEvent(event)

        self._old_pos = None
        self._direction = None

    def mouseMoveEvent(self, event):
        """ Событие перемещения мыши """
        super().mouseMoveEvent(event)

        pos = event.pos()
        xPos, yPos = pos.x(), pos.y()
        wm, hm = self.width() - self.MARGINS, self.height() - self.MARGINS

        if self.isMaximized() or self.isFullScreen():
            self._direction = None
            self.setCursor(Qt.ArrowCursor)
            return

        if event.buttons() == Qt.LeftButton and self._old_pos:
            self._resizeWidget(pos)
            return

        if xPos <= self.MARGINS and yPos <= self.MARGINS:
            # Верхний левый угол
            self._direction = Direction.LEFT_TOP
            self.setCursor(Qt.SizeFDiagCursor)

        elif wm <= xPos <= self.width() and hm <= yPos <= self.height():
            # Нижний правый угол
            self._direction = Direction.RIGHT_BOTTOM
            self.setCursor(Qt.SizeFDiagCursor)

        elif wm <= xPos and yPos <= self.MARGINS:
            # верхний правый угол
            self._direction = Direction.RIGHT_TOP
            self.setCursor(Qt.SizeBDiagCursor)

        elif xPos <= self.MARGINS and hm <= yPos:
            # Нижний левый угол
            self._direction = Direction.LEFT_BOTTOM
            self.setCursor(Qt.SizeBDiagCursor)

        elif 0 <= xPos <= self.MARGINS and self.MARGINS <= yPos <= hm:
            # Влево
            self._direction = Direction.LEFT
            self.setCursor(Qt.SizeHorCursor)

        elif wm <= xPos <= self.width() and self.MARGINS <= yPos <= hm:
            # Право
            self._direction = Direction.RIGHT
            self.setCursor(Qt.SizeHorCursor)

        elif self.MARGINS <= xPos <= wm and 0 <= yPos <= self.MARGINS:
            # выше
            self._direction = Direction.TOP
            self.setCursor(Qt.SizeVerCursor)

        elif self.MARGINS <= xPos <= wm and hm <= yPos <= self.height():
            # ниже
            self._direction = Direction.BOTTOM
            self.setCursor(Qt.SizeVerCursor)

        else:
            # Курсор по умолчанию
            self.setCursor(Qt.ArrowCursor)

    def _resizeWidget(self, pos):
        """ Отрегулируйте размер окна """
        if self._direction is None:
            return

        mpos = pos - self._old_pos
        xPos, yPos = mpos.x(), mpos.y()
        geometry = self.geometry()
        x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()

        if self._direction == Direction.LEFT_TOP:  # Верхний левый угол
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos

            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos

        elif self._direction == Direction.RIGHT_BOTTOM:  # Нижний правый угол
            if w + xPos > self.minimumWidth():
                w += xPos
                self._old_pos = pos

            if h + yPos > self.minimumHeight():
                h += yPos
                self._old_pos = pos

        elif self._direction == Direction.RIGHT_TOP:  # верхний правый угол
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos

            if w + xPos > self.minimumWidth():
                w += xPos
                self._old_pos.setX(pos.x())

        elif self._direction == Direction.LEFT_BOTTOM:  # Нижний левый угол
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos

            if h + yPos > self.minimumHeight():
                h += yPos
                self._old_pos.setY(pos.y())

        elif self._direction == Direction.LEFT:  # Влево
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            else:
                return

        elif self._direction == Direction.RIGHT:  # Право
            if w + xPos > self.minimumWidth():
                w += xPos
                self._old_pos = pos
            else:
                return

        elif self._direction == Direction.TOP:  # выше
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            else:
                return

        elif self._direction == Direction.BOTTOM:  # ниже
            if h + yPos > self.minimumHeight():
                h += yPos
                self._old_pos = pos
            else:
                return

        self.setGeometry(x, y, w, h)