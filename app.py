import datetime
import os
import re

import requests
import yagmail
from bs4 import BeautifulSoup

duplicate_line_breaks_pattern = r'(?:<br\s*?(?:>|/>)){2,}'


def sanitize(text):
    if not text:
        return ''
    return re.sub(duplicate_line_breaks_pattern, '<br/>', text)


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
    pwd = os.path.expandvars('$YAGMAIL_PASSWORD')
    sender = 'clivethescott@gmail.com'
    with yagmail.SMTP(sender, pwd) as yag:
        yag.send(subject=subject, contents=job_posts)


def download_jobs():
    technologies = [
        'spring',
        'java',
        'python',
    ]
    offers_visa_sponsorship = 'true'
    offers_relocation = 'true'
    technologies_in_url = '+'.join(technologies)
    jobs_url = f'https://stackoverflow.com/jobs/feed?t={offers_relocation}&v={offers_visa_sponsorship}&tl={technologies_in_url}'
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


content = download_jobs()
soup = BeautifulSoup(content, 'xml')
job_posts = [JobPost(data)
             for data in soup.find_all('item') if is_todays_job_post(data)]
print(f'Found {len(job_posts)} jobs for today')
wanted_job_posts = [str(post) for post in (filter(is_wanted_post, job_posts))]
print(f'Actual wanted jobs = {len(wanted_job_posts)}')
send_email(wanted_job_posts)
# print(wanted_job_posts)
