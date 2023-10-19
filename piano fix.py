from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QSound, QSoundEffect
from threading import Thread
import pygame
import sys
import os
import functools

class ChordComposer(QObject):
    chordComposed = pyqtSignal(str, object)
    def composeChord(self, root, chordType):
        intervals = {
            "major": [4, 7],
            "minor": [3, 7],
            "diminished": [3, 6]
        }
        notes = ["C4", "C40", "D4", "D40", "E4", "F4", "F40", "G4", "G40", "A4", "A40", "B4", 
                 "C5", "C50", "D5", "D50", "E5", "F5", "F50", "G5", "G50", "A5", "A50", "B5"]
        chord = [root]
        for interval in intervals[chordType]:
            index = notes.index(root)
            index = (index + interval) % 24
            chord.append(notes[index])
        chordName = " ".join(chord)
        self.chord=chord
        self.chordComposed.emit(chordName, self.chord)
        return chordName, chord

class ChordWindow(QWidget):
    chordComposed = pyqtSignal(str)
    def __init__(self, MainWindow):
        super().__init__()
        self.main_window=MainWindow
        self.chord=[]
        self.composer = ChordComposer()
        self.label = QLabel("No chord composed yet.")
        self.rootNoteCombo = QComboBox()
        self.rootNoteCombo.addItems(["C4", "C40", "D4", "D40", "E4", "F4", "F40", "G4", "G40", "A4", "A40", "B4"])
        self.chordTypeCombo = QComboBox()
        self.chordTypeCombo.addItems(["major", "minor","diminished"])
        self.composeButton = QPushButton("Compose chord")
        self.composeButton.clicked.connect(self.composeChord)
        self.resetButton = QPushButton("Reset")
        self.resetButton.clicked.connect(self.reset)
        self.composer.chordComposed.connect(self.displayChord)
        self.sendToPianoButton = QPushButton("Send to Piano")
        self.sendToPianoButton.clicked.connect(self.highlightPianoButtons)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Root note:"))
        layout.addWidget(self.rootNoteCombo)
        layout.addWidget(QLabel("Chord type:"))
        layout.addWidget(self.chordTypeCombo)
        layout.addWidget(self.label)
        layout.addWidget(self.composeButton)
        layout.addWidget(self.resetButton)
        layout.addWidget(self.sendToPianoButton)
        self.setLayout(layout)
    
    def composeChord(self):
        root = self.rootNoteCombo.currentText()
        chordType = self.chordTypeCombo.currentText()
        self.composer.composeChord(root, chordType)

        self.sendToPianoButton.setEnabled(True)
    
    def displayChord(self, chordName, chord):
        self.label.setText("Chord composed: {}".format(chordName))
        self.chordComposed.emit(chordName)
        self.chord=chord

    def highlightPianoButtons(self):
        self.noteIndex = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.playNextNote)
        self.timer.start(50)

    def playNextNote(self):
        if self.noteIndex < len(self.chord):
            button = self.main_window.buttons.get(self.chord[self.noteIndex])
            if button:
                button.setStyleSheet("background-color: rgb(255,165,0)")
                button.noteSound.play()
                self.noteIndex += 1
                if self.noteIndex == len(self.chord):
                    QTimer.singleShot(2000, self.reset)
            else:
                self.timer.stop()

    def reset(self):
        for button in self.main_window.buttons.values():
            button.setStyleSheet(button.original_style_sheet)
        self.timer.stop()
        self.label.setText("No chord composed yet.")

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(659, 400)
        
        self.mw  = MainWindow
        
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: white;")

        self.volume=50

        self.pianoButtons()

        self.sustainCheck=QtWidgets.QCheckBox(self.centralwidget)
        self.sustainCheck.move(20,230)
        self.sustainCheck.setText("Sustain")

        self.volumeSlider=QtWidgets.QSlider(self.centralwidget)
        self.volumeSlider.setRange(0,100)
        self.volumeSlider.setValue(50)
        self.volumeSlider.move(20,320)
        self.volumeSlider.setOrientation(Qt.Horizontal)
        self.volumeSlider.setTickPosition(QSlider.TicksBelow)
        self.volumeSlider.setTickInterval(25)
        self.volumeSlider.setStyleSheet("QSlider::tick { background: red; }")
        self.volumeName=QLabel("Volume",self.centralwidget)
        self.volumeName.move(20,300)

        self.buttonChordFind=QPushButton(self.centralwidget)
        self.buttonChordFind.move(150,300)
        self.buttonChordFind.setText("Open Chord Finder")
        self.buttonChordFind.setStyleSheet("background-color: white")
        
        self.notelabel=QtWidgets.QLabel("                      ", self.centralwidget)
        self.notelabel.setFont(QFont('Calibri',10))
        self.notelabel.setStyleSheet("border:1px solid black; background-color: white")
        self.notelabel.move(300, 230)

        self.announce=QtWidgets.QLabel("0 means #(sharp); example C40: C#4", self.centralwidget)
        self.announce.move(410, 232) 

        self.chordNotes=[]

        self.sustainCheck.raise_()

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        self.th = {}

        self.volumeSlider.valueChanged.connect(self.set_Volume)
        self.buttonChordFind.clicked.connect(self.openChordFind)

        print(self.buttons.keys())
    
    def set_Volume(self,value):
        self.volume=value
        
    def notes_sound(self, sound_file, volume):
        pygame.mixer.music.set_volume(volume / 100)
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

    def set_chord_notes(self, chord_notes):
        self.chordNotes = chord_notes

    def openChordFind(self):
        self.newChordWindow=ChordWindow(self)
        self.newChordWindow.chordComposed.connect(self.updateNoteLabel)
        self.newChordWindow.setWindowTitle("Chord Finder")
        self.newChordWindow.resize(300,200)
        self.newChordWindow.move(1300,400)
        self.newChordWindow.show()

    def pianoButtons(self):
        self.buttons={}
        buttonLabelWhite= ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"]
        keyboardWhite   = ["A" , "S" , "D" , "F" , "G" , "H" , "J" , "K" , "L" , "Z" , "X" , "C" , "V" , "B" , "N"]
        buttonLabelBlack= ["C40", "D40", " ", "F40", "G40", "A40", " ", "C50", "D50", " ", "F50", "G50", "A50", " "]
        keyboardBlack   = ["W"  , "E"  , " ", "T"  , "Y"  , "U"  , " ", "O" , "P"  , " ", " "  , " "  , " "  , " "]

        for i, label in enumerate(buttonLabelWhite):
            buttonWhite=QPushButton(self.centralwidget)
            buttonWhite.setGeometry(QtCore.QRect((40*i)+20, 30, 41, 181))
            buttonWhite.setStyleSheet("background-color: rgb(242, 242, 242);\n"
            "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
            "}\n")
            buttonWhite.setObjectName(label)
            buttonWhite.clicked.connect(functools.partial(self.button_clicked, buttonWhite))
            shortcutWhite=QShortcut(self.centralwidget)
            shortcutWhite.setKey(QKeySequence(keyboardWhite[i]))
            shortcutWhite.activated.connect(buttonWhite.click)
            self.buttons[label]=buttonWhite
            self.buttons[label].original_style_sheet = buttonWhite.styleSheet()
            self.buttons[label].noteSound = QSound("Sounds/normal/{}.wav".format(label))
            
        for i, label in enumerate(buttonLabelBlack):
            if i !=2 and i != 6 and i !=9 and i != 13:
                buttonBlack=QPushButton(self.centralwidget)
                buttonBlack.setGeometry(QtCore.QRect((40*i)+40, 30, 31, 111))
                buttonBlack.setStyleSheet("background-color: rgb(0, 0, 255);\n"
                "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), stop:1 rgba(255, 255, 255, 255));\n"
                "}\n")
                buttonBlack.setObjectName(label)
                buttonBlack.clicked.connect(functools.partial(self.button_clicked,buttonBlack))
                shortcutBlack=QShortcut(self.centralwidget)
                shortcutBlack.setKey(QKeySequence(keyboardBlack[i]))
                shortcutBlack.activated.connect(buttonBlack.click)
                self.buttons[label]=buttonBlack
                self.buttons[label].original_style_sheet = buttonBlack.styleSheet()
                self.buttons[label].noteSound = QSound("Sounds/normal/{}.wav".format(label))
        
    def setPressedStyleSheetNormal(self,button):
        button.setStyleSheet("background-color: rgb(255, 0, 0);")

    def setPressedStyleSheetSustain(self,button):
        button.setStyleSheet("background-color: rgb(255, 0, 255);")

    def button_clicked(self, button):
        sender = self.mw.sender()
        object_code = sender.objectName()
        self.timer = QTimer()
        if self.sustainCheck.isChecked()==True:
            self.run_threads_sustain(object_code)
            self.setPressedStyleSheetSustain(button)
            self.timer.setInterval(500)
        else:
            self.run_threads_v1(object_code)
            self.setPressedStyleSheetNormal(button)
            self.timer.setInterval(100)

        self.timer.setSingleShot(True)
        self.timer.timeout.connect(functools.partial(self.reset_button,button))
        self.timer.start()

        button.setChecked(True)
        button.setChecked(False)

    def play_chord(self, chord_notes):
        self.chordNotes = chord_notes
        for note in chord_notes:
            button = self.get_button_from_note(note)
            if button:
                self.button_clicked(button)

    def get_button_from_note(self, note):
        for button in self.pianoButtons:
            if button.text() == note:
                return button
        return None

    def reset_button(self, button):
        if len(button.objectName())==2:
            button.setStyleSheet("background-color: rgb(242, 242, 242);\n"
            "background-color: qlineargradient(spread:pad, x1:1, y1:0.711, x2:0.903455, y2:0.711, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
             "}\n")
        else:
            button.setStyleSheet("background-color: rgb(0, 0, 255);\n"
            "background-color: qlineargradient(spread:pad, x1:0.028, y1:0.619, x2:1, y2:0.494, stop:0.852273 rgba(0, 0, 0, 250), stop:1 rgba(255, 255, 255, 255));\n"
            "}\n")

    def highlightPianoButtons(self, notes):
        for note in notes:
            button = self.buttons.get(note)
            if button:
                button.setStyleSheet("background-color: yellow")

    def run_threads_v1(self, object_code):
        self.notelabel.setText(object_code)

        self.th[object_code] = Thread(target = self.notes_sound, args = ('Sounds/normal/'+'{}.wav'.format(object_code),self.volume)) 
        self.th[object_code].start()
        self.th[object_code].join()
        
    def run_threads_sustain(self, object_code):
        self.notelabel.setText(object_code)

        self.th[object_code] = Thread(target = self.notes_sound, args = ('Sounds/suspend/'+'{}.wav'.format(object_code),self.volume)) 
        self.th[object_code].start()
        self.th[object_code].join()

    def showNotes(self,notesPath):
        self.notes=QLabel()
        self.notes.setText(notesPath)

    def updateNoteLabel(self, chordName):
        self.notelabel.setText(chordName)
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Piano Chord Learning App"))

if __name__ == "__main__":
    import sys
    pygame.init()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())