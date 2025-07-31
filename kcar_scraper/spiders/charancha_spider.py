from shutil import ExecError
import scrapy
from no_encar_scraper.items import KcarScraperItem
import xml.etree.ElementTree as ET
import time
from scrapy import signals

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "ru,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 YaBrowser/25.6.0.0 Safari/537.36",
}

class CharanchaSpider(scrapy.Spider):
    name = "charancha_new"
    allowed_domains = ["charancha.com"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 64,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 64,
        "DOWNLOAD_DELAY": 0,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = 1
        self.size = 150
        self.total_pages = 27
        self.base_url = "https://charancha.com/v1/cars?page={}&size={}"
        self.found_cars = 0
        self.not_found_cars = 0

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CharanchaSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_opened(self):
        self.start_time = time.time()
        print("Паукчок начал свою работу")

    def spider_closed(self):
        self.end_time = time.time()
        print("Паукчок окончил свою работу")
        print(f"Найдено машин: {self.found_cars}")
        print(f"Не найдено машин: {self.not_found_cars}")
        print(f"Время работы: {self.end_time - self.start_time} секунд")

    def start_requests(self):
        print(f"Начало сбора данных с страницы {self.page}")
        
        yield scrapy.Request(
            url=self.base_url.format(self.page, self.size),
            method="GET",
            headers=headers,
            callback=self.parse,
        )

    def next_page(self):
        self.page += 1
        if self.page <= self.total_pages:
            print(f"Переход на страницу {self.page}")
            yield scrapy.Request(
                url=self.base_url.format(self.page, self.size),
                method="GET",
                headers=headers,
                callback=self.parse,
            )

    def parse(self, response):
        print(f"Страница {self.page} загружена. Статус запроса: {response.status}")

        if response.status != 200:
            self.logger.warning(f"Страница {self.page} не загружена. Статус запроса: {response.status}")
            self.not_found_cars += 1
            return None

        try:
            root = ET.fromstring(response.text)
            cars = root.findall("content/content")

            for car in cars:
                try:
                    item = KcarScraperItem()
                    item["api_id"] = car.findtext("sellNo")
                    item["brand"] = car.findtext("brand")  # ПОД ВОПРОСОМ, ВСЕГДА ЛИ ВОЗВРАЩАЕТ FALSE
                    item["model"] = car.findtext("modelNm")
                    item["year"] = car.findtext("releaseYyyymmDt")[:4]
                    item["mileage"] = car.findtext("mileage")
                    item["color"] = car.findtext("colorNm")
                    item["finish"] = car.findtext("sellPrice")
                    item["engine"] = car.findtext("fuelNm")
                    item["engine_show"] = car.findtext("fuelNm")
                    item["grade"] = car.findtext("gradeNm")
                    item["equip"] = None
                    item["drive"] = None
                    item["engine_volume"] = car.findtext("displacement")
                    item["repairs_damage"] = None
                    item["source_link"] = f"https://charancha.com/bu/sell/view?sellNo={car.findtext("vehicleId")}"
                    item["transmission"] = car.findtext("transmissionNm")
                    item["body_type"] = car.findtext("bodyTypeNm")
                    item["pasngr_сnt"] = None
                    item["photos"] = car.findtext("carImg")
                    item["rate"] = None
                    item["lot"] = None
                    item["power_volume"] = None
                    item["month"] = car.findtext("releaseYyyymmDt")[4:6]
                    item["auction"] = "charancha"
                    item["brand_country"] = car.findtext("makerNm") # СЛОВАРЬ БРЕНД-СТРАНА

                    self.found_cars += 1
                    print(f"Параметры для машины {item["api_id"]} загружены")
                    yield item

                except Exception as e:
                    self.not_found_cars += 1
                    print(f"Ошибка при загрузке параметров для машины {item["api_id"]}: {e}")

            yield from self.next_page()

        except Exception as e:
            self.not_found_cars += 1
            print(f"Ошибка при загрузке страницы {self.page}: {e}")
            return None