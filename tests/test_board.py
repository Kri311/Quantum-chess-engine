"""Tests for the Board class."""

import pytest

from engine.board import Board
from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position


class TestBoardCreation:
    """Board initialisation and basic properties."""

    def test_default_board_size(self) -> None:
        """Board defaults to 3x3."""
        board = Board()
        assert board.size == 3

    def test_custom_board_size(self) -> None:
        """Board accepts a custom size."""
        board = Board(size=8)
        assert board.size == 8

    def test_empty_board(self) -> None:
        """A new board has no pieces."""
        board = Board()
        assert board.piece_count == 0


class TestPiecePlacement:
    """Placing, querying, and removing pieces."""

    def test_place_and_get(self) -> None:
        """Placing a piece makes it retrievable."""
        board = Board()
        pos = Position(0, 0)
        piece = Piece(Color.WHITE, PieceType.PAWN)
        board.place_piece(pos, piece)
        assert board.get_piece(pos) == piece

    def test_is_occupied(self) -> None:
        """is_occupied reflects presence of a piece."""
        board = Board()
        pos = Position(1, 1)
        assert not board.is_occupied(pos)
        board.place_piece(pos, Piece(Color.BLACK, PieceType.PAWN))
        assert board.is_occupied(pos)

    def test_remove_piece(self) -> None:
        """Removing a piece returns it and empties the square."""
        board = Board()
        pos = Position(2, 2)
        piece = Piece(Color.WHITE, PieceType.PAWN)
        board.place_piece(pos, piece)
        removed = board.remove_piece(pos)
        assert removed == piece
        assert board.get_piece(pos) is None

    def test_remove_empty_square(self) -> None:
        """Removing from an empty square returns None."""
        board = Board()
        assert board.remove_piece(Position(0, 0)) is None

    def test_place_out_of_bounds(self) -> None:
        """Placing outside the board raises ValueError."""
        board = Board(size=2)
        with pytest.raises(ValueError):
            board.place_piece(Position(2, 2), Piece(Color.WHITE, PieceType.PAWN))



class TestBoardQueries:
    """Querying pieces by colour and bounds checking."""

    def test_pieces_by_color(self) -> None:
        """Filter pieces by colour."""
        board = Board()
        w = Piece(Color.WHITE, PieceType.PAWN)
        b = Piece(Color.BLACK, PieceType.PAWN)
        board.place_piece(Position(0, 0), w)
        board.place_piece(Position(2, 2), b)

        whites = list(board.pieces_by_color(Color.WHITE))
        blacks = list(board.pieces_by_color(Color.BLACK))
        assert len(whites) == 1
        assert len(blacks) == 1
        assert whites[0][1].color is Color.WHITE

    def test_is_within_bounds(self) -> None:
        """Bounds checking for various positions."""
        board = Board(size=3)
        assert board.is_within_bounds(Position(0, 0))
        assert board.is_within_bounds(Position(2, 2))

    def test_all_pieces(self) -> None:
        """all_pieces returns a snapshot."""
        board = Board()
        p = Piece(Color.WHITE, PieceType.PAWN)
        board.place_piece(Position(1, 1), p)
        pieces = board.all_pieces
        assert len(pieces) == 1
        # Modifying the snapshot doesn't affect the board.
        pieces.clear()
        assert board.piece_count == 1


class TestBoardCopy:
    """Deep copy semantics."""

    def test_copy_independence(self) -> None:
        """Copying creates an independent board."""
        board = Board()
        board.place_piece(Position(0, 0), Piece(Color.WHITE, PieceType.PAWN))
        copy = board.copy()
        copy.remove_piece(Position(0, 0))
        assert board.piece_count == 1
        assert copy.piece_count == 0


class TestBoardDisplay:
    """String representation."""

    def test_to_grid(self) -> None:
        """to_grid returns correct characters."""
        board = Board()
        board.place_piece(Position(0, 1), Piece(Color.BLACK, PieceType.PAWN))
        board.place_piece(Position(2, 1), Piece(Color.WHITE, PieceType.PAWN))
        grid = board.to_grid()
        assert grid[0][1] == "B"
        assert grid[2][1] == "W"
        assert grid[1][1] == "."

    def test_str_not_empty(self) -> None:
        """String representation is non-empty."""
        board = Board()
        assert len(str(board)) > 0
