#   This file is part of the ecoAlert project.
#   Copyright (c) 2021 John Lyu
#   All Rights Reserved.
#   Unauthorized copying of this file, via any medium is strictly prohibited
#   Proprietary and confidential

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from ecoAlert import settings

DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(settings.DATABASE)


def create_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


class ModelUpdateMixin:
    """Documents for ModelUpdateMixin"""

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Announcement(DeclarativeBase, ModelUpdateMixin):
    """Sqlalchemy ORM"""
    __tablename__ = "announcement"

    id = Column(Integer, primary_key=True)
    secCode = Column("secCode", String, nullable=True)
    secName = Column("secName", String, nullable=True)
    orgId = Column("orgId", String, nullable=True)
    announcementId = Column("announcementId", String, nullable=True)
    announcementTitle = Column("announcementTitle", String, nullable=True)
    announcementTime = Column("announcementTime", String, nullable=True)
    adjunctUrl = Column("adjunctUrl", String, nullable=True)
    adjunctSize = Column("adjunctSize", String, nullable=True)
    adjunctType = Column("adjunctType", String, nullable=True)
    storageTime = Column("storageTime", String, nullable=True)
    columnId = Column("columnId", String, nullable=True)
    pageColumn = Column("pageColumn", String, nullable=True)
    announcementType = Column("announcementType", String, nullable=True)
    associateAnnouncement = Column("associateAnnouncement", String, nullable=True)
    important = Column("important", String, nullable=True)
    batchNum = Column("batchNum", String, nullable=True)
    announcementContent = Column("announcementContent", String, nullable=True)
    orgName = Column("orgName", String, nullable=True)
    announcementTypeName = Column("announcementTypeName", String, nullable=True)
