"""Lógica do personagem principal (Mago Invocador)."""

from __future__ import annotations

import pygame

import settings
from entities import Entity


class Player(Entity):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(
            x=x,
            y=y,
            width=settings.PLAYER_WIDTH,
            height=settings.PLAYER_HEIGHT,
            color=settings.PLAYER_COLOR,
            max_hp=settings.PLAYER_HP,
        )
        self.facing = 1

    def update(self, keys: pygame.key.ScancodeWrapper, solids: list[pygame.Rect]) -> None:
        self.velocity.x = 0

        if keys[pygame.K_a]:
            self.velocity.x = -settings.PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_d]:
            self.velocity.x = settings.PLAYER_SPEED
            self.facing = 1

        self.velocity.y += settings.GRAVITY
        if self.velocity.y > 14:
            self.velocity.y = 14

        self.move_and_collide(solids)

    def jump(self) -> None:
        if self.on_ground:
            self.velocity.y = settings.PLAYER_JUMP_SPEED
