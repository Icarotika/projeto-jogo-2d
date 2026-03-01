"""Loop principal do jogo do Mago Invocador."""

from __future__ import annotations

import pygame

import settings
from camera import Camera
from enemies import Enemy
from player import Player
from summons import ExplosiveCard, MageSummon, WarriorSummon


def build_level() -> list[pygame.Rect]:
    """Cria chão e plataformas simples para movimentação."""
    solids = [
        pygame.Rect(0, settings.GROUND_Y, settings.WORLD_WIDTH, settings.SCREEN_HEIGHT - settings.GROUND_Y),
        pygame.Rect(280, 390, 160, 24),
        pygame.Rect(560, 330, 180, 24),
        pygame.Rect(860, 285, 140, 24),
        pygame.Rect(1170, 350, 220, 24),
        pygame.Rect(1520, 305, 180, 24),
        pygame.Rect(1840, 265, 160, 24),
    ]
    return solids


def spawn_enemies() -> list[Enemy]:
    return [
        Enemy(480, 420, 420, 700),
        Enemy(900, 235, 860, 1000),
        Enemy(1310, 300, 1200, 1450),
        Enemy(1700, 255, 1580, 1860),
    ]


def draw_world(
    screen: pygame.Surface,
    camera_x: int,
    solids: list[pygame.Rect],
    player: Player,
    enemies: list[Enemy],
    mage_summons: list[MageSummon],
    warrior_summons: list[WarriorSummon],
    cards: list[ExplosiveCard],
    ui_font: pygame.font.Font,
) -> None:
    screen.fill(settings.BG_COLOR)

    for solid in solids:
        color = settings.GROUND_COLOR if solid.y >= settings.GROUND_Y else settings.PLATFORM_COLOR
        pygame.draw.rect(screen, color, solid.move(-camera_x, 0))

    player.draw(screen, camera_x)

    for enemy in enemies:
        enemy.draw(screen, camera_x, ui_font)

    for summon in mage_summons:
        summon.draw(screen, camera_x)

    for summon in warrior_summons:
        summon.draw(screen, camera_x)

    for card in cards:
        card.draw(screen, camera_x)

    help_text = (
        "A/D mover | ESPAÇO pular | J mago | K guerreiro | L carta explosiva"
    )
    ui_surface = ui_font.render(help_text, True, settings.WHITE)
    screen.blit(ui_surface, (16, 14))


def main() -> None:
    pygame.init()
    pygame.display.set_caption(settings.TITLE)
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    ui_font = pygame.font.Font(None, 24)

    solids = build_level()
    player = Player(80, settings.GROUND_Y - settings.PLAYER_HEIGHT)
    enemies = spawn_enemies()
    camera = Camera(settings.WORLD_WIDTH, settings.SCREEN_WIDTH)

    mage_summons: list[MageSummon] = []
    warrior_summons: list[WarriorSummon] = []
    cards: list[ExplosiveCard] = []

    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_j:
                    mage_summons.append(
                        MageSummon(
                            player.rect.centerx + (player.facing * 20),
                            player.rect.bottom - 46,
                            player.facing,
                        )
                    )
                elif event.key == pygame.K_k:
                    warrior_summons.append(
                        WarriorSummon(player.rect.centerx + (player.facing * 22), player.rect.bottom - 50)
                    )
                elif event.key == pygame.K_l:
                    card_x = player.rect.centerx + (player.facing * 28)
                    card_y = player.rect.bottom - 10
                    cards.append(ExplosiveCard(card_x, card_y))

        keys = pygame.key.get_pressed()
        player.update(keys, solids)

        for enemy in enemies:
            enemy.update(solids)

        for summon in mage_summons:
            summon.update(dt, solids, enemies)

        for summon in warrior_summons:
            summon.update(dt, solids, enemies)

        for card in cards:
            card.update(dt, enemies)

        mage_summons = [s for s in mage_summons if not s.expired]
        warrior_summons = [s for s in warrior_summons if not s.expired]
        cards = [c for c in cards if not c.expired]
        enemies = [e for e in enemies if e.alive]

        camera.update(player.rect.centerx)
        draw_world(
            screen,
            camera.apply_x(),
            solids,
            player,
            enemies,
            mage_summons,
            warrior_summons,
            cards,
            ui_font,
        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
