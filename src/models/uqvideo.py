from typing import Dict


class UqVideo:
    def __init__(self, dict: Dict, html_url: str):
        self.duration = dict.get("duration")
        self.image_url = dict.get("image_url")
        self.resolution = dict.get("resolution")
        self.size = (dict.get("size") / 1024 / 1024).__round__(2).__str__() + " MB"
        self.title = dict.get("title")
        self.type = dict.get("type")
        self.url = dict.get("url")
        self.html_url = html_url

    def __repr__(self):
        return f"UqVideo(title={self.title}, url={self.url})"
