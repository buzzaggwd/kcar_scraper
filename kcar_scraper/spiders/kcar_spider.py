import scrapy
from scrapy_splash import SplashRequest
from scrapy.http import FormRequest
from kcar_scraper.items import KcarItem
import json
from kcar_scraper.dictionaries import ACCIDENT_HISTORY_COMMENT_MAP, CAR_CATEGORY_MAP, DRIVING_TYPE_MAP, FUEL_TYPE_MAP, TRANSMITION_NAME_MAP
from kcar_scraper.utils import normalize_date
import time
from scrapy import signals

headers = """
Accept: application/json, text/plain, */*
Accept-Encoding: gzip, deflate, br, zstd
Accept-Language: ru,en;q=0.9
Cache-Control: no-cache
Connection: keep-alive
Cookie: ab.storage.deviceId.79570721-e48c-4ca4-b9d6-e036e9bfeff8=%7B%22g%22%3A%221c3656e0-a5fd-7829-a851-8623d6375bb7%22%2C%22c%22%3A1752718738682%2C%22l%22%3A1752718738682%7D; _ba_rand=73; _ba_exist=true; _ba_initial_refer=; _ba_ssid=LuJhTaE7; _ba_page_ct=2025-07-17T02%3A19%3A04.894Z; _gid=GA1.2.1884833337.1752718746; grb_ck@cbd6aecb=f85b69ab-6498-c7b6-aaf3-1db049c2a8a9; grb_ui@cbd6aecb=02ab7db6-97bd-ab65-2cc7-19e32a1d1f91; grb_id_permission@cbd6aecb=fail; grb_ip_permission@cbd6aecb=fail; WMONID=NlhH-KqnUCh; _fwb=1955U5F1hsZxIxqYJgZnCca.1752718784168; _kmpid=km|kcar.com|1752718784867|aa166cce-439a-41d5-aebc-c8bba80f8e6f; _gcl_au=1.1.97021100.1752718744; dmcself_fp=fe3ae3a327d0aa9552731d201c3e8aff; _spfp=sp.1.fe3ae3a327d0aa9552731d201c3e8aff.1752718883; _spfp_v2_2=sp.2.2.1752718883.67863; _ba_last_2nd_url=https%3A%2F%2Fwww.kcar.com%2Fbc%2FtimedealCar%2Flist; _ba_parent_seq=2; _ba_last_url=https%3A%2F%2Fwww.kcar.com%2Fbc%2Fdetail%2FcarInfoDtl%3Fi_sCarCd%3DEC61213755; amplitude_id_86cd6422ba1c1dd78d122ad0b1158d6akcar.com=eyJkZXZpY2VJZCI6IjZhZDA2MzdlLWVlZmEtNDVjZi05M2JlLWI1OWUwMjQ1ODMyY1IiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTc1MjcxODczOTA5NCwibGFzdEV2ZW50VGltZSI6MTc1MjcxOTcyMTEzNiwiZXZlbnRJZCI6OSwiaWRlbnRpZnlJZCI6Niwic2VxdWVuY2VOdW1iZXIiOjE1fQ==; ab.storage.sessionId.79570721-e48c-4ca4-b9d6-e036e9bfeff8=%7B%22g%22%3A%226002fa3c-86cc-3c61-f41c-ea2597aaafca%22%2C%22e%22%3A1752721521143%2C%22c%22%3A1752718738701%2C%22l%22%3A1752719721143%7D; _ga_N2QC9KJL32=GS2.1.s1752718743$o1$g1$t1752719734$j60$l0$h0; _dc_gtm_UA-23566107-15=1; _ga_17DVLNK818=GS2.1.s1752718745$o1$g1$t1752719735$j50$l0$h0; _ga=GA1.1.700649585.1752718744; _ga_12BKR6ZT1H=GS2.2.s1752718792$o1$g1$t1752719735$j60$l0$h0
Expires: 0
Host: api.kcar.com  
Origin: https://www.kcar.com
Pragma: no-cache
Referer: https://www.kcar.com/
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-site
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 YaBrowser/25.6.0.0 Safari/537.36
sec-ch-ua: "Chromium";v="136", "YaBrowser";v="25.6", "Not.A/Brand";v="99", "Yowser";v="2.5"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
""".strip().split(
    "\n"
)


class KcarSpider(scrapy.Spider):
    name = "kcar"
    allowed_domains = ["api.kcar.com"]
    start_urls = []

    custom_settings = {
        "CONCURRENT_REQUESTS": 64,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 32,
        "DOWNLOAD_DELAY": 0,
        "RETRY_ENABLED": False,
        "COOKIES_ENABLED": False,
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "ERROR",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.found_cars = 0
        self.not_found_cars = 0

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(KcarSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.closed, signal=signals.spider_closed)
        return spider

    def opened(self, spider):
        self.start_time = time.time()
        print("Паук начал свою работу")

    def start_requests(self):
        ranges = [
            ("EC611", 22223, 33333),  # 1
            ("EC611", 33334, 44444),  # 6
            ("EC611", 44445, 55555),  # 24
            ("EC611", 55556, 66666),  # 82
            ("EC611", 66667, 77777),  # 178
            ("EC611", 77778, 88888),  # 431
            ("EC611", 88889, 99999),  # 873
            ("EC612", 0, 11111),      # 1787
            ("EC612", 11112, 22222),  # 3689
            ("EC612", 22223, 33333),  # 1770
        ]

        for prefix, start_num, end_num in ranges:
            for number in range(start_num, end_num + 1):
                car_id = f"{prefix}{number:05}"
                url = f"https://api.kcar.com/bc/car-info-detail-of-ng?i_sCarCd={car_id}&i_sPassYn=N&bltbdKnd=CM050"
                yield scrapy.Request(
                    url,
                    callback=self.parse_one_car,
                    meta={"car_id": car_id},
                    headers=self.get_headers(),
                )

    def get_headers(self):
        dict_headers = {}
        for header in headers:
            try:
                key, value = header.split(": ")
                dict_headers[key] = value
            except:
                pass
        return dict_headers

    def parse_one_car(self, response):
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

        except Exception as e:
            self.logger.error(f"[{car_id}] Ошибка при обработке полей: {e}")
            self.not_found_cars += 1
            return

        self.found_cars += 1
        self.logger.info(f"[{car_id}] Успех!")
        yield item

    def closed(self, spider):
        end_time = time.time()
        duration = end_time - self.start_time
        minutes, seconds = divmod(duration, 60)
        print(f"Паук закончил работу")
        print(f"Время работы программы: {int(minutes)} минут {int(seconds)} секунд")
        print(f"Найдено машин: {self.found_cars}")
        print(f"Не найдено машин: {self.not_found_cars}")