"""update_users

Revision ID: e8fdc40aa2dd
Revises: 72fc6176fd78
Create Date: 2023-05-20 19:01:30.888493

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "e8fdc40aa2dd"
down_revision = "72fc6176fd78"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "hrs_users",
        sa.Column("nickname", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("hrs_users", "nickname")
    # ### end Alembic commands ###
