"""bookings

Revision ID: 003
Revises: 002
Create Date: 2026-10-02 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

# Enum is created explicitly with checkfirst=True so that re-running the
# migration on a DB that already has the type doesn't error out.
# create_type=False tells SQLAlchemy NOT to emit CREATE TYPE itself when
# building the Column definition — we manage the lifecycle manually.
BOOKING_STATUS_ENUM = postgresql.ENUM(
    'PENDING', 'CONFIRMED', 'FAILED', 'CANCELLED',
    name='bookingstatus',
    create_type=False,   # we create it ourselves below
)


def upgrade() -> None:
    # Explicit creation with checkfirst so idempotent
    BOOKING_STATUS_ENUM.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'bookings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('centre_test_id', sa.Integer(), nullable=False),
        sa.Column('appointment_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', BOOKING_STATUS_ENUM, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['centre_test_id'], ['centre_tests.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_status'), 'bookings', ['status'], unique=False)
    op.create_index(op.f('ix_bookings_user_id'), 'bookings', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_bookings_user_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_status'), table_name='bookings')
    op.drop_table('bookings')
    BOOKING_STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
