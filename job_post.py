class JobPost:
    def __init__(self, url: str, company: str, categories: [str], title: str,
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
            f'{self.company} @ {self.published_on}\n'
            f'{self.title}\n'
            f'{self.url}\n'
            f'{self.categories}\n\n'
            f'{self.description}'
        )
