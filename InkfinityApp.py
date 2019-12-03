from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter import filedialog
import copy
from PIL import ImageTk, Image, ImageOps
import requests
from io import BytesIO

def __init__(app, root, canvas):
    app.board = Board(app)
    app.brush = Brush(app)
    app.activeButton = None
    app.blendingTool = BlendingTool(app)
    app.eraser = Eraser() 
    app.magicWand = MagicWand()

    app.brushButton = Button(root, text='brush', command = lambda:useBrush(app))
    app.brushButton.pack()

    app.blendButton = Button(root, text='blend', command = lambda:useBlend(app))
    app.blendButton.pack()

    app.pictureButton = Button(root, text='import picture', 
        command = lambda:usePicture(app, root, canvas))
    app.pictureButton.pack()

    app.penButton = Button(root, text='pen', command = lambda:usePen(app))
    app.penButton.pack()

    app.magicWandButton = Button(root, text='Magic Wand', 
        command = lambda:useMagicWand(app))
    app.magicWandButton.pack()

    app.resetButton = Button(root, text='reset', 
        command = lambda:resetBoard(app, canvas))
    app.resetButton.pack()

    app.changeColorButton = Button(root, text='change color', 
        command = lambda:chooseColor(app))
    app.changeColorButton.pack()

    app.mouseDown = False   
    app.mouseDrag = False
    app.hasImage = False

def usePicture(app, root, canvas):
    window = Toplevel(root)

    responseText = StringVar()
    app.entry = Entry(window, textvariable = responseText)
    app.entry.grid(column=0, row=0)
    app.urlButton = Button(window, text = 'import image from url', 
        command = lambda:openUrlImage(app, window, canvas))   
    app.urlButton.grid(column=1, row=0)

    app.entryButton = Button(window, text = 'import image from local directory', 
        command = lambda:openLocalImage(app,window, canvas))   
    app.entryButton.grid(column=0, row=1)

    app.mirrorButton = Button(window, text = 'mirror imported image', 
        command = lambda:mirrorImage(app, window, canvas))
    app.mirrorButton.grid(column=0, row=2)

def openUrlImage(app, window, canvas):
    response = requests.get(app.entry.get())
    imageFromUrl = Image.open(BytesIO(response.content))
    imageFromUrl = imageFromUrl.resize((app.width,app.height))
    app.resizedImage = imageFromUrl
    app.image = ImageTk.PhotoImage(imageFromUrl)
    canvas.create_image(250,250,image=app.image)
    app.hasImage = True

