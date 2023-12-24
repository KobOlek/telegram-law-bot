import requests
from bs4 import BeautifulSoup

class Parser:
    code_first_part_of_url = "https://i.factor.ua"

    def __init__(self, url):
        self.url = url
        self.__chapters = {"texts": [], "hrefs": []}
        request = requests.get(url)
        self.__html = BeautifulSoup(request.content, "html.parser")

    def get_chapters_titles(self):
        elements = self.__html.findAll("a", {"class": "b-law__list-item-link"})

        self.__chapters = {
            "texts": [element.text for element in elements],
            "hrefs": [element["href"] for element in elements]
        }

        return self.__chapters

    def get_article_content(self, article_number: int, chapter_url: str):
        article_links = self.get_links(chapter_url)
        article_index = self.find_article_index(article_links, article_number)

        request = requests.get(self.code_first_part_of_url + article_links[article_index]["href"])
        html = BeautifulSoup(request.content, "html.parser")

        children = self.get_children(html)

        content = [text.text for text in children]

        return content

    def get_content_from_inclusion_and_conclusion(self, url):
        link = self.get_links(url)[0]

        request = requests.get(self.code_first_part_of_url + link["href"])
        html = BeautifulSoup(request.content, "html.parser")

        children = self.get_children(html)

        content = [text.text for text in children]

        return content

    @staticmethod
    def find_article_index(array: list, article_number) -> int:
        try:
            for i, v in enumerate(array):
                string = array[i].text.split(" ")
                if string[string.index("Стаття") + 1].replace(".", "") == str(article_number):
                    return i
        except ValueError:
            return 0

    @staticmethod
    def get_links(url):
        request = requests.get(url)
        html = BeautifulSoup(request.content, "html.parser")
        links = html.findAll("a", {"class": "b-law__list-item-link"})
        return links

    @staticmethod
    def get_children(html):
        parent = html.find("div", {"class": "legislation_article"})
        children = parent.findAll("p")
        return children
