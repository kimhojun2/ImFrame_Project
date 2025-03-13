from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
import sys, os, time
import pygame

app = QApplication(sys.argv)
pygame.mixer.init()
pygame.mixer.music.load("answer.wav")


class MainDisplay(QLabel):
    isCircle = False


    def __init__(self, index):
        super().__init__()
        self.image_paths = self.loadPath()
        self.index = index
        self.setupUI()

        self.initNextThread()
        self.initPrevThread()

    
    def initNextThread(self):
        self.next_thread = NextThread()
        self.next_thread.next_signal.connect(self.nextImage)
        self.next_thread.start()
    

    def closeNextThread(self):
        self.next_thread.stop()

    
    def initPrevThread(self):
        self.prev_thread = PrevThread()
        self.prev_thread.prev_signal.connect(self.prevImage)
        self.prev_thread.start()


    def loadPath(self):
        return [os.path.join("images/", entry) for entry in os.listdir("images/") if os.path.isfile(os.path.join("images/", entry))]
    
    
    def setupUI(self):
        pixmap = QPixmap(self.image_paths[self.index])

        self.showFullScreen()
        self.setPixmap(pixmap)
        self.setScaledContents(True)


    def setImage(self, index):
        pixmap = QPixmap(self.image_paths[index])
        self.setPixmap(pixmap)

    
    def nextImage(self):
        self.image_paths = self.loadPath()
        self.index = (self.index + 1) % len(self.image_paths)
        self.setImage(self.index)

    
    def prevImage(self):
        self.image_paths = self.loadPath()
        self.index = (self.index - 1) % len(self.image_paths)
        self.setImage(self.index)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.image_paths = self.loadPath()
            self.index = (self.index + 1) % len(self.image_paths)
            self.setImage(self.index)
        elif event.key() == Qt.Key_Left:
            self.image_paths = self.loadPath()
            self.index = (self.index - 1) % len(self.image_paths)
            self.setImage(self.index)
        elif event.key() == Qt.Key_Up:
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # self.initNextThread()

            # self.isCircle = not self.isCircle
            # self.update()
        elif event.key() == Qt.Key_Down:
            self.closeNextThread()
        elif event.key() == Qt.Key_Escape:
            self.close()
    

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isCircle:
            painter = QPainter(self)
            painter.setBrush(QBrush(QColor(255, 20, 147)))
            painter.setRenderHint(QPainter.Antialiasing)
            center_x = self.width() // 7 * 6
            center_y = self.height() // 4
            radius = min(self.width(), self.height()) // 20
            painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
        else:
            pass


class NextThread(QThread):
    next_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True


    def run(self):
        while self.running:
            time.sleep(3)
            self.next_signal.emit()
    
    
    def stop(self):
        self.running = False
        self.quit()


class PrevThread(QThread):
    prev_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True


    def run(self):
        while self.running:
            time.sleep(5)
            self.prev_signal.emit()
        
    
    def stop(self):
        self.running = False


window = MainDisplay(0)
sys.exit(app.exec_())
