import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(current_dir, "ffmpeg_bin")

ydl_opts = {
    'ffmpeg_location': ffmpeg_path,
}
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QComboBox,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPalette, QColor
from yt_dlp import YoutubeDL


class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.download_folder = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Media Downloader')
        self.setFixedSize(500, 250)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#cc8e33'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Paste URL here...")
        self.download_btn = QPushButton("Download", self)
        self.download_btn.clicked.connect(self.handle_download)

        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.download_btn)

        self.source_dropdown = QComboBox(self)
        self.source_dropdown.addItems(["YouTube", "Facebook", "Instagram", "Other"])

        self.format_dropdown = QComboBox(self)
        self.format_dropdown.addItems(["MP3", "MP4"])

        self.folder_button = QPushButton("Choose Download Folder", self)
        self.folder_button.clicked.connect(self.select_folder)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(url_layout)
        layout.addSpacing(10)
        layout.addWidget(self.source_dropdown)
        layout.addSpacing(10)
        layout.addWidget(self.format_dropdown)
        layout.addStretch()

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.folder_button)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.download_folder = folder

    def handle_download(self):
        url = self.url_input.text()
        file_format = self.format_dropdown.currentText()

        if not url:
            QMessageBox.warning(self, "Missing URL", "Please enter a URL.")
            return

        if not self.download_folder:
            QMessageBox.warning(self, "No Folder", "Please choose a download folder.")
            return

        ydl_opts = {
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'ffmpeg_location': r'C:\Users\abels\Downloads\ffmpeg-7.1.1-essentials_build\bin',
            'quiet': True,
            'noplaylist': True,
        }

        if file_format == "MP3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }],
})
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            QMessageBox.information(self, "Success", "Download completed!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download failed:\n{str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DownloaderApp()
    window.show()
    sys.exit(app.exec_())