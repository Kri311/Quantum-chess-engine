"""
Pygame graphical interface.

``ChessGUI`` owns the event loop, delegates rendering to
``BoardRenderer``, and manages piece selection, move highlighting,
animation playback, and game-over states.
"""

from __future__ import annotations

import pygame

import config
from engine.constants import Color
from engine.evaluator import Evaluator
from engine.game import Game
from engine.move import Move
from engine.position import Position
from ui.animations import MoveAnimator
from ui.renderer import BoardRenderer
from ai.hybrid_engine import HybridEngine


class ChessGUI:
    """Pygame front-end for the 3×3 pawn chess game.

    Attributes:
        game: The underlying ``Game`` instance.
        engine: The AI engine to use, or None for two-player human.
        ai_color: The color the AI plays, or None.
    """

    def __init__(self, engine: HybridEngine | None = None, ai_color: Color | None = None) -> None:
        """Initialise pygame and create the window."""
        pygame.init()
        pygame.display.set_caption("Quantum Chess Engine — 3×3 Pawn Chess")

        self._screen: pygame.Surface = pygame.display.set_mode(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
            pygame.RESIZABLE,
        )
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self._renderer: BoardRenderer = BoardRenderer(self._screen)
        self._animator: MoveAnimator = MoveAnimator()

        self.game: Game = Game()
        self.engine = engine
        self.ai_color = ai_color

        # Interaction state.
        self._selected: Position | None = None
        self._legal_targets: list[Position] = []
        self._running: bool = True
        self._ai_thinking: bool = False

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run the event loop until the user quits."""
        while self._running:
            dt = self._clock.tick(config.FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _handle_events(self) -> None:
        """Process all pending pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            elif event.type == pygame.VIDEORESIZE:
                self._screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
                self._renderer.on_resize(self._screen)

            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click.
                    self._handle_click(event.pos)

    def _handle_key(self, key: int) -> None:
        """Respond to a key press.

        Args:
            key: pygame key constant.
        """
        if key == pygame.K_ESCAPE:
            self._running = False
        elif key == pygame.K_r:
            self._restart()

    def _handle_click(self, pixel: tuple[int, int]) -> None:
        """Process a left-click on the board.

        Args:
            pixel: ``(x, y)`` screen coordinates of the click.
        """
        if self._animator.is_animating or self._ai_thinking:
            return  # ignore clicks during animation or AI thinking

        if self.game.is_over():
            return
            
        if self.ai_color is not None and self.game.state.current_turn is self.ai_color:
            return  # ignore clicks if it's AI's turn

        pos = self._renderer.pixel_to_position(*pixel)
        if pos is None:
            self._deselect()
            return

        # If a piece is already selected, check if this click is a
        # legal destination.
        if self._selected is not None:
            target_move = self._find_move(self._selected, pos)
            if target_move is not None:
                self._execute_move(target_move)
                return

        # Otherwise, try to select a piece.
        piece = self.game.state.board.get_piece(pos)
        if piece is not None and piece.color is self.game.state.current_turn:
            self._select(pos)
        else:
            self._deselect()

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def _select(self, position: Position) -> None:
        """Select a piece and compute its legal targets.

        Args:
            position: The square to select.
        """
        self._selected = position
        moves = self.game.get_moves_for_position(position)
        self._legal_targets = [m.end for m in moves]

    def _deselect(self) -> None:
        """Clear the current selection."""
        self._selected = None
        self._legal_targets = []

    def _find_move(self, start: Position, end: Position) -> Move | None:
        """Find a legal move from *start* to *end*.

        Args:
            start: Source square.
            end: Destination square.

        Returns:
            The matching ``Move``, or ``None``.
        """
        for move in self.game.get_moves_for_position(start):
            if move.end == end:
                return move
        return None

    # ------------------------------------------------------------------
    # Move execution
    # ------------------------------------------------------------------

    def _execute_move(self, move: Move) -> None:
        """Start animating a move, then apply it.

        Args:
            move: The legal move to execute.
        """
        piece = self.game.state.board.get_piece(move.start)
        if piece is None:
            return

        start_px = self._renderer.position_to_pixel_center(move.start)
        end_px = self._renderer.position_to_pixel_center(move.end)
        self._animator.start(piece.color, start_px, end_px)
        self._pending_move = move
        self._deselect()

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt: float) -> None:
        """Advance animations and apply pending moves.

        Args:
            dt: Seconds elapsed since last frame.
        """
        if self._animator.is_animating:
            self._animator.update(dt)
            if not self._animator.is_animating:
                # Animation finished — apply the move.
                if hasattr(self, "_pending_move") and self._pending_move:
                    self.game.make_move(self._pending_move)
                    self._pending_move = None
                    
        # AI Turn handling
        if not self._animator.is_animating and not self.game.is_over():
            if self.engine is not None and self.game.state.current_turn is self.ai_color:
                if not getattr(self, "_ai_thinking", False):
                    self._ai_thinking = True
                    # Force a draw so the screen updates before the blocking search
                    self._draw()
                    pygame.display.flip()
                    
                    move = self.engine.select_move(self.game.state)
                    if move:
                        self._execute_move(move)
                    self._ai_thinking = False

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        """Render the current frame."""
        fps = self._clock.get_fps()

        animating = None
        if self._animator.is_animating:
            px, py = self._animator.current_pixel
            piece_type = None
            if hasattr(self, "_pending_move") and self._pending_move:
                piece = self.game.state.board.get_piece(self._pending_move.start)
                if piece:
                    piece_type = piece.piece_type
            if piece_type is not None:
                animating = (self._animator.piece_color, px, py, piece_type)

        self._renderer.draw(
            state=self.game.state,
            selected=self._selected,
            legal_targets=self._legal_targets,
            animating_piece=animating,
            fps=fps,
        )

        # Game-over overlay.
        winner = self.game.winner()
        if winner is not None:
            self._renderer.draw_winner_banner(winner)
        elif Evaluator.is_draw(self.game.state):
            self._renderer.draw_draw_banner()

    # ------------------------------------------------------------------
    # Restart
    # ------------------------------------------------------------------

    def _restart(self) -> None:
        """Reset the game to the starting position."""
        self.game.reset()
        self._deselect()
        self._animator.cancel()
