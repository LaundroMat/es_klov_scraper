import requests
from bs4 import BeautifulSoup
import re


class Scraper(object):
    def __init__(self, base_url):
        self.base_url = base_url


class KLOVScraper(Scraper):

    BASE_URL = "http://www.arcade-museum.com"

    def __init__(self):
        super(KLOVScraper, self).__init__(base_url=self.BASE_URL)

    def get_links_to_game_page(self, game_title):
        r = requests.post(self.base_url + "/results.php", data={"q": game_title, "type": "Videogame"})
        # Find link(s) to game
        soup = BeautifulSoup(r.content)
        return [{'title': tag.text, 'url': tag['href']} for tag in soup.find_all("a", text=re.compile(game_title))]

    def scrape_game_name(self, soup):
        return soup.find(attrs={"style": "font-size:32px;text-align:center"}).text


    def scrape_game_desc(self, soup):
        start_desc = soup.findAll('table')[3].h2.next.next
        end_desc = start_desc.find_next("h2")

        def loop_until_h2(text, first_element):
            if first_element.string is not None:
                text += first_element.string
            if first_element.next == end_desc:
                return text
            else:
                return loop_until_h2(text, first_element.next)

        return loop_until_h2('', start_desc)


    def scrape_game_rating(self, soup):
        s = soup.find(text="Personal Impressions Score: ")
        return None if not s else s.next_sibling.text.strip()


    def scrape_game_players(self, soup):
        s = soup.find(text=re.compile('Maximum number of Players:'))
        return s[len('Maximum number of Players: '):].strip()


    def scrape_release_date(self, soup):
        return soup.find('a', href=re.compile('year_detail')).text.strip()


    def scrape_manufacturer(self, soup):
        return soup.find('a', href=re.compile('manuf_detail')).text.strip()


    def scrape_genre(self, soup):
        return soup.find('a', href=re.compile('genre=')).text.strip()


    def scrape_images(self, soup):
        return [tag['src'] for tag in soup.findAll("img", alt=re.compile("Title screen image"))]


    def scrape_game_info(self, url):
        game = {}
        r = requests.get(self.base_url+"/"+url)

        soup = BeautifulSoup(r.content)

        game['name'] = self.scrape_game_name(soup)
        game['desc'] = self.scrape_game_desc(soup)
        game['rating'] = self.scrape_game_rating(soup)
        game['players'] = self.scrape_game_players(soup)
        game['releasedate'] = self.scrape_release_date(soup)
        game['developer'] = self.scrape_manufacturer(soup)
        game['publisher'] = self.scrape_manufacturer(soup)
        game['genre'] = self.scrape_genre(soup)
        game['image'] = self.scrape_images(soup)

        return game