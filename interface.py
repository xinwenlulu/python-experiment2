import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from experiment import *
from functionsANDwidgets import *
from random import choice


QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
app = QApplication(sys.argv)

window = QMainWindow()

ui = Ui_experimentWindow()
ui.setupUi(window)

#######################################################################################################################
#parameters to change

window.goodP = [70,80,90] # hard coded reward distribution for the good option in practice trials
window.badP = [20,30,40] # hard coded reward distribution for the bad option in practice trials

goodMean = 60 # mean of the reward distribution for the good option
badMean = 40 # mean for the reward distribution for the bad option
# conditon 1: low variance
vL = 10 # standard deviation of the reward distribution in the low variance condition
# condition 2: high variance
vH = 20 # standard deviation of the reward distribution in the high variance condition


window.practiceTrials = 5
window.trials = 5 # trial numbers used in block 1 and block 2
window.practiceGood = '9bb0fc4250e1b9456057385006052cea.png' # the good option with higher expected rewards
window.practiceBad = 'original.png'# the bad option with lower expected rewards
window.block1Good = 'images.jpeg'
window.block1Bad = 'images.png'
window.block2Good = 'images-2.jpeg'
window.block2Bad = '192858-500x500-Cat-Clip-Art-3.jpg'

#######################################################################################################################
# Initialisating variables

window.results = []
window.results2 = []
window.score = 0
window.totalScore = 0
window.numTrials = 0
window.condition = decideCondition()


window.goodVL = produceRewardDistribution(goodMean,vL)
window.goodVH = produceRewardDistribution(goodMean,vH)
window.badVL = produceRewardDistribution(badMean,vL)
window.badVH = produceRewardDistribution(badMean,vH)


def nextpage():
    currentIndex = ui.stackedPages.currentIndex()
    nextIndex =  currentIndex + 1
    ui.stackedPages.setCurrentIndex(nextIndex)
    onPageChange()


def previouspage():
    currentIndex = ui.stackedPages.currentIndex()
    previousIndex = currentIndex - 1
    ui.stackedPages.setCurrentIndex(previousIndex)

def writeResults():
    rawResult = open('Raw Result.csv','a') # a file to save raw choice result in practice and block 1 and 2
    result = open('Result.csv', 'a')  # a file to save results
    rawform = '{0} \n'
    form = '{0},{1},{2},{3},{4},{5},{6}\n'
    if ui.female.isChecked() == True:
        gender = 'female'
    else:
        gender = 'male'
    rawdata = rawform.format(window.results)
    data = form.format(ui.name.text(),ui.age.text(),gender,ui.education.currentText(),window.condition,window.HPSscore,window.results2)
    rawResult.write(rawdata)
    rawResult.close()
    result.write(data)
    result.close()


def onNextClicked():
    if ui.stackedPages.currentIndex() == 0: #Consent
        checkConsent()
    elif ui.stackedPages.currentIndex() == 1: #Demographics
        checkDemo()
    elif ui.stackedPages.currentIndex() == 2: # Questionnaire
        checkHPS()
    elif ui.stackedPages.currentIndex() == 7:
        checkChoice()
    elif ui.stackedPages.currentIndex() == 8:
        checkEstimate()
    else:
        if ui.next.isHidden() == True:
            error = FeedbackWindow()
            if ui.stackedPages.currentIndex() == 5:
                content = 'Please spin the Wheel!'
            else:
                content = 'Please finish all the trials on this page!'
            error.openFeedback(content)
        else:
            if ui.stackedPages.currentIndex() == 4:
                checkWheelCondition()
            else:
                nextpage()

def onPageChange():
    if ui.stackedPages.currentIndex() != 0:
        ui.previous.show()
    else:
        ui.previous.hide()

    if ui.stackedPages.currentIndex() == 3:
        ui.next.hide()
        initialiseTrials(ui.rightP,ui.leftP,window.practiceGood,ui.practice_left,window.practiceBad,ui.practice_right)
    elif ui.stackedPages.currentIndex() == 4:
        ui.progress.setValue(50)
        ui.next.hide()
        window.totalScore = 0 # reset total score
        updateScore(ui.block1,window.totalScore)
        initialiseTrials(ui.rightB1,ui.leftB1,window.block1Good,ui.left1,window.block1Bad,ui.right1)
    elif ui.stackedPages.currentIndex() == 5:
        ui.progress.setValue(60)
        ui.next.hide()
    elif ui.stackedPages.currentIndex() == 6:
        ui.progress.setValue(70)
        ui.next.hide()
        updateScore(ui.block2,window.totalScore)
        initialiseTrials(ui.rightB2, ui.leftB2, window.block2Good, ui.left2, window.block2Bad, ui.right2)
    elif ui.stackedPages.currentIndex() == 7: #Choice Page
        ui.progress.setValue(80)
        setChoicePic()
    elif ui.stackedPages.currentIndex() == 8: #Estimate Page
        ui.progress.setValue(90)
        setEstimate()
    elif ui.stackedPages.currentIndex() == 9:
        ui.progress.setValue(100)
        writeResults()
        ui.next.hide()
        ui.previous.hide()

