"""
Tests for 8x8 Board expansion and Knight movement rules.
"""

from engine.board import Board
from engine.constants import Color, PieceType
from engine.move import Move
from engine.piece import Piece
from engine.position import Position
from engine.rules import Rules
from engine.state import GameState
from quantum.encoder import BoardEncoder


def test_knight_moves_valid():
    """Verify knight L-shape movement logic."""
    board = Board(size=8)
    # Place a white knight in the middle of the board
    knight_pos = Position(4, 4)
    board.place_piece(knight_pos, Piece(Color.WHITE, PieceType.KNIGHT))
    
    state = GameState(board=board, current_turn=Color.WHITE)
    
    # Valid L-shapes
    valid_destinations = [
        Position(2, 3), Position(2, 5),
        Position(6, 3), Position(6, 5),
        Position(3, 2), Position(3, 6),
        Position(5, 2), Position(5, 6)
    ]
    
    for dest in valid_destinations:
        move = Move(knight_pos, dest)
        assert Rules.is_valid_move(state, move) is True

def test_status_encoder_update():
    """Verify 3-bit status encoding for pawns and knights."""
    white_pawn = Piece(Color.WHITE, PieceType.PAWN)
    black_knight = Piece(Color.BLACK, PieceType.KNIGHT)
    
    assert BoardEncoder.encode_status(white_pawn) == "101"
    assert BoardEncoder.encode_status(black_knight) == "010"
    assert BoardEncoder.encode_status(None) == "000"

    decoded_knight = BoardEncoder.decode_status_bitstring("010")
    assert decoded_knight.piece_type == PieceType.KNIGHT
    assert decoded_knight.color == Color.BLACK
