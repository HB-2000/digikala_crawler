import os
from lxml import html
from os.path import exists

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

from category import Category
from utility import *


class DigikalaSpider:
    home_page_link = 'https://www.digikala.com/'

    product_info = ['نام', 'قیمت', 'وضعیت موجودی', 'امتیاز']
    max_page_num_per_category = 100

    home_page_delay = 5
    first_page_of_category_delay = 6
    min_page_delay = 2
    max_page_delay = 3
    try_page_delay = 1

    num_of_try_page_load = 4

    saved_file_dir = './csv/'

    xpaths = {
        'product_list':
            '//*[@id="base_layout_desktop_fixed_header"]/header/nav/div[1]/div[1]/div[1]/div/span',

        'category_form_1':
            '//*['
            '@class'
            '="BaseLayoutDesktopHeaderNavigationMainMegaMenu_BaseLayoutDesktopHeaderNavigationMainMegaMenu__item__DcC5_'
            ' BaseLayoutDesktopHeaderNavigationMainMegaMenu_BaseLayoutDesktopHeaderNavigationMainMegaMenu__item'
            '--main___jxDI d-flex text-body1-strong ai-center color-900 pos-relative mt-1"]',

        'category_form_2':
            '//*['
            '@class'
            '="BaseLayoutDesktopHeaderNavigationMainMegaMenu_BaseLayoutDesktopHeaderNavigationMainMegaMenu__item__DcC5_'
            ' text-body-2 color-500 mt-1"]',

        'product_block':
            '//*[@class="d-block pointer pos-relative bg-000 overflow-hidden grow-1 py-3 px-4 px-2-lg h-full-md '
            'styles_VerticalProductCard--hover__ud7aD"]',

        'product_name':
            '//*[@class="ellipsis-2 text-body2-strong color-700 '
            'styles_VerticalProductCard__productTitle__6zjjN"]/text()',

        'product_price':
            '//*[@class="d-flex ai-center jc-end gap-1 color-700 color-400 text-h5 grow-1"]/span/text()',

        'product_inventory':
            '//*[@class="d-flex ai-center jc-end gap-1 color-400 text-h5 grow-1"]/span/text()',

        'product_score':
            '//*[@class="text-body2-strong color-700"]/text()',

        'products_list_wrapper':
            '//*[@id="ProductListPagesWrapper"]/section[1]/div[1]/div/div/div',

        'pages_block':
            '//*[@class="font-body d-flex jc-center ai-center"]',

        'next_page_button':
            '//*[@id="ProductListPagesWrapper"]/section[1]/div[2]/div[21]/div/div[3]',

        'category_name':
            'span/text()',

        'category_link':
            '@href'
    }

    def __init__(self, start_page=None, end_page=None) -> None:
        self.start_page = start_page
        self.end_page = end_page
        self.is_range_base = self.start_page is not None and self.end_page is not None

        options = self.get_browser_options()
        self.browser = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))

    @staticmethod
    def get_browser_options():
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        return options

    def get_absolute_link(self, inner_link):
        return self.home_page_link + str(inner_link)

    def load_home_page(self):
        self.browser.get(self.home_page_link)
        delay(self.home_page_delay)

        product_list_elem = self.browser.find_element(By.XPATH, self.xpaths['product_list'])
        product_list_elem.click()
        delay(self.home_page_delay)

    def get_categories(self):
        category_elems = self.get_categories_elems()
        categories = []
        for category_elem in category_elems:
            category_name = self.get_element_data(category_elem, self.xpaths['category_name'])
            category_link = self.get_element_data(category_elem, self.xpaths['category_link'])
            category = Category(category_name, category_link)
            if category not in categories:
                categories.append(category)

        return categories

    def get_categories_elems(self):
        tree = html.fromstring(self.browser.page_source)
        category_form_1_elems = tree.xpath(self.xpaths['category_form_1'])
        category_form_2_elems = tree.xpath(self.xpaths['category_form_2'])
        category_elems = category_form_1_elems + category_form_2_elems
        return category_elems

    def is_category_page(self):
        products_list_wrapper_xpath = self.xpaths['products_list_wrapper']
        products_list_wrapper_elem = self.browser.find_elements(By.XPATH, products_list_wrapper_xpath)
        return len(products_list_wrapper_elem) != 0

    @staticmethod
    def get_element_data(tree, xpath):
        elements = tree.xpath(xpath)
        if len(elements) == 0:
            return '-'
        return elements[0]

    def get_page_products(self):
        tree = html.fromstring(self.browser.page_source)

        product_block_elems = tree.xpath(self.xpaths['product_block'])
        products = []

        for product_block_elem in product_block_elems:

            product_block_html = html.tostring(product_block_elem, encoding='unicode')
            product_block_tree = html.fromstring(product_block_html)

            product_name = self.get_element_data(product_block_tree, self.xpaths['product_name'])
            product_price = self.get_element_data(product_block_tree, self.xpaths['product_price'])
            product_inventory = self.get_element_data(product_block_tree, self.xpaths['product_inventory'])
            product_score = self.get_element_data(product_block_tree, self.xpaths['product_score'])

            if product_inventory == '-':
                product_inventory = 'موجود'

            products.append([product_name, product_price, product_inventory, product_score])

        return products

    def get_next_page_link(self, link: str, page_num):

        if link.endswith('/'):
            page_link = self.get_absolute_link(link) + f'?page={page_num}'
        else:
            absolute_link = self.get_absolute_link(link)
            inx = absolute_link.rindex('/')
            page_link = absolute_link[:inx] + f'?page={page_num}&' + absolute_link[inx:]
        return page_link

    def get_category_products_data(self, category):
        self.browser.get(self.get_absolute_link(category.link))
        delay(self.first_page_of_category_delay)

        if not self.is_category_page():
            return None

        products_data = []

        for page_num in range(1, self.max_page_num_per_category + 1):
            page_link = self.get_next_page_link(category.link, page_num)
            self.browser.get(page_link)
            delay(self.min_page_delay, self.max_page_delay)

            self.load_page(page_link)

            products = self.get_page_products()

            products_data.extend(products)

            if not self.has_next_page():
                break

        return products_data

    def load_page(self,link):
        try_num = 0
        while len(self.browser.find_elements(By.XPATH, self.xpaths['pages_block'])) == 0:
            delay(self.try_page_delay)
            try_num += 1
            if try_num == self.num_of_try_page_load:
                return

        try_num = 0
        products = self.get_page_products()
        while not self.is_valid_products(products):
            delay(self.try_page_delay)
            try_num += 1
            if try_num == self.num_of_try_page_load:
                return

            products = self.get_page_products()

    def has_next_page(self):
        next_page = self.browser.find_elements(By.XPATH, self.xpaths['next_page_button'])
        return len(next_page) != 0

    @staticmethod
    def is_valid_products(products):
        if not products:
            return False

        for product in products:
            if product[0] == '-':
                return False
        return True

    def get_num_of_categories(self):
        self.load_home_page()
        return len(self.get_categories())

    def crawl(self):

        self.load_home_page()
        categories = self.get_categories()

        if not exists(self.saved_file_dir):
            os.mkdir(self.saved_file_dir)

        for i, category in enumerate(categories):

            if self.is_range_base and not (self.start_page <= i < self.end_page):
                continue

            file_name = category.name + ' - ' + slugify(category.link, True).replace('search', '')
            if not exists(self.saved_file_dir + file_name + '.csv'):
                products_data = self.get_category_products_data(category)
                if products_data:
                    write_category_to_csv(self.saved_file_dir, file_name,
                                          self.product_info, products_data)
        self.browser.close()
