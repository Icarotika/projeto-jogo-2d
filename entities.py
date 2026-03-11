"""Classes base de entidades para reaproveitamento com animação automática."""

from __future__ import annotations

from pathlib import Path

import pygame

import settings


class AnimatedEntity:
    """Entidade retangular com física, vida e sistema de animação por pastas."""

    def __init__(
        self,
        x: float,
        y: float,
        width: int,
        height: int,
        color: tuple[int, int, int],
        max_hp: int,
        animation_fps: int = settings.ANIMATION_DEFAULT_FPS,
    ) -> None:
        self.rect = pygame.Rect(int(x), int(y), width, height)
        self.max_hp = max_hp
        self.hp = max_hp
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing = "right"

        # Estrutura padrão exigida no enunciado para suportar expansão futura.
        self.animations: dict[str, list[pygame.Surface]] = {
            "idle": [],
            "run": [],
            "jump": [],
            "walk": [],
            "attack": [],
            "cast": [],
            "explosion": [],
        }

        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0.0
        self.animation_fps = animation_fps

        # Fallback visual quando não há PNGs no diretório.
        fallback = pygame.Surface((width, height), pygame.SRCALPHA)
        fallback.fill(color)
        self.fallback_frame = fallback

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    # Coloque as imagens em pastas como:
    # assets/player/run/
    # assets/enemies/slime/walk/
    # Formato recomendado: PNG com fundo transparente.
    # Nomeação recomendada de frames: run_0.png, run_1.png, run_2.png...
    # Para adicionar novos frames de animação, apenas adicione novos PNGs na pasta.
    # O sistema carrega automaticamente TODOS os .png encontrados (ordem alfabética).
    def load_animation(self, path: str, size: tuple[int, int]) -> list[pygame.Surface]:
        frames: list[pygame.Surface] = []
        folder = Path(path)
        if folder.exists() and folder.is_dir():
            for img_path in sorted(folder.glob("*.png")):
                try:
                    image = pygame.image.load(str(img_path)).convert_alpha()
                    frames.append(pygame.transform.scale(image, size))
                except pygame.error:
                    continue
        return frames

    def set_state(self, state: str, reset: bool = False) -> None:
        if state != self.state or reset:
            self.state = state
            self.frame_index = 0
            self.animation_timer = 0.0

    def _current_frames(self) -> list[pygame.Surface]:
        frames = self.animations.get(self.state, [])
        return frames if frames else [self.fallback_frame]

    def update_animation(self, dt: float, loop: bool = True) -> bool:
        frames = self._current_frames()
        if len(frames) <= 1:
            return True

        self.animation_timer += dt
        frame_time = 1.0 / max(1, self.animation_fps)
        finished = False

        while self.animation_timer >= frame_time:
            self.animation_timer -= frame_time
            self.frame_index += 1
            if self.frame_index >= len(frames):
                if loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(frames) - 1
                    finished = True
                    break
        return finished

    def move_and_collide(self, solids: list[pygame.Rect]) -> None:
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

    def current_frame(self) -> pygame.Surface:
        frames = self._current_frames()
        idx = max(0, min(self.frame_index, len(frames) - 1))
        frame = frames[idx]
        if self.facing == "left":
            return pygame.transform.flip(frame, True, False)
        return frame

    def draw(self, surface: pygame.Surface, camera_x: int) -> None:
        image = self.current_frame()
        draw_rect = image.get_rect(midbottom=(self.rect.centerx - camera_x, self.rect.bottom))
        surface.blit(image, draw_rect)
