"""
Piece movement animations.

``MoveAnimator`` drives smooth positional interpolation (lerp) between
the source and destination squares when a move is made.  The GUI polls
``is_animating`` each frame and draws the piece at the interpolated
pixel position until the animation completes.
"""

from __future__ import annotations

import config
from engine.constants import Color
from engine.position import Position


class MoveAnimator:
    """Smooth linear interpolation animator for piece movement.

    Attributes:
        is_animating: ``True`` while an animation is in progress.
    """

    def __init__(self) -> None:
        """Initialise with no active animation."""
        self.is_animating: bool = False
        self._color: Color = Color.WHITE
        self._start_x: float = 0.0
        self._start_y: float = 0.0
        self._end_x: float = 0.0
        self._end_y: float = 0.0
        self._current_x: float = 0.0
        self._current_y: float = 0.0
        self._progress: float = 0.0

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def start(
        self,
        color: Color,
        start_pixel: tuple[int, int],
        end_pixel: tuple[int, int],
    ) -> None:
        """Begin a new movement animation.

        Args:
            color: Colour of the moving piece.
            start_pixel: ``(x, y)`` pixel origin.
            end_pixel: ``(x, y)`` pixel destination.
        """
        self.is_animating = True
        self._color = color
        self._start_x, self._start_y = float(start_pixel[0]), float(
            start_pixel[1]
        )
        self._end_x, self._end_y = float(end_pixel[0]), float(end_pixel[1])
        self._current_x = self._start_x
        self._current_y = self._start_y
        self._progress = 0.0

    def update(self, dt: float) -> None:
        """Advance the animation by one time step.

        Args:
            dt: Elapsed seconds since the last frame.
        """
        if not self.is_animating:
            return

        speed = config.ANIMATION_SPEED
        self._progress += dt * speed
        if self._progress >= 1.0:
            self._progress = 1.0
            self.is_animating = False

        t = self._ease_out_quad(self._progress)
        self._current_x = self._start_x + (self._end_x - self._start_x) * t
        self._current_y = self._start_y + (self._end_y - self._start_y) * t

    def cancel(self) -> None:
        """Immediately stop the current animation."""
        self.is_animating = False
        self._progress = 0.0

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def current_pixel(self) -> tuple[float, float]:
        """Return the current interpolated pixel position.

        Returns:
            ``(x, y)`` as floats.
        """
        return self._current_x, self._current_y

    @property
    def piece_color(self) -> Color:
        """Return the colour of the piece being animated.

        Returns:
            A ``Color`` enum member.
        """
        return self._color

    # ------------------------------------------------------------------
    # Easing
    # ------------------------------------------------------------------

    @staticmethod
    def _ease_out_quad(t: float) -> float:
        """Quadratic ease-out for smooth deceleration.

        Args:
            t: Progress in ``[0, 1]``.

        Returns:
            Eased value in ``[0, 1]``.
        """
        return 1.0 - (1.0 - t) * (1.0 - t)
