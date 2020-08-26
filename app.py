import os
import webbrowser
import feedparser  # type: ignore
from datetime import datetime, date
from typing import List
from langdetect import detect  # type: ignore

from dateutil.parser import parse as parse_date
from dateutil.tz import tzlocal

EXCLUDED = [
    'India',
    'China',
    'France',
    'Deutschland',
    'Italy',
    'Austria',
    'Android',
    'iOS',
    'Big Data',
    'Cloud Engineer',
    'Cloud Native',
    'Cloud Infrastructure',
    'Apache Spark',
    'Site Reliability',
    'Machine Learning',
    'PhD',
]

TECHNOLOGIES = '+'.join([
    'spring+boot',
    'java',
])
OFFERS_VISA_SPONSORSHIP = 'true'
OFFERS_RELOCATION = 'true'
JOBS_URL = f'https://stackoverflow.com/jobs/feed?t={OFFERS_RELOCATION}&v={OFFERS_VISA_SPONSORSHIP}&tl={TECHNOLOGIES}'
DATE_FORMAT = ''
HTML_HEADER = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width" />
        <title>Job Posts</title>
    </head>
    <body>
"""
HTML_FOOTER = """
    </body>
</html>
"""
OUTPUT_FILE = 'output.html'

time_zone = tzlocal()
today = date.today()


class JobPost:
    """Represent a single job post"""

    def __init__(self, link: str, tags: List[str], title: str, summary: str, location: str, updated: datetime):
        self.link = link
        self.tags = tags
        self.title = title
        self.summary = summary
        self.location = location
        self.updated = updated

    def contains(self, text: str) -> bool:
        return text in self.title or text in self.summary or text in self.location

    def __str__(self):
        return self.title

    def render_html(self):
        return f"""
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
         -> <p>{self.title}</p>
            <p>{self.location}</p>
            <p>{self.updated}</p>
            <a href="{self.link}">{self.link}</a>
            <p>{', '.join(self.tags)}</p>
            <p>{self.summary}</p>
        """


def non_english(text: str) -> bool:
    return detect(text[:30]) != 'en'


def to_job_post(entry) -> JobPost:
    link = entry['link']
    tags = [tag['term'] for tag in entry['tags']]
    title = entry['title'].strip()
    summary = entry['summary'].strip()
    location = entry['location'].strip()
    updated = parse_date(entry['updated']).astimezone(time_zone)
    return JobPost(link, tags, title, summary, location, updated)


def include_post(post: JobPost) -> bool:
    if post.updated.date() != today or non_english(post.summary):
        return False
    for tag in EXCLUDED:
        if post.contains(tag):
            return False
    return True


def write_output(posts: List[JobPost]) -> None:
    content = '\n'.join(post.render_html() for post in posts if include_post(post))
    with open(OUTPUT_FILE, mode='wt') as f:
        f.write(HTML_HEADER)
        f.write(content)
        f.write(HTML_FOOTER)
    webbrowser.open_new_tab('file://{}'.format(os.path.realpath(OUTPUT_FILE)))


def main() -> None:
    data = feedparser.parse(JOBS_URL)
    entries = data['entries']
    posts = [to_job_post(entry) for entry in entries]
    write_output(posts)


if __name__ == "__main__":
    main()
