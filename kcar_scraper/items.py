# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class KcarItem(scrapy.Item):
    car_id = scrapy.Field()  # Айдишник автомобиля — "carCd"

    accident_history_comment = scrapy.Field()  # Комментарий к истории аварий — "acdtHistComnt"
    basic_config = scrapy.Field()  # Базовая комплектация — "grdFullNm"
    brand = scrapy.Field()  # Производитель (марка) — "mnuftrNm"
    car_category = scrapy.Field()  # Категория автомобиля — "carctgr"
    car_full_name = scrapy.Field()  # Полное название автомобиля — "carWhlNm"
    car_number_plate = scrapy.Field()  # Номерной знак — "cno"
    color = scrapy.Field()  # Цвет кузова — "extrColorNm"
    driving_type = scrapy.Field()  # Привод — "drvgYnNm"
    elan_path = scrapy.Field()  # Главное фото — "elanPath"
    engine_displacement = scrapy.Field()  # Объем двигателя — "engdispmnt"
    equipment_full = scrapy.Field()  # Полное название комплектации — "grdDtlNm"
    fuel_type = scrapy.Field()  # Тип топлива — "fuelTypecdNm"
    if_accident = scrapy.Field()  # Был ли в аварии — "acdtHistYn"
    manufacturing_date = scrapy.Field()  # Дата производства — "mfgDt"
    mileage = scrapy.Field()  # Пробег — "milg"
    model = scrapy.Field()  # Модель автомобиля — "modelNm"
    msize_img_path = scrapy.Field()  # Фото салона — "msizeImgPath"
    passenger_count = scrapy.Field()  # Кол-во мест — "pasngrCnt"
    price_full = scrapy.Field()  # Полная цена — "npriceFullType"
    transmission_name = scrapy.Field()  # Название коробки передач — "trnsmsncdNm"
    vin = scrapy.Field()  # VIN код — "vin"
