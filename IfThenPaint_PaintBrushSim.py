# importing libraries
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys
import math
import time

# window class
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("IfThenPaint Brush Simulator")

        # setting geometry to main window
        self.setGeometry(100, 100, 800, 600)

        # creating image object
        self.image = QImage(self.size(), QImage.Format_RGB32)

        # making image color to white
        self.image.fill(Qt.white)

        # enable mouse tracking so we always know cursor position
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        # variables
        # drawing flag
        self.drawing = False
        # default brush size
        self.brushSize = 20
        # default color
        self.brushColor = Qt.black
        # brush type: "Flat" or "Round"
        self.brushType = "Flat"
        # stamped line thickness (in pixels)
        self.stampThickness = 1
        # angle (in degrees) for the brush line; 90 = vertical
        self.brushAngle = 90.0
        # last time a stamp was drawn (for fixed stamp frequency)
        self.lastStampTime = 0.0
        # last normal (perpendicular) direction used for Round brush cursor/stamp
        self.lastNormal = None
        # key state for smooth simultaneous rotation and size changes
        self._keyLeft = False
        self._keyRight = False
        self._keyUp = False
        self._keyDown = False

        # timer to continuously apply key-based changes
        self._keyTimer = QTimer(self)
        self._keyTimer.timeout.connect(self._applyKeyChanges)
        self._keyTimer.start(16)

        # QPoint object to tract the point
        self.lastPoint = QPoint()
        # current cursor position for drawing guide line
        self.cursorPos = None
        # lists of top and bottom points for each stamp in the current stroke
        self.topPoints = []
        self.bottomPoints = []

        # creating menu bar
        mainMenu = self.menuBar()

        # creating file menu for save and clear action
        fileMenu = mainMenu.addMenu("File")

        # creating brush type menu
        brushTypeMenu = mainMenu.addMenu("Brush Type")

        # creating stamp thickness menu
        thicknessMenu = mainMenu.addMenu("Stamp Thickness")

        # adding brush color to main menu
        b_color = mainMenu.addMenu("Brush Color")

        # creating save action
        saveAction = QAction("Save", self)
        # adding short cut for save action
        saveAction.setShortcut("Ctrl + S")
        # adding save to the file menu
        fileMenu.addAction(saveAction)
        # adding action to the save
        saveAction.triggered.connect(self.save)

        # creating clear action
        clearAction = QAction("Clear", self)
        # adding short cut to the clear action
        clearAction.setShortcut("Ctrl + C")
        # adding clear to the file menu
        fileMenu.addAction(clearAction)
        # adding action to the clear
        clearAction.triggered.connect(self.clear)

        # creating brush type actions with check indicators
        brushTypeGroup = QActionGroup(self)
        brushTypeGroup.setExclusive(True)
        flatAction = QAction("Flat", self, checkable=True)
        roundAction = QAction("Round", self, checkable=True)
        brushTypeGroup.addAction(flatAction)
        brushTypeGroup.addAction(roundAction)
        brushTypeMenu.addAction(flatAction)
        brushTypeMenu.addAction(roundAction)
        flatAction.triggered.connect(self.setBrushFlat)
        roundAction.triggered.connect(self.setBrushRound)
        # default brush type is Flat
        flatAction.setChecked(True)

        # creating stamp thickness actions with check indicators
        thicknessGroup = QActionGroup(self)
        thicknessGroup.setExclusive(True)

        thickness1 = QAction("1 px", self, checkable=True)
        thickness10 = QAction("10 px", self, checkable=True)

        thicknessMenu.addAction(thickness1)
        thicknessMenu.addAction(thickness10)

        thicknessGroup.addAction(thickness1)
        thicknessGroup.addAction(thickness10)

        thickness1.triggered.connect(lambda: self.setStampThickness(1))
        thickness10.triggered.connect(lambda: self.setStampThickness(10))

        # default stamp thickness is 1 px
        thickness1.setChecked(True)

        # creating options for brush color with check indicators
        colorGroup = QActionGroup(self)
        colorGroup.setExclusive(True)

        # creating action for black color
        black = QAction("Black", self, checkable=True)
        b_color.addAction(black)
        colorGroup.addAction(black)
        black.triggered.connect(self.blackColor)

        # similarly repeating above steps for different color
        green = QAction("Green", self, checkable=True)
        b_color.addAction(green)
        colorGroup.addAction(green)
        green.triggered.connect(self.greenColor)

        yellow = QAction("Yellow", self, checkable=True)
        b_color.addAction(yellow)
        colorGroup.addAction(yellow)
        yellow.triggered.connect(self.yellowColor)

        blue = QAction("Blue", self, checkable=True)
        b_color.addAction(blue)
        colorGroup.addAction(blue)
        blue.triggered.connect(self.blueColor)

        red = QAction("Red", self, checkable=True)
        b_color.addAction(red)
        colorGroup.addAction(red)
        red.triggered.connect(self.redColor)

        # default brush color is black
        black.setChecked(True)


    # method for checking mouse cicks
    def mousePressEvent(self, event):

        # if left mouse button is pressed
        if event.button() == Qt.LeftButton:
            # make drawing flag true
            self.drawing = True
            # make last point to the point of cursor
            self.lastPoint = event.pos()
            # allow an immediate stamp on first movement (50 Hz => 0.02 s)
            self.lastStampTime = time.time() - 0.02
            # start new top/bottom paths for this stroke
            self.topPoints = []
            self.bottomPoints = []
        # update current cursor position
        self.cursorPos = event.pos()
        self.update()

    # method for tracking mouse activity
    def mouseMoveEvent(self, event):
        # always track cursor position
        self.cursorPos = event.pos()

        # checking if left button is pressed and drawing flag is true
        if (event.buttons() & Qt.LeftButton) and self.drawing:

            # enforce a fixed stamp frequency of 50 Hz (every 0.02 seconds)
            now = time.time()
            if now - self.lastStampTime < 0.02:
                # still update preview line, but skip stamping
                self.update()
                return

            # creating painter object
            painter = QPainter(self.image)

            # set the pen of the painter for the main stamped line (square line caps, 1px thick)
            painter.setPen(QPen(self.brushColor, self.stampThickness,
                            Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))

            # draw a line centered at the cursor position,
            # with total length equal to the brush size
            half_len = self.brushSize / 2.0
            x = event.pos().x()
            y = event.pos().y()

            if self.brushType == "Round" and (event.pos() != self.lastPoint):
                # for Round brush, stamp is always perpendicular to the path direction
                vx = x - self.lastPoint.x()
                vy = y - self.lastPoint.y()
                length = math.hypot(vx, vy)
                if length == 0:
                    angle_rad = math.radians(self.brushAngle)
                    nx = math.cos(angle_rad)
                    ny = math.sin(angle_rad)
                else:
                    # normalized direction vector
                    vx /= length
                    vy /= length
                    # perpendicular normal vector
                    nx = -vy
                    ny = vx
                # remember last perpendicular direction for Round brush
                self.lastNormal = (nx, ny)
                dx = half_len * nx
                dy = half_len * ny
            else:
                # for Flat brush (or degenerate case), use the current brush angle
                angle_rad = math.radians(self.brushAngle)
                dx = half_len * math.cos(angle_rad)
                dy = half_len * math.sin(angle_rad)

            top_point = QPointF(x - dx, y - dy)
            bottom_point = QPointF(x + dx, y + dy)
            painter.drawLine(top_point, bottom_point)

            # append current top and bottom points to their paths
            self.topPoints.append(top_point)
            self.bottomPoints.append(bottom_point)

            # now draw a 1-pixel-wide line along the center of the drawn path
            painter.setPen(QPen(self.brushColor, 1,
                            Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())

            # draw lines connecting all top points along the drawn path
            if len(self.topPoints) > 1:
                painter.drawLine(self.topPoints[-2], self.topPoints[-1])

            # draw lines connecting all bottom points along the drawn path
            if len(self.bottomPoints) > 1:
                painter.drawLine(self.bottomPoints[-2], self.bottomPoints[-1])

            # update lastPoint so the path line follows the stroke
            self.lastPoint = event.pos()
            # record stamp time
            self.lastStampTime = now

        # update to repaint cursor guide line
        self.update()

    # method for mouse left button release
    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            # make drawing flag false
            self.drawing = False

    # clear cursor position when leaving the window
    def leaveEvent(self, event):
        self.cursorPos = None
        self.update()
        super().leaveEvent(event)

    # handle key presses to control rotation and brush size
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self._keyLeft = True
        elif key == Qt.Key_Right:
            self._keyRight = True
        elif key == Qt.Key_Up:
            self._keyUp = True
        elif key == Qt.Key_Down:
            self._keyDown = True
        else:
            super().keyPressEvent(event)

    # handle key release to stop continuous changes
    def keyReleaseEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self._keyLeft = False
        elif key == Qt.Key_Right:
            self._keyRight = False
        elif key == Qt.Key_Up:
            self._keyUp = False
        elif key == Qt.Key_Down:
            self._keyDown = False
        else:
            super().keyReleaseEvent(event)

    # continuously apply key-based angle and size changes
    def _applyKeyChanges(self):
        changed = False

        if self._keyLeft:
            self.brushAngle = (self.brushAngle - 2.0) % 360.0
            changed = True

        if self._keyRight:
            self.brushAngle = (self.brushAngle + 2.0) % 360.0
            changed = True

        if self._keyUp:
            # increase brush size
            self.brushSize = min(self.brushSize + 1, 150)
            changed = True

        if self._keyDown:
            # decrease brush size
            self.brushSize = max(self.brushSize - 1, 20)
            changed = True

        if changed:
            self.update()

    # paint event
    def paintEvent(self, event):
        # create a canvas
        canvasPainter = QPainter(self)

        # draw rectangle  on the canvas
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

        # draw a guide line at the cursor, with length equal to brush size
        if self.cursorPos is not None:
            canvasPainter.setRenderHint(QPainter.Antialiasing, True)
            canvasPainter.setPen(QPen(self.brushColor, self.stampThickness,
                                  Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
            half_len = self.brushSize / 2.0
            x = self.cursorPos.x()
            y = self.cursorPos.y()

            if self.brushType == "Round" and self.drawing and (self.cursorPos != self.lastPoint):
                # for Round brush while drawing, cursor line is perpendicular to path
                vx = x - self.lastPoint.x()
                vy = y - self.lastPoint.y()
                length = math.hypot(vx, vy)
                if length == 0:
                    # fallback to vertical if movement is too small
                    dx = 0
                    dy = half_len
                else:
                    vx /= length
                    vy /= length
                    nx = -vy
                    ny = vx
                    dx = half_len * nx
                    dy = half_len * ny
                # remember last perpendicular direction while drawing
                self.lastNormal = (nx, ny)
            elif self.brushType == "Round":
                # Round brush but no path being drawn:
                # keep cursor line perpendicular to the last drawn path if available,
                # otherwise snap to vertical
                if self.lastNormal is not None:
                    nx, ny = self.lastNormal
                    dx = half_len * nx
                    dy = half_len * ny
                else:
                    dx = 0
                    dy = half_len
            else:
                # Flat brush uses the current brush angle
                angle_rad = math.radians(self.brushAngle)
                dx = half_len * math.cos(angle_rad)
                dy = half_len * math.sin(angle_rad)
            p1 = QPointF(x - dx, y - dy)
            p2 = QPointF(x + dx, y + dy)
            canvasPainter.drawLine(p1, p2)

    # method for saving canvas
    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                          "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        if filePath == "":
            return
        self.image.save(filePath)

    # method for clearing every thing on canvas
    def clear(self):
        # make the whole canvas white
        self.image.fill(Qt.white)
        # update
        self.update()

    # methods for changing brush type
    def setBrushFlat(self):
        self.brushType = "Flat"

    def setBrushRound(self):
        self.brushType = "Round"

    # method for changing stamp thickness
    def setStampThickness(self, thickness):
        self.stampThickness = thickness

    # methods for changing brush color
    def blackColor(self):
        self.brushColor = Qt.black

    def greenColor(self):
        self.brushColor = Qt.green

    def blueColor(self):
        self.brushColor = Qt.blue

    def yellowColor(self):
        self.brushColor = Qt.yellow

    def redColor(self):
        self.brushColor = Qt.red



# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# showing the window
window.show()

# start the app
sys.exit(App.exec())