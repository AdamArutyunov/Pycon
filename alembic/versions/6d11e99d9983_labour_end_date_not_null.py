"""Labour end_date NOT NULL

Revision ID: 6d11e99d9983
Revises: ae82612dc3c1
Create Date: 2020-11-11 16:07:37.516635

"""
from alembic import op
from data import db_session
from data.models.labour import *
from Constants import *
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d11e99d9983'
down_revision = 'ae82612dc3c1'
branch_labels = None
depends_on = None


def upgrade():
    db_session.global_init(DATABASE_URI)
    session = db_session.create_session()
    labours = session.query(Labour).all()
    for l in labours:
        l.end_date = datetime.datetime.now()
    session.commit()
    
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("labours") as batch_op:
        batch_op.alter_column('end_date',
                       existing_type=sa.DATETIME(),
                       nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('labours', 'end_date',
               existing_type=sa.DATETIME(),
               nullable=True)
    # ### end Alembic commands ###
