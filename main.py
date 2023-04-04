from digikala_spider import DigikalaSpider
from multisprider import Multispider

if __name__ == '__main__':
    num_of_spiders = 3
    multispider = Multispider(num_of_spiders, DigikalaSpider().get_num_of_categories())
    multispider.multi_crawl()


