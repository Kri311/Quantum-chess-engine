"""
Board and piece renderer for the Pygame GUI.

``BoardRenderer`` handles all drawing operations: the grid, pieces,
highlights for selected squares and legal moves, turn indicators, and
the winner banner.  It is decoupled from event handling (which lives in
``ChessGUI``).
"""

from __future__ import annotations

from typing import Sequence

import pygame

import config
from engine.board import Board
from engine.constants import Color
from engine.move import Move
from engine.position import Position
from engine.state import GameState


class BoardRenderer:
    """Draws the chess board, pieces, and overlays onto a pygame surface.

    Attributes:
        surface: The target ``pygame.Surface``.
        cell_size: Pixel size of one board square.
        board_origin: ``(x, y)`` pixel offset of the top-left corner.
    """

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def __init__(self, surface: pygame.Surface) -> None:
        """Create a renderer bound to *surface*.

        Args:
            surface: The pygame display surface to draw on.
        """
        self.surface: pygame.Surface = surface
        self.cell_size: int = 0
        self.board_origin: tuple[int, int] = (0, 0)
        self._font: pygame.font.Font | None = None
        self._small_font: pygame.font.Font | None = None
        self._title_font: pygame.font.Font | None = None
        self._recalculate_layout()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _recalculate_layout(self) -> None:
        """Recompute cell size and origin after a window resize."""
        w, h = self.surface.get_size()
        status_bar_height = 80
        available = min(w, h - status_bar_height)
        self.cell_size = available // config.BOARD_SIZE
        board_pixels = self.cell_size * config.BOARD_SIZE
        self.board_origin = (
            (w - board_pixels) // 2,
            (h - status_bar_height - board_pixels) // 2,
        )
        font_size = max(self.cell_size // 2, 16)
        self._font = pygame.font.SysFont("dejavusans", font_size)
        self._small_font = pygame.font.SysFont("dejavusans", font_size // 2)
        self._title_font = pygame.font.SysFont("dejavusans", font_size // 3)

    def on_resize(self, surface: pygame.Surface) -> None:
        """Handle a window resize event.

        Args:
            surface: The new display surface.
        """
        self.surface = surface
        self._recalculate_layout()

    # ------------------------------------------------------------------
    # Coordinate conversion
    # ------------------------------------------------------------------

    def pixel_to_position(self, pixel_x: int, pixel_y: int) -> Position | None:
        """Convert pixel coordinates to a board ``Position``.

        Args:
            pixel_x: X coordinate in pixels.
            pixel_y: Y coordinate in pixels.

        Returns:
            The corresponding ``Position``, or ``None`` if outside the board.
        """
        ox, oy = self.board_origin
        col = (pixel_x - ox) // self.cell_size
        row = (pixel_y - oy) // self.cell_size
        if 0 <= row < config.BOARD_SIZE and 0 <= col < config.BOARD_SIZE:
            return Position(row, col)
        return None

    def position_to_pixel_center(self, position: Position) -> tuple[int, int]:
        """Return the pixel centre of the square at *position*.

        Args:
            position: Board coordinate.

        Returns:
            ``(cx, cy)`` pixel coordinates.
        """
        ox, oy = self.board_origin
        cx = ox + position.col * self.cell_size + self.cell_size // 2
        cy = oy + position.row * self.cell_size + self.cell_size // 2
        return cx, cy

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(
        self,
        state: GameState,
        selected: Position | None = None,
        legal_targets: Sequence[Position] = (),
        animating_piece: tuple[Color, float, float] | None = None,
        fps: float = 0.0,
    ) -> None:
        """Render the full scene.

        Args:
            state: Current game state to draw.
            selected: Currently selected square (highlighted).
            legal_targets: Squares to mark as legal move destinations.
            animating_piece: If set, ``(color, pixel_x, pixel_y)`` of a
                piece being animated (the source square is drawn empty).
            fps: Frames-per-second value to display.
        """
        self.surface.fill(config.COLOR_BACKGROUND)
        self._draw_board(selected, legal_targets)
        self._draw_pieces(state, animating_piece)
        if animating_piece is not None:
            self._draw_animated_piece(*animating_piece)
        self._draw_status_bar(state, fps)

    def _draw_board(
        self,
        selected: Position | None,
        legal_targets: Sequence[Position],
    ) -> None:
        """Draw the grid squares with optional highlights."""
        ox, oy = self.board_origin
        legal_set = set(legal_targets)

        for row in range(config.BOARD_SIZE):
            for col in range(config.BOARD_SIZE):
                x = ox + col * self.cell_size
                y = oy + row * self.cell_size
                pos = Position(row, col)

                # Base colour.
                if (row + col) % 2 == 0:
                    color = config.COLOR_LIGHT_SQUARE
                else:
                    color = config.COLOR_DARK_SQUARE

                # Overlay highlights.
                if pos == selected:
                    color = config.COLOR_SELECTED
                elif pos in legal_set:
                    color = config.COLOR_HIGHLIGHT

                pygame.draw.rect(
                    self.surface,
                    color,
                    (x, y, self.cell_size, self.cell_size),
                )

                # Grid border.
                pygame.draw.rect(
                    self.surface,
                    (60, 60, 60),
                    (x, y, self.cell_size, self.cell_size),
                    width=1,
                )

        # Legal-move dot indicators.
        for target in legal_set:
            if target != selected:
                cx, cy = self.position_to_pixel_center(target)
                pygame.draw.circle(
                    self.surface,
                    (0, 0, 0, 80),
                    (cx, cy),
                    self.cell_size // 8,
                )

    def _draw_pieces(
        self,
        state: GameState,
        animating_piece: tuple[Color, float, float] | None,
    ) -> None:
        """Draw every piece on the board (skipping the animating one)."""
        for pos, piece in state.board.all_pieces.items():
            # Skip the piece that is currently being animated.
            if animating_piece is not None:
                anim_color, _, _ = animating_piece
                # We skip drawing by comparing the position below.

            cx, cy = self.position_to_pixel_center(pos)
            self._draw_piece_circle(cx, cy, piece.color)

    def _draw_piece_circle(self, cx: int, cy: int, color: Color) -> None:
        """Draw a single piece as a filled circle with a letter label.

        Args:
            cx: Centre X pixel.
            cy: Centre Y pixel.
            color: Piece colour.
        """
        radius = self.cell_size // 3

        if color is Color.WHITE:
            fill = config.COLOR_WHITE_PIECE
            outline = (80, 80, 80)
            text_color = (0, 0, 0)
            label = "W"
        else:
            fill = config.COLOR_BLACK_PIECE
            outline = (180, 180, 180)
            text_color = (255, 255, 255)
            label = "B"

        # Shadow.
        pygame.draw.circle(
            self.surface, (30, 30, 30), (cx + 2, cy + 3), radius
        )
        # Main circle.
        pygame.draw.circle(self.surface, fill, (cx, cy), radius)
        # Outline.
        pygame.draw.circle(self.surface, outline, (cx, cy), radius, width=2)
        # Label.
        if self._font is not None:
            text_surf = self._font.render(label, True, text_color)
            text_rect = text_surf.get_rect(center=(cx, cy))
            self.surface.blit(text_surf, text_rect)

    def _draw_animated_piece(
        self, color: Color, px: float, py: float
    ) -> None:
        """Draw the piece that is currently being animated.

        Args:
            color: Piece colour.
            px: Current pixel X.
            py: Current pixel Y.
        """
        self._draw_piece_circle(int(px), int(py), color)

    def _draw_status_bar(self, state: GameState, fps: float) -> None:
        """Draw the bottom status bar with turn info and FPS."""
        w, h = self.surface.get_size()
        bar_height = 80
        bar_y = h - bar_height

        # Bar background.
        pygame.draw.rect(
            self.surface,
            (35, 35, 35),
            (0, bar_y, w, bar_height),
        )
        # Divider line.
        pygame.draw.line(
            self.surface,
            (80, 80, 80),
            (0, bar_y),
            (w, bar_y),
            width=2,
        )

        if self._font is not None:
            # Turn indicator.
            turn_text = f"Turn: {state.current_turn}"
            turn_surf = self._font.render(turn_text, True, config.COLOR_TEXT)
            self.surface.blit(turn_surf, (20, bar_y + 10))

            # Move count.
            moves_text = f"Moves: {len(state.move_history)}"
            moves_surf = self._font.render(moves_text, True, config.COLOR_TEXT)
            self.surface.blit(moves_surf, (20, bar_y + 45))

        if self._small_font is not None:
            # FPS.
            fps_text = f"FPS: {fps:.0f}"
            fps_surf = self._small_font.render(fps_text, True, (120, 120, 120))
            fps_rect = fps_surf.get_rect(topright=(w - 10, bar_y + 10))
            self.surface.blit(fps_surf, fps_rect)

            # Restart hint.
            hint_surf = self._small_font.render(
                "R: Restart | ESC: Quit", True, (100, 100, 100)
            )
            hint_rect = hint_surf.get_rect(topright=(w - 10, bar_y + 30))
            self.surface.blit(hint_surf, hint_rect)

    def draw_winner_banner(self, winner: Color) -> None:
        """Overlay a semi-transparent winner announcement.

        Args:
            winner: The winning colour.
        """
        w, h = self.surface.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.surface.blit(overlay, (0, 0))

        if self._font is not None:
            text = f"{winner} WINS!"
            text_surf = self._font.render(text, True, (255, 215, 0))
            text_rect = text_surf.get_rect(center=(w // 2, h // 2 - 20))
            self.surface.blit(text_surf, text_rect)

        if self._small_font is not None:
            sub = "Press R to restart"
            sub_surf = self._small_font.render(sub, True, (200, 200, 200))
            sub_rect = sub_surf.get_rect(center=(w // 2, h // 2 + 30))
            self.surface.blit(sub_surf, sub_rect)

    def draw_draw_banner(self) -> None:
        """Overlay a semi-transparent draw announcement."""
        w, h = self.surface.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.surface.blit(overlay, (0, 0))

        if self._font is not None:
            text_surf = self._font.render("DRAW", True, (180, 180, 180))
            text_rect = text_surf.get_rect(center=(w // 2, h // 2 - 20))
            self.surface.blit(text_surf, text_rect)

        if self._small_font is not None:
            sub_surf = self._small_font.render(
                "Press R to restart", True, (200, 200, 200)
            )
            sub_rect = sub_surf.get_rect(center=(w // 2, h // 2 + 30))
            self.surface.blit(sub_surf, sub_rect)
