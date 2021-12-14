import pretty_errors
import scrapy
from scrapy_splash import SplashRequest

class FindQuotesSpider(scrapy.Spider):
    name = 'find_quotes'
    allowed_domains = ['quotes.toscrape.com']

    script = '''
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash::wait(0.5))
            return splash:html()
    '''

    def start_requests(self):
        yield SplashRequest(url='http://quotes.toscrape.com/js/', callback=self.parse, endpoint='execute', args={
            'lua_source': self.script
        })

    def parse(self, response):
        quotes_to_scrape = response.xpath("//div[@class='quote']")
        dict_of_text_author_tags = {}
        for quotes in quotes_to_scrape:
            dict_of_text_author_tags["text"] = response.xpath(".//span[@class='text']/text()").get()
            dict_of_text_author_tags["author"] = response.xpath(".//span[2]/small[@class='author']/text()").get()
            dict_of_text_author_tags["tags"] = response.xpath(".//div[@class='tags']/a/text()").getall()

            yield dict_of_text_author_tags
    
        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page:
            absolute_url = f"http://quotes.toscrape.com{next_page}"
            yield SplashRequest(url=absolute_url, callback=self.parse, endpoint='execute', args={
                    'lua_source': self.script
                })