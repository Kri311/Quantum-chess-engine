"""Tests for the Move class."""

import pytest

from engine.constants import Color, Direction
from engine.move import Move
from engine.position import Position


class TestMoveCreation:
    """Move instantiation and properties."""

    def test_basic_move(self) -> None:
        """Create a non-capture move."""
        m = Move(start=Position(2, 1), end=Position(1, 1))
        assert m.start == Position(2, 1)
        assert m.end == Position(1, 1)
        assert m.capture is False

    def test_capture_move(self) -> None:
        """Create a capture move."""
        m = Move(start=Position(2, 1), end=Position(1, 0), capture=True)
        assert m.capture is True

    def test_frozen(self) -> None:
        """Moves are immutable."""
        m = Move(start=Position(0, 0), end=Position(1, 0))
        with pytest.raises(AttributeError):
            m.capture = True  # type: ignore[misc]


class TestMoveDirection:
    """Direction detection for pawn moves."""

    def test_white_forward(self) -> None:
        """White moves upward (decreasing row)."""
        m = Move(start=Position(2, 1), end=Position(1, 1))
        assert m.direction(Color.WHITE) is Direction.FORWARD

    def test_black_forward(self) -> None:
        """Black moves downward (increasing row)."""
        m = Move(start=Position(0, 1), end=Position(1, 1))
        assert m.direction(Color.BLACK) is Direction.FORWARD

    def test_white_diagonal_left(self) -> None:
        """White diagonal left capture."""
        m = Move(start=Position(2, 1), end=Position(1, 0), capture=True)
        assert m.direction(Color.WHITE) is Direction.DIAGONAL_LEFT

    def test_white_diagonal_right(self) -> None:
        """White diagonal right capture."""
        m = Move(start=Position(2, 1), end=Position(1, 2), capture=True)
        assert m.direction(Color.WHITE) is Direction.DIAGONAL_RIGHT

    def test_black_diagonal_left(self) -> None:
        """Black diagonal left capture."""
        m = Move(start=Position(0, 1), end=Position(1, 0), capture=True)
        assert m.direction(Color.BLACK) is Direction.DIAGONAL_LEFT

    def test_black_diagonal_right(self) -> None:
        """Black diagonal right capture."""
        m = Move(start=Position(0, 1), end=Position(1, 2), capture=True)
        assert m.direction(Color.BLACK) is Direction.DIAGONAL_RIGHT

    def test_invalid_direction(self) -> None:
        """Non-pawn displacement raises ValueError."""
        m = Move(start=Position(0, 0), end=Position(2, 2))
        with pytest.raises(ValueError):
            m.direction(Color.WHITE)


class TestMoveDisplay:
    """String representation."""

    def test_str_noncapture(self) -> None:
        """Non-capture move string."""
        m = Move(start=Position(2, 1), end=Position(1, 1))
        s = str(m)
        assert "→" in s
        assert "×" not in s

    def test_str_capture(self) -> None:
        """Capture move string includes capture marker."""
        m = Move(start=Position(2, 1), end=Position(1, 0), capture=True)
        s = str(m)
        assert "×" in s
