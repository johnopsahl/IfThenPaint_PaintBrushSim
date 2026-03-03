# importing libraries
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys
import math

# window class
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("Paint with PyQt5")

        # setting geometry to main window
        self.setGeometry(100, 100, 800, 600)

        # creating image object
        self.image = QImage(self.size(), QImage.Format_RGB32)

        # making image color to white
        self.image.fill(Qt.white)

        # variables
        # drawing flag
        self.drawing = False
        # default brush size
        self.brushSize = 2
        # default color
        self.brushColor = Qt.black

        # QPoint object to tract the point
        self.lastPoint = QPoint()

        # store the last drawn path as a list of points
        self.lastPathPoints = []

        # rotation range for projected line (degrees)
        self.rectStartAngle = 0.0
        self.rectEndAngle = 360.0

        # creating menu bar
        mainMenu = self.menuBar()

        # creating file menu for save and clear action
        fileMenu = mainMenu.addMenu("File")

        # adding brush size to main menu
        b_size = mainMenu.addMenu("Brush Size")

        # adding brush color to ain menu
        b_color = mainMenu.addMenu("Brush Color")

        # menu for path-related actions
        path_menu = mainMenu.addMenu("Path")

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

        # action to apply a stroke to the last drawn path
        strokePathAction = QAction("Apply Stroke to Last Path", self)
        strokePathAction.setShortcut("Ctrl + P")
        path_menu.addAction(strokePathAction)
        strokePathAction.triggered.connect(self.applyStrokeToLastPath)

        # action to project a rotating line onto the last path
        rectPathAction = QAction("Project Rotating Line on Last Path", self)
        rectPathAction.setShortcut("Ctrl + R")
        path_menu.addAction(rectPathAction)
        rectPathAction.triggered.connect(self.projectRotatingRectangleOnLastPath)

        # action to set rotation range for the projected line
        setRangeAction = QAction("Set Line Rotation Range...", self)
        path_menu.addAction(setRangeAction)
        setRangeAction.triggered.connect(self.setRectangleRotationRange)

        # creating options for brush sizes
        # creating action for selecting pixel of 4px
        pix_4 = QAction("4px", self)
        # adding this action to the brush size
        b_size.addAction(pix_4)
        # adding method to this
        pix_4.triggered.connect(self.Pixel_4)

        # similarly repeating above steps for different sizes
        pix_7 = QAction("7px", self)
        b_size.addAction(pix_7)
        pix_7.triggered.connect(self.Pixel_7)

        pix_9 = QAction("9px", self)
        b_size.addAction(pix_9)
        pix_9.triggered.connect(self.Pixel_9)

        pix_12 = QAction("12px", self)
        b_size.addAction(pix_12)
        pix_12.triggered.connect(self.Pixel_12)

        # creating options for brush color
        # creating action for black color
        black = QAction("Black", self)
        # adding this action to the brush colors
        b_color.addAction(black)
        # adding methods to the black
        black.triggered.connect(self.blackColor)

        # similarly repeating above steps for different color
        white = QAction("White", self)
        b_color.addAction(white)
        white.triggered.connect(self.whiteColor)

        green = QAction("Green", self)
        b_color.addAction(green)
        green.triggered.connect(self.greenColor)

        yellow = QAction("Yellow", self)
        b_color.addAction(yellow)
        yellow.triggered.connect(self.yellowColor)

        red = QAction("Red", self)
        b_color.addAction(red)
        red.triggered.connect(self.redColor)


    # method for checking mouse cicks
    def mousePressEvent(self, event):

        # if left mouse button is pressed
        if event.button() == Qt.LeftButton:
            # make drawing flag true
            self.drawing = True
            # make last point to the point of cursor
            self.lastPoint = event.pos()
            # start a new path
            self.lastPathPoints = [self.lastPoint]

    # method for tracking mouse activity
    def mouseMoveEvent(self, event):
        
        # checking if left button is pressed and drawing flag is true
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            
            # creating painter object
            painter = QPainter(self.image)
            
            # set the pen of the painter
            painter.setPen(QPen(self.brushColor, self.brushSize, 
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
            # draw line from the last point of cursor to the current point
            # this will draw only one step
            painter.drawLine(self.lastPoint, event.pos())
            
            # change the last point
            self.lastPoint = event.pos()
            # record the point in the current path
            self.lastPathPoints.append(self.lastPoint)
            # update
            self.update()

    # method for mouse left button release
    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            # make drawing flag false
            self.drawing = False

    # paint event
    def paintEvent(self, event):
        # create a canvas
        canvasPainter = QPainter(self)
        
        # draw rectangle  on the canvas
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

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

        # also clear stored path information
        self.lastPathPoints = []

    def applyStrokeToLastPath(self):
        # apply a stroke along the last drawn path using the current brush
        if len(self.lastPathPoints) < 2:
            return

        painter = QPainter(self.image)
        painter.setPen(QPen(self.brushColor, self.brushSize,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        prev_point = self.lastPathPoints[0]
        for point in self.lastPathPoints[1:]:
            painter.drawLine(prev_point, point)
            prev_point = point

        self.update()

    def projectRotatingRectangleOnLastPath(self):
        # project a rotating line along the last drawn path
        if len(self.lastPathPoints) < 2:
            return

        painter = QPainter(self.image)
        painter.setPen(QPen(self.brushColor, 1,
                            Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))

        segment_count = len(self.lastPathPoints) - 1

        for i in range(1, len(self.lastPathPoints)):
            p1 = self.lastPathPoints[i - 1]
            p2 = self.lastPathPoints[i]

            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()

            if dx == 0 and dy == 0:
                continue

            angle_deg = math.degrees(math.atan2(dy, dx))

            # fraction of the way along the path for this segment
            if segment_count > 1:
                t = (i - 1) / (segment_count - 1)
            else:
                t = 0.0

            # interpolate additional rotation between start and end angles
            extra_angle = self.rectStartAngle + t * (self.rectEndAngle - self.rectStartAngle)
            total_angle = angle_deg + extra_angle

            cx = (p1.x() + p2.x()) / 2.0
            cy = (p1.y() + p2.y()) / 2.0

            painter.save()
            painter.translate(cx, cy)
            painter.rotate(total_angle)

            line_length = self.brushSize * 6
            line = QLineF(-line_length / 2.0, 0.0,
                          line_length / 2.0, 0.0)
            painter.drawLine(line)

            painter.restore()

        self.update()

    def setRectangleRotationRange(self):
        # allow the user to set start and end rotation angles in degrees
        start_angle, ok1 = QInputDialog.getDouble(
            self, "Start Angle", "Start angle (degrees):",
            self.rectStartAngle, -3600.0, 3600.0, 1
        )
        if not ok1:
            return

        end_angle, ok2 = QInputDialog.getDouble(
            self, "End Angle", "End angle (degrees):",
            self.rectEndAngle, -3600.0, 3600.0, 1
        )
        if not ok2:
            return

        self.rectStartAngle = start_angle
        self.rectEndAngle = end_angle

    # methods for changing pixel sizes
    def Pixel_4(self):
        self.brushSize = 4

    def Pixel_7(self):
        self.brushSize = 7

    def Pixel_9(self):
        self.brushSize = 9

    def Pixel_12(self):
        self.brushSize = 12

    # methods for changing brush color
    def blackColor(self):
        self.brushColor = Qt.black

    def whiteColor(self):
        self.brushColor = Qt.white

    def greenColor(self):
        self.brushColor = Qt.green

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