"""Systemtest table

Revision ID: 1582640ba8e9
Revises: 674e34bcf5ca
Create Date: 2020-04-28 14:18:39.372074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1582640ba8e9'
down_revision = '674e34bcf5ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('systemtest',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('system_id', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('cpu_usage', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_systemtest_timestamp'), 'systemtest', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_systemtest_timestamp'), table_name='systemtest')
    op.drop_table('systemtest')
    # ### end Alembic commands ###
