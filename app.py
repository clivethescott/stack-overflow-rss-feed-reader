import datetime
import os
import re
import webbrowser

import requests
import yagmail
from bs4 import BeautifulSoup
from langdetect import detect

from job_post import JobPost

TECHNOLOGIES = '+'.join([
    'spring+boot',
    'java',
])
OFFERS_VISA_SPONSORSHIP = 'true'
OFFERS_RELOCATION = 'true'
JOBS_URL = f'https://stackoverflow.com/jobs/feed?t={OFFERS_RELOCATION}&v={OFFERS_VISA_SPONSORSHIP}&tl={TECHNOLOGIES}'

EXCLUDED = [
    'India',
    'Japan',
    'China',
    'Intern',
    'France',
    'Switzerland',
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

DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'
DUPLICATE_LINE_BREAKS_PATTERN = r'(?:<br\s*?(?:>|/>)){2,}'
DUPLICATE_LINE_REGEX = re.compile(DUPLICATE_LINE_BREAKS_PATTERN)


def remove_duplicate_line_breaks(text: str):
    """ Removes duplicate line breaks i.e </br>'s """
    if not text:
        return ''
    return DUPLICATE_LINE_REGEX.sub('<br/>', text)


def email(job_posts: [JobPost]):
    print(f'Sending email for {len(job_posts)} jobs')

    subject = 'Stack Overflow Job Posts for today'
    sender = 'clivethescott@gmail.com'
    with yagmail.SMTP(sender) as yag:
        yag.send(subject=subject, contents=job_posts)


def open_in_browser(url: str):
    webbrowser.open_new_tab(url)


def view(job_posts: [JobPost]):
    if len(job_posts) > 10:
        print('Got more than 10 jobs')
        print(job_posts)
    for post in job_posts:
        open_in_browser(post.url)


def notify(job_posts: [JobPost]):
    if not job_posts:
        print('No job posts could be found')
        return
    view(job_posts)


def is_todays_job_post(data):
    date_str = data.pubDate.text.replace('Z', 'UTC')
    post_date = datetime.datetime.strptime(date_str, DATE_FORMAT)
    today = datetime.date.today()
    return today == post_date.date()


def is_english(text):
    return detect(text[:50]) == 'en'


def include_post(post):
    for tag in EXCLUDED:
        if post.contains(tag):
            return False
    return is_english(post.description)


def create_job_post(item) -> JobPost:
    url = item.link.text
    company = item.find('a10:name').text
    categories = ', '.join(
        category.string for category in item.find_all('category'))
    title = item.title.text
    published_on = item.pubDate.text
    description = remove_duplicate_line_breaks(item.description.text)

    return JobPost(url, company, categories, title, published_on, description)


def parse_job_posts(content):
    soup = BeautifulSoup(content, 'xml')
    for item in soup.find_all('item'):
        if is_todays_job_post(item):
            job_post = create_job_post(item)
            yield job_post


def matching_jobs(content) -> [JobPost]:
    return (post for post in parse_job_posts(content) if include_post(post))


def download_jobs():
    print('Downloading jobs from', JOBS_URL)
    return requests.get(JOBS_URL).content


all_jobs = download_jobs()
matches = list(matching_jobs(all_jobs))
notify(matches)
