"""Inimigos simples com patrulha e barra de HP."""

from __future__ import annotations

import pygame

import settings
from entities import Entity


class Enemy(Entity):
    def __init__(self, x: int, y: int, patrol_left: int, patrol_right: int) -> None:
        super().__init__(
            x=x,
            y=y,
            width=settings.ENEMY_WIDTH,
            height=settings.ENEMY_HEIGHT,
            color=settings.ENEMY_COLOR,
            max_hp=settings.ENEMY_HP,
        )
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.direction = 1

    def update(self, solids: list[pygame.Rect]) -> None:
        if not self.alive:
            return

        self.velocity.x = settings.ENEMY_SPEED * self.direction
        self.velocity.y += settings.GRAVITY
        if self.velocity.y > 12:
            self.velocity.y = 12

        self.move_and_collide(solids)

        if self.rect.left <= self.patrol_left:
            self.rect.left = self.patrol_left
            self.direction = 1
        elif self.rect.right >= self.patrol_right:
            self.rect.right = self.patrol_right
            self.direction = -1

    def draw(self, surface: pygame.Surface, camera_x: int, font: pygame.font.Font) -> None:
        if not self.alive:
            return

        super().draw(surface, camera_x)

        hp_ratio = self.hp / self.max_hp
        bar_width = self.rect.width
        bar_height = 6
        bar_x = self.rect.left - camera_x
        bar_y = self.rect.top - 14

        pygame.draw.rect(surface, settings.HP_BG_COLOR, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(
            surface,
            settings.HP_FILL_COLOR,
            (bar_x, bar_y, int(bar_width * hp_ratio), bar_height),
        )

        hp_text = font.render(str(self.hp), True, settings.WHITE)
        surface.blit(hp_text, (bar_x + 4, bar_y - 16))
