from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time


chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode
# chrome_options.add_argument("--no-sandbox")  # Prevent crashes in Docker
# chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes in Docker

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=chrome_options
)

if __name__ == "__main__":
    driver.get("https://vww.papadustream.tv/episode/victorious-1x6")
    btn_link = driver.find_element("xpath", "//a[contains(@class, 'thumb')]")
    btn_link.click()
    time.sleep(1)
    # find 'li' with child 'span' with text 'uqload'
    uqload_li = driver.find_element(
        "xpath",
        "//li[contains(@onclick, 'showVideo')]/span[contains(text(), 'uqload')]",
    )
    uqload_li.click()
