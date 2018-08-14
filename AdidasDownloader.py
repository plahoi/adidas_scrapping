#!/usr/bin/env python
# -*- coding: utf-8 -*-

# export PYTHONIOENCODING=UTF-8

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import re
import os
from bs4 import BeautifulSoup
import requests
import shutil
import asyncio
import aiohttp
import tqdm
import time

class AdidasDownloader:
    def log(self):
        pass

    def __init__(self):
        #self.base_url = 'http://www.adidas.ru'
        self.folder = 'files'
        self.search_items_per_page = 120
        self.semaphore = asyncio.Semaphore(5)
        self.driver = webdriver.Chrome()
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    # Получаем все значения offset для подстаовки в урл
    def get_search_url_sizes(self, base_url):
        start = 0
        # url = 'https://www.adidas.ru/search?sz=120&start=0'
        url = base_url + '/search?sz=' + str(self.search_items_per_page) + '&start=' + str(start)
        response = requests.get(url)
        parser = BeautifulSoup(response.content, 'html.parser')
        data = parser.find('select', class_='paging-select')
        max_items_amount = len(data.find_all('option')) * self.search_items_per_page
        url_search_size_list = [i for i in range(start, max_items_amount, self.search_items_per_page)]

        return url_search_size_list

    def write_links_to_file(self, base_url, file_name):
        open(os.path.join(self.folder, file_name), 'w').close() #empty file
        result_links = []

        # https://github.com/cassiobotaro/fast_scraping_asyncio/blob/master/scraping.py
        async def get(*args, **kwargs):
            async with aiohttp.ClientSession() as session:
                async with session.get(*args, **kwargs) as resp:
                    return await resp.text()

        def get_links(page):
            parser = BeautifulSoup(page, 'html.parser')
            links = parser.find_all('a', class_='product-link')
            return [link.get('href') for link in links]

        async def append_links(start):
            url = base_url + '/search?sz=' + str(self.search_items_per_page) + '&start=' + str(start)
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            with await self.semaphore:
                page = await get(url, compress=True, headers=headers)
                result_links.append(get_links(page))

        async def wait_with_progress(coros):
            for f in tqdm.tqdm(asyncio.as_completed(coros), total=len(coros)):
                await f

        pages = self.get_search_url_sizes(base_url)
        loop = asyncio.get_event_loop()
        f = [append_links(d) for d in pages]
        loop.run_until_complete(wait_with_progress(f))

        with open(os.path.join(self.folder, file_name), 'a+') as f:
            for bunch in result_links:
                f.write('\n'.join(bunch))

    def download_html(self, urls):
        load_more_button_name = 'BV_TrackingTag_Review_Display_NextPage'
        geolocated_price_button_yes_xpath = 'ui-dialog-titlebar-close'
        # id = dialogcontainer
        for url in urls:
            self.driver.get(url)
            # click on comments button until it exists
            # bvseo-paginationLink
            # time.sleep(5)
            load_more_button_exists = True
            try:
                geolocated_price_button_yes = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.CLASS_NAME, geolocated_price_button_yes_xpath)))
                geolocated_price_button_yes.click()
            except TimeoutException as e:
                pass
            while load_more_button_exists:
                try:
                    load_more_button = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.NAME, load_more_button_name)))
                    load_more_button.click()
                    time.sleep(1)
                except TimeoutException as e:
                    load_more_button_exists = False

            with open(re.search('\w+\.html', url).group(), 'w', encoding='utf-8') as file:
                file.write(self.driver.page_source)

        #self.driver.quit()