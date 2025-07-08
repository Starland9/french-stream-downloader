from ui.downloader import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt6.QtCore import QThread, pyqtSignal

from models.media import Media
from models.uqvideo import UqVideo
from uqload_dl import UQLoad
from selenium import webdriver
import os
from selenium.webdriver.common.by import By


class UqloadMediasProviderThread(QThread):
    uqvideos_getted = pyqtSignal(list)

    def __init__(self, driver: webdriver, url: str):
        super().__init__()
        self.driver = driver
        self.url = url

    def run(self):
        self.uqvideos_getted.emit(self.get_all_uqvideos())

    def get_all_links_containing_uqload(self):
        self.driver.get(self.url)

        links = self.driver.find_elements(
            "xpath", "//div[contains(@data-url-default, 'uqload')]")
        result = [link.get_attribute("data-url-default") for link in links]

        return result

    @staticmethod
    def get_uqvideo_from_link(link):
        uqload = UQLoad(url=link)
        return UqVideo(dict=uqload.get_video_info(), html_url=link)

    def get_all_uqvideos(self):
        links = self.get_all_links_containing_uqload()
        uqvideos = []
        for link in links:
            try:
                uqvideos.append(self.get_uqvideo_from_link(link))
            except:
                pass
        return uqvideos


class DownloaderThread(QThread):
    current_uqvideo_getted = pyqtSignal(str)
    on_dl_progress = pyqtSignal(int, int)
    on_dl_complete = pyqtSignal()

    def __init__(self, uqvideos: list[UqVideo]):
        super().__init__()
        self.uqvideos = uqvideos
        self.dl_path = os.getcwd() + "/downloads"

        if not os.path.exists(self.dl_path):
            os.mkdir(self.dl_path)

    def run(self):
        for index, video in enumerate(self.uqvideos):
            self.current_uqvideo_getted.emit(
                f"{index + 1}/{len(self.uqvideos)} || {video.title}"
            )
            uqload = UQLoad(
                url=video.html_url,
                on_progress_callback=self.dl_progress,
                output_dir=self.dl_path,
            )
            uqload.download()

        self.on_dl_complete.emit()

    def dl_progress(self, current, total):
        self.on_dl_progress.emit(current, total)


class DownloaderWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, driver, media: Media):
        super().__init__()
        self.uqvideos = None
        self.dlThread = None
        self.setupUi(self)
        self.retranslateUi(self)

        self.mediaTitlelabel.setText(media.title)

        self.statusbar.showMessage("Getting Videos... Please wait")
        self.uqvideos_thread = UqloadMediasProviderThread(driver, media.url)
        self.uqvideos_thread.start()
        self.uqvideos_thread.uqvideos_getted.connect(self.fill_all_uqvideos)
        self.dlButton.clicked.connect(self.download)
        self.dlButton.setEnabled(False)

    def fill_all_uqvideos(self, uqvideos: list[UqVideo]):
        self.uqvideos = uqvideos
        self.statusbar.showMessage("Filling... Please wait")

        self.tableWidget.setRowCount(len(uqvideos))
        for index, uqvideo in enumerate(uqvideos):
            self.tableWidget.setItem(
                index, 0, QTableWidgetItem(str(index + 1)))
            self.tableWidget.setItem(index, 1, QTableWidgetItem(uqvideo.title))
            self.tableWidget.setItem(
                index, 2, QTableWidgetItem(uqvideo.duration))
            self.tableWidget.setItem(
                index, 3, QTableWidgetItem(uqvideo.resolution))
            self.tableWidget.setItem(index, 4, QTableWidgetItem(uqvideo.size))
            self.tableWidget.setItem(index, 5, QTableWidgetItem(uqvideo.type))

        self.statusbar.showMessage("Done")
        self.dlButton.setEnabled(True)

    def download(self):
        self.statusbar.showMessage("Downloading... Please wait")
        self.dlThread = DownloaderThread(self.uqvideos)
        self.dlThread.current_uqvideo_getted.connect(
            self.current_uqvideo_getted)
        self.dlThread.on_dl_progress.connect(self.dl_progress)
        self.dlThread.on_dl_complete.connect(self.download_complete)
        self.dlThread.start()
        self.dlButton.setText("Downloading...")
        self.dlButton.setEnabled(False)

    def current_uqvideo_getted(self, title):
        self.currentFileNameLabel.setText(title)

    def dl_progress(self, current, total):
        self.dlProgresBar.setValue(int(current / total * 100))

    def download_complete(self):
        self.statusbar.showMessage("Done")
        self.dlButton.setText("Download")
        self.dlButton.setEnabled(True)
