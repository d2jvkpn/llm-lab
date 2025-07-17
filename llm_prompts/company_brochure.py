#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

class Website:
    """
    A utility class to represent a website that we have scraped
    """

    url: str
    title: str
    text: str

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        self.title = soup.title.string if soup.title else "No title found"
        for e in soup.body([
            "script", "style", "img", "input",
            "iframe", "meta", "noscript", "button",
        ]):
            e.decompose()

        self.text = soup.body.get_text(separator="\n", strip=True)

    def get_contents(self):
        return f"Webpage title:\n{self.title}\n\nWebpage Contents:\n{self.text}\n"


def prompt(url):
    website = Website(url.strip())

    prompt = "Please generate a company brochure. Here is their landing page:\n{}".format(
        website.get_contents(),
    )

    return prompt
