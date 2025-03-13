import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, Qt, pyqtSlot

class WorkerThread(QThread):
    update_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str, bool)  # 스레드 상태와 이름을 전송

    def __init__(self, name, shared_data, mutex, interval, increment):
        super().__init__()
        self.name = name
        self.shared_data = shared_data
        self.mutex = mutex
        self.interval = interval
        self.increment = increment
        self.active = True

    def run(self):
        self.status_signal.emit(self.name, True)  # 스레드 시작 신호
        while self.active:
            self.sleep(self.interval)
            self.mutex.lock()
            self.shared_data.value += self.increment
            current_value = self.shared_data.value
            self.mutex.unlock()
            self.update_signal.emit(current_value)
        self.status_signal.emit(self.name, False)  # 스레드 종료 신호

    def stop(self):
        self.active = False

class SharedData:
    def __init__(self):
        self.value = 0
        self.mutex = QMutex()

class MainWindow(QMainWindow):
    def __init__(self, shared_data):
        super().__init__()
        self.shared_data = shared_data
        self.active_threads = set()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Thread Control and Status Display")
        layout = QVBoxLayout()
        
        self.label = QLabel("Initial value: 0", self)
        self.thread_status_label = QLabel("Active threads: None", self)
        self.thread_status_label.setAlignment(Qt.AlignRight)
        
        layout.addWidget(self.label)
        layout.addWidget(self.thread_status_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.worker1 = WorkerThread("Worker 1", self.shared_data, self.shared_data.mutex, 2, 10)
        self.worker1.update_signal.connect(self.update_label)
        self.worker1.status_signal.connect(self.update_thread_status)
        self.worker1.start()

        self.worker2 = WorkerThread("Worker 2", self.shared_data, self.shared_data.mutex, 3, 5)
        self.worker2.update_signal.connect(self.update_label)
        self.worker2.status_signal.connect(self.update_thread_status)

    @pyqtSlot(int)
    def update_label(self, value):
        self.label.setText(f"Updated value: {value}")
        if value > 20 and not self.worker2.isRunning():
            self.worker2.start()
        elif value > 50 and self.worker2.isRunning():
            self.worker2.stop()

    @pyqtSlot(str, bool)
    def update_thread_status(self, name, is_active):
        if is_active:
            self.active_threads.add(name)
        else:
            self.active_threads.discard(name)
        active_threads_str = ", ".join(self.active_threads)
        self.thread_status_label.setText(f"Active threads: {active_threads_str if active_threads_str else 'None'}")

    def closeEvent(self, event):
        self.worker1.terminate()
        if self.worker2.isRunning():
            self.worker2.terminate()
        super().closeEvent(event)

shared_data = SharedData()
app = QApplication(sys.argv)
main_window = MainWindow(shared_data)
main_window.show()
sys.exit(app.exec_())