def checkWheelCondition():
    if 'noWheel' not in window.condition:
        nextpage()
    else:
        ui.stackedPages.setCurrentIndex(6)
        onPageChange()

def initialiseTrials(rightbutton,leftbutton,goodPic,leftPicWid,badPic,rightPicWid):
    createConfidenceButtons(rightbutton)
    createConfidenceButtons(leftbutton, 'left')
    assignFunctions('left', leftbutton)
    assignFunctions('right', rightbutton)
    setStimulus(goodPic, leftPicWid, leftbutton, badPic, rightPicWid, rightbutton)

def setChoicePic():
    B1G = QPixmap(window.block1Good)
    ui.B1G.setPixmap(B1G)
    ui.B1G2.setPixmap(B1G)
    B1B = QPixmap(window.block1Bad)
    ui.B1B.setPixmap(B1B)
    ui.B1B2.setPixmap(B1B)
    B2G = QPixmap(window.block2Good)
    ui.B2G.setPixmap(B2G)
    ui.B2G2.setPixmap(B2G)
    B2B = QPixmap(window.block2Bad)
    ui.B2B.setPixmap(B2B)
    ui.B2B2.setPixmap(B2B)

def checkChoice():
    error = FeedbackWindow()
    questions = ['1','2','3','4']
    errorMessage = ''
    result =[]

    for i in range(len(ui.choiceWid.children())):
        number = questions[i]
        comparison = ui.choiceWid.children()[i]

        if all(option.isChecked() == False for option in comparison.children()) == True:
            errorMessage += 'Please state your confidence for comparison ' + number + ' \n'
        else:
            for option in comparison.children():
                if option.isChecked() == True:
                    choiceContent = option.objectName()
                    choiceContent = choiceContent[:3]
                    result.append(choiceContent)

    window.results2.append(result)

    if errorMessage == '':
        nextpage()
    else:
        errorMessage += 'Please complete this page before proceeding! '
        error.openFeedback(errorMessage)


def setEstimate():
    B1G = QPixmap(window.block1Good)
    ui.B1Gpic.setPixmap(B1G)
    B1B = QPixmap(window.block1Bad)
    ui.B1Bpic.setPixmap(B1B)
    B2G = QPixmap(window.block2Good)
    ui.B2Gpic.setPixmap(B2G)
    B2B = QPixmap(window.block2Bad)
    ui.B2Bpic.setPixmap(B2B)

def checkEstimate():
    error = FeedbackWindow()
    alist = [ui.B1Gestimate, ui.B1Bestimate, ui.B2Gestimate, ui.B2Bestimate]
    errorMessage = ''

    for i in range(len(alist)):
        answer = alist[i].text()
        if 'estimation' in answer:
            number = str(i + 1)
            errorMessage += 'Please enter your estimated reward for picture ' + number + '. \n'
        else:
            estimate = alist[i].text()
            window.results2.append(estimate)

    if errorMessage == '':
        nextpage()
        ui.next.hide()
    else:
        errorMessage += 'Please complete this page before proceeding! '
        error.openFeedback(errorMessage)

def checkConsent():
    error = FeedbackWindow()
    nameNOTentered = 'Please enter your name! \n'
    boxNOTchecked = 'Please give your consent by checking the boxes in front of all statements! \n'
    generalMessage = 'Please complete the consent form before taking part in this experiment! '

    if ui.name.text() != '' and all(checkbox.isChecked() == True for checkbox in ui.checkContainer.children()) == True:
        # name entered and all checkbox checked

        nextpage()
        ui.progress.setValue(10)  # update the progress bar

    else:  # if any required field on the consent page is empty

        if ui.name.text() == '':  # name is not entered
            if any(checkbox.isChecked() == False for checkbox in ui.checkContainer.children()) == True:
                # any checkbox is not checked
                errorMessage = nameNOTentered + boxNOTchecked + generalMessage
            else:  # name not entered and all checkbox checked
                errorMessage = nameNOTentered + generalMessage
        else:  # name entered and any checkbox not checked
            errorMessage = boxNOTchecked + generalMessage

        error.openFeedback(errorMessage)


