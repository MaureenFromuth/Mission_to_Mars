# Import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
import sys

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_image(browser) 
    }
    # Stop webdriver and return data
    sys.setrecursionlimit(2000)
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()
    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    try:
        # find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None
    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    return img_url

def mars_facts():
    try:
      # use 'read_html" to scrape the facts table into a dataframe
      df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
      return None
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemisphere_image(browser):
    sys.setrecursionlimit(2000)
    # Visit the URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    # Set the a variable called 'html' and run a parser against the variable
    html = browser.html
    hemi_image_soup = soup(html, 'html.parser')
    # Create a variable that provides the first part of the hemisphere website 
    base_url ="https://astrogeology.usgs.gov"
    # Create a list to hold the images and titles.
    hemisphere_image_urls = []
    # Find all of the 'div' elements that have 'item' as a class
    hemi_images = hemi_image_soup.find_all("div", class_='item')
    for h in hemi_images:
        # Create a dictionary for responses
        hemispheres = {}
        
        # Find the links that get us to the hemisphere page
        href = h.find('a', class_='itemLink product-item')    
        link = base_url + href['href']
        browser.visit(link)
        
        # Repeate the original step to access the html of the new website
        hemi_site_html = browser.html
        hemi_site_soup = soup(hemi_site_html, 'html.parser')
        
        # Identify the title of the image by searching out the h2 title and removing the text
        img_title = hemi_site_soup.find('div', class_='content').find('h2', class_='title').text
        
        #Assign the 'image_title' variable to the 'title' key in the 'hemisphere' dictionary
        hemispheres['title'] = img_title
        
        # Identify the url of the image by searching out the downloads class and removing the href
        img_url = hemi_site_soup.find('div', class_='downloads').find('a')['href']
    
        #Assign the 'image_url' variable to the 'url_img' key in the 'hemisphere' dictionary
        hemispheres['url_img'] = img_url
        
        # Append dictionary to list
        hemisphere_image_urls.append(hemispheres)
        
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())



