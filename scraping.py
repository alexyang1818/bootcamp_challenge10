# import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt


def scrape_all():

    # initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True) # headless is set as True so we don't need to see the scraping in action.

    news_title, news_paragraph = mars_news(browser)

    # run all scraping functions and store results in dictionary
    data = {
            'news_title': news_title,
            'news_paragraph': news_paragraph,
            'featured_image': featured_image(browser),
            'facts': mars_facts(),
            'last_modified': dt.datetime.now(),
            'hemispheres':scrape_hemispheres(browser)
    }
    
    # stop webdriver and return data
    browser.quit()
    return data


# # scrape articles

def mars_news(browser):

    # visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # optional delay for loading the page
    # searching for elements with a specific combination of tag (div) and attribute (list_text)
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text') # select_one selects the first one. same as find()

        # use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # news_title

        # use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p


# # scrape images from another website
# 

def featured_image(browser):

    # visit url
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)

    try:
        # find and click the full image button
        full_image_elem = browser.find_by_tag('button')[1]
        full_image_elem.click()


        # parse the resulting html with soup
        html = browser.html
        img_soup = soup(html, 'html.parser')


        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        # img_url_rel


        img_url = url + img_url_rel
        # img_url
        # browser.visit(img_url)

    except AttributeError:
        return None

    return img_url


# # scrape Mars facts

def mars_facts():

    try:
        # use pandas to extract table contents. the url has two tables
        df = pd.read_html('https://galaxyfacts-mars.com')[0]  # create df from the first html table

    except BaseException: # A BaseException is a little bit of a catchall when it comes to error handling, suitable for read_html()
        return None

    # assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    # df.head()


    # df2 = pd.read_html('https://galaxyfacts-mars.com')[1]  # create df from the second html table
    # df2.head()

    # convert dataframe into HTML format, add bootstrap
    return df.to_html()


    # browser.quit()

def scrape_hemispheres(browser):
    # Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    img_soup = soup(html, 'html.parser')
    imgs = img_soup.find_all('div', class_='description')
    for img in imgs:
        title = img.find('a').find('h3').get_text()
        link = url + img.find('a').get('href')
        browser.visit(link)
        full_img_html = browser.html
        full_img_soup = soup(full_img_html, 'html.parser')
        full_img_url = url+full_img_soup.find_all('a', target='_blank')[2].get('href')
        hemisphere_image_urls.append({
            'img_url':full_img_url,
            'title':title
        })

    return hemisphere_image_urls


if __name__ == '__main__':
    # if running as script, print scraped data
    print(scrape_all())

