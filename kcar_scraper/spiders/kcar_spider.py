from requests import post
import scrapy
from scrapy_splash import SplashRequest
from scrapy.http import FormRequest
from kcar_scraper.items import KcarItem
import json
from kcar_scraper.dictionaries import ACCIDENT_HISTORY_COMMENT_MAP, CAR_CATEGORY_MAP, DRIVING_TYPE_MAP, FUEL_TYPE_MAP, TRANSMITION_NAME_MAP
from kcar_scraper.utils import normalize_date
import time
from scrapy import signals


headers = {
    "accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ru,en;q=0.9",
}


class KcarSpider(scrapy.Spider):
    name = "kcar"
    allowed_domains = ["api.kcar.com"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 64,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 32,
        "DOWNLOAD_DELAY": 2,
        "DOWNLOAD_TIMEOUT": 30,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 408, 110],
        "COOKIES_ENABLED": False,
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "ERROR",
        "HTTP_PROXY": "http://E5v1LcD1ap7I:J4hV3PCe@pool.proxy.market:10000",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.found_cars = 0
        self.not_found_cars = 0
        self.base_url = "https://api.kcar.com/bc/car-info-detail-of-ng?i_sCarCd={}&i_sPassYn=N&bltbdKnd=CM050"


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(KcarSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_opened(self):
        self.start_time = time.time()
        print("Паук начал свою работу")

    def spider_closed(self):
        self.end_time = time.time()
        print(f"Паук закончил работу")
        print(f"Найдено машин: {self.found_cars}")
        print(f"Не найдено машин: {self.not_found_cars}")
        print(f"Время работы: {self.end_time - self.start_time} секунд")


    def start_requests(self):
        ranges = [
            # ("EC611", 88889, 99999),  # 873
            # ("EC612", 0, 11111),      # 1787
            ("EC612", 11112, 22222),  # 3689
            # ("EC612", 22223, 33333),  # 1770
        ]

        for prefix, start_num, end_num in ranges:
            for number in range(start_num, end_num + 1):
                car_id = f"{prefix}{number:05}"
                print(f"[{car_id}] {self.base_url.format(car_id)}")
                yield scrapy.Request(
                    url=self.base_url.format(car_id),
                    method="POST",
                    callback=self.parse_one_car,
                    meta={
                        "proxy": "http://E5v1LcD1ap7I:J4hV3PCe@pool.proxy.market:10000",
                    },
                    headers=headers,
                )

    def parse_one_car(self, response):
        print(f"!parse_one_car! {response.status}")
        car_id = response.meta["car_id"]

        if response.status != 200:
            self.logger.warning(f"[{car_id}] Статус ответа не 200: {response.status}")
            self.not_found_cars += 1
            return

        data = response.json()
        rvo_data = data.get("data", {}).get("rvo")

        if not rvo_data:
            self.logger.warning(f"[{car_id}] Нет rvo")
            self.not_found_cars += 1
            return

        item = KcarItem()
        item["car_id"] = rvo_data.get("carCd")

        if not item["car_id"]:
            self.logger.warning(f"[{car_id}] Нет carCd в rvo")
            self.not_found_cars += 1
            return

        try:
            item["accident_history_comment"] = ACCIDENT_HISTORY_COMMENT_MAP.get(rvo_data.get("acdtHistComnt"), rvo_data.get("acdtHistComnt"))
            item["basic_config"] = rvo_data.get("grdNm")
            item["brand"] = rvo_data.get("mnuftrNm")
            item["car_category"] = CAR_CATEGORY_MAP.get(rvo_data.get("carctgr"), rvo_data.get("carctgr"))
            item["car_full_name"] = rvo_data.get("carWhlNm")
            item["car_number_plate"] = rvo_data.get("cno")
            item["color"] = rvo_data.get("extrColorNm")
            item["driving_type"] = DRIVING_TYPE_MAP.get(rvo_data.get("drvgYnNm"), rvo_data.get("drvgYnNm"))
            item["elan_path"] = rvo_data.get("elanPath")
            item["engine_displacement"] = int(rvo_data.get("engdispmnt", 0))
            item["equipment_full"] = rvo_data.get("grdDtlNm")
            item["fuel_type"] = FUEL_TYPE_MAP.get(rvo_data.get("fuelTypecdNm"), rvo_data.get("fuelTypecdNm"))
            item["if_accident"] = rvo_data.get("acdtHistYn") == "1"
            item["manufacturing_date"] = normalize_date(rvo_data.get("mfgDt"))
            item["mileage"] = int(rvo_data.get("milg", 0))
            item["model"] = rvo_data.get("modelNm")
            item["msize_img_path"] = rvo_data.get("msizeImgPath")
            item["passenger_count"] = int(rvo_data.get("pasngrCnt", 0))
            item["price_full"] = int(rvo_data.get("npriceFullType", 0))
            item["transmission_name"] = TRANSMITION_NAME_MAP.get(rvo_data.get("trnsmsncdNm"), rvo_data.get("trnsmsncdNm"))
            item["vin"] = rvo_data.get("vin")

            self.found_cars += 1
            self.logger.info(f"[{car_id}] Успех!")
            print(f"{car_id} {item['brand']} {item['model']} {item['year']} {item['price']}")
            yield item

        except Exception as e:
            self.logger.error(f"[{car_id}] Ошибка при обработке полей: {e}")
            self.not_found_cars += 1
            return
