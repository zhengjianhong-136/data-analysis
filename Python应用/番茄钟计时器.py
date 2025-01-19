import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox, QFileDialog, QDesktopWidget
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.background_image = None
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0
        
        # 初始化音频播放器
        self.player = QMediaPlayer()
        # 默认提示音
        self.sound_file = r'C:\Users\ZJH\Music\MetroGnome - iPhone (铃声).mp3'

    def initUI(self):
        self.setWindowTitle('番茄钟计时器')
        self.setGeometry(300, 300, 500, 400)

        # 创建背景标签
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, 500, 400)
        self.set_default_background()

        # 主布局（透明）
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # 设置布局边距

        # 背景选择按钮
        # bg_btn_layout = QHBoxLayout()
        # choose_bg_btn = QPushButton('选择背景', self)
        # choose_bg_btn.clicked.connect(self.choose_background)
        # reset_bg_btn = QPushButton('重置背景', self)
        # reset_bg_btn.clicked.connect(self.set_default_background)
        
        # bg_btn_layout.addWidget(choose_bg_btn)
        # bg_btn_layout.addWidget(reset_bg_btn)
        # layout.addLayout(bg_btn_layout)
        
        # 输入时间部分
        input_layout = QHBoxLayout()
        self.time_input = QLineEdit(self)
        self.time_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 180); 
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.time_input.setPlaceholderText('输入时间(分钟)')
        input_layout.addWidget(self.time_input)
        
        # 开始按钮
        start_btn = QPushButton('开始', self)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(52, 152, 219, 200);
                border-radius: 5px;
                padding: 5px;
            }
        """)
        start_btn.clicked.connect(self.start_timer)
        input_layout.addWidget(start_btn)
        
        layout.addLayout(input_layout)
        
        # 显示剩余时间的标签
        self.timer_label = QLabel('00:00', self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet('''
            QLabel {
                font-size: 48px; 
                color: white; 
                background-color: rgba(0, 0, 0, 100);
                border-radius: 10px;
            }
        ''')
        layout.addWidget(self.timer_label)
        
        # 选择音频文件按钮
        choose_sound_btn = QPushButton('选择提示音', self)
        choose_sound_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 180); 
                border-radius: 5px;
                padding: 5px;
            }
        """)
        choose_sound_btn.clicked.connect(self.choose_sound_file)
        layout.addWidget(choose_sound_btn)
        
        # 暂停和重置按钮
        btn_layout = QHBoxLayout()
        pause_btn = QPushButton('暂停/继续', self)
        pause_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 5px;
                padding: 5px;
            }
        """)
        pause_btn.clicked.connect(self.pause_timer)
        reset_btn = QPushButton('重置', self)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 5px;
                padding: 5px;
            }
        """)
        reset_btn.clicked.connect(self.reset_timer)
        
        btn_layout.addWidget(pause_btn)
        btn_layout.addWidget(reset_btn)
        layout.addLayout(btn_layout)
        
        # 居中显示
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def set_default_background(self):
        # 默认背景（渐变色）
        self.background_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    spread:pad, 
                    x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(200, 230, 255, 255), 
                    stop:1 rgba(170, 210, 255, 255)
                );
            }
        """)
        self.background_image = None

    def choose_background(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 
                                                   '选择背景图片', 
                                                   '', 
                                                   '图片文件 (*.png *.jpg *.jpeg *.bmp)')
        if file_name:
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            self.background_label.setPixmap(scaled_pixmap)
            self.background_label.setScaledContents(True)
            self.background_image = file_name

    # 其他方法保持不变（start_timer, update_timer等）与之前的代码相同
    def start_timer(self):
        try:
            minutes = int(self.time_input.text())
            if minutes <= 0:
                raise ValueError
            
            self.remaining_time = minutes * 60
            self.timer.start(1000)  # 每秒更新
        except ValueError:
            QMessageBox.warning(self, '错误', '请输入有效的时间(正整数)')

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            minutes, seconds = divmod(self.remaining_time, 60)
            self.timer_label.setText(f'{minutes:02d}:{seconds:02d}')
        else:
            self.timer.stop()
            self.timer_label.setText('00:00')
            self.show_notification()

    def pause_timer(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(1000)

    def reset_timer(self):
        self.timer.stop()
        self.remaining_time = 0
        self.timer_label.setText('00:00')
        self.time_input.clear()

    def choose_sound_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 
                                                   '选择音频文件', 
                                                   '', 
                                                   '音频文件 (*.mp3 *.wav *.ogg)')
        if file_name:
            self.sound_file = file_name
            QMessageBox.information(self, '提示', f'已选择音频文件：{file_name}')

    def show_notification(self):
        #QMessageBox.information(self, '时间到', '番茄钟时间已结束！')
        
        # 播放提示音
        if self.sound_file:
            url = QUrl.fromLocalFile(self.sound_file)
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()
        else:
            QApplication.beep()

def main():
    app = QApplication(sys.argv)
    timer = PomodoroTimer()
    timer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
