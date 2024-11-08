class Media:
    def __init__(self, title: str, url: str, image_url: str = None):
        self.title = title
        self.url = url
        self.image_url = image_url

    staticmethod

    def from_web_element(element):
        title = element.find_element(
            "xpath", ".//div[contains(@class, 'short-title')]"
        ).text
        url = element.find_element(
            "xpath", ".//a[contains(@class, 'short-poster img-box with-mask')]"
        ).get_attribute("href")
        image_url = element.find_element("xpath", ".//img").get_attribute("src")
        return Media(title, url, image_url)

    def __str__(self):
        return {
            "title": self.title,
            "url": self.url,
            "image_url": self.image_url,
        }.__str__()
