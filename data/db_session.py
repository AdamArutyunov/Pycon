import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session, scoped_session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()
__factory = None
pycon_scoped_session = None

def global_init(db_file):
    global __factory
    global pycon_scoped_session

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Connecting to database on {conn_str}.")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    pycon_scoped_session = scoped_session(__factory)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


def create_scoped_session():
    global pycon_scoped_session
    return pycon_scoped_session
