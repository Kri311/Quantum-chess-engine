"""Integration tests — end-to-end workflows."""

from engine.board import Board
from engine.constants import Color, PieceType
from engine.evaluator import Evaluator
from engine.game import Game
from engine.move import Move
from engine.move_generator import MoveGenerator
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from quantum.encoder import BoardEncoder
from quantum.decoder import BoardDecoder


class TestClassicalGamePlay:
    """Full classical game loop."""

    def test_game_creation(self) -> None:
        """Game initialises with correct starting state."""
        game = Game()
        assert game.state.current_turn is Color.WHITE
        assert game.state.board.piece_count == 2

    def test_make_move(self) -> None:
        """Making a move updates the game state."""
        game = Game()
        moves = game.get_legal_moves()
        assert len(moves) > 0
        game.make_move(moves[0])
        assert game.state.current_turn is Color.BLACK

    def test_full_game_terminates(self) -> None:
        """A sequence of moves leads to a terminal state."""
        game = Game()
        max_moves = 20  # Safety limit.
        for _ in range(max_moves):
            if game.is_over():
                break
            moves = game.get_legal_moves()
            if not moves:
                break
            game.make_move(moves[0])
        # Game should terminate within 20 moves on a 3x3 board.
        assert game.is_over() or len(game.get_legal_moves()) == 0

    def test_game_reset(self) -> None:
        """Reset returns the game to starting position."""
        game = Game()
        game.make_move(game.get_legal_moves()[0])
        game.reset()
        assert game.state.current_turn is Color.WHITE
        assert len(game.state.move_history) == 0


class TestEncoderDecoderRoundTrip:
    """Encode classical state to quantum and decode back."""

    def test_position_round_trip_all_squares(self) -> None:
        """Every 3x3 position survives encode → decode."""
        for row in range(3):
            for col in range(3):
                pos = Position(row, col)
                encoded = BoardEncoder.encode_position(pos, 3)
                decoded = BoardDecoder.decode_position(encoded, 3)
                assert decoded == pos

    def test_status_round_trip(self) -> None:
        """Piece statuses survive encode → decode."""
        for piece, expected_bits in [
            (None, "00"),
            (Piece(Color.BLACK, PieceType.PAWN), "01"),
            (Piece(Color.WHITE, PieceType.PAWN), "10"),
        ]:
            bits = BoardEncoder.encode_status(piece)
            assert bits == expected_bits
            decoded = BoardDecoder.decode_status(bits)
            if piece is None:
                assert decoded is None
            else:
                assert decoded is not None
                assert decoded.color is piece.color

    def test_board_encoding_completeness(self) -> None:
        """Board encoding produces entries for all 9 squares."""
        board = Board(size=3)
        board.place_piece(Position(2, 1), Piece(Color.WHITE, PieceType.PAWN))
        board.place_piece(Position(0, 1), Piece(Color.BLACK, PieceType.PAWN))
        state = GameState(board=board)

        encoded = BoardEncoder.encode_board(state)
        assert len(encoded) == 9

        # Verify paper Table II encoding values.
        expected_coords = {
            "(0,0)": "0000",
            "(0,1)": "0100",
            "(0,2)": "1000",
            "(1,0)": "0001",
            "(1,1)": "0101",
            "(1,2)": "1001",
            "(2,0)": "0010",
            "(2,1)": "0110",
            "(2,2)": "1010",
        }
        for key, expected_coord in expected_coords.items():
            assert encoded[key][0] == expected_coord, (
                f"Coordinate mismatch for {key}: "
                f"got {encoded[key][0]}, expected {expected_coord}"
            )


class TestEvaluatorIntegration:
    """Evaluator with real game states."""

    def test_initial_position_balanced(self) -> None:
        """Initial position has roughly balanced evaluation."""
        game = Game()
        score = Evaluator.evaluate(game.state)
        # Should be close to 0 (balanced).
        assert abs(score) < 5.0

    def test_white_promotion_wins(self) -> None:
        """White reaching row 0 gives a large positive score."""
        board = Board(size=3)
        board.place_piece(Position(0, 1), Piece(Color.WHITE, PieceType.PAWN))
        board.place_piece(Position(2, 0), Piece(Color.BLACK, PieceType.PAWN))
        state = GameState(board=board)
        score = Evaluator.evaluate(state)
        assert score > 50.0

    def test_black_promotion_wins(self) -> None:
        """Black reaching last row gives a large negative score."""
        board = Board(size=3)
        board.place_piece(Position(2, 0), Piece(Color.WHITE, PieceType.PAWN))
        board.place_piece(Position(2, 1), Piece(Color.BLACK, PieceType.PAWN))
        state = GameState(board=board)
        score = Evaluator.evaluate(state)
        assert score < -50.0
