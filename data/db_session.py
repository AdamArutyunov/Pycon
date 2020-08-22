import os
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as dec
from sqlalchemy.orm import Session, scoped_session
from Constants import *

SqlAlchemyBase = dec.declarative_base()
__factory = None
__scoped_session = None
os.chdir(APP_ROOT)


def global_init(db_file):
    global __factory
    global __scoped_session

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Connecting to database on {conn_str}.")

    engine = sa.create_engine(conn_str, echo=False)
        
    __factory = orm.sessionmaker(bind=engine)
    __scoped_session = scoped_session(__factory)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session():
    global __scoped_session
    return __scoped_session
