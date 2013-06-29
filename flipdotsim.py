from Tkinter import *
import thread
import socket

class FlipdotSim():
    def __init__(self, 
                 imageSize = (40,16),
                 pixelSize = 10, 
                 udpPort = 2323):
        self.udpPort = udpPort
        self.flipdotMatrixSimulatorWidget = FlipdotMatrixSimulatorWidget(imageSize, pixelSize)
        self.udpHostSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.udpHostSocket.bind(("", self.udpPort))

    def run(self):
        thread.start_new_thread(self.RunServer, ())
        mainloop()

    def RunServer(self):
        try: 
            while True:
                rawData = self.udpHostSocket.recv(4096)
                imageArray = ImageArrayAdapter().convertPacketToImageArray(rawData)
                self.flipdotMatrixSimulatorWidget.show(imageArray)
        finally: 
            self.udpHostSocket.close() 

class ImageArrayAdapter():
    def __init__(self):
        self.arrayOfBinaryInts = []

    def convertPacketToImageArray(self, udpPacketStr):
        self.arrayOfBinaryInts = []
        byteArray = bytearray(udpPacketStr)
        for byte in byteArray:
            self.__appendByteToArrayOfBinaryInts(byte)
        return self.arrayOfBinaryInts
    
    def __appendByteToArrayOfBinaryInts(self, byte):
        byteValue = int(byte)
        for i in range(8):
            if byteValue/(2**(7-i)) > 0:
                self.arrayOfBinaryInts.append(1)
            else: 
                self.arrayOfBinaryInts.append(0)
            byteValue = byteValue%(2**(7-i))


class FlipdotMatrixSimulatorWidget():
    BLACKCOLOR = 0
    WHITECOLOR = 1
    
    def __init__(self,
                 imageSize = (40,16),
                 pixelSize = 10): 
        self.imageSize = imageSize
        self.pixelSize = pixelSize
        self.master = Tk()
        self.canvas = Canvas(self.master, width=imageSize[0]*10, height=imageSize[1]*10)
        self.canvas.pack()
        self.initEmptyPixels()
        
    def initEmptyPixels(self):
        self.clearPixels()
        for xValue in range(self.imageSize[0]):
            for yValue in range(self.imageSize[1]):
                self.addPixel(xValue, yValue, self.BLACKCOLOR)

    def show(self, imageArray):
        self.clearPixels()
        for xValue in range(self.imageSize[0]):
            for yValue in range(self.imageSize[1]):
                i = self.imageSize[0]*yValue + xValue
                color = imageArray[i]
                self.addPixel(xValue, yValue, color)
        self.canvas.update_idletasks()

    def clearPixels(self):
        self.canvas.delete(ALL)
        self.canvas.update_idletasks()
    
    def addPixel(self, xValue, yValue, color):
        xmin = xValue * self.pixelSize
        xmax = xmin + self.pixelSize-1
        ymin = yValue * self.pixelSize
        ymax = ymin + self.pixelSize-1
        if color == self.BLACKCOLOR:
                rectcolor = "black"
        else:
                rectcolor = "white"
        self.canvas.create_rectangle(xmin, ymin, xmax, ymax, fill=rectcolor)

if __name__ == '__main__':
    FlipdotSim(imageSize=(40,16), pixelSize = 10, udpPort=2323).run()
