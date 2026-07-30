"""Tests for GameState."""

from engine.board import Board
from engine.constants import Color, PieceType
from engine.evaluator import Evaluator
from engine.move import Move
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState


def _initial_state() -> GameState:
    """Create the standard starting state."""
    board = Board(size=3)
    board.place_piece(Position(2, 1), Piece(Color.WHITE, PieceType.PAWN))
    board.place_piece(Position(0, 1), Piece(Color.BLACK, PieceType.PAWN))
    return GameState(board=board, current_turn=Color.WHITE)


class TestGameStateBasics:
    """State creation and turn management."""

    def test_initial_turn(self) -> None:
        """Game starts with White's turn."""
        state = _initial_state()
        assert state.current_turn is Color.WHITE

    def test_switch_turn(self) -> None:
        """switch_turn toggles the current player."""
        state = _initial_state()
        state.switch_turn()
        assert state.current_turn is Color.BLACK
        state.switch_turn()
        assert state.current_turn is Color.WHITE

    def test_empty_move_history(self) -> None:
        """Initial state has empty move history."""
        state = _initial_state()
        assert len(state.move_history) == 0


class TestApplyMove:
    """Applying moves to GameState."""

    def test_apply_move_creates_new_state(self) -> None:
        """apply_move returns a new state, not a mutation."""
        state = _initial_state()
        move = Move(Position(2, 1), Position(1, 1))
        new_state = state.apply_move(move)
        assert new_state is not state
        assert new_state.board is not state.board

    def test_apply_move_switches_turn(self) -> None:
        """After applying a move, the turn switches."""
        state = _initial_state()
        move = Move(Position(2, 1), Position(1, 1))
        new_state = state.apply_move(move)
        assert new_state.current_turn is Color.BLACK

    def test_apply_move_updates_board(self) -> None:
        """The piece moves to the new position."""
        state = _initial_state()
        move = Move(Position(2, 1), Position(1, 1))
        new_state = state.apply_move(move)
        assert new_state.board.get_piece(Position(1, 1)) is not None
        assert new_state.board.get_piece(Position(2, 1)) is None

    def test_apply_capture_removes_enemy(self) -> None:
        """Capture removes the enemy piece."""
        board = Board(size=3)
        board.place_piece(Position(2, 1), Piece(Color.WHITE, PieceType.PAWN))
        board.place_piece(Position(1, 0), Piece(Color.BLACK, PieceType.PAWN))
        state = GameState(board=board, current_turn=Color.WHITE)

        move = Move(Position(2, 1), Position(1, 0), capture=True)
        new_state = state.apply_move(move)

        assert new_state.board.get_piece(Position(1, 0)).color is Color.WHITE
        assert new_state.board.piece_count == 1

    def test_apply_move_records_history(self) -> None:
        """Move history is updated."""
        state = _initial_state()
        move = Move(Position(2, 1), Position(1, 1))
        new_state = state.apply_move(move)
        assert len(new_state.move_history) == 1
        assert new_state.move_history[0] == move


class TestTerminalDetection:
    """Game-over detection."""

    def test_not_terminal_initially(self) -> None:
        """Initial position is not terminal."""
        state = _initial_state()
        assert state.is_terminal() is False

    def test_white_promotion_terminal(self) -> None:
        """White reaching row 0 is terminal."""
        board = Board(size=3)
        board.place_piece(Position(0, 1), Piece(Color.WHITE, PieceType.PAWN))
        board.place_piece(Position(2, 0), Piece(Color.BLACK, PieceType.PAWN))
        state = GameState(board=board)
        assert state.is_terminal() is True

    def test_capture_terminal(self) -> None:
        """Capturing the only enemy piece is terminal."""
        board = Board(size=3)
        board.place_piece(Position(1, 1), Piece(Color.WHITE, PieceType.PAWN))
        state = GameState(board=board)
        assert state.is_terminal() is True  # Black has no pieces.


class TestWinnerDetection:
    """Winner detection via Evaluator."""

    def test_white_wins_promotion(self) -> None:
        """White wins by reaching row 0."""
        board = Board(size=3)
        board.place_piece(Position(0, 1), Piece(Color.WHITE, PieceType.PAWN))
        board.place_piece(Position(2, 0), Piece(Color.BLACK, PieceType.PAWN))
        state = GameState(board=board)
        assert Evaluator.winner(state) is Color.WHITE

    def test_black_wins_promotion(self) -> None:
        """Black wins by reaching the last row."""
        board = Board(size=3)
        board.place_piece(Position(2, 0), Piece(Color.WHITE, PieceType.PAWN))
        board.place_piece(Position(2, 1), Piece(Color.BLACK, PieceType.PAWN))
        state = GameState(board=board)
        assert Evaluator.winner(state) is Color.BLACK

    def test_no_winner_yet(self) -> None:
        """No winner in the initial position."""
        state = _initial_state()
        assert Evaluator.winner(state) is None
