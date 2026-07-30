"""Tests for the quantum BoardEncoder."""

import pytest

from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position
from quantum.encoder import BoardEncoder


class TestPositionEncoding:
    """Coordinate encoding per the base paper."""

    def test_square_1_encoding(self) -> None:
        """Square (0,0) encodes to '0000'."""
        assert BoardEncoder.encode_position(Position(0, 0), 3) == "0000"

    def test_square_2_encoding(self) -> None:
        """Square (0,1) encodes to '0100'."""
        assert BoardEncoder.encode_position(Position(0, 1), 3) == "0100"

    def test_square_3_encoding(self) -> None:
        """Square (0,2) encodes to '1000'."""
        assert BoardEncoder.encode_position(Position(0, 2), 3) == "1000"

    def test_square_4_encoding(self) -> None:
        """Square (1,0) encodes to '0001'."""
        assert BoardEncoder.encode_position(Position(1, 0), 3) == "0001"

    def test_square_5_encoding(self) -> None:
        """Square (1,1) encodes to '0101'."""
        assert BoardEncoder.encode_position(Position(1, 1), 3) == "0101"

    def test_square_6_encoding(self) -> None:
        """Square (1,2) encodes to '1001'."""
        assert BoardEncoder.encode_position(Position(1, 2), 3) == "1001"

    def test_square_7_encoding(self) -> None:
        """Square (2,0) encodes to '0010'."""
        assert BoardEncoder.encode_position(Position(2, 0), 3) == "0010"

    def test_square_8_encoding(self) -> None:
        """Square (2,1) encodes to '0110'."""
        assert BoardEncoder.encode_position(Position(2, 1), 3) == "0110"

    def test_square_9_encoding(self) -> None:
        """Square (2,2) encodes to '1010'."""
        assert BoardEncoder.encode_position(Position(2, 2), 3) == "1010"


class TestPositionRoundTrip:
    """Encode then decode should be identity."""

    def test_all_squares_round_trip(self) -> None:
        """Every 3x3 position survives encode/decode."""
        for row in range(3):
            for col in range(3):
                pos = Position(row, col)
                bits = BoardEncoder.encode_position(pos, 3)
                decoded = BoardEncoder.decode_position_bitstring(bits, 3)
                assert decoded == pos, f"Failed for {pos}: {bits} -> {decoded}"


class TestStatusEncoding:
    """Piece status encoding per the base paper."""

    def test_empty_status(self) -> None:
        """Empty square encodes to '00'."""
        assert BoardEncoder.encode_status(None) == "00"

    def test_black_pawn_status(self) -> None:
        """Black pawn encodes to '01'."""
        piece = Piece(Color.BLACK, PieceType.PAWN)
        assert BoardEncoder.encode_status(piece) == "01"

    def test_white_pawn_status(self) -> None:
        """White pawn encodes to '10'."""
        piece = Piece(Color.WHITE, PieceType.PAWN)
        assert BoardEncoder.encode_status(piece) == "10"


class TestStatusRoundTrip:
    """Status encode/decode round trip."""

    def test_empty_round_trip(self) -> None:
        """Empty survives round trip."""
        assert BoardEncoder.decode_status_bitstring("00") is None

    def test_black_round_trip(self) -> None:
        """Black pawn survives round trip."""
        piece = BoardEncoder.decode_status_bitstring("01")
        assert piece is not None
        assert piece.color is Color.BLACK

    def test_white_round_trip(self) -> None:
        """White pawn survives round trip."""
        piece = BoardEncoder.decode_status_bitstring("10")
        assert piece is not None
        assert piece.color is Color.WHITE

    def test_invalid_status(self) -> None:
        """Invalid status raises ValueError."""
        with pytest.raises(ValueError):
            BoardEncoder.decode_status_bitstring("11")


class TestBoardEncoding:
    """Full board encoding."""

    def test_encode_board(self) -> None:
        """Encoding a board produces entries for all squares."""
        from engine.board import Board
        from engine.state import GameState

        board = Board(size=3)
        board.place_piece(Position(0, 1), Piece(Color.BLACK, PieceType.PAWN))
        board.place_piece(Position(2, 1), Piece(Color.WHITE, PieceType.PAWN))
        state = GameState(board=board)

        encoded = BoardEncoder.encode_board(state)
        assert len(encoded) == 9  # 3x3 = 9 squares.

        # Check specific squares.
        assert encoded["(0,1)"][1] == "01"  # Black pawn.
        assert encoded["(2,1)"][1] == "10"  # White pawn.
        assert encoded["(1,1)"][1] == "00"  # Empty.
