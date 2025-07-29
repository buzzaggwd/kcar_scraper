# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    MetaData,
    ForeignKey,
    Boolean,
    URL,
    Text,
)
from sqlalchemy.orm import Session
import os
from kcar_scraper.items import CharanchaItem, KcarItem
from scrapy.exceptions import DropItem

Base = declarative_base()


class KcarTable(Base):
    __tablename__ = "kcardata"

    car_id = Column(String, primary_key=True)

    accident_history_comment = Column(String)
    basic_config = Column(String)
    brand = Column(String)
    car_category = Column(String)
    car_full_name = Column(String)
    car_number_plate = Column(String)
    color = Column(String)
    driving_type = Column(String)
    elan_path = Column(Text)
    engine_displacement = Column(Integer)
    equipment_full = Column(String)
    fuel_type = Column(String)
    if_accident = Column(Boolean)
    manufacturing_date = Column(String)
    mileage = Column(Integer)
    model = Column(String)
    msize_img_path = Column(Text)
    passenger_count = Column(Integer)
    price_full = Column(Integer)
    transmission_name = Column(String)
    vin = Column(String)

    def __init__(
        self,
        car_id,
        accident_history_comment,
        basic_config,
        brand,
        car_category,
        car_full_name,
        car_number_plate,
        color,
        driving_type,
        elan_path,
        engine_displacement,
        equipment_full,
        fuel_type,
        if_accident,
        manufacturing_date,
        mileage,
        model,
        msize_img_path,
        passenger_count,
        price_full,
        transmission_name,
        vin,
    ):
        self.car_id = car_id
        self.accident_history_comment = accident_history_comment
        self.basic_config = basic_config
        self.brand = brand
        self.car_category = car_category
        self.car_full_name = car_full_name
        self.car_number_plate = car_number_plate
        self.color = color
        self.driving_type = driving_type
        self.elan_path = elan_path
        self.engine_displacement = engine_displacement
        self.equipment_full = equipment_full
        self.fuel_type = fuel_type
        self.if_accident = if_accident
        self.manufacturing_date = manufacturing_date
        self.mileage = mileage
        self.model = model
        self.msize_img_path = msize_img_path
        self.passenger_count = passenger_count
        self.price_full = price_full
        self.transmission_name = transmission_name
        self.vin = vin

    def __repr__(self):
        return "<Data %s %s %s %s %s>" % (
            self.car_id,
            self.brand,
            self.model,
            self.equipment_full,
            self.manufacturing_date,
        )


class KcarScraperPipeline(object):
    def __init__(self):
        basename = "kcar_data_scraped.sqlite"
        self.engine = create_engine(f"sqlite:///{basename}", echo=False)
        if not os.path.exists(basename):
            Base.metadata.create_all(self.engine)

    def open_spider(self, spider):
        self.session = Session(bind=self.engine)

    def process_item(self, item, spider):
        if isinstance(item, KcarItem):
            data_dict = dict(item)
            existing = self.session.get(KcarTable, data_dict["car_id"])
            if not existing:
                try:
                    self.session.add(KcarTable(**data_dict))
                    self.session.flush()
                except Exception as e:
                    spider.logger.error(
                        f"Возникла ошибка при добавлении в базу {data_dict['car_id']}: {e}"
                    )
            else:
                spider.logger.info(
                    f"Машина {data_dict['car_id']} уже существует в базе данных."
                )
        return item

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()


class CharanchaTable(Base):
    __tablename__ = "charancha"

    car_id = Column(String, primary_key=True)

    # inspectionValidityStartDt = Column(String)
    # inspectionValidityEndDt = Column(String)
    # purposeName = Column(String)
    # specNo = Column(String)
    
    assortName = Column(String)
    capacity = Column(Integer)
    carName = Column(String)
    carType = Column(String)
    cylinder = Column(Integer)
    displacement = Column(Integer)
    formName = Column(String)
    fuelNm = Column(String)
    gasMileage = Column(Integer)
    height = Column(Integer)
    length = Column(Integer)
    width = Column(Integer)
    weight = Column(Integer)
    transmissionNm = Column(String)
    modelYyyyDt = Column(String)
    releaseDt = Column(String)
    motorFormName = Column(String)
    motorPs = Column(Integer)
    motorsRpm = Column(Integer)
    price = Column(Integer)
    # maxLoad = Column(Integer)
    regNo = Column(String)
    vin = Column(String)

    def __init__(
        self,
        car_id,
        # inspectionValidityStartDt,
        # inspectionValidityEndDt,
        # purposeName,
        # specNo,
        assortName,
        capacity,
        carName,
        carType,
        cylinder,
        displacement,
        formName,
        fuelNm,
        gasMileage,
        height,
        length,
        width,
        weight,
        transmissionNm,
        modelYyyyDt,
        releaseDt,
        motorFormName,
        motorPs,
        motorsRpm,
        price,
        # maxLoad,
        regNo,
        vin,
    ):
        self.car_id = car_id
        # self.inspectionValidityStartDt = inspectionValidityStartDt
        # self.inspectionValidityEndDt = inspectionValidityEndDt
        # self.purposeName = purposeName
        # self.specNo = specNo
        self.assortName = assortName
        self.capacity = capacity
        self.carName = carName
        self.carType = carType
        self.cylinder = cylinder
        self.displacement = displacement
        self.formName = formName
        self.fuelNm = fuelNm
        self.gasMileage = gasMileage
        self.height = height
        self.length = length
        self.width = width
        self.weight = weight
        self.transmissionNm = transmissionNm
        self.modelYyyyDt = modelYyyyDt
        self.releaseDt = releaseDt
        self.motorFormName = motorFormName
        self.motorPs = motorPs
        self.motorsRpm = motorsRpm
        self.price = price
        # self.maxLoad = maxLoad
        self.regNo = regNo
        self.vin = vin

    def __repr__(self):
        return "<Data %s %s %s %s %s>" % (
            self.car_id,
            self.carName,
            self.assortName,
            self.carType,
            self.releaseDt,
        )

class CharanchaScraperPipeline(object):
    def __init__(self):
        basename = "charancha_data_scraped.sqlite"
        self.engine = create_engine(f"sqlite:///{basename}", echo=False)
        if not os.path.exists(basename):
            Base.metadata.create_all(self.engine)

    def open_spider(self, spider):
        self.session = Session(bind=self.engine)

    def process_item(self, item, spider):
        if isinstance(item, CharanchaItem):
            data_dict = dict(item)
            existing = self.session.get(CharanchaTable, data_dict["car_id"])
            if not existing:
                try:
                    self.session.add(CharanchaTable(**data_dict))
                    self.session.flush()
                except Exception as e:
                    spider.logger.error(
                        f"Возникла ошибка при добавлении в базу {data_dict['car_id']}: {e}"
                    )
            else:
                spider.logger.info(
                    f"Машина {data_dict['car_id']} уже существует в базе данных."
                )
        return item

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()
