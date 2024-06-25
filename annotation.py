import sys
import time
import json
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QThread, pyqtSignal
import mss
from pynput import keyboard, mouse
import cv2
import ffmpeg

class AnnotationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.actions = []
        self.recording = False

    def initUI(self):
        self.setWindowTitle('Action Annotation Tool')
        self.setGeometry(100, 100, 800, 600)

        self.label_action = QLabel('Action:', self)
        self.label_details = QLabel('Details:', self)

        self.text_action = QLineEdit(self)
        self.text_details = QLineEdit(self)

        self.btn_start = QPushButton('Start Recording', self)
        self.btn_start.clicked.connect(self.start_recording)

        self.btn_stop = QPushButton('Stop Recording', self)
        self.btn_stop.clicked.connect(self.stop_recording)
        self.btn_stop.setEnabled(False)

        self.label_log = QLabel('Action Log:', self)
        self.text_log = QTextEdit(self)
        self.text_log.setReadOnly(True)

        layout_action = QVBoxLayout()
        layout_action.addWidget(self.label_action)
        layout_action.addWidget(self.text_action)
        layout_action.addWidget(self.label_details)
        layout_action.addWidget(self.text_details)
        layout_action.addWidget(self.btn_start)
        layout_action.addWidget(self.btn_stop)

        layout_log = QVBoxLayout()
        layout_log.addWidget(self.label_log)
        layout_log.addWidget(self.text_log)

        layout_main = QHBoxLayout()
        layout_main.addLayout(layout_action)
        layout_main.addLayout(layout_log)

        self.setLayout(layout_main)

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.thread_record = RecordThread()
            self.thread_record.signal_action.connect(self.record_action)
            self.thread_record.start()
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.log_message('Recording started.')

    def stop_recording(self):
        if self.recording:
            self.thread_record.stop()
            self.thread_record.wait()
            self.recording = False
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.log_message('Recording stopped.')
            self.save_actions()
            self.thread_record.save_video('screen_recording.mp4')

    def record_action(self, action, details):
        self.actions.append({
            'timestamp': time.time(),
            'action': action,
            'details': details
        })
        self.log_message(f"Recorded action: {action} - {details}")

    def log_message(self, message):
        current_log = self.text_log.toPlainText()
        self.text_log.setPlainText(current_log + '\n' + message)
        cursor = self.text_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_log.setTextCursor(cursor)

    def save_actions(self):
        with open('recorded_actions.json', 'w') as f:
            json.dump(self.actions, f, indent=4)

class RecordThread(QThread):
    signal_action = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.stopped = False
        self.frames = []
        self.start_time = time.time()
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_keyboard_press, on_release=self.on_keyboard_release)

    def run(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while not self.stopped:
                img = sct.grab(monitor)
                img_np = np.array(img)
                img_np = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
                self.frames.append(img_np)
                self.signal_action.emit("Screen Capture", f"Captured screen image at {time.time() - self.start_time:.2f}s")
                time.sleep(0.1)  # Adjust as needed to control frame rate

        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def stop(self):
        self.stopped = True

    def on_keyboard_press(self, key):
        try:
            action = f"Key Pressed: {key.char}"
        except AttributeError:
            action = f"Special Key Pressed: {key}"
        self.signal_action.emit(action, f"Keyboard event at {time.time() - self.start_time:.2f}s")

    def on_keyboard_release(self, key):
        try:
            action = f"Key Released: {key.char}"
        except AttributeError:
            action = f"Special Key Released: {key}"
        self.signal_action.emit(action, f"Keyboard event at {time.time() - self.start_time:.2f}s")

    def on_mouse_click(self, x, y, button, pressed):
        action = f"Mouse {'Pressed' if pressed else 'Released'}: {button} at ({x}, {y})"
        self.signal_action.emit(action, f"Mouse event at {time.time() - self.start_time:.2f}s")

    def save_video(self, output_file):
        height, width, layers = self.frames[0].shape
        size = (width, height)
        out = cv2.VideoWriter('temp_video.avi', cv2.VideoWriter_fourcc(*'XVID'), 10, size)
        
        for frame in self.frames:
            out.write(frame)
        out.release()

        ffmpeg.input('temp_video.avi').output(output_file).run()
        os.remove('temp_video.avi')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AnnotationApp()
    ex.show()
    sys.exit(app.exec_())
