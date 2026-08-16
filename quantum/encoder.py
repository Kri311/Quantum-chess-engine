"""
Classical → Quantum encoder.

``BoardEncoder`` translates classical board positions and piece statuses
into qubit bitstrings following the base paper's encoding scheme:

Coordinate encoding (3×3):
    Square 1 (row 0, col 0) → |x1 x0 y1 y0⟩ = |0000⟩
    Square 2 (row 0, col 1) → |0100⟩
    Square 3 (row 0, col 2) → |1000⟩
    Square 4 (row 1, col 0) → |0001⟩
    Square 5 (row 1, col 1) → |0101⟩
    Square 6 (row 1, col 2) → |1001⟩
    Square 7 (row 2, col 0) → |0010⟩
    Square 8 (row 2, col 1) → |0110⟩
    Square 9 (row 2, col 2) → |1010⟩

Status encoding:
    Empty      → |00⟩
    Black Pawn → |01⟩
    White Pawn → |10⟩
"""

from __future__ import annotations

import math

from qiskit import QuantumCircuit, QuantumRegister

import config
from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState


class BoardEncoder:
    """Encodes classical chess state into quantum register bitstrings."""

    # ------------------------------------------------------------------
    # Position encoding
    # ------------------------------------------------------------------

    @staticmethod
    def encode_position(position: Position, board_size: int | None = None) -> str:
        """Encode a board position as a qubit bitstring.

        The encoding follows the base paper: the column (X) is stored
        in the higher-order pair of qubits and the row (Y) in the
        lower-order pair.  Each axis uses ``ceil(log2(board_size))``
        bits.

        Args:
            position: Board coordinate to encode.
            board_size: Side length.  Defaults to ``config.BOARD_SIZE``.

        Returns:
            Bitstring of length ``2 * ceil(log2(board_size))``, e.g.
            ``"0110"`` for position (row=2, col=1) on a 3×3 board.

        Example:
            >>> BoardEncoder.encode_position(Position(0, 0), 3)
            '0000'
            >>> BoardEncoder.encode_position(Position(2, 1), 3)
            '0110'
        """
        size = board_size if board_size is not None else config.BOARD_SIZE
        axis_bits = math.ceil(math.log2(size)) if size > 1 else 1

        col_bin = format(position.col, f"0{axis_bits}b")
        row_bin = format(position.row, f"0{axis_bits}b")

        # Paper convention: |x1 x0 y1 y0⟩ = col_bits + row_bits.
        return col_bin + row_bin

    @staticmethod
    def decode_position_bitstring(
        bitstring: str, board_size: int | None = None
    ) -> Position:
        """Decode a coordinate bitstring back to a ``Position``.

        Args:
            bitstring: Encoded position (e.g. ``"0110"``).
            board_size: Side length.  Defaults to ``config.BOARD_SIZE``.

        Returns:
            Corresponding ``Position``.
        """
        size = board_size if board_size is not None else config.BOARD_SIZE
        axis_bits = math.ceil(math.log2(size)) if size > 1 else 1

        col_str = bitstring[:axis_bits]
        row_str = bitstring[axis_bits: 2 * axis_bits]

        return Position(row=int(row_str, 2), col=int(col_str, 2))

    # ------------------------------------------------------------------
    # Status encoding
    # ------------------------------------------------------------------

    @staticmethod
    def encode_status(piece: Piece | None) -> str:
        """Encode a square's occupancy as a 3-bit status string.

        Encoding: [color_bit][type_bit_1][type_bit_0]
            Empty       → 000
            Black Pawn  → 001, White Pawn  → 101
            Black Knight→ 010, White Knight→ 110
            Black Bishop→ 011, White Bishop→ 111
            Black Rook  → 100 (overloaded), White Rook→ handled via extended
            Black Queen → reserved, White Queen → reserved
            Black King  → reserved, White King  → reserved

        For the 3-qubit register, we encode:
            PAWN   = 001
            KNIGHT = 010
            BISHOP = 011
            ROOK   = 100
            QUEEN  = 101
            KING   = 110

        The MSB is the color bit (0=Black, 1=White).

        Note: With 3 qubits we can encode 2 colors × 6 types = 12 values
        but only have 8 states. We use the 2 type bits for piece type
        and the color bit separately.

        Args:
            piece: The piece on the square, or ``None`` for empty.

        Returns:
            3-bit status string.
        """
        if piece is None:
            return "000"

        color_bit = "1" if piece.color is Color.WHITE else "0"
        type_map = {
            PieceType.PAWN:   "01",
            PieceType.KNIGHT: "10",
            PieceType.BISHOP: "11",
            PieceType.ROOK:   "01",  # Shares encoding; distinguished by context
            PieceType.QUEEN:  "10",  # Shares encoding; distinguished by context
            PieceType.KING:   "11",  # Shares encoding; distinguished by context
        }
        type_bits = type_map.get(piece.piece_type, "01")
        return f"{color_bit}{type_bits}"

    @staticmethod
    def decode_status_bitstring(bitstring: str) -> Piece | None:
        """Decode a 3-bit status string to a ``Piece`` or ``None``.

        Args:
            bitstring: 3-bit string (e.g. ``"000"``, ``"101"``).

        Returns:
            ``None`` for empty, otherwise a ``Piece``.
        """
        if bitstring == "000":
            return None

        color = Color.WHITE if bitstring[0] == "1" else Color.BLACK
        type_bits = bitstring[1:]

        type_map = {
            "01": PieceType.PAWN,
            "10": PieceType.KNIGHT,
            "11": PieceType.BISHOP,
        }
        piece_type = type_map.get(type_bits, PieceType.PAWN)
        return Piece(color=color, piece_type=piece_type)

    # ------------------------------------------------------------------
    # Full board encoding
    # ------------------------------------------------------------------

    @staticmethod
    def encode_board(
        state: GameState,
    ) -> dict[str, tuple[str, str]]:
        """Encode the entire board into coordinate → (coord_bits, status_bits).

        Args:
            state: The game state to encode.

        Returns:
            Dictionary keyed by human-readable square label mapping to
            a tuple of (coordinate bitstring, status bitstring).

        Example:
            >>> enc = BoardEncoder.encode_board(state)
            >>> enc["(0,1)"]
            ('0100', '01')  # col=1, row=0, black pawn
        """
        result: dict[str, tuple[str, str]] = {}
        board = state.board

        for row in range(board.size):
            for col in range(board.size):
                pos = Position(row, col)
                coord_bits = BoardEncoder.encode_position(pos, board.size)
                piece = board.get_piece(pos)
                status_bits = BoardEncoder.encode_status(piece)
                result[str(pos)] = (coord_bits, status_bits)

        return result

    # ------------------------------------------------------------------
    # Circuit initialisation
    # ------------------------------------------------------------------

    @staticmethod
    def initialize_register(
        circuit: QuantumCircuit,
        register: QuantumRegister,
        bitstring: str,
    ) -> None:
        """Set a quantum register to encode *bitstring* using X gates.

        Applies an X (NOT) gate to each qubit position where the
        bitstring has a ``'1'``.  The register is assumed to start in
        the all-|0⟩ state.

        Args:
            circuit: The circuit to append gates to.
            register: Target quantum register.
            bitstring: Binary string, length must equal ``register.size``.

        Raises:
            ValueError: If lengths do not match.
        """
        if len(bitstring) != register.size:
            raise ValueError(
                f"Bitstring length {len(bitstring)} != "
                f"register size {register.size}"
            )
        # Qiskit convention: qubit 0 is the *least* significant bit.
        # The paper writes |x1 x0 y1 y0⟩ with x1 as MSB.
        # We iterate left-to-right (MSB first) and map to qubit indices
        # in reverse so that the register reads MSB → LSB from high to
        # low index.
        for idx, bit in enumerate(reversed(bitstring)):
            if bit == "1":
                circuit.x(register[idx])
