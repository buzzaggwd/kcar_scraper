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
from kcar_scraper.items import KcarScraperItem
from scrapy.exceptions import DropItem

Base = declarative_base()

class KcarTable(Base):
    __tablename__ = "kcardata"   # ИМЯ ТАБЛИЦЫ 

    api_id = Column(String, primary_key=True)
    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    mileage = Column(Integer)
    color = Column(String)
    finish = Column(String)
    engine = Column(String)
    engine_show = Column(String)
    grade = Column(String)
    equip = Column(String)
    drive = Column(String)
    engine_volume = Column(Integer)
    repairs_damage = Column(Text)
    source_link = Column(String)
    transmission = Column(String)
    body_type = Column(String)
    pasngr_сnt = Column(String)
    photos = Column(Text)
    rate = Column(String)
    lot = Column(String)
    power_volume = Column(String)
    month = Column(Integer)
    auction = Column(String)
    brand_country = Column(String)

    def __repr__(self):
        return "<Data %s %s %s %s %s>" % (
            self.api_id,
            self.brand,
            self.model,
            self.month,
            self.year,
        )


class KcarScraperPipelineNew(object):
    def __init__(self):
        basename = "kcar_data_scraped_another_items.sqlite"    # ИМЯ БАЗЫ
        self.engine = create_engine(f"sqlite:///{basename}", echo=False)
        if not os.path.exists(basename):
            Base.metadata.create_all(self.engine)

    def open_spider(self, spider):
        self.session = Session(bind=self.engine)

    def process_item(self, item, spider):
        if isinstance(item, KcarScraperItem):
            data_dict = dict(item)
            existing = self.session.get(KcarTable, data_dict["api_id"])
            if not existing:
                try:
                    self.session.add(KcarTable(**data_dict))
                    self.session.flush()
                except Exception as e:
                    spider.logger.error(
                        f"Возникла ошибка при добавлении в базу {data_dict['api_id']}: {e}"
                    )
            else:
                spider.logger.info(
                    f"Машина {data_dict['api_id']} уже существует в базе данных."
                )
        return item

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()
