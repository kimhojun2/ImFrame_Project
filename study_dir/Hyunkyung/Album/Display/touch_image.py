# 터치디스플레이용
from PyQt5 import QtCore, QtGui

class TouchImage(QtCore.QObject):
    def __init__(self, label):
        super().__init__()
        self.label = label
        self.label.setAttribute(QtCore.Qt.WA_AcceptTouchEvents, True)

    def eventFilter(self, obj, event):
        if event.type() in [QtCore.QEvent.TouchBegin, QtCore.QEvent.TouchUpdate]:
            self.handle_touch(event)
        return super().eventFilter(obj, event)

    def handle_touch(self, event):
        points = event.touchPoints()
        if len(points) == 2:
            p1, p2 = points[0].pos(), points[1].pos()
            distance = (p1 - p2).manhattanLength()
            self.zoom_image(distance)

    def zoom_image(self, distance):
        factor = distance / 300  #임시로 넣어둔 값
        pixmap = self.label.pixmap()
        if pixmap:
            self.label.setPixmap(pixmap.scaled(pixmap.size() * factor, QtCore.Qt.KeepAspectRatio))
