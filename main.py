# Joust by S Paget

import asyncio
import pygame as pg
import random
import loader

from util import SPAWN_POINTS, wrapped_distance, LANES
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
delta = 0


async def main():
    global delta, state, enemies_spawning, player1

    while state['running']:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                # sys.exit()
                return

        current_time = pg.time.get_ticks()

        keys = pg.key.get_pressed()
        pg.event.clear()
        on_key(keys, pg.K_ESCAPE, toggle, 'running')    # exit game
        on_key(keys, pg.K_p, toggle, 'paused')
        on_key(keys, pg.K_k, lambda: player1.die(score))
        on_key(keys, pg.K_g, toggle_god_mode, (current_time, keys))

        current_wave = state['wave']
        waves = state['waves']

        if player1.lives < 1:
            if state['game_over'] == 0:
                state['game_over'] = current_time
            draw_text('THY GAME IS OVER', 285, 369, 1500, (240, 240, 240))
            if current_time > state['game_over'] + 1000:
                on_key(keys, pg.K_SPACE, toggle, 'restart')

        if state['restart']:
            score.clear()
            player1 = Player(Sprites, add_sprite, state)
            current_wave = 0
            state['wave'] = 0
            state['wave_start'] = current_time
            state['game_over'] = 0
            state['increment_wave'] = True
            for wave_num in waves.keys():
                for task_data in waves[wave_num]['tasks']:
                    task_data['started'] = False

            for enemy in enemies:
                enemy.kill()
            state['restart'] = False

        if (current_time > state['wave_start'] + 6000 and len(enemies_spawning) == 0
                and len(enemies.sprites()) == 0 and len(eggs.sprites()) == 0):
            state['increment_wave'] = True

        if state['increment_wave']:
            score.reset()
            current_wave += 1
            state['wave'] = current_wave
            state['wave_start'] = current_time
            state['increment_wave'] = False
            wave_index = current_wave % len(waves) if current_wave != len(waves) else len(waves)
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

        generate_enemies(current_time, enemies_spawning)

        if not state['paused']:
            player.update(current_time, delta, keys, platforms, enemies, eggs, score, state)
            platforms.update(current_time)
            enemies.update(current_time, delta, platforms, enemies)
            eggs.update(current_time, delta, platforms, eggs)
            for message in messages:
                message.update(current_time, lambda m: messages.remove(m))

        sprite_rects = all_sprites.draw(screen)
        draw_god_mode()
        draw_lives()
        score.draw(screen, Sprites.chars)

        # for debugging
        # for lane in LANES:
        #     lava_rect = [0, lane, 900, 1]
        #     pg.draw.rect(screen, (255, 0, 0), lava_rect)

        pg.display.update(sprite_rects)
        delta = clock.tick(60) / 1000

        await asyncio.sleep(0)


messages = []
enemies_spawning = []

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


def generate_enemies(current_time, spawning):
    global state
    if current_time > state['next_spawn_time'] and len(spawning) > 0:
        enemy_type = spawning[0]
        choices = SPAWN_POINTS.copy()
        choices.sort(key=lambda c: wrapped_distance(c[0], c[1], player1.x, player1.y, 900))
        choices = choices[-3:]
        random.shuffle(choices)
        add_sprite(enemies, Enemy(Sprites, choices[0], enemy_type))
        spawning.pop(0)
        state['next_spawn_time'] = current_time + 1000


def draw_lives():
    start_x = 330
    for num in range(player1.lives):
        x = start_x + num * 19
        screen.blit(Sprites.life, [x, 570])


def set_spawning(*to_spawn):
    global enemies_spawning
    enemies_spawning = list(to_spawn)


def create_player():
    add_sprite(player, player1)
    player1.lives -= 1


def on_key(keys, key, action, args=None):
    if keys[key]:
        if key not in state['keys_last_frame']:
            if isinstance(args, tuple):
                action(*args)
            elif args:
                action(args)
            else:
                action()
        state['keys_last_frame'].append(key)
    elif key in state['keys_last_frame']:
        state['keys_last_frame'].remove(key)


def toggle(val):
    state[val] = not state[val]


