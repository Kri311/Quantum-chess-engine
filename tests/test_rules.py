"""Tests for Rules and MoveGenerator."""

import pytest

from engine.board import Board
from engine.constants import Color, PieceType
from engine.move import Move
from engine.move_generator import MoveGenerator
from engine.piece import Piece
from engine.position import Position
from engine.rules import Rules
from engine.state import GameState


def _make_state(
    white_pos: tuple[int, int],
    black_pos: tuple[int, int],
    turn: Color = Color.WHITE,
) -> GameState:
    """Helper to create a state with one pawn per side."""
    board = Board(size=3)
    board.place_piece(
        Position(*white_pos), Piece(Color.WHITE, PieceType.PAWN)
    )
    board.place_piece(
        Position(*black_pos), Piece(Color.BLACK, PieceType.PAWN)
    )
    return GameState(board=board, current_turn=turn)


class TestRulesValidation:
    """Move validation via Rules.is_valid_move."""

    def test_white_forward_valid(self) -> None:
        """White pawn can move forward into empty square."""
        state = _make_state((2, 1), (0, 1))
        move = Move(Position(2, 1), Position(1, 1))
        assert Rules.is_valid_move(state, move) is True

    def test_white_forward_blocked(self) -> None:
        """White pawn cannot move forward into occupied square."""
        state = _make_state((2, 1), (1, 1))
        move = Move(Position(2, 1), Position(1, 1))
        assert Rules.is_valid_move(state, move) is False

    def test_white_diagonal_capture(self) -> None:
        """White pawn can capture diagonally."""
        state = _make_state((2, 1), (1, 0))
        move = Move(Position(2, 1), Position(1, 0), capture=True)
        assert Rules.is_valid_move(state, move) is True

    def test_white_diagonal_no_enemy(self) -> None:
        """White pawn cannot move diagonally without an enemy."""
        state = _make_state((2, 1), (0, 0))
        move = Move(Position(2, 1), Position(1, 0), capture=True)
        assert Rules.is_valid_move(state, move) is False

    def test_black_forward(self) -> None:
        """Black pawn can move forward (increasing row)."""
        state = _make_state((2, 1), (0, 1), turn=Color.BLACK)
        move = Move(Position(0, 1), Position(1, 1))
        assert Rules.is_valid_move(state, move) is True

    def test_wrong_color_piece(self) -> None:
        """Cannot move opponent's piece."""
        state = _make_state((2, 1), (0, 1))
        move = Move(Position(0, 1), Position(1, 1))
        assert Rules.is_valid_move(state, move) is False

    def test_backward_move_invalid(self) -> None:
        """Pawns cannot move backward."""
        state = _make_state((1, 1), (0, 1))
        move = Move(Position(1, 1), Position(2, 1))
        assert Rules.is_valid_move(state, move) is False


class TestMoveGenerator:
    """Legal move generation."""

    def test_initial_white_moves(self) -> None:
        """White has exactly one forward move from initial position."""
        state = _make_state((2, 1), (0, 1))
        moves = MoveGenerator.generate_legal_moves(state)
        assert len(moves) == 1
        assert moves[0].end == Position(1, 1)

    def test_capture_available(self) -> None:
        """Diagonal capture appears in legal moves."""
        state = _make_state((2, 1), (1, 0))
        moves = MoveGenerator.generate_legal_moves(state)
        captures = [m for m in moves if m.capture]
        assert len(captures) == 1
        assert captures[0].end == Position(1, 0)

    def test_no_moves_blocked(self) -> None:
        """No moves when pawn is completely blocked."""
        state = _make_state((1, 0), (0, 0))
        moves = MoveGenerator.generate_legal_moves(state)
        # White at (1,0), Black at (0,0): forward blocked,
        # diagonal (0,1) is empty so no capture.
        # White can only capture at (0, 1) if black is there.
        forward_moves = [m for m in moves if not m.capture]
        assert len(forward_moves) == 0

    def test_moves_for_position(self) -> None:
        """Generate moves for a specific position."""
        state = _make_state((2, 1), (0, 1))
        moves = MoveGenerator.generate_moves_for_position(
            state, Position(2, 1)
        )
        assert len(moves) >= 1

    def test_empty_position_moves(self) -> None:
        """No moves for an empty square."""
        state = _make_state((2, 1), (0, 1))
        moves = MoveGenerator.generate_moves_for_position(
            state, Position(1, 1)
        )
        assert len(moves) == 0


class TestRulesHelpers:
    """Helper methods on Rules."""

    def test_check_bounds_valid(self) -> None:
        """Valid position is within bounds."""
        assert Rules.check_bounds(Position(0, 0), 3) is True
        assert Rules.check_bounds(Position(2, 2), 3) is True

    def test_is_forward_move(self) -> None:
        """Detect forward moves."""
        m = Move(Position(2, 1), Position(1, 1))
        assert Rules.is_forward_move(m, Color.WHITE) is True
        assert Rules.is_forward_move(m, Color.BLACK) is False

    def test_is_diagonal_capture(self) -> None:
        """Detect diagonal captures."""
        m = Move(Position(2, 1), Position(1, 0), capture=True)
        assert Rules.is_diagonal_capture(m, Color.WHITE) is True
