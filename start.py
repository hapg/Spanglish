import sys
import re
import requests
from PySide2.QtWidgets import QDialog, QApplication, QTextEdit, QLabel
from PySide2 import QtUiTools, QtGui, QtCore
#from pyqtconfig import QSettingsManager
from googletrans import Translator

class AppWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = QtUiTools.QUiLoader().load("ui/mainwindow.ui")
        self.settings = QtCore.QSettings("IanG", "Spanglish")
        self.translator = Translator()

        self.spanish_book, self.spanish_chapters = self.load_book("books/spanish.txt")
        self.english_book, self.english_chapters = self.load_book("books/english.txt")
        #self.settings = QSettingsManager()
        self.spanish_index = self.settings.value('spanish_index') or 0
        self.english_index = self.settings.value('english_index') or 0
        self.spanish_line = ""
        self.english_line = ""
        self.chapter = self.settings.value('chapter') or 0

        #self.spanish_le = TranslateTextEdit(widget=self, parent=self.ui.main_frame)
        self.spanish_le = QTextEdit(self.ui.main_frame)
        self.spanish_le.setReadOnly(True)
        self.spanish_le.selectionChanged.connect(self.translate)
        self.ui.main_frame_layout.insertWidget(0, self.spanish_le)

        self.ui.spanish_line_back_btn.clicked.connect(self.on_spanish_line_back)
        self.ui.spanish_line_forward_btn.clicked.connect(self.on_spanish_line_forward)
        self.ui.english_line_back_btn.clicked.connect(self.on_english_line_back)
        self.ui.english_line_forward_btn.clicked.connect(self.on_english_line_forward)

        self.ui.chapter_back_btn.clicked.connect(self.on_chapter_back)
        self.ui.chapter_forward_btn.clicked.connect(self.on_chapter_forward)
        self.ui.sentence_back_btn.clicked.connect(self.on_sentence_back)
        self.ui.sentence_forward_btn.clicked.connect(self.on_sentence_forward)

        font = self.spanish_le.font()
        font.setPointSize(32)  # change it's size
        self.spanish_le.setFont(font)
        self.ui.english_le.setFont(font)
        self.ui.translate_le.setFont(font)

        self.update()

        self.ui.show()

    def load_book(self, path):
        book = []
        chapters = []
        with open(path, "r", encoding="utf8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            result = re.split('\.[^0-9]', line)
            book.extend(result)
            if '— CHAPTER ' in line or 'CAPÍTULO ' in line:
                chapters.append(len(book))

        return book, chapters

    def translate(self):
        cursor = self.spanish_le.textCursor()
        text = cursor.selectedText()
        if text:
            try:
                translated = self.translator.translate(text)  # , src="es", dest="en")
                print("{} -- {}".format(text, translated.text))
                text = translated.text
                if translated.pronunciation:
                    text += '  "{}"'.format(translated.pronunciation)
                self.ui.translate_le.setText(text)
            except:
                pass


    def update(self):
        self.settings.setValue("spanish_index", self.spanish_index)
        self.settings.setValue("english_index", self.english_index)
        self.settings.setValue("chapter", self.chapter)
        self.spanish_line = self.spanish_book[self.spanish_index]
        self.english_line = self.english_book[self.english_index]
        self.spanish_le.setText(self.spanish_line)
        self.ui.english_le.setText(self.english_line)
        self.ui.translate_le.setText('')
        print("chapter: {}".format(self.chapter))
        print("spanish: {}".format(self.spanish_index))
        print("english: {}".format(self.english_index))

    def on_chapter_forward(self):
        if self.chapter > len(self.spanish_chapters):
            return
        self.spanish_index = self.spanish_chapters[self.chapter + 1]
        self.english_index = self.english_chapters[self.chapter + 1]
        self.chapter += 1
        self.update()

    def on_chapter_back(self):
        if self.chapter == 0:
            return
        self.spanish_index = self.spanish_chapters[self.chapter - 1]
        self.english_index = self.english_chapters[self.chapter - 1]
        self.chapter -= 1
        self.update()

    def on_sentence_forward(self):
        self.spanish_index += 1
        self.english_index += 1
        self.update()

    def on_sentence_back(self):
        self.spanish_index -= 1
        self.english_index -= 1
        self.update()

    def on_spanish_line_back(self):
        self.spanish_index -= 1
        self.update()

    def on_spanish_line_forward(self):
        self.spanish_index += 1
        self.update()

    def on_english_line_back(self):
        self.english_index -= 1
        self.update()

    def on_english_line_forward(self):
        self.english_index += 1
        self.update()


class TranslateTextEdit(QTextEdit):
    def __init__(self, widget, *args, **kwargs):
        self.widget = widget
        self.clicked = False
        self.mouse_pos = None
        self.ann = None
        self.translator = Translator()
        super(TranslateTextEdit, self).__init__()

    def mousePressEvent(self, event):
        try:
            if event.button() == QtCore.Qt.LeftButton:
                self.clicked = True
                self.mouse_pos = event.pos()
                cursor = self.cursorForPosition(self.mouse_pos)
                cursor.select(QtGui.QTextCursor.WordUnderCursor)
                text = cursor.selectedText()

                if text:
                    translated = self.translator.translate(text) #, src="es", dest="en")
                    print("{} -- {}".format(text, translated.text))
                    text = translated.text
                    if translated.pronunciation:
                        text += '  "{}"'.format(translated.pronunciation)
                    self.widget.ui.translate_le.setText(text)

        except Exception as e:
            pass


app = QApplication(sys.argv)
w = AppWindow()
sys.exit(app.exec_())