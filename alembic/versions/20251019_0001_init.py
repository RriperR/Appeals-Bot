from alembic import op
import sqlalchemy as sa


revision = "20251019_0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("telegram_id", sa.BigInteger, nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("username", sa.String(255)),
        sa.Column("phone", sa.String(64)),
        sa.Column("email", sa.String(255)),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    op.create_table(
        "commissions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
    )
    op.create_unique_constraint("uq_commissions_title", "commissions", ["title"])

    op.create_table(
        "appeals",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("commission_id", sa.Integer, sa.ForeignKey("commissions.id"), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("contact", sa.String(255)),
        sa.Column("status", sa.String(32), server_default="NEW", nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
    )
    op.create_index("ix_appeals_status", "appeals", ["status"])
    op.create_index("ix_appeals_user_commission", "appeals", ["user_id", "commission_id"])

    op.create_table(
        "appeal_files",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("appeal_id", sa.Integer, sa.ForeignKey("appeals.id"), nullable=False),
        sa.Column("telegram_file_id", sa.String(512), nullable=False),
        sa.Column("file_name", sa.String(255)),
        sa.Column("mime_type", sa.String(128)),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
    )
    op.create_index("ix_appeal_files_appeal_id", "appeal_files", ["appeal_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("appeal_id", sa.Integer, sa.ForeignKey("appeals.id")),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("sent_ok", sa.Boolean, server_default="false", nullable=False),
        sa.Column("error", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("sent_at", sa.DateTime),
    )

    op.create_table(
        "admin_requests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reason", sa.Text),
        sa.Column("status", sa.String(32), server_default="PENDING", nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
    )
    op.create_unique_constraint("uq_admin_requests_user", "admin_requests", ["user_id"])

    op.create_table(
        "admin_roles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_superadmin", sa.Boolean, server_default="false", nullable=False),
    )
    op.create_unique_constraint("uq_admin_roles_user", "admin_roles", ["user_id"])

def downgrade() -> None:
    op.drop_table("admin_roles")
    op.drop_table("admin_requests")
    op.drop_table("notifications")
    op.drop_index("ix_appeal_files_appeal_id", table_name="appeal_files")
    op.drop_table("appeal_files")
    op.drop_index("ix_appeals_user_commission", table_name="appeals")
    op.drop_index("ix_appeals_status", table_name="appeals")
    op.drop_table("appeals")
    op.drop_constraint("uq_commissions_title", "commissions", type_="unique")
    op.drop_table("commissions")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
