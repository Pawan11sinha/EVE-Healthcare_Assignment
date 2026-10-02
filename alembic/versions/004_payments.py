"""payments

Revision ID: 004
Revises: 003
Create Date: 2026-10-02 18:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

# create_type=False: we manage the enum lifecycle manually (checkfirst).
PAYMENT_STATUS_ENUM = postgresql.ENUM(
    'PENDING', 'SUCCESS', 'FAILED',
    name='paymentstatus',
    create_type=False,
)


def upgrade() -> None:
    PAYMENT_STATUS_ENUM.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('booking_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', PAYMENT_STATUS_ENUM, nullable=False),
        sa.Column('provider_reference', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_booking_id'), 'payments', ['booking_id'], unique=False)
    op.create_index(op.f('ix_payments_provider_reference'), 'payments', ['provider_reference'], unique=True)
    op.create_index(op.f('ix_payments_status'), 'payments', ['status'], unique=False)
    op.create_index(op.f('ix_payments_user_id'), 'payments', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_payments_user_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_status'), table_name='payments')
    op.drop_index(op.f('ix_payments_provider_reference'), table_name='payments')
    op.drop_index(op.f('ix_payments_booking_id'), table_name='payments')
    op.drop_table('payments')
    PAYMENT_STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
