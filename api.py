
import uvicorn
from fastapi import FastAPI, Body, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from selenium import webdriver
import urllib.parse
from src.models.media import Media
from src.models.uqvideo import UqVideo
from uqload_dl import UQLoad
import os
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


# --- Constants ---
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")

# --- Selenium WebDriver Setup ---
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=chrome_options
)


# --- FastAPI App ---
app = FastAPI(
    title="French-Stream API",
    description="An API to search, get video links, and download from French-Stream.",
    version="1.0.0",
)

# --- Helper Functions ---


def search_media(text: str) -> list[Media]:
    """
    Searches for media on french-streaming.tv and returns a list of Media objects.
    """
    uri = urllib.parse.quote(text)
    driver.get(f"https://www.french-streaming.tv/search/{uri}")

    series = driver.find_elements(
        "xpath", "//div[contains(@class, 'short serie')]"
    )
    films = driver.find_elements(
        "xpath", "//div[contains(@class, 'short-in nl')]"
    )

    all_results = series + films
    if len(all_results) > 10:
        all_results = all_results[:10]

    return [Media.from_web_element(sf) for sf in all_results]


async def get_uqvideos_from_media_url(url: str) -> list[UqVideo]:
    """
    Gets all UqVideo objects from a media page URL.
    """
    driver.get(url)
    try:
        uqloadButton = driver.find_element(
            "xpath", "//a[contains(@data-href, 'uqload') and contains(@id, 'singh1')]"
        )
        uqloadButton.click()
        video_links_elements = driver.find_elements(
            "xpath", "//a[contains(@data-href, 'uqload')]"
        )
        links = [link.get_attribute("data-href")
                 for link in video_links_elements]
    except Exception:
        links_elements = driver.find_elements(
            "xpath", "//div[contains(@data-url-default, 'uqload')]"
        )
        links = [link.get_attribute("data-url-default")
                 for link in links_elements]

    uqvideos = []
    for link in links:
        try:
            uqload = UQLoad(url=link)
            # Run the blocking, problematic function in a separate thread
            video_info = await run_in_threadpool(uqload.get_video_info)
            uqvideos.append(UqVideo(dict=video_info, html_url=link))
        except Exception as e:
            print(f"Error getting video info for {link}: {e}")
            pass
    return uqvideos


async def download_video_in_background(video_url: str):
    """
    Downloads a video from a UQload URL in the background.
    """
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    try:
        uqload = UQLoad(url=video_url, output_dir=DOWNLOADS_DIR)
        # Run the blocking download call in a thread pool as well
        await run_in_threadpool(uqload.download)
        print(f"Finished downloading {video_url}")
    except Exception as e:
        print(f"Error downloading {video_url}: {e}")


# --- API Endpoints ---

@app.get("/search", summary="Search for media")
async def search(query: str):
    """
    Searches for movies and series on French-Stream.

    - **query**: The search term (e.g., "The Matrix", "La Casa de Papel").
    """
    # This is CPU-bound by Selenium, could also be run in a threadpool
    # but let's keep it simple for now.
    search_results = await run_in_threadpool(search_media, query)
    return {"results": [media.to_dict() for media in search_results]}


@app.post("/get-videos", summary="Get video links from a media URL")
async def get_videos(media_url: str = Body(..., embed=True, description="The URL of the media page from a search result.")):
    """
    Takes a media page URL and scrapes it to find direct UQload video links.
    """
    video_results = await get_uqvideos_from_media_url(media_url)
    return {"results": [video.to_dict() for video in video_results]}


@app.post("/download", summary="Download a video in the background")
async def download(background_tasks: BackgroundTasks, video_url: str = Body(..., embed=True, description="The UQload page URL of the video to download.")):
    """
    Starts a background task to download a video from its UQload URL.
    The video will be saved in the `downloads` directory on the server.
    """
    background_tasks.add_task(download_video_in_background, video_url)
    return {"message": "Download started in background.", "video_url": video_url}

# --- Lifecycle Events ---


@app.on_event("startup")
def startup_event():
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)


@app.on_event("shutdown")
def shutdown_event():
    driver.quit()


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
