# Joust by S Paget

import asyncio
import pygame as pg
import random
import loader

from enemy import Enemy
from player import Player
from actors import Platform, Godmode, Score

pg.init()
pg.mixer.pre_init(44100, -16, 2, 512)


def generate_enemies(sprites, enemies, spawn_points, to_spawn):
    chosen = spawn_points.copy()
    random.shuffle(chosen)
    for count in range(1):
        enemy_type = random.randint(0, 1)
        enemies.add(Enemy(sprites, chosen[count], enemy_type))
        to_spawn -= 1

    return enemies, to_spawn


def draw_lava(screen):
    lava_rect = [0, 620, 900, 80]
    pg.draw.rect(screen, (255, 0, 0), lava_rect)
    return lava_rect


def draw_lives(lives, screen, life_image):
    start_x = 342
    for num in range(lives):
        x = start_x + num * 19
        screen.blit(life_image, [x, 570])


running = True
paused = False
p_down_last_frame = False
#clock = pg.time.Clock()
window = pg.display.set_mode((900, 650))
pg.display.set_caption('Joust')
screen = pg.display.get_surface()
clear_surface = screen.copy()

player = pg.sprite.RenderUpdates()
enemies = pg.sprite.RenderUpdates()
eggs = pg.sprite.RenderUpdates()
platforms = pg.sprite.RenderUpdates()
god_sprite = pg.sprite.RenderUpdates()


class Sprites:
    sheet = "resources/graphics/spritesheet.png"
    life = pg.image.load("resources/graphics/life.png").convert_alpha()
    p1mount = loader.load_image(58, 79, 12, 7, 3, sheet)
    ostrich = loader.load_sprite(347, 19, 16, 20, 3, 5, 8, sheet)
    buzzard = loader.load_sprite(191, 44, 20, 14, 3, 3, 7, sheet)
    bounder = loader.load_sprite(58, 69, 12, 7, 3, 0, 1, sheet)
    hunter = loader.load_sprite(73, 69, 12, 7, 3, 0, 1, sheet)
    spawn = loader.load_sliced_sprites(60, 60, "resources/graphics/spawn1.png")
    egg = loader.load_sprite(140, 69, 9, 7, 3, 6, 4, sheet)
    alpha = loader.load_sprite(2, 93, 5, 7, 3, 6, 49, sheet)
    p1 = Platform(pg.image.load("resources/graphics/plat1.png"), 166, 550)
    p2 = Platform(loader.load_image(370, 0, 64, 8, 3, sheet), 315, 420)
    p3 = Platform(loader.load_image(92, 0, 88, 9, 3, sheet), 250, 201)
    p4 = Platform(loader.load_image(0, 0, 33, 7, 3, sheet), -10, 168)
    p5 = Platform(loader.load_image(39, 0, 47, 7, 3, sheet), 759, 168)
    p6 = Platform(loader.load_image(186, 0, 63, 8, 3, sheet), 0, 354)
    p7 = Platform(loader.load_image(319, 0, 46, 7, 3, sheet), 770, 354)
    p8 = Platform(loader.load_image(254, 0, 58, 11, 3, sheet), 606, 330)
    platforms = [p1, p2, p3, p4, p5, p6, p7, p8]


p1 = Player(Sprites)

god = Godmode()
god_sprite.add(Godmode())
spawn_points = [[690, 270], [378, 500], [327, 141], [48, 300]]

player.add(p1)
platforms.add(Sprites.platforms)
pg.display.update()
next_spawn_time = pg.time.get_ticks() + 2000
enemies_to_spawn = 6  # test. make 6 enemies to start
score = Score()


async def main():
    global running, next_spawn_time, enemies_to_spawn, enemies, screen, clear_surface, paused, p_down_last_frame

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                # sys.exit()
                return

#        delta = clock.tick() * 0.001
        current_time = pg.time.get_ticks()

        player.clear(screen, clear_surface)
        enemies.clear(screen, clear_surface)
        eggs.clear(screen, clear_surface)
        god_sprite.clear(screen, clear_surface)

        # make enemies
        if current_time > next_spawn_time and enemies_to_spawn > 0:
            enemies, enemies_to_spawn = generate_enemies(Sprites, enemies, spawn_points, enemies_to_spawn)
            next_spawn_time = current_time + 2000

        keys = pg.key.get_pressed()
        pg.event.clear()

        # If they have pressed Escape, close down Pygame
        if keys[pg.K_ESCAPE]:
            running = False

        if keys[pg.K_p]:
            if not p_down_last_frame:
                paused = not paused
            p_down_last_frame = True
        else:
            p_down_last_frame = False

        # check for God mode toggle
        if keys[pg.K_g]:
            god.toggle(current_time)
            if not god.on:
                screen.fill((0, 0, 0))

        if not paused:
            player.update(current_time, keys, platforms, enemies, god, eggs, score)
            platforms.update()
            enemies.update(current_time, keys, platforms, enemies)
            eggs.update(current_time, platforms)

        enemiesRects = enemies.draw(screen)
        playerRect = player.draw(screen)
        eggRects = eggs.draw(screen)
        lavaRect = draw_lava(screen)
        platRects = platforms.draw(screen)

        draw_lives(p1.lives, screen, Sprites.life)
        score.draw(screen, Sprites.alpha)

        pg.display.update(playerRect)
        pg.display.update(lavaRect)
        pg.display.update(platRects)
        pg.display.update(enemiesRects)
        pg.display.update(eggRects)

        if god.on:
            screen.fill((0, 0, 0))
            font = pg.font.SysFont(None, 24)
            # img = font.render(f'FPS: {clock.get_fps():3.4f}', True, (0, 0, 255))
            img = font.render(f'FPS: {60.0:3.4f}', True, (0, 0, 255))
            screen.blit(img, (20, 20))
            pg.display.update(god_sprite.draw(screen))
        else:
            pg.display.update(pg.Rect(850, 0, 50, 50))

    await asyncio.sleep(0)


asyncio.run(main())
