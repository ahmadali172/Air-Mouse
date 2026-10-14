"""
Smoothing of hand landmarks over time.
"""

import numpy as np


class Smoother:
    """
    Smooths points over time using an exponential moving average.
    Lower alpha = more smoothing (slower response).
    Higher alpha = less smoothing (faster response).
    """

    def __init__(self, alpha=0.2):
        self.alpha = alpha
        self.prev_points = None

    def smooth(self, points):
        """
        points: list of tuples [(x, y, z), ...]
        Returns the smoothed points as a list.
        """
        points = np.array(points)
        if self.prev_points is None:
            self.prev_points = points
            return points.tolist()

        smoothed = self.prev_points * (1 - self.alpha) + points * self.alpha
        self.prev_points = smoothed
        return smoothed.tolist()

    def reset(self):
        """Forget the previous points (use when the hand is lost)."""
        self.prev_points = None