def checkDemo():
    error = FeedbackWindow()
    ageUnder18 = 'You need to be over 18 to take part in this experiment! \n This programme will close automatically! '
    ageNOTentered = 'Please enter your age! \n'
    genderNOTselected = 'Please select your gender! \n'
    eduNOTselected = 'Please select your education level! \n'
    generalMessage = 'Demographic questions need to be completed before moving on to the next page! '
    age = int(ui.age.text())

    if age >= 18 and (ui.male.isChecked() == True or ui.female.isChecked() == True) and ui.education.currentIndex() != 0:
        # all demographics information entered and over 18

        ui.progress.setValue(20)  # update the progress bar again
        nextpage()

    else:  # if any demographics information not entered - display relevant error message based on the error

        if age == 0:

            if ui.male.isChecked() == False and ui.female.isChecked() == False and ui.education.currentIndex() == 0:
                errorMessage = ageNOTentered + genderNOTselected + eduNOTselected + generalMessage
            elif ui.education.currentIndex() == 0:
                errorMessage = ageNOTentered + eduNOTselected + generalMessage
            elif ui.male.isChecked() == False and ui.female.isChecked() == False:
                errorMessage = ageNOTentered + genderNOTselected + generalMessage
            else:
                errorMessage = ageNOTentered + generalMessage

        elif age < 18:

            errorMessage = ageUnder18
            window.timer = QTimer()
            window.timer.timeout.connect(window.close)
            window.timer.setSingleShot(True)
            window.timer.start(2000)

        elif ui.female.isChecked() == False and ui.male.isChecked() == False:

            if ui.education.currentIndex() == 0:
                errorMessage = genderNOTselected + eduNOTselected + generalMessage
            else:
                errorMessage = genderNOTselected + generalMessage

        else:  # ui.education.currentIndex == 0:
            errorMessage = eduNOTselected + generalMessage

        error.openFeedback(errorMessage)

def checkHPS():
    error = FeedbackWindow()
    questions = [ui.Q1,ui.Q2,ui.Q3,ui.Q4,ui.Q5,ui.Q6,ui.Q7,ui.Q8,ui.Q9,ui.Q10,ui.Q11,ui.Q12]
    # HPSpos = [1,3,5,6,8,9,10,11]
    HPSneg = [2,4,7,12] # reverse coding
    HPSresult = open('HPS Result.csv', 'a')  # a file to save raw data from HPS
    scoreContent = '' # a string of score in each question
    form = '{0}{1}\n' # {0} = scores from Q1-Q12; {1} = total score
    errorMessage = ''
    window.HPSscore = 0   # total score

    for question in questions:
        number = question.objectName()

        if all(option.isChecked() == False for option in question.children()) == True:
            errorMessage += 'Please answer Qestion ' + number + ' \n'
        else:
            for option in question.children():
                score = option.objectName()
                score = int(score[-1])
                if option.isChecked() == True:
                    number = int(number[-1])
                    if number in HPSneg: # reverse coding
                        score = 6-score
                    scoreContent += str(score) + ','
                    window.HPSscore += score

    if errorMessage == '':
        ui.progress.setValue(30)
        data = form.format(scoreContent, window.HPSscore)
        HPSresult.write(data)
        HPSresult.close()
        nextpage()
        ui.next.hide()
    else:
        errorMessage += 'Please complete the questionnaire before proceeding! '
        error.openFeedback(errorMessage)



def setStimulus(pictureA,widgetLeft,buttonLeft,pictureB,widgetRight,buttonRight):
    window.position = stimulusPosition()
    pixA = QPixmap(pictureA)
    pixB = QPixmap(pictureB)
    if window.position == 1: # change sides of the stimulus
        widgetLeft.setPixmap(pixB)
        widgetRight.setPixmap(pixA)
        for btn in buttonLeft.children():
            btn.changeColour('blue')
        for btn in buttonRight.children():
            btn.changeColour('yellow')
    else: #position = 0
        widgetLeft.setPixmap(pixA)
        widgetRight.setPixmap(pixB)
        for btn in buttonLeft.children():
            btn.changeColour('yellow')
        for btn in buttonRight.children():
            btn.changeColour('blue')

