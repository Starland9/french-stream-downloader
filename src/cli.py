from uqload_dl import UQLoad
import time


def get_all_links_from_file(file_path: str) -> list[str]:
    with open(file_path, "r") as f:
        return f.readlines()


def on_progress(current, total):
    print(f"{current}/{total}")


if __name__ == "__main__":
    links = get_all_links_from_file("src/links.txt")

    for link in links:
        print(f"Downloading {link}")
        link = link.strip()
        uqload = UQLoad(link, output_dir="output", on_progress_callback=on_progress)
        uqload.download()
        time.sleep(1)

    print("Done")
