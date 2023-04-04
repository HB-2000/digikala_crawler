from digikala_spider import DigikalaSpider
from threading import Thread
from utility import *


class Multispider:

    def __init__(self, num_of_spiders, num_of_pages) -> None:
        self.num_of_spider = num_of_spiders
        self.num_of_pages = num_of_pages
        self.spiders = []
        self.threads = []

        self.spiders_range = self.divide_pages()

    def divide_pages(self):
        num_of_pages_per_spider = self.num_of_pages // self.num_of_spider

        spiders_range = []
        for i in range(self.num_of_spider):
            start = i * num_of_pages_per_spider
            end = start + num_of_pages_per_spider
            spiders_range.append([start, end])
        if spiders_range[-1][1] < self.num_of_pages:
            spiders_range[-1][1] = self.num_of_pages

        return spiders_range

    def multi_crawl(self):
        self.spiders = [DigikalaSpider(*self.spiders_range[i]) for i in range(self.num_of_spider)]
        self.threads = [Thread(target=self.spiders[i].crawl) for i in range(self.num_of_spider)]

        for thread in self.threads:
            delay(5, 6)
            thread.start()

        for thread in self.threads:
            thread.join()
