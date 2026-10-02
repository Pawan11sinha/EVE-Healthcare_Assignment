"""webhook

Revision ID: 005
Revises: 004
Create Date: 2026-10-02 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'webhook_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('result', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhook_events_event_id'), 'webhook_events', ['event_id'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_webhook_events_event_id'), table_name='webhook_events')
    op.drop_table('webhook_events')
