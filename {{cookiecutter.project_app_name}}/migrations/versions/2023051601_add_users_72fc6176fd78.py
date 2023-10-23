"""add_users

Revision ID: 72fc6176fd78
Revises: 19dd89306fda
Create Date: 2023-05-16 20:01:12.906736

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "72fc6176fd78"
down_revision = "19dd89306fda"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "hrs_users",
        sa.Column(
            "uuid",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp(0)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp(0)"),
            nullable=False,
        ),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index(op.f("ix_hrs_users_uuid"), "hrs_users", ["uuid"], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_hrs_users_uuid"), table_name="hrs_users")
    op.drop_table("hrs_users")
    # ### end Alembic commands ###