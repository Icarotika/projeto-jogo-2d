"""Classes base de entidades para reaproveitamento."""

from __future__ import annotations

import pygame


class Entity:
    """Entidade retangular com física e vida básica."""

    def __init__(
        self,
        x: float,
        y: float,
        width: int,
        height: int,
        color: tuple[int, int, int],
        max_hp: int,
    ) -> None:
        self.rect = pygame.Rect(int(x), int(y), width, height)
        self.color = color
        self.max_hp = max_hp
        self.hp = max_hp
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def move_and_collide(self, solids: list[pygame.Rect]) -> None:
        """Move a entidade e resolve colisão eixo X/Y com blocos sólidos."""
        self.rect.x += int(self.velocity.x)
        for solid in solids:
            if self.rect.colliderect(solid):
                if self.velocity.x > 0:
                    self.rect.right = solid.left
                elif self.velocity.x < 0:
                    self.rect.left = solid.right

        self.rect.y += int(self.velocity.y)
        self.on_ground = False
        for solid in solids:
            if self.rect.colliderect(solid):
                if self.velocity.y > 0:
                    self.rect.bottom = solid.top
                    self.on_ground = True
                    self.velocity.y = 0
                elif self.velocity.y < 0:
                    self.rect.top = solid.bottom
                    self.velocity.y = 0

    def draw(self, surface: pygame.Surface, camera_x: int) -> None:
        draw_rect = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, self.color, draw_rect)
