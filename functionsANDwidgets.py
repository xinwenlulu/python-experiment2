import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from experiment import *
from math import sqrt
from random import *
import numpy as np
from os import listdir

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
app = QApplication(sys.argv)

window = QMainWindow()
ui = Ui_experimentWindow()

window.conditionList = ['winVL','winVH','loseVL','loseVH','noWheelVL','noWheelVH']
window.wheelCondition = ['win','lose','noWheel']
window.varianceCondition = ['VL','VH']

def produceRewardDistribution(mu,sigma):
    d = []
    for i in range(5):
        s = np.random.normal(mu, sigma)
        s = int(s)
        d.append(s)
    return d

def findMinCondition(pastConditions):
    winVLCount = 0
    winVHCount = 0
    loseVLCount = 0
    loseVHCount = 0
    noWheelVLCount = 0
    noWheelVHCount = 0
    for item in pastConditions:
        if 'win' in item:
            if 'VL' in item:
                winVLCount += 1
            else:  # VH
                winVHCount += 1
        elif 'lose' in item:
            if 'VL' in item:
                loseVLCount += 1
            else:
                loseVHCount += 1
        else:  # noWheel
            if 'VL' in item:
                noWheelVLCount += 1
            else:
                noWheelVHCount += 1
    count = [winVLCount, winVHCount, loseVLCount, loseVHCount, noWheelVLCount, noWheelVHCount]
    minCount = min(count)
    for i in range(len(count)):
        if count[i] == minCount:
            condition = window.conditionList[i]
    return condition


def decideCondition():
    files = listdir()
    if 'Result.csv' not in files:
        condition = choice(window.conditionList)
    else:
        pastConditions = []
        result = open('Result.csv','r')
        content = result.read()
        content = content.split('\n')

        for line in content:
            if line != '':
                line = line.split(',')
                pastCondition = line[4]
                pastConditions.append(pastCondition)
        condition = findMinCondition(pastConditions)
    return condition

def stimulusPosition():
    positions = [0,1]
    newTrialPosition = choice(positions)
    return newTrialPosition


class FeedbackWindow(QWidget):

    def openFeedback(self, contentString, warning = True):
        myWindow = QMessageBox()
        if warning == True:
            myWindow.setIcon(QMessageBox.Warning)
            myWindow.setWindowTitle('ERROR')
            myWindow.setText('ERROR')
        myWindow.setInformativeText(contentString)
        myWindow.setStandardButtons(QMessageBox.Ok)

        # position the error window
        myWindow.move(self.rect().center())

        myWindow.exec_()
        myWindow.show()


class MyLabel(QLabel):

    clicked = pyqtSignal()

    def mousePressEvent(self,mouseEvent):
        self.clicked.emit()

    def setlabel(self,content,colour):
        self.setText(content)
        self.adjustSize()
        self.setAutoFillBackground(True)
        myPalette = self.palette()
        myPalette.setColor(QPalette.Window,QColor(colour))
        self.setPalette(myPalette)

    def changeColour(self,newcolour): # used when stimulus switch sides
        myPalette = self.palette()
        myPalette.setColor(QPalette.Window, QColor(newcolour))
        self.setPalette(myPalette)

    def setfeedback(self,content,geometry):
        self.setText(content)
        self.setFont(QFont('Arial', 40))
        self.setAutoFillBackground(True)
        myPalette = self.palette()
        myPalette.setColor(QPalette.Window, QColor('white'))
        self.setPalette(myPalette)
        self.setGeometry(geometry)
        self.setAlignment(Qt.AlignCenter)
        self.show()
        window.timer = QTimer()
        window.timer.timeout.connect(self.hide)
        window.timer.setSingleShot(True)
        window.timer.start(800)

    def showTotalScore(self,totalScore):
        self.setText('Total Score: ' + totalScore)
        self.setFont(QFont('Arial', 14))
        self.setAutoFillBackground(True)
        myPalette = self.palette()
        myPalette.setColor(QPalette.WindowText, QColor('green'))
        self.setPalette(myPalette)
        self.setGeometry(300,330,160,20)
        self.setAlignment(Qt.AlignCenter)
        self.show()

    def trialEnd(self,block):
        self.setText('You have reached the end of ' + block + ' trials. \nPress Next to proceed.')
        self.setFont(QFont('Arial', 18))
        self.setAutoFillBackground(True)
        myPalette = self.palette()
        myPalette.setColor(QPalette.Window, QColor('white'))
        self.setPalette(myPalette)
        self.setGeometry(230, 430, 321, 80)
        self.adjustSize()
        self.setAlignment(Qt.AlignCenter)
        self.show()

    #def setStimuli(self,picture,position):
        #pix = QPixmap(picture)
        #self.setPixmap(pix)
        #if position == 'left':
            #self.setGeometry(40,300,170,200)
        #else:
            #self.setGeometry(560,300,170,200)
        #self.picC.setScaledContents(True)
        #self.show()


class RotatablePic(QLabel):

    def displayWheel(self,picture):
        self.setGeometry(QRect(210, 130, 341, 321))
        self.setPixmap(QPixmap(picture))
        self.setScaledContents(True)
        self.show()

    def rotate(self):

        self.rotateFor = 6  # rotate 5 times
        self.currentRotate = 0

        window.timer = QTimer()
        window.timer.timeout.connect(self.onRotation)
        window.timer.start(200)

    def onRotation(self):

        originalPIC = self.pixmap()
        dimension = originalPIC.size().width()
        transformation = QTransform().rotate(90)
        rotatedPIC = originalPIC.transformed(transformation, Qt.SmoothTransformation)
        rotatedPIC = rotatedPIC.scaled(dimension*sqrt(2), dimension*sqrt(2))
        self.setPixmap(rotatedPIC)

        if self.currentRotate == self.rotateFor:
            window.timer.stop()

        self.currentRotate += 1


def createConfidenceButtons(widet, position = 'right', fontSize = 13, width = 22, height = 32, maxConfidence = 6):
    x = 2
    for i in range(maxConfidence):
        myLabel = MyLabel(widet)
        if position == 'right':  # (1,2,3,4,5,6)
            content = str(i + 1)
            myLabel.setlabel(content,'blue')
        else:  # position == 'left (6,5,4,3,2,1)
            content = str(6 - i)
            myLabel.setlabel(content,'yellow')

        myLabel.setFont(QFont('Arial', fontSize))
        myLabel.setGeometry(x,10,width,height)
        x += width + 2
        myLabel.setAlignment(Qt.AlignCenter)

        myLabel.setObjectName(position + content)
        myLabel.show()
