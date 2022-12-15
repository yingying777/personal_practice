from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import datetime
from random import randint
from time import sleep
import json
import pandas as pd

homepage = "https://www.redfin.com"
cookie = 'CTK=1erdpj5ra30a3000; indeed_rcc=CTK; _ga=GA1.2.318062999.1665767093; RF="wKGgxUwMHWV1aKM-FTjqiMrjRY8zAroFxocW7SGr9uJASaKa98Jda29TEymDVLcsmEvuK92ca2Dtd5yKNhNcUKG0t6uFyyEKsykPXWNo6I27EaFd4OICD2Bt_Jpgg56XgFvTKtAsucnXD-_j2MlK5Q=="; g_state={"i_l":0}; _gcl_au=1.1.1819277427.1667954667; LOCALE=en; __ssid=f51a95d14a8f1b503272170e69f447a; SOCK="8Jwf6vLmIBNR6GZm3TFUl4fMS9k="; SHOE="op4sqNxfm0CK7bj4F1LJgve3XvO5ylcaidARMwW_TOmV0vyWn6Qki_Y9Gltrmt8fura-DG5GXTwfZteJbFWoKrSb8oD94Hrugx55YGEp0SPzKBmYlMmv-buLJvFGm-MxyE33l_WYczZmkQKP4OWz7wsz"; _cfuvid=KH03VzeydOoPGXgctT8J9y1_xM0e8l00fexeAcZ7Ps4-1670957260730-0-604800000; CSRF=ENKG4ujAV3V6iRCQbsXyUm4C9eV5iyLi; _gid=GA1.2.628011567.1670957263; SHARED_INDEED_CSRF_TOKEN=l6YEvSYrXf5v3UQwcUJXklZDOAE6hc5P; MICRO_CONTENT_CSRF_TOKEN=0Jzs7QpLWeTZAzc1kKbGcYmbBDRUDBLu; LC="co=US"; PPID=eyJraWQiOiJhZjA5OGY5Yi0xYTM0LTRhZjgtYjhkOS04MTVjNDhiZGQ4YjIiLCJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJzdWIiOiI0ZDllMDhiMTM5ODNlZmM4IiwiYXVkIjoiYzFhYjhmMDRmIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF1dGgiOiJnb29nbGUiLCJjcmVhdGVkIjoxNjY3OTU1MDA1MDAwLCJyZW1fbWUiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9zZWN1cmUuaW5kZWVkLmNvbSIsImV4cCI6MTY3MDk4MDIwNCwiaWF0IjoxNjcwOTc4NDA0LCJsb2dfdHMiOjE2Njc5NTUwMDc2MDIsImVtYWlsIjoieWluZ3lpbmd0YW5nNzc3QGdtYWlsLmNvbSJ9.SwSt1swPlBLO7IsSPsy1NMe4WFF-Bq_5kLHJx5I5mzxYb6IQLFdIzr43CexUXRtiC7Fdkdg5liOXHiNHrHGLzQ; __cf_bm=bXFWIOMo58AGlPWUpbqMhDt43eEXoRzZyU_auQyEpY0-1670978405-0-ASWGTJiuAoVcYLXS2EMjy0mNe4540DgTlXuMSmHQEZ/4H+GljqL26qDVGZAujejIQg8k5lSpMeRCTw3jdnwWBCw=; _gat=1; _gali=sj_e013eca3e0417b99'
useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
zipcode = ['95124','95118','95123']

def get_soup(url):
    """
    This function get the beautifulsoup object of a webpage.

    Args:
        url (str): the link string of webpage

    Returns:
        soup (obj): beautifulsoup object
    """
    request = Request(url, headers={'User-Agent': 'Resistance is futile',
                                    'cookie': cookie,
                                    'user-agent': useragent})
    response = urlopen(request)
    return BeautifulSoup(response, "html.parser")

def get_links(url):
    """
    This function gets the links of the houses on the houselist page.

    Args:
        url (str): link to houselist page

    Returns:
        house_page_links (list): list of links to the webpages of the houses
    """
    try:
        house_page_links = []

        soup = get_soup(url)  # Get the raw data from page that contains lists of houses in current zipcode
          
        pages = soup.select('span.pageText')[0].get_text()[-1]  # Find out how many pages does it have
        pages = int(pages)
        
        for page in range(1, pages+1):

            if page > 1:
                url = url + '/page-' + str(page)
                soup = get_soup(url)  # Get the raw data from 2nd+ page that contains lists of houses in current zipcode

            rawdata = soup.select('a.slider-item')
            for rd in rawdata:
                subpage = rd.get("href")
                house_page_links.append(subpage)
        return house_page_links
    except Exception as e:
        print("Exception: get_house_links_from_page {}".format(e))

def get_detail_info(url):
    """
    This function get all the useful info from the job webpage.

    Args:
        url (str): link to house webpage

    Returns:
        data (dict): dictionary with keywords: 
                     time_stamp, price, beds, baths, area, address, original_link
    """

    try:
        soup = get_soup(url)
        address = soup.select('div.street-address')[0].getText() + soup.select('div.dp-subtext')[0].getText()
        rawdata = soup.select('div.home-main-stats-variant')[0]
        if rawdata:
            price = rawdata.find('div', {"data-rf-test-id": "abp-price"}).find('div', class_='statsValue').getText()
            beds = rawdata.find('div', {"data-rf-test-id": "abp-beds"}).find('div', class_='statsValue').getText()
            baths = rawdata.find('div', {"data-rf-test-id": "abp-baths"}).find('div', class_='statsValue').getText()
            area = rawdata.find('div', {"data-rf-test-id": "abp-sqFt"}).find('span', class_='statsValue').getText() + " sqft"
            
            data = {}

            data["time_stamp"] = now() 
            data["price"] = price
            data["beds"] = beds
            data["baths"] = baths
            data["area"] = area
            data["address"] = address
            data["original_link"] = url
            print(json.dumps(data, sort_keys=True, indent=4))
            return data
    except Exception as e:
        print("Exception: get_detail_info {}".format(e))

    
def now():
    return datetime.today().strftime('%Y-%m-%d %H:%M:%S')

def main(zipcode):
    """
    Args:
        zipcode (str): example: '95129'

    Returns:
    """
    url = "https://www.redfin.com/zipcode/{}/filter/status=active+comingsoon+contingent+pending".format(zipcode)
    links = get_links(url)
    result = []
    for link in links:
        url = homepage + link 
        result.append(get_detail_info(url))

        # Add random delay
        delay = randint(32,65)
        print("Sleep " + str(delay) + "s")
        sleep(delay)    
    return result    

if __name__ == "__main__":

    # one zipcode contains less than 100 houses listing so we have to add this extra step
    # to add one more list to summerize overall objects
    mydata = []
    for zp in zipcode:
        mydata.append(main(zp))
    
    # Generate csv file  
    df = pd.DataFrame.from_dict(mydata)
    df.to_csv(r'summary.csv', index=False, header=True)
