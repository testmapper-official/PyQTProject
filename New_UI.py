import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from pyclass.App import App
from pyclass.FramelessWindow import FramelessWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FramelessWindow()
    window.setWindowTitle('Text Reader v0.2a') # Название окна
    window.setWindowIcon(QIcon('icon.ico'))
    window.show()

    screen = app.primaryScreen()
    size = screen.size()

    # Добавить свое окно
    main = App(window)
    window.setMinimumSize(600, 400)
    width = size.width() // 3 * 2
    height = size.height() // 3 * 2
    window.setGeometry(size.width() // 2 - width // 2, size.height() // 2 - height // 2, width, height)
    window.setWidget(main)
    main.show()

    sys.exit(app.exec_())
