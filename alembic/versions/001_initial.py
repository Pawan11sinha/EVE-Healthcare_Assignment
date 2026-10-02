"""initial

Revision ID: 001
Revises: 
Create Date: 2026-10-02 15:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'diagnostic_centres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnostic_centres_city'), 'diagnostic_centres', ['city'], unique=False)
    op.create_index(op.f('ix_diagnostic_centres_id'), 'diagnostic_centres', ['id'], unique=False)
    op.create_index(op.f('ix_diagnostic_centres_name'), 'diagnostic_centres', ['name'], unique=False)

    op.create_table(
        'diagnostic_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnostic_tests_id'), 'diagnostic_tests', ['id'], unique=False)
    op.create_index(op.f('ix_diagnostic_tests_name'), 'diagnostic_tests', ['name'], unique=True)

    op.create_table(
        'centre_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('centre_id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.CheckConstraint('price > 0', name='chk_price_positive'),
        sa.ForeignKeyConstraint(['centre_id'], ['diagnostic_centres.id'], ),
        sa.ForeignKeyConstraint(['test_id'], ['diagnostic_tests.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('centre_id', 'test_id', name='uq_centre_test')
    )
    op.create_index(op.f('ix_centre_tests_id'), 'centre_tests', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_centre_tests_id'), table_name='centre_tests')
    op.drop_table('centre_tests')
    op.drop_index(op.f('ix_diagnostic_tests_name'), table_name='diagnostic_tests')
    op.drop_index(op.f('ix_diagnostic_tests_id'), table_name='diagnostic_tests')
    op.drop_table('diagnostic_tests')
    op.drop_index(op.f('ix_diagnostic_centres_name'), table_name='diagnostic_centres')
    op.drop_index(op.f('ix_diagnostic_centres_id'), table_name='diagnostic_centres')
    op.drop_index(op.f('ix_diagnostic_centres_city'), table_name='diagnostic_centres')
    op.drop_table('diagnostic_centres')
