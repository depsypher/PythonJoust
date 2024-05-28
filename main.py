# Joust by S Paget

import asyncio
import pygame as pg
import random
import loader

from enemy import Enemy
from message import Message
from player import Player
from actors import GodMode, Score
from cliff import Cliff

pg.init()
pg.mixer.pre_init(44100, -16, 2, 512)
pg.display.set_caption('Joust')
window = pg.display.set_mode((900, 650))
clock = pg.time.Clock()
screen = pg.display.get_surface()
clear_surface = screen.copy()


async def main():
    global clock, screen, clear_surface, state, enemies, enemies_spawning

    while state['running']:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                # sys.exit()
                return

        delta = clock.tick(60) * 0.001
        current_time = pg.time.get_ticks()

        current_wave = state['wave']
        waves = state['waves']

        if state['increment_wave']:
            current_wave += 1
            state['wave'] = current_wave
            state['wave_start'] = current_time
            state['increment_wave'] = False
            wave_index = current_wave % len(waves) if current_wave != len(waves) else len(waves)
            wave_data = waves[wave_index]
            enemies_spawning = wave_data['enemies'].copy()
            reset = len(waves) - 1 if wave_index == 1 else wave_index - 1
            for task_data in waves[reset]['tasks']:
                task_data['started'] = False

        wave_index = current_wave % len(waves) if current_wave != len(waves) else len(waves)
        wave_data = waves[wave_index]

        for task_data in wave_data['tasks']:
            if not task_data['started'] and ((state['wave_start'] + task_data['delay']) < current_time):
                task = task_data['task']
                if len(task[1]) > 0 and task[1][0] == 'WAVE':
                    task[0](*task[1], current_wave)
                else:
                    task[0](*task[1])
                task_data['started'] = True

        all_sprites.clear(screen, clear_surface)

        # make enemies
        if current_time > state['next_spawn_time'] and len(enemies_spawning) > 0:
            enemy_type = enemies_spawning[0]#random.randint(0, 1)
            generate_enemies(Sprites, enemies, spawn_points, enemy_type)
            enemies_spawning.pop(0)
            state['next_spawn_time'] = current_time + 2000

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
            state['god'].toggle(current_time)
            if not state['god'].on:
                screen.blit(clear_surface, (20, 20), (0, 0, 200, 20))

        if len(enemies_spawning) == 0 and len(enemies.sprites()) == 0 and len(eggs.sprites()) == 0:
            state['increment_wave'] = True

        if not state['paused']:
            player.update(current_time, keys, platforms, enemies, eggs, score, state)
            platforms.update(current_time)
            enemies.update(current_time, keys, platforms, enemies)
            eggs.update(current_time, platforms)
            for message in messages:
                message.update(current_time, lambda m: messages.remove(m))

        if state['god'].on:
            font = pg.font.SysFont(None, 24)
            img = font.render(f'FPS: {clock.get_fps():3.4f}'
                              f' x_speed: {player1.x_speed}', True, (0, 0, 255))
            rect = img.get_rect().copy()
            rect.width += 10
            screen.blit(clear_surface, (20, 20), rect)
            screen.blit(img, (20, 20))
            add_sprite(god_sprite, state['god'])
        else:
            all_sprites.remove(god_sprite)

        lavaRect = draw_lava(screen)
        sprite_rects = all_sprites.draw(screen)

        draw_lives(player1.lives, screen, Sprites.life)
        score.draw(screen, Sprites.chars)

        pg.display.update(lavaRect)
        pg.display.update(sprite_rects)

        await asyncio.sleep(0)


messages = []
player = pg.sprite.RenderUpdates()
enemies = pg.sprite.RenderUpdates()
eggs = pg.sprite.RenderUpdates()
platforms = pg.sprite.RenderUpdates()
god_sprite = pg.sprite.RenderUpdates()
all_sprites = pg.sprite.RenderUpdates()


def add_sprite(group, sprite):
    if group is not None:
        group.add(sprite)
    all_sprites.add(sprite)


def draw_text(text, x, y, duration, color=None, wave=None):
    if wave:
        text = f"{text} {wave}"
    message = Message(text, Sprites.chars, x, y, duration, color)
    add_sprite(None, message)
    messages.append(message)


