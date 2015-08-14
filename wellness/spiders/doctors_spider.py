from scrapy.spiders import SitemapSpider
from scrapy.spiders.sitemap import iterloc
from wellness.items import WellnessItem
from scrapy.http import Request
from scrapy.utils.sitemap import Sitemap, sitemap_urls_from_robots
import psycopg2
import re
import logging

__author__ = 'roman'

# regular experssion for check practice years
years_re = re.compile("\d+")

conn = psycopg2.connect("host=umimag.brand57.ru dbname=wellness user=postgres password=simplepass")


def doctor_exists(url):
    global conn
    cur = conn.cursor()
    cur.execute("SELECT * FROM results WHERE item_url = %s", (url,))
    result = cur.fetchone()
    return bool(result)

class DoctorsSpider(SitemapSpider):
    name = 'doctors'

    sitemap_urls = ['http://www.wellness.com/sitemap-index.xml']

    sitemap_rules = [
        ('\/dir\/\d+\/((?!directions).)*$', 'parse_doctor')
    ]

    def _parse_sitemap(self, response):
        if response.url.endswith('/robots.txt'):
            for url in sitemap_urls_from_robots(response.body):
                yield Request(url, callback=self._parse_sitemap)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                self.logger.warning("Ignoring invalid sitemap: %(response)s",
                               {'response': response}, extra={'spider': self})
                return

            s = Sitemap(body)
            if s.type == 'sitemapindex':
                for loc in iterloc(s, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        yield Request(loc, callback=self._parse_sitemap)
            elif s.type == 'urlset':
                for loc in iterloc(s):
                    for r, c in self._cbs:
                        if r.search(loc):
                            if not doctor_exists(loc):
                                self.logger.debug("Doctor's url not found in db. Fetching data")
                                yield Request(loc, callback=c)
                            else:
                                self.logger.debug("Doctor's url found in db. Passing it on")
                            break


    def parse_website(self, response, result):
        # todo: make this method return value
        website = response.selector.xpath(
            "//div[@class='bordered-container featured-right-container']/a/@href").extract()
        if not website:
            website = response.selector.xpath("//a[@target='website']/@href").extract()
        if website:
            result['website'] = website[0]

    def parse_street(self, response, result):
        # todo: make this method return value
        street_xpath = "//span[@itemprop='streetAddress']/"
        street = response.selector.xpath(street_xpath + "span[@class='address-line1']/text()").extract()
        if not street:
            street = response.selector.xpath(street_xpath + "text()").extract()
        if street:
            street_name = street[0].strip()
            if street_name:
                result['street'] = street_name
            else:
                self.log("Street string is empty!!!", logging.ERROR)

    def parse_featured(self, response):
        """
        This method parses "featured" pages of wellness.com
        :param response:
        :return:
        """
        global years_re
        result = WellnessItem()
        result['item_url'] = response.url
        name = response.selector.xpath('//h1/text()').extract()
        if name:
            result['name'] = name[0]
        business_name = response.selector.xpath("//b[@class='clear']/text()").extract()
        if business_name:
            result['business_name'] = business_name[0]

        self.parse_street(response, result)

        city = response.selector.xpath("//span[@itemprop='addressLocality']/text()").extract()
        if city:
            result['city'] = city[0]
        state = response.selector.xpath("//span[@itemprop='addressRegion']/text()").extract()
        if state:
            result['state'] = state[0]
        zip = response.selector.xpath("//span[@itemprop='postalCode']/text()").extract()
        if zip:
            result['zip'] = zip[0]
        primary_speciality = response.selector.xpath("//h2[@class='normal']/text()").extract()
        if primary_speciality:
            result['primary_speciality'] = primary_speciality[0]
        staff = response.selector.xpath(
            "//div[@class='business-hours-container item-container']/span[1]/text()").extract()
        if staff:
            result['staff'] = staff[0].split(u'\n\n')
        years = response.selector.xpath(
            "//div[@class='bordered-container featured-right-container']/span[@class='listing-h2 h2-style'][1]/text()").extract()
        if years:
            m = years_re.match(years[0])
            if m:
                result['years'] = int(m.group(0))
        rating = response.selector.xpath("//div[@class='listing item-rating']/text()").extract()
        if rating:
            result['rating'] = float(rating[0])
        reviews_count = response.selector.xpath("//div[@class='item-rating-container']/a/text()").extract()
        if reviews_count:
            reviews_count_str = reviews_count[0].replace('\n', '').replace('\r', '').strip()
            m = years_re.search(reviews_count_str)
            if m:
                result['reviews_count'] = int(m.group(0))

        self.parse_website(response, result)

        return result

    def parse_not_featured(self, response):
        """
        parses info about non-featured doctor
        :param response:
        :return:
        """
        global years_re
        result = WellnessItem()
        result['item_url'] = response.url
        name = response.selector.xpath('//h1/text()').extract()
        if name:
            result['name'] = name[0]
        business_name = response.selector.xpath("//b[@class='clear']/text()").extract()
        if business_name:
            result['business_name'] = business_name[0]

        self.parse_street(response, result)

        city = response.selector.xpath("//span[@itemprop='addressLocality']/text()").extract()
        if city:
            result['city'] = city[0]

        state = response.selector.xpath("//span[@itemprop='addressRegion']/text()").extract()
        if state:
            result['state'] = state[0]
        zip = response.selector.xpath("//span[@itemprop='postalCode']/text()").extract()
        if zip:
            result['zip'] = zip[0]
        primary_speciality = response.selector.xpath("//h2[@class='normal']/text()").extract()
        if primary_speciality:
            result['primary_speciality'] = primary_speciality[0]
        staff = response.selector.xpath(
            "//b/text()[contains(.,'Staff')]/parent::b/"
            "parent::div/text()[string-length(translate(normalize-space(.), ' ', '')) > 0]").extract()
        if staff:
            staff = [person.strip() for person in staff]
            result['staff'] = staff
        rating = response.selector.xpath("//div[@class='listing item-rating']/text()").extract()
        if rating:
            result['rating'] = float(rating[0])
        reviews_count = response.selector.xpath("//div[@class='item-rating-container']/a/text()").extract()
        if reviews_count:
            reviews_count_str = reviews_count[0].replace('\n', '').replace('\r', '').strip()
            m = years_re.search(reviews_count_str)
            if m:
                result['reviews_count'] = int(m.group(0))

        years = response.selector.xpath(
            "//b[text()='Years In Practice']/ancestor::div[@class='listing-half-container']/text()[2]"
        ).extract()
        if years:
            years = years[0].strip()
            result['years'] = int(years)

        websites = response.selector.xpath("//*[contains(text(), 'website')]").extract()
        if len(websites) > 1:
            self.logger.info("Found non-featured page with website. Page url: %s", response.url)

        self.parse_website(response, result)

        return result

    def parse_doctor(self, response):
        """
        Parses information about doctor
        :param scrapy.http.Response response:
        :return:

        @url http://www.wellness.com/dir/451897/chiropractor/fl/jacksonville/frank-hurst-dc
        @scrapes  item_url name street city state zip primary_speciality years rating reviews_count
        """
        is_featured = response.selector.xpath("//img[@title='Wellness.com Featured Provider']").extract()
        if not is_featured:
            result = self.parse_not_featured(response)
        else:
            result = self.parse_featured(response)

        return result






