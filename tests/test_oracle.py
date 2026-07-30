"""Tests for the MoveOracle."""

from engine.board import Board
from engine.constants import Color, PieceType
from engine.move import Move
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from quantum.oracle import MoveOracle


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


class TestCandidateGeneration:
    """Generate all candidate moves."""

    def test_generates_candidates(self) -> None:
        """Candidate list is non-empty for a typical position."""
        state = _make_state((2, 1), (0, 1))
        candidates = MoveOracle.generate_all_candidates(state)
        assert len(candidates) > 0

    def test_candidates_include_legal_and_illegal(self) -> None:
        """Candidates include both legal and illegal moves."""
        state = _make_state((2, 1), (0, 1))
        candidates = MoveOracle.generate_all_candidates(state)
        legal = MoveOracle.compute_legal_indices(state, candidates)
        # Should have at least one legal move and at least one
        # candidate that is NOT legal (diagonal without enemy).
        assert len(legal) >= 1
        assert len(legal) < len(candidates)


class TestLegalIndices:
    """Compute which candidate indices are legal."""

    def test_forward_move_is_legal(self) -> None:
        """Forward move into empty square is marked legal."""
        state = _make_state((2, 1), (0, 1))
        candidates = MoveOracle.generate_all_candidates(state)
        legal = MoveOracle.compute_legal_indices(state, candidates)
        # Find the forward move index.
        for idx in legal:
            m = candidates[idx]
            if m.end == Position(1, 1) and not m.capture:
                break
        else:
            assert False, "Forward move not in legal indices"

    def test_capture_marked_legal(self) -> None:
        """Diagonal capture is marked legal when enemy is present."""
        state = _make_state((2, 1), (1, 0))
        candidates = MoveOracle.generate_all_candidates(state)
        legal = MoveOracle.compute_legal_indices(state, candidates)
        capture_found = any(
            candidates[i].capture for i in legal
        )
        assert capture_found


class TestOracleCircuit:
    """Oracle circuit construction."""

    def test_oracle_builds_without_error(self) -> None:
        """Oracle circuit can be constructed."""
        from qiskit import QuantumCircuit, QuantumRegister

        n_qubits = 2
        move_reg = QuantumRegister(n_qubits, "move")
        flag_reg = QuantumRegister(1, "flag")
        circuit = QuantumCircuit(move_reg, flag_reg)

        legal_indices = [1]  # Mark index 1 as legal.
        MoveOracle.build_legality_oracle(
            circuit, move_reg, flag_reg, legal_indices, n_qubits
        )

        # Should have added gates.
        assert circuit.size() > 0

    def test_phase_oracle_builds(self) -> None:
        """Phase oracle can be constructed."""
        from qiskit import QuantumCircuit, QuantumRegister

        n_qubits = 2
        move_reg = QuantumRegister(n_qubits, "move")
        flag_reg = QuantumRegister(1, "flag")
        circuit = QuantumCircuit(move_reg, flag_reg)

        MoveOracle.build_phase_oracle(
            circuit, move_reg, flag_reg, [0, 1], n_qubits
        )
        assert circuit.size() > 0
