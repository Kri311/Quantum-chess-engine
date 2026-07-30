"""Tests for the Pure Quantum Engine package."""

import pytest

from engine.board import Board
from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from pure_quantum_engine.registers import PureQuantumRegisters
from pure_quantum_engine.circuit import PureQuantumCircuitBuilder
from pure_quantum_engine.engine import PureQuantumEngine


def _make_state() -> GameState:
    board = Board(size=3)
    board.place_piece(Position(2, 1), Piece(Color.WHITE, PieceType.PAWN))
    board.place_piece(Position(0, 1), Piece(Color.BLACK, PieceType.PAWN))
    return GameState(board=board, current_turn=Color.WHITE)


class TestPureQuantumRegisters:
    """Register allocation tests."""

    def test_register_allocation_count(self) -> None:
        regs = PureQuantumRegisters(board_size=3)
        # 4 + 4 + 2 + 2 + 2 + 5 = 19 qubits
        assert regs.total_qubits == 19


class TestPureQuantumCircuit:
    """Circuit assembly tests."""

    def test_build_circuit(self) -> None:
        state = _make_state()
        circuit, regs = PureQuantumCircuitBuilder.build_full_chess_circuit(
            state, Position(2, 1), Position(1, 1), Color.WHITE
        )
        assert circuit.num_qubits == 19
        assert circuit.depth() > 0
        assert circuit.count_ops()["measure"] == 19


class TestPureQuantumEngineExecution:
    """Engine execution tests."""

    def test_execute_move(self) -> None:
        state = _make_state()
        engine = PureQuantumEngine()
        counts, metrics = engine.execute_move(
            state, Position(2, 1), Position(1, 1), Color.WHITE
        )
        assert metrics.num_qubits == 19
        assert metrics.total_gates > 15
        assert metrics.execution_time_ms > 0
        assert len(counts) > 0
