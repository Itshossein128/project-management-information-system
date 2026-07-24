"""Registry for alert checkers."""

import logging
from typing import Callable

logger = logging.getLogger(__name__)


class AlertCheckerRegistry:
    """
    A registry for alert checkers, adhering to the Open-Closed Principle.
    New checkers can be added by simply decorating them.
    """

    def __init__(self):
        self._checkers: dict[str, Callable] = {}

    def register(self, alert_type: str) -> Callable:
        """
        Decorator to register a new checker function for a specific alert type.
        """
        def decorator(func: Callable) -> Callable:
            normalized_type = (alert_type or '').lower()
            if normalized_type in self._checkers:
                logger.warning(
                    "Overwriting existing checker for alert type '%s'",
                    normalized_type,
                )
            self._checkers[normalized_type] = func
            return func
        return decorator

    def get_checker(self, alert_type: str) -> Callable | None:
        """Retrieve the checker for a specific alert type."""
        normalized_type = (alert_type or '').lower()
        return self._checkers.get(normalized_type)

    def evaluate(self, rule, project_id) -> None:
        """Execute the checker for the given rule."""
        checker = self.get_checker(rule.alert_type)
        if checker:
            checker(rule, project_id)
        else:
            logger.warning("No checker registered for alert type '%s'", rule.alert_type)


alert_registry = AlertCheckerRegistry()