def openLocalImage(app, window, canvas):
    #CITATION: opening file name from https://pythonspot.com/tk-file-dialogs/
    window.directory = filedialog.askopenfilename(initialdir = "/",
        title = "Select file",
        filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    imageFromLocalFile = Image.open(window.directory)
    imageFromLocalFile = imageFromLocalFile.resize((app.width, app.height))
    app.resizedImage = imageFromLocalFile
    app.image =ImageTk.PhotoImage(imageFromLocalFile)
    canvas.create_image(250,250,image=app.image)
    app.hasImage = True

def mirrorImage(app, window, canvas):
    app.resizedImage = ImageOps.mirror(app.resizedImage)
    app.image =ImageTk.PhotoImage(app.resizedImage)
    canvas.create_image(250,250,image=app.image)

def chooseColor(app):
    app.brush.hexColor = askcolor()[1]
    print(app.brush.hexColor)

def useBlend(app):
    app.activeButton = 'blend'

def resetBoard(app, canvas):
    app.board = Board(app)
    app.brush.pointNum=0
    canvas.delete("all")
    app.mouseDrag = False
    app.mouseDown = False
    app.activeButton = None

def useBrush(app):
    app.activeButton = 'brush'
    app.brush.brushRadius = 20

def usePen(app):
    app.activeButton = 'brush'
    app.brush.brushRadius = 1

def useMagicWand(app):
    app.moveObject = False
    app.magicWand = MagicWand()
    app.activeButton = 'magicWand'

def mouseDragged(app, event, canvas):
    if app.activeButton == 'brush':
        app.brush.cx, app.brush.cy = event.x, event.y
    elif app.activeButton == 'magicWand':
        app.magicWand.cx, app.magicWand.cy = event.x, event.y
        if app.magicWand.isEnclosed and ((event.y,event.x) in 
            app.magicWand.moveAreaSet):
            app.moveObject = True
            print("moving")
    app.mouseDrag = True

def drawAll(app, canvas, event):
    if app.activeButton == 'brush':
        if app.mouseDown or app.mouseDrag:
            app.brush.draw(event, canvas)
            app.board.updateBoard(app, canvas)

    elif app.activeButton == 'magicWand':
        if app.magicWand.isEnclosed == False:
            if app.mouseDown or app.mouseDrag:
                app.magicWand.draw(event, canvas)
                app.board.updateBoard(app, canvas)

        elif app.magicWand.isEnclosed and app.moveObject == True:
            if app.magicWand.hasOldPoints==True:
                startPointCoords = app.magicWand.oldDrawnPointsInArea[0][1][2]
                startPoint = app.magicWand.oldDrawnPointsInArea[0][0]

                for point in range(1,len(app.magicWand.oldDrawnPointsInArea)):
                    if point == startPoint+1:
                        coords = app.magicWand.oldDrawnPointsInArea[point][1][2]
                        canvas.create_line(startPointCoords[0], 
                            startPointCoords[1], coords[0], coords[1],
                            fill = 'white',
                            width = app.magicWand.oldDrawnPointsInArea[point][1][3]+3,
                            capstyle=ROUND, smooth = TRUE, splinesteps = 100)
                        startPoint = point
                        startPointCoords = coords
                    else:
                        startPoint = point
                        startPointCoords = app.magicWand.drawnPointsInArea[point][1][2]

            app.magicWand.moveArea(app, event, canvas)

            startPointCoords = app.magicWand.drawnPointsInArea[0][1][2]
            startPoint = app.magicWand.drawnPointsInArea[0][0]

            for point in range(1,len(app.magicWand.drawnPointsInArea)):
                if point == startPoint+1:
                    coords = app.magicWand.drawnPointsInArea[point][1][2]
                    canvas.create_line(startPointCoords[0], startPointCoords[1], 
                        coords[0], coords[1],
                        fill = app.magicWand.drawnPointsInArea[point][1][0], 
                        width = app.magicWand.drawnPointsInArea[point][1][3],
                        capstyle=ROUND, smooth = TRUE, splinesteps = 100)
                    startPoint = point
                    startPointCoords = coords
                 
                else:
                    startPoint = point
                    startPointCoords = app.magicWand.drawnPointsInArea[point][1][2]

    elif app.activeButton == "blend":
        app.blendingTool.draw(canvas, event, app.board.boardList)


class Board(object):
    def __init__(self, app):
        self.rgbColor = (255,255,255)
        self.hexColor = "#%02x%02x%02x" % self.rgbColor
        self.defaultColor = "#%02x%02x%02x" % (255,255,255)

        self.rows = app.width
        self.cols = app.height
        self.boardList = ([[[self.hexColor,'board', (j,i)] for j in range(self.cols)] 
            for i in range(self.rows)])

    def updateBoard(self, app, canvas):
        if app.activeButton == 'brush':
            x,y = app.brush.cx, app.brush.cy
            r = app.brush.brushRadius

            if app.brush.brushRadius == 1:
                for row in range(y, y+1):
                    for col in range(x, x+1):
                        app.brush.pointNum+=1
                        app.board.boardList[row][col] = ([app.brush.hexColor, 
                                'brush', (col, row), app.brush.pointNum, r])
                        print(row,col, app.board.boardList[row][col])
            else:
                 for row in range(y-(r//10), y+(r//10)):
                    for col in range(x-(r//10), x+(r//10)):
                        app.brush.pointNum+=1
                        app.board.boardList[row][col] = ([app.brush.hexColor, 
                                'brush', (col, row), app.brush.pointNum, r])
                        print(row,col, app.board.boardList[row][col])
        
        if app.activeButton == 'magicWand' and app.magicWand.isEnclosed == False:
            x,y = app.magicWand.cx, app.magicWand.cy
            r = app.magicWand.brushRadius
            app.board.boardList[y][x].append('magicWand')
            print(app.board.boardList[y][x])
            app.magicWand.selectArea(x, y, app.board.boardList, canvas)

class Brush(object):
    def __init__(self, app):
        self.rgbColor = (0,0,0)

        #CITATION: hex conversion code from https://stackoverflow.com/a/41384190
        self.hexColor = "#%02x%02x%02x" % self.rgbColor

        self.texture = 'pen'
        self.brushRadius = 1
        self.pointNum = 0

        self.cx = None
        self.cy = None
        self.oldX = None
        self.oldY = None

    def draw(self, event, canvas):
        canvas.create_line(self.cx, self.cy, event.x, event.y,
                            width=self.brushRadius, fill=self.hexColor,
                            capstyle=ROUND, smooth = TRUE, splinesteps = 100)
        self.cx, self.cy = event.x, event.y

class BlendingTool(Brush):
    def __init__(self, app):
        super().__init__(self)
        self.blendedColors = None
        self.brushRadius = 20
        self.colorSet = None
        self.colorDict = None
        self.blendedBoard = None
    
    def getColorMidpoints(self, rgb1, rgb2, midpoints):
        interval1 = (rgb1[0] + rgb2[0])//midpoints
        interval2 = (rgb1[1] + rgb2[1])//midpoints
        interval3 = (rgb1[2] + rgb2[2])//midpoints

        midpointList = []
        for point in range(midpoints+1):
            midpointList.append(tuple(((interval1*point), (interval2*point), 
                (interval3*point))))

        return midpointList

    def getColors(self, event, board):
        colorSet = set()
        boardList = []
        x,y = self.cx, self.cy
        r = self.brushRadius
        for row in range(y-(r//10), y+(r//10)):
            for col in range(x-(r//10), x+(r//10)):
                colorSet.add(board[row][col][0])
                boardList.append(board[row][col])
        self.boardList = boardList
        self.colorSet = colorSet
    
    def canBlend(self):
        return (len(self.colorSet) > 1)
    
    def seperateColors(self):
        colorDict = dict()
        for i in range(len(self.boardList)):
            point = self.boardList[i]
            print(point, self.colorSet)
            colorDict[point[0]] = (colorDict.get(point[0], []) + [point[2]])
        self.colorDict = colorDict
    
    @staticmethod
    def distance(x1, y1, x2, y2):
        return (((x1-x2)**2)+((y1-y2)**2))
    
    @staticmethod
    def convertToRGB(hexadecimal):
        #CITATION: conversion code from https://stackoverflow.com/a/29643643
        h = hexadecimal.replace('#', '')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def blendBoard(self):
        blendedBoard = []
        if self.canBlend():
            print(self.colorSet)
            tempColorSet = copy.deepcopy(self.colorSet)
            print(tempColorSet)
            for color in self.colorSet:
                print(tempColorSet)
                otherColorSet = tempColorSet - {color}
                for point in self.colorDict[color]:
                    print(tempColorSet, otherColorSet)
                    for otherColor in otherColorSet:
                        for otherPoint in self.colorDict[otherColor]:
                            if (BlendingTool.distance(point[0],point[1], 
                                otherPoint[0], otherPoint[1]) < 2):
                                rgb1 = BlendingTool.convertToRGB(color)
                                rgb2 = BlendingTool.convertToRGB(otherColor)
                                print(rgb1, rgb2)
                                midpoints = 2

                                midColors = self.getColorMidpoints(rgb1, rgb2, midpoints)
                                blendedBoard.append([[midColors], [point, otherPoint]])
            self.blendedBoard = blendedBoard

    def draw(self, canvas, event, board):
        self.cx, self.cy = event.x, event.y
        self.getColors(event,board)
        if self.canBlend():
            self.seperateColors()
            self.blendBoard()
            print(self.blendedBoard)






    
class Eraser(object):
    def __init__(self):
        self.brushSize = None
        self.cx = None
        self.cy = None
        self.r = None

    def erase(self):
        pass

    def changeSize(self):
        pass

class MagicWand(object):
    def __init__(self):
        self.brushRadius = 1
        self.isEnclosed = False
        self.selectedAreaSet = set()
        self.moveAreaSet = set()
        self.cx = None 
        self.cy = None
        self.boardList = None
        self.defaultColor = "#%02x%02x%02x" % (255,255,255)
        self.drawnPointsInArea = None
        self.oldDrawnPointsInArea = None
        self.hasOldPoints = False

    def selectArea(self, cx, cy, boardList, canvas):
        if not self.isEnclosed:
            if (cx,cy) in self.selectedAreaSet:
                self.boardList = boardList
                self.defineSelectedAreaBounds(canvas)
                self.isEnclosed = True
                self.findDrawnPointsInSelectedArea()
                print('ENCLOSED')
            else:
                self.selectedAreaSet.add((cx,cy))

    def defineSelectedAreaBounds(self, canvas):
        bounds = []

        selectedRows = []
        for row in range(len(self.boardList)):
            for col in range(len(self.boardList[0])):
                if 'magicWand' in self.boardList[row][col]:
                    selectedRows.append(row)
        self.minRow = min(selectedRows)
        self.maxRow = max(selectedRows)

        self.colBounds = []
        for row in range(self.minRow, self.maxRow+1):
            selectedCols = []
            for col in range(len(self.boardList[0])):
                if 'magicWand' in self.boardList[row][col]:
                    selectedCols.append(col)
            if len(selectedCols)<=1:
                self.colBounds.append(self.colBounds[-1])
            else:
                minCol = min(selectedCols)
                maxCol = max(selectedCols)
                self.colBounds.append((minCol, maxCol))

        index = 0
        for row in range(self.minRow,self.maxRow+1):
            for col in range(self.colBounds[index][0], self.colBounds[index][1]):
                self.boardList[row][col].append('selected')
                print(self.boardList[row][col])
                self.moveAreaSet.add((row,col))
            index+=1
        #self.testDraw(canvas)
        
    def testDraw(self, canvas):
        index = 0
        for row in range(self.minRow,self.maxRow+1):
#            for col in range(self.colBounds[index][0], self.colBounds[index][1]):
            canvas.create_line(self.colBounds[index][0], row, 
                self.colBounds[index][1], row, fill = self.defaultColor)
            index+=1

    def moveArea(self, app, event, canvas):
        x,y = self.cx, self.cy
        distX = event.x-x
        distY = event.y-y
        self.oldDrawnPointsInArea = copy.deepcopy(self.drawnPointsInArea)
        print(self.oldDrawnPointsInArea)
        self.hasOldPoints = True

        for point in range(len(self.drawnPointsInArea)):
            coords = self.drawnPointsInArea[point][1][2]
            xCoord, yCoord = coords[0], coords[1]
            self.drawnPointsInArea[point][1][2] = (xCoord+distX, yCoord+distY)

        self.cx = event.x
        self.cy = event.y

    def findDrawnPointsInSelectedArea(self):
        pointDict = dict()
        for row in range(len(self.boardList)):
            for col in range(len(self.boardList[0])):
                if ('selected' in self.boardList[row][col] and 
                    'brush' in self.boardList[row][col]):
                    tempList = copy.deepcopy(self.boardList[row][col])
                    pointNum = self.boardList[row][col][3]
                    pointDict[pointNum] = tempList[:3] + tempList[4:]
        self.drawnPointsInArea = sorted(list(pointDict.items()))
        print(self.drawnPointsInArea)

    def draw(self, event, canvas):
        canvas.create_line(self.cx, self.cy, event.x, event.y,
                    width=self.brushRadius, fill='red',
                    capstyle=ROUND, smooth = TRUE, splinesteps = 100)

        self.cx, self.cy = event.x, event.y

#CITATION: adapted basic Tkinter setup from 
# http://www.krivers.net/15112-f18/notes/notes-oopy-animation.html
def run(width=300, height=300):
    def drawAllWrapper(app, canvas, event):
        drawAll(app, canvas, event)

    def mousePressedWrapper(app, event, canvas):
        mouseDragged(app, event, canvas)

# Set up data and call init
    class Struct(object): pass
    app = Struct()
    app.width = width
    app.height = height

    # create the root
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window

    # create the canvas
    canvas = Canvas(root, width=app.width, height=app.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()

  # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(app, event, canvas))
    root.bind('<B1-Motion>', lambda event:
                            drawAllWrapper(app, canvas, event))

    __init__(app, root, canvas)

    # launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(500, 500)