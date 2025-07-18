"""Add is_featured to Property model

Revision ID: f5f9ea3bdc5d
Revises: 159cb37f4140
Create Date: 2025-05-26 17:45:39.969533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5f9ea3bdc5d'
down_revision = '159cb37f4140'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('property', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_featured', sa.Boolean(), nullable=False))
        batch_op.create_index(batch_op.f('ix_property_date_listed'), ['date_listed'], unique=False)
        batch_op.create_index(batch_op.f('ix_property_is_featured'), ['is_featured'], unique=False)
        batch_op.create_index(batch_op.f('ix_property_status'), ['status'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('property', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_property_status'))
        batch_op.drop_index(batch_op.f('ix_property_is_featured'))
        batch_op.drop_index(batch_op.f('ix_property_date_listed'))
        batch_op.drop_column('is_featured')

    # ### end Alembic commands ###
