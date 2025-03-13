from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os

#디스플레이 기본(화면에 띄우기, 좌우로 넘기기)
class DisplayImage(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.showFullScreen()
        self.setScaledContents(True)
        self.setAttribute(QtCore.Qt.WA_AcceptTouchEvents, True)
        self.image_folder = "images"
        self.images = sorted([os.path.join(self.image_folder, f) for f in os.listdir(self.image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))])
        self.current_image_index = 0
        self.original_pixmap = None  # 원본 이미지 사이즈
        self.label = self  # label 속성에 현재 위젯을 할당

        # 첫 번째 이미지 로드
        if self.images:
            self.display_image(self.images[self.current_image_index])
        else:
            print("저장된 이미지가 없습니다")

    def display_image(self, image_path):
        print(image_path)
        if image_path.lower().endswith('.gif'):  # GIF 파일 처리
            movie = QtGui.QMovie(image_path)
            self.setMovie(movie)
            movie.start()
        else:  # 일반 이미지 파일 처리
            pixmap = QtGui.QPixmap(image_path)
            self.setPixmap(pixmap)

    #터치로 사진 전환
    def mousePressEvent(self, event):
        if event.x() > self.width() / 2:
            self.next_image()
        else:
            self.previous_image()
    
    #키보드로 사진 전환
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            self.next_image()
        elif event.key() == QtCore.Qt.Key_Left:
            self.previous_image()

    #다음 이미지로 전환
    def next_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.display_image(self.images[self.current_image_index])
    #이전 이미지로 전환
    def previous_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.display_image(self.images[self.current_image_index])

#터치 디스플레이용
class TouchImage(QtCore.QObject):
    def __init__(self, label):
        super().__init__()
        self.label = label
        self.label.setAttribute(QtCore.Qt.WA_AcceptTouchEvents, True)
        self.start_positions = []

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.TouchBegin or event.type() == QtCore.QEvent.TouchUpdate:
            self.handle_touch(event)
        return super().eventFilter(obj, event)

    # 손가락 두개로 줌인 position 찾기
    def handle_touch(self, event):
        points = event.touchPoints()
        if len(points) == 2:
            p1, p2 = points[0].pos(), points[1].pos()
            distance = (p1 - p2).manhattanLength()
            self.zoom_image(distance)

    def zoom_image(self, distance):
        factor = distance / 300  # 임의값
        pixmap = self.label.pixmap()
        if pixmap:
            self.label.setPixmap(pixmap.scaled(pixmap.size() * factor, QtCore.Qt.KeepAspectRatio))

#음성 인식용
class MicImage:
    def __init__(self, label):
        self.label = label
    
    #음성으로 줌인
    def on_mic_zoom_in(self,position):
        pass
    
    #음성으로 원래 이미지 사이즈로 돌리기
    def on_mic_go_original(self):
        pass

#모션 인식용
class MotionSensorImage:
    def __init__(self, label):
        self.label = label
        
    def on_motion_zoom_in(self, position):
        pass

    def on_motion_zoom_out(self, position):
        pass
    
    def stop_zoom(self):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    display = DisplayImage()
    touch_manager = TouchImage(display.label)
    display.label.installEventFilter(touch_manager)
    display.show()
    sys.exit(app.exec_())
