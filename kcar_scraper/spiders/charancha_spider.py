import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from twisted.internet import asyncioreactor
asyncioreactor.install()

import scrapy
from scrapy_splash import SplashRequest
from scrapy.http import FormRequest
from kcar_scraper.items import CharanchaItem
import json
# from kcar_scraper.dictionaries import (
#     ACCIDENT_HISTORY_COMMENT_MAP,
#     CAR_CATEGORY_MAP,
#     DRIVING_TYPE_MAP,
#     FUEL_TYPE_MAP,
#     TRANSMITION_NAME_MAP,
# )
# from kcar_scraper.utils import normalize_date
import time
from scrapy import signals
from urllib.parse import quote
import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs
import random

# headers = {
#     "Content-Type": "application/json;charset=UTF-8",
#     "Origin": "https://charancha.com",
#     "Referer": "https://charancha.com/bu/sell/list",
#     "User-Agent": "Mozilla/5.0",
#     "X-Requested-With": "XMLHttpRequest",
# }

# max_pages = 740

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)



class CharanchaSpider(scrapy.Spider):
    name = "charancha"
    allowed_domains = ["charancha.com"]
    start_urls = []
    start_url = "https://charancha.com/bu/sell/pcListCtl"
    max_pages = 750

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
        "Accept-Language": "ru,en;q=0.9",
        "Origin": "https://charancha.com",
        "Referer": "https://charancha.com/bu/sell/list",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 YaBrowser/25.6.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    base_data = {
        "perPageNum": "15",
        "pageSize": "",
        "order": "",
        "makerCdSearch": "",
        "modelCdSearch": "",
        "modelDetailCdSearch": "",
        "gradeDetailCdSearch": "",
        "carTypeSearch": "",
        "releaseDtStart": "",
        "releaseDtEnd": "2025",
        "mileageStart": "",
        "mileageEnd": "999999",
        "sellPriceStart": "",
        "sellPriceEnd": "999999999",
        "fuelSearch": "",
        "transmissionSearch": "",
        "colorSearch": "",
        "accidentSearch": "",
        "sortSearch": "",
        "regionSearch": "",
        "optionSearch": "",
        "inputSearchType": "",
        "inputSearch": "",
        "makerSearch": "",
        "modelSearch": "",
        "modelDetailSearch": "",
        "gradeSearch": "",
        "userKeySearch": "",
        "countryCdSearch": "ALL",
        "makerNmSearch": "",
        "modelNmSearch": "",
        "modelDetailNmSearch": "",
        "inputNmSearch": "",
        "gradeDetailCdYn": "",
        "trimType": "MAKER",
        "parentCode": "",
        "mdlCd": "",
        "depth": "",
        "mdlNm": "",
        "classificationCd": "",
        "modelDetailNm": "",
        "dealerNm": "",
        "dealerKey": "",
        "carNoNm": "",
        "sellNo": "",
        "sellerKey": "",
        "selMdlCd": "",
        "menuType": "type1",
        "makerCd": "",
        "modelCd": "",
        "modelDetailCd": "",
        "gradeCd": "",
        "gradeDetailCd": "",
        "sellPrice": "",
        "viewFlag": ""
    }

    custom_settings = {
        "CONCURRENT_REQUESTS": 64,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 64,
        "DOWNLOAD_DELAY": 0,
        "RETRY_ENABLED": False,
        "COOKIES_ENABLED": False,
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "ERROR",
        "HTTPERROR_ALLOW_ALL": True,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def __init__(self, start_page=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.found_cars = 0
        self.not_found_cars = 0
        # self.max_pages = 100
        self.start_page = int(start_page)
        self.retry_counts = {}
        self.max_retries = 3

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CharanchaSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.closed, signal=signals.spider_closed)
        return spider

    def opened(self, spider):
        self.start_time = time.time()
        print("Паук начал свою работу")

    def start_requests(self):
        data = self.base_data.copy()
        data["page"] = str(self.start_page)

        headers = self.headers.copy()
        headers["User-Agent"] = get_random_user_agent()

        yield scrapy.FormRequest(
            url=self.start_url,
            method="POST",
            formdata=data,
            headers=self.headers,
            callback=self.parse_car_list,
            meta={"pageNum": self.start_page, "formdata": data}
        )


    def parse_car_list(self, response):
        pageNum = response.meta.get("pageNum", "??")
        print(f"Обрабатываем страницу {pageNum}")

        car_blocks = response.xpath("//li[contains(@class, 'cars__li')]")
        if not car_blocks:
            retries = self.retry_counts.get(pageNum, 0)
            if retries < self.max_retries:
                print(f"[RETRY] Страница {pageNum} пустая — пробуем снова ({retries + 1}/{self.max_retries})")
                self.retry_counts[pageNum] = retries + 1

                yield scrapy.FormRequest(
                    url=self.start_url,
                    method="POST",
                    formdata=response.meta["formdata"],
                    headers=self.headers,
                    callback=self.parse_car_list,
                    meta={"pageNum": pageNum, "formdata": response.meta["formdata"]},
                    dont_filter=True
                )
            else:
                print(f"[INFO] Страница {pageNum} пустая — стоп после {self.max_retries} попыток.")
            return

        for block in car_blocks:
            full_id = block.xpath("./@id").get()
            if full_id and full_id.startswith("chr"):
                sellNo = full_id[3:]
                print(f"Нашел машину: {sellNo}")
                car_url = f"https://charancha.com/bu/sell/view?sellNo={sellNo}"
                yield scrapy.Request(
                    url=car_url,
                    callback=self.parse_car_page,
                    cb_kwargs={"sellNo": sellNo}
                )

        current_data = response.meta.get("formdata", {}).copy()
        next_page = pageNum + 1

        if next_page <= self.max_pages:
            current_data["page"] = str(next_page)
            print(f"[INFO] Переходим на страницу {next_page}")
            yield scrapy.FormRequest(
                url=self.start_url,
                method="POST",
                formdata=current_data,
                headers=self.headers,
                callback=self.parse_car_list,
                meta={"pageNum": next_page, "formdata": current_data}
            )


    def extract_car_number_from_html(self, response):
        pattern = re.compile(r'var carInfo = ({.*?});', re.DOTALL)
        match = pattern.search(response.text)
        if match:
            json_text = match.group(1)
            try:
                car_info = json.loads(json_text)
                car_number = car_info.get('carNo')
                # print(f"[DEBUG] car_number from JS JSON: {car_number}")
                return car_number
            except json.JSONDecodeError:
                print("[ERROR] JSON decode failed")
        else:
            print("[WARN] carInfo JSON not found in response")
        return None


    def request_molit_by_car_number(self, car_number, sellNo):
        if not car_number:
            self.logger.warning(f"Нет car_number для sellNo={sellNo}")
            return None

        encoded = quote(car_number.strip())
        api_url = f"https://charancha.com/v1/molits/{encoded}?summarize=false&type=DEFAULT"
        # print(f"[DEBUG] Запрос к API: {api_url}")

        return scrapy.Request(
            url=api_url,
            callback=self.parse_molits,
            headers={
                "User-Agent": get_random_user_agent(),
                "Referer": f"https://charancha.com/bu/sell/view?sellNo={sellNo}"
            },
            meta={"car_id": sellNo, "car_number": car_number},
            dont_filter=True
        )


    def parse_car_page(self, response, sellNo):
        # molit_id = response.xpath("//script[contains(text(), 'molitNo')]/text()").re_first(r'"molitNo":"(.*?)"')
        # if molit_id:
        #     api_url = f"https://charancha.com/v1/molits/{molit_id}?summarize=false&type=DEFAULT"
        #     headers_with_referer = {
        #         "User-Agent": "Mozilla/5.0",
        #         "Accept": "*/*",
        #         "Referer": response.url
        #     }
        #     print(f"Запрос к API по molit_id: {api_url}")
        #     yield scrapy.Request(
        #         url=api_url,
        #         headers=headers_with_referer,
        #         callback=self.parse_molits,
        #         meta={"car_id": sellNo},
        #         dont_filter=True
        #     )
        # else:
            car_number = response.xpath("//th[contains(text(), '차량번호')]/following-sibling::td[1]/text()").get()

            if not car_number:
                car_number = response.xpath("//li[@data-id='carNo']//span/text()").get()

            if not car_number:
                car_number = self.extract_car_number_from_html(response)

            if car_number:
                car_number = car_number.strip()
                # print(f"[car page] Найден номер: {car_number}")
                yield self.request_molit_by_car_number(car_number, sellNo)
            else:
                # print(f"[car page] Номер машины не найден")
                self.not_found_cars += 1

            # car_number = self.extract_car_number_from_html(response)
            # if car_number:
            #     print(f"Запрос к API по car_number: {car_number}")
            #     yield self.request_molit_by_car_number(car_number, sellNo)
            # else:
            #     self.logger.warning(f"Не удалось найти molit_id и car_number для машины {sellNo}")
            #     self.not_found_cars += 1


    def parse_molits(self, response):
        car_id = response.meta.get("car_id")
        # print(f"parse_molits вызван для sellNo={car_id}, status={response.status}")

        if response.status != 200:
            self.logger.warning(f"Ошибка HTTP {response.status} для машины {car_id}")
            self.not_found_cars += 1
            return

        try:
            root = ET.fromstring(response.text)
            
            item = CharanchaItem()
            item["car_id"] = car_id
            item["modelYyyyDt"] = root.findtext("modelYyyyDt")
            item["displacement"] = root.findtext("displacement")
            item["releaseDt"] = root.findtext("releaseDt")
            # item["inspectionValidityStartDt"] = root.findtext("inspectionValidityStartDt")
            # item["inspectionValidityEndDt"] = root.findtext("inspectionValidityEndDt")
            item["fuelNm"] = root.findtext("fuelNm")
            item["transmissionNm"] = root.findtext("transmissionNm")
            item["regNo"] = root.findtext("regNo")
            item["carType"] = root.findtext("carType")
            item["assortName"] = root.findtext("assortName")
            # item["purposeName"] = root.findtext("purposeName")
            item["carName"] = root.findtext("carName")
            item["formName"] = root.findtext("formName")
            item["vin"] = root.findtext("vin")
            item["motorFormName"] = root.findtext("motorFormName")
            # item["specNo"] = root.findtext("specNo")
            item["length"] = root.findtext("length")
            item["width"] = root.findtext("width")
            item["height"] = root.findtext("height")
            item["weight"] = root.findtext("weight")
            item["motorPs"] = root.findtext("motorPs")
            item["motorsRpm"] = root.findtext("motorsRpm")
            item["capacity"] = root.findtext("capacity")
            item["cylinder"] = root.findtext("cylinder")
            item["gasMileage"] = root.findtext("gasMileage")
            item["price"] = root.findtext("price")

            non_null_fields = [v for v in item.values() if v not in [None, "", "null"]]
            if len(non_null_fields) < 3:
                self.logger.warning(f"[molits] Почти пустой ответ для {car_id}, ретраем")
                car_number = response.meta.get("car_number")
                yield self.request_molit_by_car_number(car_number, car_id)
                return

            self.found_cars += 1
            yield item

        except ET.ParseError as e:
            self.not_found_cars += 1
            self.logger.warning(f"[molits] Ошибка парсинга XML для машины {car_id}: {e}")


    def closed(self, spider):
        end_time = time.time()
        duration = end_time - self.start_time
        minutes, seconds = divmod(duration, 60)
        print(f"Паук закончил работу")
        print(f"Время работы программы: {int(minutes)} минут {int(seconds)} секунд")
        print(f"Найдено машин: {self.found_cars}")
        print(f"Не найдено машин: {self.not_found_cars}")