def newTrialStimulus():
    if ui.stackedPages.currentIndex() == 3:
        picA = window.practiceGood
        picB = window.practiceBad
        widLeft = ui.practice_left
        widRight = ui.practice_right
        btnLeft = ui.leftP
        btnRight = ui.rightP
    elif ui.stackedPages.currentIndex() == 4:
        picA = window.block1Good
        picB = window.block1Bad
        widLeft = ui.left1
        widRight = ui.right1
        btnLeft = ui.leftB1
        btnRight = ui.rightB1
    else: #index = 6
        picA = window.block2Good
        picB = window.block2Bad
        widLeft = ui.left2
        widRight = ui.right2
        btnLeft = ui.leftB2
        btnRight = ui.rightB2
    setStimulus(picA, widLeft, btnLeft, picB, widRight, btnRight)

def findGeometry():
    if ui.stackedPages.currentIndex() == 3:
        leftGEO = ui.practice_left.geometry()
        rightGEO = ui.practice_right.geometry()
    elif ui.stackedPages.currentIndex() == 4:
        leftGEO = ui.left1.geometry()
        rightGEO = ui.right1.geometry()
    else: # index = 6
        leftGEO = ui.left2.geometry()
        rightGEO = ui.right2.geometry()
    return (leftGEO,rightGEO)

def showPoints(points,geometry):
    feedback = MyLabel(ui.stackedPages)
    feedback.setfeedback(points, geometry)
    if ui.stackedPages.currentIndex() == 3:
        page = ui.practice
    elif ui.stackedPages.currentIndex() ==4:
        page = ui.block1
    else:
        page = ui.block2
    updateScore(page,window.totalScore)

def updateScore(widget,totalScore):
    scorelbl = MyLabel(widget)
    totalScore = str(totalScore)
    scorelbl.showTotalScore(totalScore)

def hideButtons(block):
    if block == 'practice':
        for btn in ui.leftP.children():
            btn.hide()
        for btn in ui.rightP.children():
            btn.hide()
    elif block == 'block 1':
        for btn in ui.leftB1.children():
            btn.hide()
        for btn in ui.rightB1.children():
            btn.hide()
    else: # block 2
        for btn in ui.leftB2.children():
            btn.hide()
        for btn in ui.rightB2.children():
            btn.hide()

def checkEndTrial(result):
    if ui.stackedPages.currentIndex() == 3:
        numTrials = window.practiceTrials
    elif ui.stackedPages.currentIndex() == 4:
        numTrials = window.practiceTrials + window.trials
    else: #index = 6
        numTrials = window.practiceTrials + 2*window.trials

    if ui.stackedPages.currentIndex() == 3:
        block = 'practice'
        page = ui.practice
    elif ui.stackedPages.currentIndex() == 4:
        block = 'block 1'
        page = ui.block1
    else: #index =6
        block = 'block 2'
        page = ui.block2

    endTriallbl = MyLabel(page)
    if len(result) == 5 * numTrials:
        for btn in ui.leftP.children():
            btn.hide()
        for btn in ui.rightP.children():
            btn.hide()
        endTriallbl.trialEnd(block)
        hideButtons(block)
        ui.next.show()
    else:
        window.newTrialtimer = QTimer()
        window.newTrialtimer.timeout.connect(newTrialStimulus)
        window.newTrialtimer.setSingleShot(True)
        window.newTrialtimer.start(800)

def isPractice():
    if ui.stackedPages.currentIndex() == 3:
        output = True
    else:
        output = False
    return output

# default when position = 0, good choice on the left
# when position = 1, good choice on the right
def writeChoice(option, confidence, practice = False):
    stimulusGEO = findGeometry()
    if option == 'left':
        geometry = stimulusGEO[0]
        if window.position == 0:
            chosen = 'good'
            if practice == True:
                x = 40
                points = choice(window.goodP)
            else: # not practice
                x = 80
                if 'VL' in window.condition:
                    points = choice(window.goodVL)
                else: #VH
                    points = choice(window.goodVH)
        else: #position == 1
            chosen = 'bad'
            if practice == True:
                points = choice(window.badP)
            else:
                if 'VL' in window.condition:
                    points = choice(window.badVL)
                else:
                    points = choice(window.badVH)
    else: # right
        geometry = stimulusGEO[1]
        if window.position == 0:
            chosen = 'bad'
            if practice == True:
                points = choice(window.badP)
                x = 560
            else: # not practice
                x = 480
                if 'VL' in window.condition:
                    points = choice(window.badVL)
                else:#VH
                    points = choice(window.badVH)
        else: #position == 1
            chosen = 'good'
            if practice == True:
                points = choice(window.goodP)
            else:
                if 'VL' in window.condition:
                    points = choice(window.goodVL)
                else:
                    points = choice(window.goodVH)
    window.results.append(window.position)
    window.results.append(chosen)
    window.results.append(confidence)
    window.score = points
    window.totalScore += points
    points = str(points)
    window.results.append(points)
    window.results.append(window.totalScore)
    showPoints(points,geometry)


