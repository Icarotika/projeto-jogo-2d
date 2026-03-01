"""Câmera 2D simples com seguimento horizontal suave."""

from __future__ import annotations


class Camera:
    def __init__(self, world_width: int, screen_width: int) -> None:
        self.x = 0.0
        self.world_width = world_width
        self.screen_width = screen_width

    def update(self, target_x: int) -> None:
        desired = target_x - self.screen_width // 2
        max_x = self.world_width - self.screen_width
        desired = max(0, min(desired, max_x))

        # Suavização leve para evitar "trancos" com sprites animados de tamanhos variados.
        self.x += (desired - self.x) * 0.15

    def apply_x(self) -> int:
        return int(self.x)
