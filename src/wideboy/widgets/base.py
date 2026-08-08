from __future__ import annotations

import abc
from typing import Any

from ..core.layer import Layer


class Widget(Layer, abc.ABC):
    def __init__(
        self,
        position: tuple[int, int] = (0, 0),
        z_order: int = 10,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(position=position, z_order=z_order)
        self.settings = settings or {}
