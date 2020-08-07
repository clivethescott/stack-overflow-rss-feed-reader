from typing import Sequence


class JobPost:
    def __init__(self, url: str, company: str, categories: Sequence[str], title: str,
                 published_on: str, description: str):
        self.url = url
        self.company = company
        self.categories = categories
        self.title = title
        self.published_on = published_on
        self.description = description

    def contains(self, text: str) -> bool:
        return False if not text else text in self.title or text in self.company

    def __repr__(self):
        return (
            f"""
            {self.company} @ {self.published_on}\n
            {self.title}\n
            {self.url}\n
            {self.categories}\n
            {self.description}
            """
        )
