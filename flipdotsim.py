import thread
import socket
import pygame
from pygame.locals import *

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
        self.RunServer()

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

        pygame.init()
        self.screen = pygame.display.set_mode((imageSize[0]*pixelSize, imageSize[1]*pixelSize))
        self.screen.fill((255,255,255))
        thread.start_new_thread(self.watchCloseThread, ())
        
    def watchCloseThread(self):
        while True:
            for event in pygame.event.get():
                if event.type in (QUIT, QUIT):
                    import os
                    os.kill(os.getpid(), 9)
            pygame.time.delay(500)  

    def show(self, imageArray):
        for yValue in range(self.imageSize[1]):
            for xValue in range(self.imageSize[0]):
                i = self.imageSize[0]*yValue + xValue
                color = imageArray[i]
                self.updatePixel(xValue, yValue, color)
        pygame.display.update()

    def clearPixels(self):
        for xValue in range(self.imageSize[0]):
            for yValue in range(self.imageSize[1]):
                self.updatePixel(xValue, yValue, self.BLACKCOLOR)
        
    def updatePixel(self, xValue, yValue, color):
        surface = pygame.Surface((self.pixelSize-1, self.pixelSize-1))
        if color == self.BLACKCOLOR:
                rectcolor = (0,0,0)
        else:
                rectcolor = (255,255,255)
        surface.fill(rectcolor)
        self.screen.blit(surface, (xValue*self.pixelSize, yValue*self.pixelSize))
        
if __name__ == '__main__':
    FlipdotSim(imageSize=(40,16), pixelSize = 10, udpPort=2323).run()
