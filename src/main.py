from PyQt6.QtWidgets import QApplication
from french_stream_dl import FrenchStreamDlWindow
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode
# chrome_options.add_argument("--no-sandbox")  # Prevent crashes in Docker
# Prevent crashes in Docker
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-popup-blocking")
# chrome_options.add_argument("--disable-notifications")
# chrome_options.add_argument("--disable-javascript")

# chrome_options.add_extension("ext/adblocker.crx")

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=chrome_options
)


if __name__ == "__main__":
    app = QApplication([])
    window = FrenchStreamDlWindow(driver)
    window.show()
    app.exec()
