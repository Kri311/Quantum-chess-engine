"""
Quantum to Classical decoder.

Converts measurement bitstrings back into classical chess objects.
"""

from __future__ import annotations

import math

import config
from engine.board import Board
from engine.constants import Color
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from quantum.encoder import BoardEncoder


class BoardDecoder:
    """Decodes quantum measurement results into classical chess state."""

    @staticmethod
    def decode_position(bitstring: str, board_size: int | None = None) -> Position:
        """Decode a coordinate bitstring to a Position.

        Args:
            bitstring: Encoded coordinate e.g. "0110".
            board_size: Side length. Defaults to config.BOARD_SIZE.

        Returns:
            Decoded Position.
        """
        return BoardEncoder.decode_position_bitstring(bitstring, board_size)

    @staticmethod
    def decode_status(bitstring: str) -> Piece | None:
        """Decode a 2-bit status bitstring.

        Args:
            bitstring: "00", "01", or "10".

        Returns:
            None for vacant, Piece otherwise.
        """
        return BoardEncoder.decode_status_bitstring(bitstring)

    @staticmethod
    def decode_measurement(
        bitstring: str, board_size: int | None = None,
    ) -> dict[str, str]:
        """Parse a full measurement bitstring into labelled fields.

        Layout MSB to LSB:
            flag(1) | dst(2) | src(2) | dir(2) | target(4) | current(4)

        Args:
            bitstring: Raw measurement result.
            board_size: Side length.

        Returns:
            Dict with current, target, direction, src_status,
            dst_status, flag.
        """
        size = board_size if board_size is not None else config.BOARD_SIZE
        axis_bits = math.ceil(math.log2(size)) if size > 1 else 1
        coord_len = axis_bits * 2

        bits = bitstring[::-1]

        idx = 0
        current = bits[idx: idx + coord_len]
        idx += coord_len
        target = bits[idx: idx + coord_len]
        idx += coord_len
        direction = bits[idx: idx + 2]
        idx += 2
        src_status = bits[idx: idx + 2]
        idx += 2
        dst_status = bits[idx: idx + 2]
        idx += 2
        flag = bits[idx: idx + 1] if idx < len(bits) else "0"

        return {
            "current": current,
            "target": target,
            "direction": direction,
            "src_status": src_status,
            "dst_status": dst_status,
            "flag": flag,
        }

    @staticmethod
    def decode_move_index(bitstring: str, n_move_qubits: int) -> int:
        """Decode a move-index bitstring from Grover measurement.

        Args:
            bitstring: Binary string representing the move index.
            n_move_qubits: Number of qubits encoding the move index.

        Returns:
            Integer move index.
        """
        relevant = bitstring[-n_move_qubits:]
        return int(relevant[::-1], 2)

    @staticmethod
    def decode_board(
        measurement_results: dict[str, int],
        board_size: int | None = None,
    ) -> GameState:
        """Reconstruct a GameState from measurement counts.

        Args:
            measurement_results: {bitstring: count} from simulator.
            board_size: Side length.

        Returns:
            Reconstructed GameState.
        """
        size = board_size if board_size is not None else config.BOARD_SIZE
        best = max(measurement_results, key=lambda k: measurement_results[k])
        fields = BoardDecoder.decode_measurement(best, size)

        board = Board(size=size)
        src_piece = BoardDecoder.decode_status(fields["src_status"])
        dst_piece = BoardDecoder.decode_status(fields["dst_status"])
        src_pos = BoardDecoder.decode_position(fields["current"], size)
        dst_pos = BoardDecoder.decode_position(fields["target"], size)

        if src_piece is not None:
            board.place_piece(src_pos, src_piece)
        if dst_piece is not None:
            board.place_piece(dst_pos, dst_piece)

        return GameState(board=board, current_turn=Color.WHITE)
