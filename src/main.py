from uqload_dl import UQLoad
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # Prevent crashes in Docker
chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes in Docker

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=chrome_options
)


from french_stream_dl import FrenchStreamDlWindow
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication([])
    window = FrenchStreamDlWindow(driver)
    window.show()
    app.exec()
