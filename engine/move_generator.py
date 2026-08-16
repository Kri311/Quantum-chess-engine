"""
Legal-move generator.

``MoveGenerator`` produces every legal ``Move`` for the current player
in a given ``GameState``.  It is designed around a *strategy* approach:
piece-specific logic is encapsulated in private methods so that adding
new piece types later only requires extending this class — no changes
to ``Rules`` or ``Board``.
"""

from __future__ import annotations

from engine.board import Board
from engine.constants import Color, PieceType
from engine.move import Move
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState


class MoveGenerator:
    """Generates all legal moves for the active player."""

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @staticmethod
    def generate_legal_moves(state: GameState) -> list[Move]:
        """Return every legal move for the player whose turn it is.

        Filters out any pseudo-legal moves that would leave the king in check.
        """
        pseudo_legal_moves: list[Move] = []
        color: Color = state.current_turn

        for position, piece in state.board.pieces_by_color(color):
            pseudo_legal_moves.extend(
                MoveGenerator._generate_moves_for_piece(
                    state, position, piece
                )
            )

        return MoveGenerator._filter_safe_moves(state, pseudo_legal_moves)

    @staticmethod
    def generate_moves_for_position(
        state: GameState,
        position: Position,
    ) -> list[Move]:
        """Return legal moves for the piece at *position*."""
        piece: Piece | None = state.board.get_piece(position)
        if piece is None or piece.color is not state.current_turn:
            return []
            
        pseudo_legal_moves = MoveGenerator._generate_moves_for_piece(state, position, piece)
        return MoveGenerator._filter_safe_moves(state, pseudo_legal_moves)
        
    @staticmethod
    def _filter_safe_moves(state: GameState, moves: list[Move]) -> list[Move]:
        """Filter out moves that leave the current player's King in check."""
        legal_moves = []
        color = state.current_turn
        board = state.board
        
        for move in moves:
            # Simulate move
            moving_piece = board.get_piece(move.start)
            target_piece = board.get_piece(move.end)
            
            board.remove_piece(move.start)
            board.place_piece(move.end, moving_piece)
            
            if not MoveGenerator.is_in_check(state, color):
                legal_moves.append(move)
                
            # Undo move
            board.place_piece(move.start, moving_piece)
            if target_piece:
                board.place_piece(move.end, target_piece)
            else:
                board.remove_piece(move.end)
                
        return legal_moves

    @staticmethod
    def is_in_check(state: GameState, color: Color) -> bool:
        """Return True if the King of the given color is under attack."""
        board = state.board
        king_pos = None
        
        # Find the King
        for pos, piece in board.pieces_by_color(color):
            if piece.piece_type == PieceType.KING:
                king_pos = pos
                break
                
        if king_pos is None:
            return False  # If no King (e.g. 3x3 pawn-only variant), cannot be in check
            
        enemy_color = Color.BLACK if color is Color.WHITE else Color.WHITE
        
        # Check if any enemy piece can move to the King's position
        for pos, piece in board.pieces_by_color(enemy_color):
            enemy_moves = MoveGenerator._generate_moves_for_piece(state, pos, piece)
            for move in enemy_moves:
                if move.end == king_pos:
                    return True
                    
        return False

    # ------------------------------------------------------------------
    # Piece-specific generators (strategy methods)
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_moves_for_piece(
        state: GameState,
        position: Position,
        piece: Piece,
    ) -> list[Move]:
        """Dispatch to the piece-type–specific generator.

        Args:
            state: Current game snapshot.
            position: Square the piece sits on.
            piece: The piece to generate moves for.

        Returns:
            List of candidate ``Move`` objects that pass validation.
        """
        if piece.piece_type is PieceType.PAWN:
            return MoveGenerator._pawn_moves(state, position, piece.color)
        if piece.piece_type is PieceType.KNIGHT:
            return MoveGenerator._knight_moves(state, position, piece.color)
        if piece.piece_type is PieceType.BISHOP:
            return MoveGenerator._sliding_moves(state, position, piece.color, [(1, 1), (1, -1), (-1, 1), (-1, -1)])
        if piece.piece_type is PieceType.ROOK:
            return MoveGenerator._sliding_moves(state, position, piece.color, [(1, 0), (-1, 0), (0, 1), (0, -1)])
        if piece.piece_type is PieceType.QUEEN:
            return MoveGenerator._sliding_moves(state, position, piece.color, [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)])
        if piece.piece_type is PieceType.KING:
            return MoveGenerator._king_moves(state, position, piece.color)

        return []

    @staticmethod
    def _pawn_moves(
        state: GameState,
        position: Position,
        color: Color,
    ) -> list[Move]:
        """Generate all legal pawn moves from *position*.

        A pawn may:
        * Move one square forward if the target is empty.
        * Move two squares forward from its starting rank if both
          squares ahead are empty.
        * Capture diagonally if the target holds an enemy piece.

        Args:
            state: Current game snapshot.
            position: Source square.
            color: Colour of the pawn.

        Returns:
            List of legal ``Move`` objects.
        """
        board: Board = state.board
        forward_dir = -1 if color is Color.WHITE else 1
        forward_row = position.row + forward_dir
        candidates: list[Move] = []

        # Single forward move.
        if 0 <= forward_row < board.size:
            forward_pos = Position(forward_row, position.col)
            if board.get_piece(forward_pos) is None:
                candidates.append(Move(start=position, end=forward_pos, capture=False))

                # Two-square opening move from starting rank.
                start_rank = board.size - 2 if color is Color.WHITE else 1
                if position.row == start_rank:
                    double_row = position.row + 2 * forward_dir
                    if 0 <= double_row < board.size:
                        double_pos = Position(double_row, position.col)
                        if board.get_piece(double_pos) is None:
                            candidates.append(Move(start=position, end=double_pos, capture=False))

        # Diagonal captures.
        for col_offset in (-1, 1):
            new_col = position.col + col_offset
            if 0 <= forward_row < board.size and 0 <= new_col < board.size:
                diag_pos = Position(forward_row, new_col)
                target_piece = board.get_piece(diag_pos)
                if target_piece is not None and target_piece.color is not color:
                    candidates.append(Move(start=position, end=diag_pos, capture=True))

        return candidates

    @staticmethod
    def _knight_moves(
        state: GameState,
        position: Position,
        color: Color,
    ) -> list[Move]:
        """Generate all legal knight moves from *position*."""
        board = state.board
        candidates: list[Move] = []
        
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for d_row, d_col in knight_offsets:
            target_row = position.row + d_row
            target_col = position.col + d_col
            
            if 0 <= target_row < board.size and 0 <= target_col < board.size:
                target_pos = Position(target_row, target_col)
                target_piece = board.get_piece(target_pos)
                
                capture = target_piece is not None
                if capture and target_piece.color is color:
                    continue  # Can't capture own piece
                    
                move = Move(start=position, end=target_pos, capture=capture)
                candidates.append(move)
                    
        return candidates

    @staticmethod
    def _sliding_moves(
        state: GameState,
        position: Position,
        color: Color,
        directions: list[tuple[int, int]]
    ) -> list[Move]:
        board = state.board
        candidates: list[Move] = []
        
        for d_row, d_col in directions:
            current_row, current_col = position.row + d_row, position.col + d_col
            while 0 <= current_row < board.size and 0 <= current_col < board.size:
                target_pos = Position(current_row, current_col)
                target_piece = board.get_piece(target_pos)
                
                if target_piece is None:
                    candidates.append(Move(start=position, end=target_pos, capture=False))
                elif target_piece.color is not color:
                    candidates.append(Move(start=position, end=target_pos, capture=True))
                    break
                else:
                    break
                    
                current_row += d_row
                current_col += d_col
                
        return candidates

    @staticmethod
    def _king_moves(
        state: GameState,
        position: Position,
        color: Color,
    ) -> list[Move]:
        board = state.board
        candidates: list[Move] = []
        
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        for d_row, d_col in directions:
            target_row, target_col = position.row + d_row, position.col + d_col
            if 0 <= target_row < board.size and 0 <= target_col < board.size:
                target_pos = Position(target_row, target_col)
                target_piece = board.get_piece(target_pos)
                
                if target_piece is None:
                    candidates.append(Move(start=position, end=target_pos, capture=False))
                elif target_piece.color is not color:
                    candidates.append(Move(start=position, end=target_pos, capture=True))
                    
        return candidates