def left1():
    option = 'left'
    confidence = '1'
    writeChoice(option,confidence,isPractice())
    checkEndTrial(window.results)

def left2():
    option = 'left'
    confidence = '2'
    writeChoice(option, confidence)
    checkEndTrial(window.results)


def left3():
    option = 'left'
    confidence = '3'
    writeChoice(option, confidence)
    checkEndTrial(window.results)


def left4():
    option = 'left'
    confidence = '4'
    writeChoice(option, confidence,isPractice())
    checkEndTrial(window.results)

def left5():
    option = 'left'
    confidence = '5'
    writeChoice(option, confidence,isPractice())
    checkEndTrial(window.results)

def left6():
    option = 'left'
    confidence = '6'
    writeChoice(option, confidence,isPractice())
    checkEndTrial(window.results)

def right1():
    option = 'right'
    confidence = '1'
    writeChoice(option, confidence,isPractice())
    checkEndTrial(window.results)

def right2():
    option = 'right'
    confidence = '2'
    writeChoice(option, confidence,isPractice())
    checkEndTrial(window.results)

def right3():
    option = 'right'
    confidence = '3'
    writeChoice(option, confidence,isPractice())
    checkEndTrial(window.results)

def right4():
    option = 'right'
    confidence = '4'
    writeChoice(option, confidence,isPractice())
    checkEndTrial(window.results)

def right5():
    option = 'right'
    confidence = '5'
    writeChoice(option, confidence,isPractice())
    checkEndTrial(window.results)

def right6():
    option = 'right'
    confidence = '6'
    writeChoice(option, confidence,isPractice())
    checkEndTrial(window.results)

def assignFunctions(position,widget):
    if position == 'left':
        for btn in widget.children():
            if btn.objectName()[-1] == '1':
                btn.clicked.connect(left1)
            elif btn.objectName()[-1] == '2':
                btn.clicked.connect(left2)
            elif btn.objectName()[-1] == '3':
                btn.clicked.connect(left3)
            elif btn.objectName()[-1] == '4':
                btn.clicked.connect(left4)
            elif btn.objectName()[-1] == '5':
                btn.clicked.connect(left5)
            else:  # btn.objectName()[-1] == '6':
                btn.clicked.connect(left6)
    else: #posiiton == 'right'
        for btn in widget.children():
            if btn.objectName()[-1] == '1':
                btn.clicked.connect(right1)
            elif btn.objectName()[-1] == '2':
                btn.clicked.connect(right2)
            elif btn.objectName()[-1] == '3':
                btn.clicked.connect(right3)
            elif btn.objectName()[-1] == '4':
                btn.clicked.connect(right4)
            elif btn.objectName()[-1] == '5':
                btn.clicked.connect(right5)
            else:  # btn.objectName()[-1] == '6':
                btn.clicked.connect(right6)


def showWheelResults():
    ui.next.show()
    feedback = FeedbackWindow()
    if 'win' in window.condition:
        pic = 'red.jpeg'
        window.totalScore += 500
        content = 'Congratulations! You just won 500 points!'
    else: # condition == 'lose'
        pic = 'green.jpeg'
        window.totalScore -= 500
        content = 'Oops! You just lost 500 points!'
    wheelPic = RotatablePic(ui.wheel)  # wheel page
    wheelPic.displayWheel(pic)
    feedback.openFeedback(content,False)


def wheelTimer():
    window.resultTimer = QTimer()
    window.resultTimer.timeout.connect(showWheelResults)
    window.resultTimer.setSingleShot(True)
    window.resultTimer.start(1600)


ui.date.setDate(QDate.currentDate())     # fetch the system time as default --- user don't need to enter the date
ui.stackedPages.setCurrentIndex(0)              # starts from the first page - consent page
ui.progress.setValue(0)                         # default the progress bar value
ui.previous.hide()
ui.previous.clicked.connect(previouspage)
ui.next.clicked.connect(onNextClicked)

wheelPic = RotatablePic(ui.wheel)  # wheel page
wheelPic.displayWheel("wheel_greendessert_small-300x300.png")
ui.spin.clicked.connect(wheelPic.rotate)
ui.spin.clicked.connect(wheelTimer)
ui.spin.clicked.connect(ui.spin.hide)



window.show()
sys.exit(app.exec_())