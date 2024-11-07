from uqload_dl import UQLoad
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
import time
from progress1bar import ProgressBar
import os


def get_all_links_containing_uqload(driver):
    links = driver.find_elements("xpath", "//a[contains(@href, 'uqload')]")
    return [link.get_attribute("href") for link in links]


def on_progress(current, total):
    os.system("clear")
    print(f"Downloaded {current / 1024 / 1024} of {total / 1024 / 1024} MB")
    time.sleep(1)
    if current == total:
        print("Download complete")


def uqload_dl(url):
    uqload = UQLoad(url=url, on_progress_callback=on_progress, output_dir="output")
    uqload.download()  #
    uqload.get_video_info()


if __name__ == "__main__":
    driver.get(
        "https://fsmirror7.lol/s-tv/167126-icarly-saison-1-streaming-complet-vf-vostfr.html"
    )
    links = get_all_links_containing_uqload(driver)
    print("We have {} links".format(len(links)))
    with ProgressBar(total=len(links)) as progress_bar:
        for link in links:
            print(f"Downloading {link}")
            uqload_dl(link)
            print(f"Downloaded {link}")

    driver.quit()
