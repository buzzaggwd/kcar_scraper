# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class KcarScraperItem(scrapy.Item):
    api_id = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    year = scrapy.Field()
    mileage = scrapy.Field()
    color = scrapy.Field()
    finish = scrapy.Field()
    engine = scrapy.Field()
    engine_show = scrapy.Field()
    grade = scrapy.Field()
    equip = scrapy.Field()
    drive = scrapy.Field()
    engine_volume = scrapy.Field()
    repairs_damage = scrapy.Field()
    source_link = scrapy.Field()
    transmission = scrapy.Field()
    body_type = scrapy.Field()
    pasngr_сnt = scrapy.Field()
    photos = scrapy.Field()
    rate = scrapy.Field()
    lot = scrapy.Field()
    power_volume = scrapy.Field()
    month = scrapy.Field()
    auction = scrapy.Field()
    brand_country = scrapy.Field()

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


class CharanchaItem(scrapy.Item):
    car_id = scrapy.Field()  # Айдишник автомобиля

    # inspectionValidityStartDt = scrapy.Field()
    # inspectionValidityEndDt = scrapy.Field()
    # purposeName = scrapy.Field()
    # specNo = scrapy.Field()

    assortName = scrapy.Field()  # Тип кузова (승용 = легковой)
    capacity = scrapy.Field()  # Число посадочных мест
    carName = scrapy.Field()  # Полное наименование модели
    carType = scrapy.Field()  # Класс авто (대형 = большой)
    cylinder = scrapy.Field()  # Количество цилиндров
    displacement = scrapy.Field()  # Объeм двигателя в куб. см
    formName = scrapy.Field()  # Код кузов комплектации
    fuelNm = scrapy.Field()  # Тип топлива (например, бензин)
    gasMileage = scrapy.Field()  # Расход топлива (л/100 км)
    height = scrapy.Field()
    length = scrapy.Field()
    width = scrapy.Field()  # Габариты (мм)
    weight = scrapy.Field()  # Масса (кг)
    transmissionNm = scrapy.Field()  # Тип коробки передач (자동 = автомат)
    modelYyyyDt = scrapy.Field()  # Год модели
    releaseDt = scrapy.Field()  # Дата выпуска
    motorFormName = scrapy.Field()  # Тип мотора (кодировочное имя)
    motorPs = scrapy.Field()  # Мощность двигателя (л. с.)
    motorsRpm = scrapy.Field()  # Максимальные обороты двигателя
    price = scrapy.Field()  # Опубликованная цена (в KRW, южнокорейская вона)
    # maxLoad = scrapy.Field()  # Максимальная грузоподъёмность (чаще ноль — легковушка)
    regNo = scrapy.Field()  # Регистрационный номер (корейские знаки)
    vin = scrapy.Field()  # Уникальный VIN
