# Joust by S Paget

import asyncio
import pygame
import random
import loader

from enemy import Enemy
from player import Player
from actors import Platform, Godmode, Score

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)


def generate_enemies(sprites, enemies, spawn_points, to_spawn):
    chosen = spawn_points.copy()
    random.shuffle(chosen)
    for count in range(1):
        enemy_type = random.randint(0, 1)
        enemies.add(Enemy(sprites, chosen[count], enemy_type))
        to_spawn -= 1

    return enemies, to_spawn


def draw_lava(screen):
    lava_rect = [0, 600, 900, 50]
    pygame.draw.rect(screen, (255, 0, 0), lava_rect)
    return lava_rect


def draw_lava2(screen):
    lava_rect = [0, 620, 900, 30]
    pygame.draw.rect(screen, (255, 0, 0), lava_rect)
    return lava_rect


def draw_lives(lives, screen, life_image):
    start_x = 342
    for num in range(lives):
        x = start_x + num * 19
        screen.blit(life_image, [x, 570])


running = True
window = pygame.display.set_mode((900, 650))
pygame.display.set_caption('Joust')
screen = pygame.display.get_surface()
clear_surface = screen.copy()

player = pygame.sprite.RenderUpdates()
enemies = pygame.sprite.RenderUpdates()
eggs = pygame.sprite.RenderUpdates()
platforms = pygame.sprite.RenderUpdates()
god_sprite = pygame.sprite.RenderUpdates()

life_image = pygame.image.load("resources/graphics/life.png").convert_alpha()

image_sprites = {
    "spawn":     loader.load_sliced_sprites(60, 60, "resources/graphics/spawn1.png"),
    "egg":       loader.load_sliced_sprites(40, 33, "resources/graphics/egg.png"),
    "bird":      loader.load_sliced_sprites(60, 60, "resources/graphics/playerMounted.png"),
    "player_unmounted": loader.load_sliced_sprites(60, 60, "resources/graphics/playerUnMounted.png"),
}


class Sprites:
    buzzard = loader.load_sprite(191, 44, 20, 14, 3, 3, 7, "resources/graphics/spritesheet.png")
    bounder = loader.load_sprite(586, 44, 12, 7, 3, 0, 1, "resources/graphics/spritesheet.png")
    hunter = loader.load_sprite(35, 69, 12, 7, 3, 0, 1, "resources/graphics/spritesheet.png")
    spawn = loader.load_sliced_sprites(60, 60, "resources/graphics/spawn1.png")
    alpha = loader.load_sprite(2, 93, 5, 7, 3, 6, 49, "resources/graphics/spritesheet.png")
    p1 = Platform(pygame.image.load("resources/graphics/plat1.png"), 166, 550)
    p2 = Platform(loader.load_image(370, 0, 64, 8, 3, "resources/graphics/spritesheet.png"), 315, 420)
    p3 = Platform(loader.load_image(92, 0, 88, 9, 3, "resources/graphics/spritesheet.png"), 250, 201)
    p4 = Platform(loader.load_image(0, 0, 33, 7, 3, "resources/graphics/spritesheet.png"), 0, 168)
    p5 = Platform(loader.load_image(39, 0, 47, 7, 3, "resources/graphics/spritesheet.png"), 759, 168)
    p6 = Platform(loader.load_image(186, 0, 63, 8, 3, "resources/graphics/spritesheet.png"), 0, 354)
    p7 = Platform(loader.load_image(319, 0, 46, 7, 3, "resources/graphics/spritesheet.png"), 770, 354)
    p8 = Platform(loader.load_image(254, 0, 58, 11, 3, "resources/graphics/spritesheet.png"), 606, 330)
    platforms = [p1, p2, p3, p4, p5, p6, p7, p8]


player_bird = Player(image_sprites)

god = Godmode()
god_sprite.add(Godmode())
spawn_points = [[690, 270], [378, 500], [327, 141], [48, 300]]

player.add(player_bird)
platforms.add(Sprites.platforms)
pygame.display.update()
next_spawn_time = pygame.time.get_ticks() + 2000
enemies_to_spawn = 6  # test. make 6 enemies to start
score = Score()


async def main():
    global running, next_spawn_time, enemies_to_spawn, enemies

    while running:
        current_time = pygame.time.get_ticks()
        player.clear(screen, clear_surface)
        enemies.clear(screen, clear_surface)
        eggs.clear(screen, clear_surface)
        god_sprite.clear(screen, clear_surface)

        # make enemies
        if current_time > next_spawn_time and enemies_to_spawn > 0:
            enemies, enemies_to_spawn = generate_enemies(Sprites, enemies, spawn_points, enemies_to_spawn)
            next_spawn_time = current_time + 2000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # sys.exit()
                return

        keys = pygame.key.get_pressed()
        pygame.event.clear()

        # If they have pressed Escape, close down Pygame
        if keys[pygame.K_ESCAPE]:
            running = False

        # check for God mode toggle
        if keys[pygame.K_g]:
            god.toggle(current_time)

        player.update(current_time, keys, platforms, enemies, god, eggs, score)
        platforms.update()
        enemies.update(current_time, keys, platforms, enemies)
        eggs.update(current_time, platforms)

        enemiesRects = enemies.draw(screen)
        playerRect = player.draw(screen)
        eggRects = eggs.draw(screen)
        lavaRect = draw_lava(screen)
        platRects = platforms.draw(screen)
        lavarect2 = draw_lava2(screen)

        draw_lives(player_bird.lives, screen, life_image)
        score.draw(screen, Sprites.alpha)

        godrect = god_sprite.draw(screen) if god.on else pygame.Rect(850, 0, 50, 50)

        pygame.display.update(playerRect)
        pygame.display.update(lavaRect)
        pygame.display.update(lavarect2)
        pygame.display.update(platRects)
        pygame.display.update(enemiesRects)
        pygame.display.update(eggRects)
        pygame.display.update(godrect)
        await asyncio.sleep(0)


asyncio.run(main())