def toggle_god_mode(current_time, keys):
    if keys[pg.K_g]:
        state['god'].toggle(current_time)
        if not state['god'].on:
            screen.blit(clear_surface, (20, 20), (0, 0, 200, 20))


def draw_god_mode():
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


class Sprites:
    sheet = "resources/graphics/spritesheet.png"
    life = loader.load_image(89, 79, 6, 7, 3, sheet)
    p1mount = loader.load_image(58, 79, 12, 7, 3, sheet)
    ostrich = loader.load_sprite(348, 19, 16, 20, 3, 5, 8, sheet)
    buzzard = loader.load_sprite(191, 44, 20, 20, 3, 3, 7, sheet)
    bounder = loader.load_sprite(58, 69, 12, 7, 3, 0, 1, sheet)
    hunter = loader.load_sprite(73, 69, 12, 7, 3, 0, 1, sheet)
    egg = loader.load_sprite(140, 69, 9, 7, 3, 6, 4, sheet)
    poof = loader.load_sprite(414, 69, 11, 11, 3, 3, 3, sheet)
    flames = loader.load_sprite(1, 69, 8, 18, 3, 3, 4, sheet)
    chars = loader.load_sprite(1, 93, 11, 7, 3, 0, 50, sheet)
    chars_small = loader.load_sprite(1, 105, 5, 5, 3, 4, 36, sheet)
    c1 = Cliff(None, -60, 550, flames)
    c2 = Cliff(loader.load_image(385, 0, 64, 8, 3, sheet), 315, 420)     # mid-bottom
    c3 = Cliff(loader.load_image(82, 0, 88, 9, 3, sheet), 250, 201)      # mid-top
    c4 = Cliff(loader.load_image(0, 9, 50, 7, 3, sheet), -60, 168)          # top-left
    c5 = Cliff(loader.load_image(0, 0, 64, 7, 3, sheet), 759, 168)       # top-right
    c6 = Cliff(loader.load_image(173, 0, 80, 8, 3, sheet), -50, 354)        # bottom-left
    c7 = Cliff(loader.load_image(319, 0, 63, 7, 3, sheet), 770, 354)     # bottom-right
    c8 = Cliff(loader.load_image(254, 0, 58, 11, 3, sheet), 606, 330)    # mid-right
    platforms = [c1, c2, c3, c4, c5, c6, c7, c8]


state = {
    'running': True,
    'paused':  False,
    'god': GodMode(),
    'keys_last_frame': [],
    'next_spawn_time': 0,
    'wave': 0,
    'wave_start': 0,
    'increment_wave': True,
    'game_over': 0,
    'restart': False,
    'waves': {
        1: {
            'tasks': [
                {
                    'delay': 1600,
                    'task': (create_player, ()),
                    'started': False
                },
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
                {
                    'delay': 5000,
                    'task': (set_spawning, ([0, 0, 0])),
                    'started': False
                },
            ]
        },
        2: {
            'tasks': [
                {
                    'delay': 0,
                    'task': (draw_text, ("WAVE",  342, 240, 3000, (240, 240, 240))),
                    'started': False
                },
                {
                    'delay': 0,
                    'task': (draw_text, ('SURVIVAL WAVE', 280, 320, 3000, (240, 240, 240))),
                    'started': False
                },
                {
                    'delay': 4000,
                    'task': (set_spawning, ([0, 0, 0, 0])),
                    'started': False
                },
            ],
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
                {
                    'delay': 4000,
                    'task': (set_spawning, ([0, 0, 0, 0, 0, 0])),
                    'started': False
                },
            ],
        },
        4: {
            'tasks': [
                {
                    'delay': 0,
                    'task': (draw_text, ("WAVE",  342, 240, 3000, (240, 240, 240))),
                    'started': False
                },
                {
                    'delay': 4000,
                    'task': (set_spawning, ([0, 0, 0, 1, 1, 1])),
                    'started': False
                },
            ],
        },
    }
}
player1 = Player(Sprites, add_sprite, state)
add_sprite(platforms, Sprites.platforms)
score = Score()

asyncio.run(main())
