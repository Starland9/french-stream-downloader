from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from models.media import Media
import requests
from io import BytesIO
from ui.media_widget import Ui_Form
from downloader import DownloaderWindow


class MediaWidget(QWidget, Ui_Form):
    def __init__(self, driver, media: Media):
        super().__init__()
        self.setupUi(self)
        self.media = media
        self.driver = driver

        response = requests.get(media.image_url)
        image_data = BytesIO(response.content)

        pixmap = QPixmap()
        pixmap.loadFromData(image_data.read())

        self.imageLabel.setPixmap(pixmap)
        self.titleLabel.setText(media.title)

        self.dlButton.clicked.connect(self.download)

    def download(self):
        print(f"Download {self.media.url}")
        self.downloader = DownloaderWindow(self.driver, self.media)
        self.downloader.show()
