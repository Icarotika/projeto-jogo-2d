"""Lógica do personagem principal (Mago Invocador)."""

from __future__ import annotations

import pygame

import settings
from entities import AnimatedEntity


class Player(AnimatedEntity):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(
            x=x,
            y=y,
            width=settings.PLAYER_WIDTH,
            height=settings.PLAYER_HEIGHT,
            color=settings.PLAYER_COLOR,
            max_hp=settings.PLAYER_HP,
            animation_fps=settings.ANIMATION_PLAYER_FPS,
        )
        self.mana = settings.PLAYER_MANA

        # Como adicionar personagem novo no futuro:
        # 1) Crie pasta assets/<novo_personagem>/idle, run, jump.
        # 2) Copie o padrão de carregamento de animações usado aqui.
        self.animations["idle"] = self.load_animation("assets/player/idle", (46, 62))
        self.animations["run"] = self.load_animation("assets/player/run", (46, 62))
        self.animations["jump"] = self.load_animation("assets/player/jump", (46, 62))

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        self.velocity.x = 0
        if keys[pygame.K_a]:
            self.velocity.x = -settings.PLAYER_SPEED
            self.facing = "left"
        if keys[pygame.K_d]:
            self.velocity.x = settings.PLAYER_SPEED
            self.facing = "right"

    def apply_physics(self, solids: list[pygame.Rect]) -> None:
        self.velocity.y += settings.GRAVITY
        self.velocity.y = min(self.velocity.y, 14)
        self.move_and_collide(solids)

    def update_state(self) -> None:
        if not self.on_ground:
            self.set_state("jump")
        elif abs(self.velocity.x) > 0:
            self.set_state("run")
        else:
            self.set_state("idle")

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper, solids: list[pygame.Rect]) -> None:
        self.handle_input(keys)
        self.apply_physics(solids)
        self.update_state()
        self.update_animation(dt, loop=True)

    def jump(self) -> None:
        if self.on_ground:
            self.velocity.y = settings.PLAYER_JUMP_SPEED
