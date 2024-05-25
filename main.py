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
        add_sprite(enemies, Enemy(sprites, chosen[count], enemy_type))
        to_spawn -= 1

    return to_spawn


def draw_lava(screen):
    lava_rect = [0, 620, 900, 80]
    pg.draw.rect(screen, (255, 0, 0), lava_rect)
    return lava_rect


def draw_lives(lives, screen, life_image):
    start_x = 342
    for num in range(lives):
        x = start_x + num * 19
        screen.blit(life_image, [x, 570])


def add_sprite(group, sprite):
    group.add(sprite)
    all_sprites.add(sprite)


state = {
    'running': True,
    'paused':  False,
    'p_down_last_frame': False
}

window = pg.display.set_mode((900, 650))


class Sprites:
    sheet = "resources/graphics/spritesheet.png"
    life = pg.image.load("resources/graphics/life.png").convert_alpha()
    p1mount = loader.load_image(58, 79, 12, 7, 3, sheet)
    ostrich = loader.load_sprite(348, 19, 16, 20, 3, 5, 8, sheet)
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
    p9 = Platform(None, -19, 550)
    p10 = Platform(None, 723, 550)
    platforms = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10]


god = Godmode()
spawn_points = [[690, 270], [378, 500], [327, 141], [48, 300]]

player = pg.sprite.RenderUpdates()
enemies = pg.sprite.RenderUpdates()
eggs = pg.sprite.RenderUpdates()
platforms = pg.sprite.RenderUpdates()
god_sprite = pg.sprite.RenderUpdates()
all_sprites = pg.sprite.RenderUpdates()

p1 = Player(Sprites, add_sprite, state)
add_sprite(player, p1)
add_sprite(platforms, Sprites.platforms)
next_spawn_time = pg.time.get_ticks() + 2000
enemies_to_spawn = 6  # test. make 6 enemies to start
score = Score()

clock = pg.time.Clock()
pg.display.set_caption('Joust')
screen = pg.display.get_surface()
clear_surface = screen.copy()


async def main():
    global clock, state, next_spawn_time, enemies_to_spawn, enemies, screen, clear_surface

    while state['running']:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                # sys.exit()
                return

        delta = clock.tick(60) * 0.001
        current_time = pg.time.get_ticks()

        all_sprites.clear(screen, clear_surface)

        # make enemies
        if current_time > next_spawn_time and enemies_to_spawn > 0:
            enemies_to_spawn = generate_enemies(Sprites, enemies, spawn_points, enemies_to_spawn)
            next_spawn_time = current_time + 2000

        keys = pg.key.get_pressed()
        pg.event.clear()

        # If they have pressed Escape, close down Pygame
        if keys[pg.K_ESCAPE]:
            state['running'] = False

        if keys[pg.K_p]:
            if not state['p_down_last_frame']:
                state['paused'] = not state['paused']
            state['p_down_last_frame'] = True
        else:
            state['p_down_last_frame'] = False

        # check for God mode toggle
        if keys[pg.K_g]:
            god.toggle(current_time)
            if not god.on:
                screen.blit(clear_surface, (20, 20), (0, 0, 200, 20))

        if not state['paused']:
            player.update(current_time, keys, platforms, enemies, god, eggs, score, state)
            platforms.update()
            enemies.update(current_time, keys, platforms, enemies)
            eggs.update(current_time, platforms)

        if god.on:
            font = pg.font.SysFont(None, 24)
            img = font.render(f'FPS: {clock.get_fps():3.4f}\nx_speed: {p1.x_speed}', True, (0, 0, 255))
            rect = img.get_rect().copy()
            rect.width += 10
            screen.blit(clear_surface, (20, 20), rect)
            screen.blit(img, (20, 20))
            add_sprite(god_sprite, god)
        else:
            all_sprites.remove(god_sprite)

        lavaRect = draw_lava(screen)
        sprite_rects = all_sprites.draw(screen)

        draw_lives(p1.lives, screen, Sprites.life)
        score.draw(screen, Sprites.alpha)

        pg.display.update(lavaRect)
        pg.display.update(sprite_rects)

        await asyncio.sleep(0)


asyncio.run(main())
