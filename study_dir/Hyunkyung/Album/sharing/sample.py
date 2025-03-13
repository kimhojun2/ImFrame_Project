import sys
import requests
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from io import BytesIO

class ImageDisplay(QLabel):
    def __init__(self, img_url):
        super().__init__()
        self.setWindowTitle('Image Display')
        self.load_image_from_url(img_url)
        self.setScaledContents(True)
        self.showFullScreen()  # 전체 화면으로 표시
        self.setAttribute(Qt.WA_DeleteOnClose, True)  # 창이 닫힐 때 위젯 삭제

    def load_image_from_url(self, url):
        response = requests.get(url)
        img_data = BytesIO(response.content)
        pixmap = QPixmap()
        pixmap.loadFromData(img_data.getvalue())
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        self.close()  # 이미지 클릭 시 프로그램 종료

def main(img_url):
    app = QApplication(sys.argv)
    display = ImageDisplay(img_url)
    display.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    img_url = "https://firebasestorage.googleapis.com/v0/b/ifind-5822e.appspot.com/o/images%2Fqudqud%2F1000000048.jpg?alt=media&token=6721de5b-ed46-4da8-8e34-de49cca4dd87"  # 이곳에 이미지 URL을 입력하세요
    main(img_url)
