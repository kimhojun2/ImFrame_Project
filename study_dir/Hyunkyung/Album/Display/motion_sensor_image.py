# motion_sensor_image.py
# 모션센서용 확대,축소
from PyQt5 import QtWidgets, QtGui, QtCore

class MotionSensorImage:
    def __init__(self, label):
        self.label = label
        self.original_pixmap = label.pixmap() if label.pixmap() else None
        self.zoom_point = QtCore.QPoint(label.width() // 2, label.height() // 2) if label else QtCore.QPoint(0, 0)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)  # 줌 인/아웃 속도
        self.calculate_initial_zoom()
        self.timer.timeout.connect(self.apply_zoom)
        
    def calculate_initial_zoom(self):
        if self.original_pixmap:
            self.update_zoom_factors()
    
    def update_zoom_factors(self):
        screen_size = self.label.window().size()
        pixmap_size = self.original_pixmap.size()
        self.min_zoom_factor = min(screen_size.width() / pixmap_size.width(), screen_size.height() / pixmap_size.height())
        self.zoom_factor = max(self.min_zoom_factor, self.zoom_factor if hasattr(self, 'zoom_factor') else 0)
        self.max_zoom_factor = 3.0
        
    #모션인식으로 포인터가 들어왔을 때 줌인
    def on_motion_zoom_in(self, position):
        self.zoom_point = position  # 마우스 위치 업데이트
        self.timer.stop()
        self.timer.timeout.disconnect()
        self.timer.timeout.connect(self.increase_zoom)
        self.timer.start()

    #모션인식으로 포인터가 들어왔을 때 줌아웃
    def on_motion_zoom_out(self, position):
        self.zoom_point = position  # 마우스 위치 업데이트
        self.timer.stop()
        self.timer.timeout.disconnect()
        self.timer.timeout.connect(self.decrease_zoom)
        self.timer.start()
    
    #손이 없어지면 확대/축소 멈춤
    def stop_zoom(self):
        self.timer.stop()
    
    #사진 변경에 따라 업데이트
    def increase_zoom(self):
        if self.zoom_factor < self.max_zoom_factor:
            self.zoom_factor += 0.05
            self.apply_zoom()
    
    def decrease_zoom(self):
        if self.zoom_factor > self.min_zoom_factor:
            self.zoom_factor -= 0.05
            self.apply_zoom()
    
    def update_original_pixmap(self, pixmap):
        self.original_pixmap = pixmap
        self.calculate_initial_zoom()
        self.apply_zoom()
        
    def apply_zoom(self):
        if self.original_pixmap:
            new_width = int(self.original_pixmap.width() * self.zoom_factor)
            new_height = int(self.original_pixmap.height() * self.zoom_factor)
            scaled_pixmap = self.original_pixmap.scaled(new_width, new_height, QtCore.Qt.KeepAspectRatio)
            self.label.setPixmap(scaled_pixmap)
            self.label.resize(new_width, new_height)
            self.center_label()

    #중심점
    def center_label(self):
        # 확대/축소된 이미지를 마우스 포인터 위치를 중심으로 배치
        window_rect = self.label.window().rect()
        label_rect = self.label.rect()
        # 이미지 중심 위치 계산
        new_x = self.zoom_point.x() - label_rect.width() * 0.5
        new_y = self.zoom_point.y() - label_rect.height() * 0.5
        # 화면 경계 안에서 이미지 위치 조정
        new_x = max(0, min(window_rect.width() - label_rect.width(), new_x))
        new_y = max(0, min(window_rect.height() - label_rect.height(), new_y))
        self.label.move(int(new_x), int(new_y))