from PyQt6.QtWidgets import QApplication, QMainWindow
from ui.main_window import Ui_MainWindow
from selenium import webdriver
import os
from models.media import Media
from PyQt6.QtCore import QThread, pyqtSignal
from media_ui import MediaWidget


class SearchThread(QThread):
    searchCompleted = pyqtSignal(list)

    def __init__(self, driver: webdriver, text: str):
        super().__init__()
        self.driver = driver
        self.text = text

    def run(self):
        self.driver.get("https://fsmirror7.lol/")
        search_field = self.driver.find_element("xpath", "//input[@id='story']")
        search_field.send_keys(self.text)
        search_field.submit()
        self.fill_all_medias()

    def fill_all_medias(self):
        series = self.driver.find_elements(
            "xpath", "//div[contains(@class, 'short serie')]"
        )
        films = self.driver.find_elements(
            "xpath", "//div[contains(@class, 'short film')]"
        )

        all_max_10 = series + films
        if len(all_max_10) > 10:
            all_max_10 = all_max_10[:10]

        return self.searchCompleted.emit(
            [Media.from_web_element(sf) for sf in all_max_10]
        )


class FrenchStreamDlWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, driver: webdriver):
        super().__init__()
        self.setupUi(self)  # (12,4)-(44,57)
        self.retranslateUi(self)
        self.init_driver(driver)  # init_driver
        self.connect_actions()  # connect_actions

        self.search_thread = None

    def init_driver(self, driver: webdriver):
        self.driver = driver

    def connect_actions(self):
        self.search_toolButton.clicked.connect(self.do_web_search)

    def do_web_search(self):
        self.search_toolButton.setEnabled(False)
        self.search_toolButton.setText("Searching...")
        self.search_thread = SearchThread(self.driver, self.titleLineEdit.text())
        self.search_thread.searchCompleted.connect(self.fill_all_medias)
        self.search_thread.start()

    def fill_all_medias(self, medias: list[Media]):
        self.clear_all_medias()
        self.search_toolButton.setEnabled(True)
        self.search_toolButton.setText("Search")

        for media in medias:
            media_widget = MediaWidget(self.driver, media)
            self.verticalLayout.addWidget(media_widget)

    def clear_all_medias(self):
        for i in reversed(range(self.verticalLayout.count())):
            self.verticalLayout.itemAt(i).widget().deleteLater()
