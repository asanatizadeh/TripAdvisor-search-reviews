import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

chrome_driver_path = 'chrome driver path'


def get_title(element):
    try:
        return element.find_element_by_class_name('postTitle').text
    except NoSuchElementException:
        return None


def get_text(element):
    try:
        return element.find_element_by_class_name('postBody').text
    except NoSuchElementException:
        return None


def get_date(element):
    try:
        return element.find_element_by_class_name('postDate').text
    except NoSuchElementException:
        return None


def get_author(element):
    try:
        return element.find_element_by_class_name('username').text
    except NoSuchElementException:
        return None


def get_author_profile(element):
    try:
        return element.find_element_by_class_name('username').find_element_by_tag_name('a').get_attribute('href')
    except NoSuchElementException:
        return None


def get_post_count(element):
    try:
        return element.find_element_by_class_name('postBadge').text
    except NoSuchElementException:
        return None


def get_review_count(element):
    try:
        return element.find_element_by_class_name('reviewerBadge').text
    except NoSuchElementException:
        return None


def get_helpful_count(element):
    try:
        return element.find_element_by_class_name('helpfulVotesBadge').text
    except NoSuchElementException:
        return None


if __name__ == '__main__':

    driver = webdriver.Chrome(chrome_driver_path)
    driver.get("https://www.tripadvisor.com/SearchForums?q=review+bribe&x=22&y=11&pid=34633&s=+")

    # collect all the links  to all the forum posts
    item_links = []
    error = False
    while error is False:
        table_cells = driver.find_elements_by_tag_name('td')
        current_page = table_cells[-1].find_element_by_tag_name('b').text
        table = driver.find_element_by_class_name('forumsearchresults')
        rows = table.find_elements_by_class_name('topofgroup')
        print(f'found {len(rows)} links on page {current_page}')
        for i in rows:
            item_links.append(i.find_element_by_tag_name('a').get_attribute('href'))

        try:
            next_button = table_cells[-1].find_element_by_xpath("//*[contains(text(), 'Next')]")
            next_button.click()
            time.sleep(1)

        except NoSuchElementException:
            print('No further page to scrape.')
            error = True
    
    pd.DataFrame(item_links, columns=['review_threat_link']).to_csv('Review Bribe Links.csv', index=False)
    # iterate over the links and collect the text of the review threats
    with open('bribes.csv', newline='', mode='a') as csvfile:
        link_reader = csv.writer(csvfile, delimiter='|', quotechar='"')
        header = ['post_title', 'post_text', 'post_date', 'author',
                  'user_profile', 'user_posts', 'user_reviews', 'helpful_votes',
                  'url']
        link_reader.writerow(header)
        for item_link in item_links:
            driver.get(item_link)

            # locate the main post and collect all the information.
            review_box = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME,
                                                                                         "firstPostBox")))
            print(f'Review {item_links.index(item_link)}: {item_link}')
            row = [
                get_title(review_box),  # post_title
                get_text(review_box),  # post_text
                get_date(review_box),  # post_date
                get_author(review_box),  # author
                get_author_profile(review_box),  # user_profile
                get_post_count(review_box),  # user_posts
                get_review_count(review_box),  # user_reviews
                get_helpful_count(review_box),  # helpful_votes
                item_link,  # direct url
                ]

            link_reader.writerow(row)

    driver.close()


df = pd.read_csv('threats.csv', delimiter= '|')
df1 = pd.read_csv('bribes.csv', delimiter= '|')

data = pd.concat((df, df1), axis= 0)
data.sort_values('url', inplace=True)

data2 = data.drop_duplicates()

data2.to_csv('Reviews_threat_bribe_TA.csv')
