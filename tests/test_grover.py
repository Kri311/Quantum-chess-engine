"""Tests for Grover's search algorithm."""

import math

from engine.board import Board
from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from quantum.grover import GroverSearch
from quantum.diffuser import GroverDiffuser


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


class TestIterationCalculation:
    """Optimal Grover iteration count."""

    def test_single_solution(self) -> None:
        """One solution in 4 items: floor(pi/4 * sqrt(4)) = 1."""
        iters = GroverSearch.calculate_iterations(4, 1)
        assert iters == 1

    def test_single_solution_large(self) -> None:
        """One solution in 16 items: floor(pi/4 * 4) = 3."""
        iters = GroverSearch.calculate_iterations(16, 1)
        assert iters == 3

    def test_half_solutions(self) -> None:
        """Half solutions: floor(pi/4 * sqrt(2)) = 1."""
        iters = GroverSearch.calculate_iterations(4, 2)
        assert iters == 1

    def test_all_solutions(self) -> None:
        """All items are solutions: returns 1."""
        iters = GroverSearch.calculate_iterations(4, 4)
        assert iters == 1

    def test_no_solutions(self) -> None:
        """No solutions: returns 1."""
        iters = GroverSearch.calculate_iterations(4, 0)
        assert iters == 1


class TestDiffuserCircuit:
    """Grover diffuser construction."""

    def test_diffuser_builds(self) -> None:
        """Standalone diffuser circuit is created."""
        circuit = GroverDiffuser.build_diffuser_circuit(3)
        assert circuit.num_qubits == 3
        assert circuit.size() > 0

    def test_diffuser_appends_to_circuit(self) -> None:
        """Diffuser can be appended to an existing circuit."""
        from qiskit import QuantumCircuit, QuantumRegister

        qr = QuantumRegister(2, "q")
        circuit = QuantumCircuit(qr)
        initial_size = circuit.size()
        GroverDiffuser.build_diffuser(circuit, qr)
        assert circuit.size() > initial_size


class TestGroverSearch:
    """End-to-end Grover search."""

    def test_search_returns_legal_move(self) -> None:
        """Grover search returns a legal move."""
        state = _make_state((2, 1), (0, 1))
        grover = GroverSearch()
        result = grover.search(state)
        assert result is not None
        # The result should be a legal move.
        from engine.move_generator import MoveGenerator

        legal_moves = MoveGenerator.generate_legal_moves(state)
        legal_pairs = {(m.start, m.end) for m in legal_moves}
        assert (result.start, result.end) in legal_pairs

    def test_search_with_capture(self) -> None:
        """Grover search handles positions with captures."""
        state = _make_state((2, 1), (1, 0))
        grover = GroverSearch()
        result = grover.search(state)
        assert result is not None

    def test_search_no_moves(self) -> None:
        """Grover search returns None when no candidates exist."""
        # Create a state with no pieces for current player.
        board = Board(size=3)
        board.place_piece(
            Position(0, 1), Piece(Color.BLACK, PieceType.PAWN)
        )
        state = GameState(board=board, current_turn=Color.WHITE)
        grover = GroverSearch()
        result = grover.search(state)
        assert result is None
