import datetime
import os
import re

import requests
import yagmail
from bs4 import BeautifulSoup

duplicate_line_breaks_pattern = r'(?:<br\s*?(?:>|/>)){2,}'
duplicate_line_regex = re.compile(duplicate_line_breaks_pattern)


def sanitize(text):
    if not text:
        return ''
    return duplicate_line_regex.sub('<br/>', text)


class JobPost:

    def __init__(self, item):
        self.url = item.link.text
        self.company = item.find('a10:name').text
        categories = [c.string for c in item.find_all('category')]
        self.categories = ', '.join(categories)
        self.title = item.title.text
        self.published_on = item.pubDate.text
        self.description = sanitize(item.description.text)

    def containsText(self, text):
        return text in self.title or text in self.company

    def __repr__(self):
        return (
            f'\n\n----------------------------------------------------------------------\n\n'
            f'{self.company} @ {self.published_on}\n'
            f'{self.title}\n'
            f'{self.url}\n'
            f'{self.categories}\n\n'
            f'{self.description}'
        )


def send_email(job_posts):

    if not job_posts:
        print('No job posts could be found')
        return

    print(f'Sending email for {len(job_posts)} jobs')

    subject = 'Stack Overflow Job Posts for today'
    pwd = os.environ.get('YAGMAIL_PASSWORD')
    sender = 'clivethescott@gmail.com'
    with yagmail.SMTP(sender, pwd) as yag:
        yag.send(subject=subject, contents=job_posts)


def download_jobs():
    technologies = [
        'spring',
        'spring boot',
        'java',
    ]
    offers_visa_sponsorship = 'true'
    offers_relocation = 'true'
    url_encoded_technologies = '+'.join(technologies)
    jobs_url = f'https://stackoverflow.com/jobs/feed?t={offers_relocation}&v={offers_visa_sponsorship}&tl={url_encoded_technologies}'
    print('Downloading jobs from', jobs_url)
    return requests.get(jobs_url).text


def use_local_jobs():
    print('Using local jobs...')
    local_jobs_file = os.path.expandvars(
        '$HOME/Downloads/stack_overflow_feed.xml')
    with open(local_jobs_file) as f:
        return f.read()


date_format = '%a, %d %b %Y %H:%M:%S %z'
today = datetime.date.today()


def is_todays_job_post(data):

    date_str = data.pubDate.text
    post_date = datetime.datetime.strptime(date_str, date_format)
    return today == post_date.date()


filtered_content = [
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


def is_wanted_post(post):
    for tag in filtered_content:
        if post.containsText(tag):
            return False
    return True


def parse_job_posts(content):
    soup = BeautifulSoup(content, 'xml')
    for item in soup.find_all('item'):
        if is_todays_job_post(item):
            yield JobPost(item)


def get_wanted_job_posts(posts):
    for post in posts:
        if is_wanted_post(post):
            yield str(post)


def get_job_posts(content):
    job_posts = parse_job_posts(content)
    return get_wanted_job_posts(job_posts)


content = download_jobs()
wanted_job_posts = list(get_job_posts(content))
send_email(wanted_job_posts)
# print(wanted_job_posts)
