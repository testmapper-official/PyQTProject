import json

from PyQt5.QtGui import *
from PyQt5.Qsci import QsciScintilla, QsciLexerPython

class QSimplePythonEditor(QsciScintilla):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set font defaults
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(8)
        font.setBold(False)
        self.setFont(font)
        self.setReadOnly(True)


        # Set background editor

        # Set margin defaults
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("0000") + 12)
        self.setMarginLineNumbers(0, True)
        self.setMarginType(1, self.SymbolMargin)
        self.setMarginWidth(1, 12)

        # Set indentation defaults
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setBackspaceUnindents(True)
        self.setIndentationGuides(True)

        #self.setWrapMode(QTextEdit.NoWrap) - Работает только с TextEdit, Qscintilla слишком особенная
        self.setWrapMode(QsciScintilla.SC_WRAP_NONE)


        # self.setFolding(QsciScintilla.CircledFoldStyle)

        # Set caret defaults
        #self.setCaretForegroundColor(QColor(247, 247, 241)) : Dark Theme
        self.setCaretForegroundColor(QColor(200, 200, 200))
        self.setCaretWidth(2)

        # Set selection color defaults
        self.setSelectionBackgroundColor(QColor(61, 61, 152, 125))
        self.resetSelectionForegroundColor()

        # Set multiselection defaults
        self.SendScintilla(QsciScintilla.SCI_SETMULTIPLESELECTION, True)
        self.SendScintilla(QsciScintilla.SCI_SETMULTIPASTE, 1)
        self.SendScintilla(
            QsciScintilla.SCI_SETADDITIONALSELECTIONTYPING, True)

        lexer = QsciLexerPython(self)
        lexer.setDefaultPaper(QColor(29, 30, 24))
        lexer.setDefaultColor(QColor(200, 200, 200))
        self.setLexer(lexer)

    def setTheme(self, dark=True):
        if dark:
            # self.setCaretForegroundColor(QColor(247, 247, 241)) : Dark Theme
            self.setCaretForegroundColor(QColor(247, 247, 241))
            # Set selection color defaults
            self.setSelectionBackgroundColor(QColor(61, 61, 152, 125))
            self.resetSelectionForegroundColor()

            # Set multiselection defaults
            self.SendScintilla(QsciScintilla.SCI_SETMULTIPLESELECTION, True)
            self.SendScintilla(QsciScintilla.SCI_SETMULTIPASTE, 1)
            self.SendScintilla(
                QsciScintilla.SCI_SETADDITIONALSELECTIONTYPING, True)

            lexer = QsciLexerPython(self)
            lexer.setDefaultPaper(QColor(29, 30, 24))
            lexer.setDefaultColor(QColor(200, 200, 200))
            self.setLexer(lexer)
        else:
            self.setCaretForegroundColor(QColor(0, 0, 0))

            # Set selection color defaults
            self.setSelectionBackgroundColor(QColor(61, 61, 152, 125))
            self.resetSelectionForegroundColor()

            # Set multiselection defaults
            self.SendScintilla(QsciScintilla.SCI_SETMULTIPLESELECTION, True)
            self.SendScintilla(QsciScintilla.SCI_SETMULTIPASTE, 1)
            self.SendScintilla(
                QsciScintilla.SCI_SETADDITIONALSELECTIONTYPING, True)

            lexer = QsciLexerPython(self)
            lexer.setDefaultPaper(QColor(255, 255, 255))
            lexer.setDefaultColor(QColor(0, 0, 0))
            self.setLexer(lexer)
