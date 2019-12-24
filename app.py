import datetime
import os

import requests
import yagmail
from bs4 import BeautifulSoup


class JobPost:

    def __init__(self, item):
        self.url = item.link.text
        self.company = item.find('a10:name').text
        categories = [c.string for c in item.find_all('category')]
        self.categories = ', '.join(categories)
        self.title = item.title.text
        self.published_on = item.pubDate.text
        self.description = item.description.text

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

    print(f'Sending email for {len(job_posts)} jobs')

    if not job_posts:
        print('No job posts could be found')
        return
    yag = yagmail.SMTP()
    subject = 'Stack Overflow Job Posts for today'
    yag.send(subject=subject, contents=job_posts)


def download_jobs():
    keywords = [
        'spring',
        'java',
        'python',
    ]
    keywords_in_url = '+'.join(keywords)
    jobs_url = f'https://stackoverflow.com/jobs/feed?tl={keywords_in_url}'
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


content = download_jobs()
soup = BeautifulSoup(content, 'xml')
job_posts = [str(JobPost(data))
             for data in soup.find_all('item') if is_todays_job_post(data)]
# send_email(job_posts)
print(job_posts)
