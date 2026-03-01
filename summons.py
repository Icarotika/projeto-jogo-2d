"""Invocações do mago: mago (cast único), guerreiro (golpe único) e carta explosiva."""

from __future__ import annotations

from dataclasses import dataclass
import math

import pygame

import settings
from enemies import Enemy
from entities import AnimatedEntity


@dataclass
class Projectile:
    rect: pygame.Rect
    direction: int
    speed: float
    damage: int
    timer: float
    frames: list[pygame.Surface]
    frame_index: int = 0
    frame_timer: float = 0.0

    @property
    def alive(self) -> bool:
        return self.timer > 0

    def update(self, dt: float) -> None:
        self.rect.x += int(self.speed * self.direction)
        self.timer -= dt

        if len(self.frames) > 1:
            self.frame_timer += dt
            if self.frame_timer >= 1 / settings.ANIMATION_SUMMON_FPS:
                self.frame_timer = 0.0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, surface: pygame.Surface, camera_x: int) -> None:
        if self.frames:
            frame = self.frames[self.frame_index]
            if self.direction < 0:
                frame = pygame.transform.flip(frame, True, False)
            draw_rect = frame.get_rect(center=(self.rect.centerx - camera_x, self.rect.centery))
            surface.blit(frame, draw_rect)
        else:
            pygame.draw.rect(surface, settings.PROJECTILE_COLOR, self.rect.move(-camera_x, 0))


class MageSummon(AnimatedEntity):
    """Invocação de longa distância: aparece, faz cast, dispara 1 projétil e some."""

    def __init__(self, x: int, y: int, facing: str) -> None:
        super().__init__(x, y, 30, 46, settings.MAGE_COLOR, max_hp=1, animation_fps=settings.ANIMATION_SUMMON_FPS)
        self.facing = facing
        self.animations["cast"] = self.load_animation("assets/summons/mage/cast", (34, 48))
        self.set_state("cast", reset=True)

        projectile_frames = self.load_animation("assets/summons/mage/projectile", (20, 10))
        direction = 1 if facing == "right" else -1
        self.projectile = Projectile(
            rect=pygame.Rect(self.rect.centerx + direction * 20, self.rect.centery - 6, 20, 10),
            direction=direction,
            speed=8.5,
            damage=settings.MAGE_DAMAGE,
            timer=1.3,
            frames=projectile_frames,
        )
        self.cast_time = 0.18
        self.life_timer = settings.MAGE_MAX_LIFETIME
        self.has_fired = False
        self.expired = False

    def update(self, dt: float, enemies: list[Enemy]) -> None:
        self.life_timer -= dt
        self.cast_time -= dt
        self.update_animation(dt, loop=False)

        if not self.has_fired and self.cast_time <= 0:
            self.has_fired = True

        if self.has_fired and self.projectile.alive:
            self.projectile.update(dt)
            for enemy in enemies:
                if enemy.alive and self.projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(self.projectile.damage)
                    self.projectile.timer = 0
                    print(f"Mago invocado acertou inimigo. HP: {enemy.hp}")
                    break

        if self.life_timer <= 0:
            self.expired = True

    def draw(self, surface: pygame.Surface, camera_x: int) -> None:
        # O mago não permanece no mapa: aparece apenas durante o cast inicial.
        if not self.has_fired:
            super().draw(surface, camera_x)
        if self.has_fired and self.projectile.alive:
            self.projectile.draw(surface, camera_x)


class WarriorSummon(AnimatedEntity):
    """Invocação melee: aparece, anima ataque, causa dano em área à frente e desaparece."""

    def __init__(self, x: int, y: int, facing: str) -> None:
        super().__init__(x, y, 34, 52, settings.WARRIOR_COLOR, max_hp=1, animation_fps=settings.ANIMATION_SUMMON_FPS)
        self.facing = facing

        # Coloque frames de ataque em assets/summons/warrior/attack/
        # Exemplo: attack_0.png, attack_1.png, attack_2.png
        self.animations["attack"] = self.load_animation("assets/summons/warrior/attack", (42, 58))
        self.set_state("attack", reset=True)

        self.life_timer = settings.WARRIOR_LIFETIME
        self.attack_done = False
        self.expired = False

    def update(self, dt: float, enemies: list[Enemy]) -> None:
        self.life_timer -= dt
        finished = self.update_animation(dt, loop=False)

        if not self.attack_done:
            if self.facing == "right":
                hitbox = pygame.Rect(self.rect.right, self.rect.top - 8, 64, self.rect.height + 16)
            else:
                hitbox = pygame.Rect(self.rect.left - 64, self.rect.top - 8, 64, self.rect.height + 16)

            for enemy in enemies:
                if enemy.alive and hitbox.colliderect(enemy.rect):
                    enemy.take_damage(settings.WARRIOR_DAMAGE)
                    print(f"Guerreiro invocado acertou inimigo. HP: {enemy.hp}")
            self.attack_done = True

        if finished or self.life_timer <= 0:
            self.expired = True


class ExplosiveCard(AnimatedEntity):
    """Armadilha com animação idle/explosion e dano em área."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 24, 12, settings.CARD_COLOR, max_hp=1, animation_fps=settings.ANIMATION_SUMMON_FPS)

        # Coloque imagens da carta em:
        # assets/summons/card/idle/ -> idle_0.png, idle_1.png...
        # assets/summons/card/explosion/ -> explosion_0.png, explosion_1.png...
        # Para novos efeitos basta adicionar PNGs nas pastas acima.
        self.animations["idle"] = self.load_animation("assets/summons/card/idle", (26, 14))
        self.animations["explosion"] = self.load_animation("assets/summons/card/explosion", (120, 120))
        self.set_state("idle", reset=True)

        self.active = True
        self.expired = False
        self.explosion_radius = 80
        self._damage_applied = False

    def update(self, dt: float, enemies: list[Enemy]) -> None:
        if self.active:
            self.update_animation(dt, loop=True)
            for enemy in enemies:
                if enemy.alive and self.rect.colliderect(enemy.rect):
                    self.active = False
                    self.set_state("explosion", reset=True)
                    break
        else:
            if not self._damage_applied:
                self._apply_explosion_damage(enemies)
                self._damage_applied = True
            finished = self.update_animation(dt, loop=False)
            if finished:
                self.expired = True

    def _apply_explosion_damage(self, enemies: list[Enemy]) -> None:
        for enemy in enemies:
            if not enemy.alive:
                continue
            dist = math.dist(self.rect.center, enemy.rect.center)
            if dist <= self.explosion_radius:
                falloff = max(0.4, 1.0 - (dist / self.explosion_radius))
                damage = int(settings.CARD_DAMAGE * falloff)
                enemy.take_damage(damage)
                print(f"Carta explosiva causou {damage} de dano. HP: {enemy.hp}")

    def draw(self, surface: pygame.Surface, camera_x: int) -> None:
        if self.state == "explosion":
            image = self.current_frame()
            draw_rect = image.get_rect(center=(self.rect.centerx - camera_x, self.rect.centery))
            surface.blit(image, draw_rect)
            return
        super().draw(surface, camera_x)
