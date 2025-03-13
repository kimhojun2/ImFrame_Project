#image_load.py
#에러때문에 일단 지금은 사용 안함
from PyQt5 import QtCore, QtGui

class ImageLoaderThread(QtCore.QThread):
    imageLoaded = QtCore.pyqtSignal(object)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        if self.image_path.lower().endswith('.gif'):
            self.imageLoaded.emit(self.image_path)  # GIF 경로를 직접 전달
        else:
            pixmap = QtGui.QPixmap(self.image_path)
            if not pixmap.isNull():
                self.imageLoaded.emit(pixmap)
            else:
                self.imageLoaded.emit(None)