def generate_enemies(sprites, enemies, spawn_points, enemy_type):
    chosen = spawn_points.copy()
    random.shuffle(chosen)
    add_sprite(enemies, Enemy(sprites, chosen[0], enemy_type))


def draw_lava(screen):
    lava_rect = [0, 620, 900, 80]
    pg.draw.rect(screen, (255, 0, 0), lava_rect)
    return lava_rect


def draw_lives(lives, screen, life_image):
    start_x = 330
    for num in range(lives):
        x = start_x + num * 19
        screen.blit(life_image, [x, 570])


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
    poof = loader.load_sprite(414, 69, 11, 11, 3, 3, 3, sheet)
    chars = loader.load_sprite(1, 93, 11, 7, 3, 0, 50, sheet)
    chars_small = loader.load_sprite(1, 105, 5, 5, 3, 4, 36, sheet)
    c1 = Cliff(None, -60, 550)
    c2 = Cliff(loader.load_image(370, 0, 64, 8, 3, sheet), 315, 420)     # mid-bottom
    c3 = Cliff(loader.load_image(92, 0, 88, 9, 3, sheet), 250, 201)      # mid-top
    c4 = Cliff(loader.load_image(0, 0, 33, 7, 3, sheet), -10, 168)          # top-left
    c5 = Cliff(loader.load_image(39, 0, 47, 7, 3, sheet), 759, 168)      # top-right
    c6 = Cliff(loader.load_image(186, 0, 63, 8, 3, sheet), 0, 354)       # bottom-left
    c7 = Cliff(loader.load_image(319, 0, 46, 7, 3, sheet), 770, 354)     # bottom-right
    c8 = Cliff(loader.load_image(254, 0, 58, 11, 3, sheet), 606, 330)    # mid-right
    platforms = [c1, c2, c3, c4, c5, c6, c7, c8]


spawn_points = [
    [690, 270],     # right
    [378, 491],     # bottom
    [327, 141],     # top
    [48, 294],      # left
]

state = {
    'running': True,
    'paused':  False,
    'god': GodMode(),
    'p_down_last_frame': False,
    'next_spawn_time': pg.time.get_ticks() + 2000,
    'wave': 0,
    'wave_start': 0,
    'increment_wave': True,
    'waves': {
        1: {
            'tasks': [
                {
                    'delay': 1500,
                    'task': (draw_text, ("WAVE",  342, 240, 3000, (240, 240, 240))),
                    'started': False
                },
                {
                    'delay': 1500,
                    'task': (draw_text, ('PREPARE TO JOUST', 260, 320, 3000, (240, 240, 240))),
                    'started': False
                },
                {
                    'delay': 3000,
                    'task': (draw_text, ('BUZZARD BAIT!', 303, 396, 1500, (240, 240, 240))),
                    'started': False
                },
            ],
            'enemies': [0, 0, 0]
        },
        2: {
            'tasks': [
                {
                    'delay': 1500,
                    'task': (draw_text, ("WAVE",  342, 240, 3000, (240, 240, 240))),
                    'started': False
                },
                {
                    'delay': 1500,
                    'task': (draw_text, ('SURVIVAL WAVE', 260, 320, 3000, (240, 240, 240))),
                    'started': False
                },
            ],
            'enemies': [0, 0, 0, 0]
        },
        3: {
            'tasks': [
                {
                    'delay': 0,
                    'task': (draw_text, ("WAVE",  342, 240, 3000, (240, 240, 240))),
                    'started': False
                },
                {
                    'delay': 0,
                    'task': (Sprites.c1.burn, ()),
                    'started': False
                },
            ],
            'enemies': [0, 0, 0, 0, 0, 0]
        },
        4: {
            'tasks': [
                {
                    'delay': 0,
                    'task': (draw_text, ("WAVE",  342, 240, 3000, (240, 240, 240))),
                    'started': False
                },
            ],
            'enemies': [0, 0, 0, 1, 1, 1]
        },
    }
}

enemies_spawning = []
score = Score()

player1 = Player(Sprites, add_sprite, state)
add_sprite(player, player1)
add_sprite(platforms, Sprites.platforms)

asyncio.run(main())
