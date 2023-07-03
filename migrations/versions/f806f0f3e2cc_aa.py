"""aa

Revision ID: f806f0f3e2cc
Revises: 8460fd8bae19
Create Date: 2023-05-23 23:40:04.387103

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f806f0f3e2cc'
down_revision = '8460fd8bae19'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('player_white_cards_player_id_fkey', 'player_white_cards', type_='foreignkey')
    op.drop_constraint('player_white_cards_card_id_fkey', 'player_white_cards', type_='foreignkey')
    op.create_foreign_key(None, 'player_white_cards', 'white_cards', ['card_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'player_white_cards', 'players', ['player_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'player_white_cards', type_='foreignkey')
    op.drop_constraint(None, 'player_white_cards', type_='foreignkey')
    op.create_foreign_key('player_white_cards_card_id_fkey', 'player_white_cards', 'white_cards', ['card_id'], ['id'])
    op.create_foreign_key('player_white_cards_player_id_fkey', 'player_white_cards', 'players', ['player_id'], ['id'])
    # ### end Alembic commands ###