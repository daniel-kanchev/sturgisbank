import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from sturgisbank.items import Article


class sturgisbankSpider(scrapy.Spider):
    name = 'sturgisbank'
    start_urls = ['https://www.sturgis.bank/Our-Bank/Blog']

    def parse(self, response):
        links = response.xpath('//a[@class="edn_readMore edn_readMoreButton"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="edn_articleTitle"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//article//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
