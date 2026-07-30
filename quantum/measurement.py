"""
Measurement post-processing.

Utilities for normalising, sorting, and interpreting the raw
count dictionaries returned by Qiskit's simulator.
"""

from __future__ import annotations


class MeasurementProcessor:
    """Processes raw measurement counts from quantum circuit execution."""

    @staticmethod
    def process_counts(counts: dict[str, int]) -> dict[str, float]:
        """Normalise raw counts to probabilities.

        Args:
            counts: {bitstring: count} from the simulator.

        Returns:
            {bitstring: probability} where probabilities sum to 1.0.
        """
        total = sum(counts.values())
        if total == 0:
            return {}
        return {k: v / total for k, v in counts.items()}

    @staticmethod
    def get_most_likely(counts: dict[str, int]) -> str:
        """Return the bitstring with the highest count.

        Args:
            counts: {bitstring: count} from the simulator.

        Returns:
            The most frequently measured bitstring.

        Raises:
            ValueError: If counts is empty.
        """
        if not counts:
            raise ValueError("Cannot get most likely from empty counts")
        return max(counts, key=lambda k: counts[k])

    @staticmethod
    def get_top_k(
        counts: dict[str, int], k: int
    ) -> list[tuple[str, float]]:
        """Return the top-k most probable results.

        Args:
            counts: {bitstring: count} from the simulator.
            k: Number of top results to return.

        Returns:
            List of (bitstring, probability) tuples, sorted descending.
        """
        total = sum(counts.values())
        if total == 0:
            return []
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [(bs, count / total) for bs, count in sorted_items[:k]]

    @staticmethod
    def validate_measurement(
        result: str, expected_length: int
    ) -> bool:
        """Check that a measurement bitstring has the expected format.

        Args:
            result: Bitstring to validate.
            expected_length: Expected number of bits.

        Returns:
            True if the bitstring is valid binary of the correct length.
        """
        if len(result) != expected_length:
            return False
        return all(c in ("0", "1") for c in result)

    @staticmethod
    def entropy(counts: dict[str, int]) -> float:
        """Calculate the Shannon entropy of the measurement distribution.

        Higher entropy means more uniform (less decisive) results.
        Lower entropy means the algorithm concentrated on fewer states.

        Args:
            counts: {bitstring: count} from the simulator.

        Returns:
            Shannon entropy in bits.
        """
        import math

        total = sum(counts.values())
        if total == 0:
            return 0.0
        h = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                h -= p * math.log2(p)
        return h
