"""
Game state representation.

``GameState`` bundles the ``Board``, the current turn, and the move
history into a single immutable-style container.  ``apply_move`` returns
a *new* state so that callers (minimax, quantum search) can explore the
game tree without mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from engine.board import Board
from engine.constants import Color
from engine.move import Move
from engine.piece import Piece
from engine.position import Position


@dataclass
class GameState:
    """Snapshot of a chess game in progress.

    Attributes:
        board: Current piece layout.
        current_turn: Colour whose turn it is to move.
        move_history: Ordered list of moves played so far.
    """

    board: Board = field(default_factory=Board)
    current_turn: Color = Color.WHITE
    move_history: list[Move] = field(default_factory=list)
    checks_received_white: int = 0
    checks_received_black: int = 0

    # ------------------------------------------------------------------
    # Turn management
    # ------------------------------------------------------------------

    def switch_turn(self) -> None:
        """Toggle ``current_turn`` to the opposing colour."""
        self.current_turn = self.current_turn.opponent()

    # ------------------------------------------------------------------
    # Move application
    # ------------------------------------------------------------------

    def apply_move(self, move: Move) -> "GameState":
        """Return a **new** ``GameState`` with *move* applied.

        The piece at ``move.start`` is relocated to ``move.end``.  If
        ``move.capture`` is ``True`` the target square's occupant is
        removed first.

        Args:
            move: The move to execute.

        Returns:
            A fresh ``GameState`` reflecting the board after the move.

        Raises:
            ValueError: If no piece exists at ``move.start``.
        """
        piece: Piece | None = self.board.get_piece(move.start)
        if piece is None:
            raise ValueError(f"No piece at {move.start} to move")

        new_board: Board = self.board.copy()
        new_board.remove_piece(move.start)

        if move.capture:
            new_board.remove_piece(move.end)

        new_board.place_piece(move.end, piece)

        new_history = list(self.move_history)
        new_history.append(move)

        return GameState(
            board=new_board,
            current_turn=self.current_turn.opponent(),
            move_history=new_history,
        )

    # ------------------------------------------------------------------
    # Terminal detection
    # ------------------------------------------------------------------

    def is_terminal(self) -> bool:
        """Check whether the game has ended.

        The game ends when one side's pawn has been captured or has
        reached the opposite promotion row.  This is a lightweight
        check — detailed winner logic is in ``Evaluator``.

        Returns:
            ``True`` if the game is over.
        """
        white_alive = any(
            True for _ in self.board.pieces_by_color(Color.WHITE)
        )
        black_alive = any(
            True for _ in self.board.pieces_by_color(Color.BLACK)
        )

        if not white_alive or not black_alive:
            return True

        # Check promotion: white reaches row 0, black reaches last row.
        for pos, piece in self.board.pieces_by_color(Color.WHITE):
            if pos.row == 0:
                return True
        for pos, piece in self.board.pieces_by_color(Color.BLACK):
            if pos.row == self.board.size - 1:
                return True

        return False

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"{self.board}\n"
            f"Turn: {self.current_turn}  |  "
            f"Moves played: {len(self.move_history)}"
        )
