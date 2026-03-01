"""Invocações do mago: mago, guerreiro e carta explosiva."""

from __future__ import annotations

import math
import random

import pygame

import settings
from entities import Entity
from enemies import Enemy


class Projectile:
    def __init__(self, x: int, y: int, direction: int, speed: float = 8.0) -> None:
        self.rect = pygame.Rect(x, y, 16, 8)
        self.direction = direction
        self.speed = speed
        self.lifetime = 1.8

    @property
    def alive(self) -> bool:
        return self.lifetime > 0

    def update(self, dt: float) -> None:
        self.rect.x += int(self.speed * self.direction)
        self.lifetime -= dt

    def draw(self, surface: pygame.Surface, camera_x: int) -> None:
        pygame.draw.rect(surface, settings.PROJECTILE_COLOR, self.rect.move(-camera_x, 0))


class SummonBase(Entity):
    def __init__(self, x: int, y: int, width: int, height: int, color: tuple[int, int, int]) -> None:
        super().__init__(x, y, width, height, color, max_hp=1)
        self.timer = settings.SUMMON_LIFETIME

    @property
    def expired(self) -> bool:
        return self.timer <= 0


class MageSummon(SummonBase):
    """Invocação de longa distância que dispara projéteis."""

    def __init__(self, x: int, y: int, facing: int) -> None:
        super().__init__(x, y, 30, 46, settings.MAGE_COLOR)
        self.facing = facing
        self.fire_cooldown = 0.2
        self.projectiles: list[Projectile] = []

    def update(self, dt: float, solids: list[pygame.Rect], enemies: list[Enemy]) -> None:
        self.timer -= dt
        self.velocity.y += settings.GRAVITY
        self.move_and_collide(solids)

        self.fire_cooldown -= dt
        if self.fire_cooldown <= 0:
            self.fire_cooldown = 0.65
            spawn_x = self.rect.centerx + 16 * self.facing
            spawn_y = self.rect.centery - 8
            self.projectiles.append(Projectile(spawn_x, spawn_y, self.facing))

        for projectile in self.projectiles:
            projectile.update(dt)

            for enemy in enemies:
                if enemy.alive and projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(settings.MAGE_DAMAGE)
                    projectile.lifetime = 0
                    print(f"Mago atingiu inimigo! HP restante: {enemy.hp}")
                    break

        self.projectiles = [p for p in self.projectiles if p.alive]

    def draw(self, surface: pygame.Surface, camera_x: int) -> None:
        super().draw(surface, camera_x)
        for projectile in self.projectiles:
            projectile.draw(surface, camera_x)


class WarriorSummon(SummonBase):
    """Invocação de curta distância que persegue e causa golpe alto."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 32, 50, settings.WARRIOR_COLOR)
        self.attack_done = False

    def update(self, dt: float, solids: list[pygame.Rect], enemies: list[Enemy]) -> None:
        self.timer -= dt
        self.velocity.y += settings.GRAVITY

        target = _get_closest_enemy(self.rect.centerx, enemies)
        if target and target.alive:
            dx = target.rect.centerx - self.rect.centerx
            self.velocity.x = max(-3.2, min(3.2, dx * 0.03))

            if self.rect.colliderect(target.rect.inflate(8, 4)) and not self.attack_done:
                target.take_damage(settings.WARRIOR_DAMAGE)
                self.attack_done = True
                self.timer = min(self.timer, 0.2)
                print(f"Guerreiro acertou inimigo! HP restante: {target.hp}")
        else:
            self.velocity.x = 0

        self.move_and_collide(solids)

    @property
    def expired(self) -> bool:
        return super().expired or self.attack_done


class ExplosiveCard:
    """Armadilha posicionada no chão que explode ao contato de inimigos."""

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, 22, 10)
        self.active = True
        self.exploding_timer = 0.0
        self.explosion_radius = 70

    @property
    def expired(self) -> bool:
        return not self.active and self.exploding_timer <= 0

    def update(self, dt: float, enemies: list[Enemy]) -> None:
        if self.active:
            for enemy in enemies:
                if enemy.alive and self.rect.colliderect(enemy.rect):
                    self.active = False
                    self.exploding_timer = 0.25
                    self._apply_explosion_damage(enemies)
                    print("Carta explosiva detonada!")
                    break
        else:
            self.exploding_timer -= dt

    def _apply_explosion_damage(self, enemies: list[Enemy]) -> None:
        for enemy in enemies:
            if not enemy.alive:
                continue
            dist = math.dist(self.rect.center, enemy.rect.center)
            if dist <= self.explosion_radius:
                falloff = max(0.4, 1.0 - (dist / self.explosion_radius))
                dmg = int(settings.CARD_DAMAGE * falloff)
                enemy.take_damage(dmg)
                print(f"Explosão causou {dmg} de dano. HP inimigo: {enemy.hp}")

    def draw(self, surface: pygame.Surface, camera_x: int) -> None:
        draw_rect = self.rect.move(-camera_x, 0)
        if self.active:
            pygame.draw.rect(surface, settings.CARD_COLOR, draw_rect)
        else:
            radius = int(self.explosion_radius * random.uniform(0.85, 1.0))
            pygame.draw.circle(surface, (255, 120, 30), draw_rect.center, radius, width=4)


def _get_closest_enemy(x: int, enemies: list[Enemy]) -> Enemy | None:
    alive = [e for e in enemies if e.alive]
    if not alive:
        return None
    return min(alive, key=lambda e: abs(e.rect.centerx - x))
