"""Create ratings table and bootstrap core tables for fresh databases."""
from alembic import op
import sqlalchemy as sa

revision = "20261026_add_rating"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Existing installations already have these tables from the app's earlier
    # create_all startup behavior. Create them here only for a fresh database.
    if not inspector.has_table("user"):
        op.create_table(
            "user",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("username", sa.String(length=80), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
            sa.UniqueConstraint("username"),
        )

    inspector = sa.inspect(bind)
    if not inspector.has_table("recipe"):
        op.create_table(
            "recipe",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["user.id"]),
        )

    inspector = sa.inspect(bind)
    if not inspector.has_table("rating"):
        op.create_table(
            "rating",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("recipe_id", sa.Integer(), nullable=False),
            sa.Column("score", sa.Integer(), nullable=False),
            sa.CheckConstraint(
                "score >= 1 AND score <= 5", name="ck_rating_score_range"
            ),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.ForeignKeyConstraint(["recipe_id"], ["recipe.id"]),
            sa.UniqueConstraint(
                "user_id", "recipe_id", name="uq_rating_user_recipe"
            ),
        )


def downgrade():
    bind = op.get_bind()
    if sa.inspect(bind).has_table("rating"):
        op.drop_table("rating")
