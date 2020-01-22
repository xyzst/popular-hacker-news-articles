"""
Hacker News (HN) Scraper

A simple utility function which retrieves the most popular hacker news articles as determined by story votes.

A story is considered popular if it has greater than or equal to 100 votes.

__author__ = "Darren Rambaud"
__email__ = "xyzst@users.noreply.github.com"
"""
import pprint
import sys

import requests
from bs4 import BeautifulSoup


def retrieve_story_elements(pages=1):
    """
    Based upon the number of pages to scrape from HN, will scrape HN's HTML data and return the desirable elements (story,
    href, and story subtext).

    Default number of pages to scrape is 1.

    :param pages: The number of pages to scrap on HN
    :return: A tuple containing two elements. In the first index, will contain the story's title and href. In the second
    index, will contain the story's subtext (which contains the number of votes at the time of scraping).
    """
    if pages <= 0:
        return [], []

    page_html = []
    for page in range(0, pages):
        response = requests.get('https://news.ycombinator.com/news?p=%s' % (page + 1))
        page_html.append(BeautifulSoup(response.text, 'html.parser'))

    front_page_links = [item for sublist in list(map(lambda x: x.select('.storylink'), page_html)) for item in sublist]
    story_subtext = [item for sublist in list(map(lambda x: x.select('.subtext'), page_html)) for item in sublist]

    return front_page_links, story_subtext


def parse_hacker_news_html(links, votes):
    """
    Given lists of HTML elements, will transform each element into a dictionary containing the title, href, and number of
    up votes. Ignores stories that do not have an associated score class.

    :param links: A list of storylink HTML elements
    :param votes: A list of subtext HTML elements
    :return: A list of dictionary objects
    """
    stories = []
    for index, link in enumerate(links):
        title = links[index].getText()
        href = links[index].get('href', None)
        v = votes[index].select('.score')
        if v:
            vote = int(votes[index].select('.score')[0].getText().replace(' points', ''))
            stories.append({
                'title': title,
                'href': href,
                'votes': vote
            })

    return stories


def filter_more_than_hundred(stories):
    return list(filter(lambda x: (x['votes'] is not None) and (x['votes'] >= 100), stories))


def sort_by_highest(stories):
    return sorted(stories, key=lambda x: x['votes'], reverse=True)


if __name__ == '__main__':
    pages_not_specified = len(sys.argv) < 2
    if pages_not_specified:
        print('[INFO] Usage: \'python popular_hacker_news_stories int\'')
        print('[WARN] Number of pages to crawl has not been specified. Will use the default configuration (1)')

    e = retrieve_story_elements() if pages_not_specified else retrieve_story_elements(int(sys.argv[1]))
    s = sort_by_highest(filter_more_than_hundred(parse_hacker_news_html(e[0], e[1])))
    pprint.pprint(s)
    print(f'{len(s)} popular stories')
