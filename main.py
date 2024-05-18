# Joust by S Paget

import asyncio
import pygame
import random

from enemy import Enemy
from player import Player
from actors import Platform, Godmode

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)


class Score:
    def __init__(self):
        self.score = 0
        self.eggs_collected = 0
        self.egg_points = [250, 500, 750, 1000]

    def collect_egg(self):
        points = self.egg_points[min(self.eggs_collected, len(self.egg_points) - 1)]
        self.score += points
        self.eggs_collected += 1
        return points

    def reset(self):
        self.eggs_collected = 0

    def draw(self, screen, digits):
        screen.blit(digits[self.score % 10], [353, 570])
        screen.blit(digits[(self.score % 100) // 10], [335, 570])
        screen.blit(digits[(self.score % 1000) // 100], [317, 570])
        screen.blit(digits[(self.score % 10000) // 1000], [299, 570])
        screen.blit(digits[(self.score % 100000) // 10000], [281, 570])
        screen.blit(digits[(self.score % 1000000) // 100000], [263, 570])


def load_sliced_sprites(w, h, filename):
    # returns a list of image frames sliced from file
    results = []
    master_image = pygame.image.load(filename).convert_alpha()
    master_width, master_height = master_image.get_size()
    for i in range(int(master_width / w)):
        results.append(master_image.subsurface((i * w, 0, w, h)))
    return results


def generate_enemies(images, enemies, spawn_points, enemies_to_spawn):
    # makes 2 enemies at a time, at 2 random different spawn points
    chosen = spawn_points.copy()
    random.shuffle(chosen)
    for count in range(2):
        enemies.add(Enemy(images, chosen[count], 0))
        enemies_to_spawn -= 1

    return enemies, enemies_to_spawn


def draw_lava(screen):
    lava_rect = [0, 600, 900, 50]
    pygame.draw.rect(screen, (255, 0, 0), lava_rect)
    return lava_rect


def draw_lava2(screen):
    lava_rect = [0, 620, 900, 30]
    pygame.draw.rect(screen, (255, 0, 0), lava_rect)
    return lava_rect


def draw_lives(lives, screen, life_image):
    start_x = 375
    for num in range(lives):
        x = start_x + num * 20
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
    "enemy":    load_sliced_sprites(60, 58, "resources/graphics/enemies2.png"),
    "spawn":    load_sliced_sprites(60, 60, "resources/graphics/spawn1.png"),
    "unmounted": load_sliced_sprites(60, 60, "resources/graphics/unmounted.png"),
    "egg":      load_sliced_sprites(40, 33, "resources/graphics/egg.png"),
    "digits":   load_sliced_sprites(21, 21, "resources/graphics/digits.png"),
    "bird":     load_sliced_sprites(60, 60, "resources/graphics/playerMounted.png"),
    "player_unmounted": load_sliced_sprites(60, 60, "resources/graphics/playerUnMounted.png"),
}

player_bird = Player(image_sprites)

god = Godmode()
god_sprite.add(Godmode())
spawn_points = [[690, 248], [420, 500], [420, 80], [50, 255]]


class Platforms:
    # we create each platform by sending it the relevant platform image,
    # the x position of the platform and the y position
    p1 = Platform(pygame.image.load("resources/graphics/plat1.png"), 200,550)
    p2 = Platform(pygame.image.load("resources/graphics/plat2.png"), 350, 395)
    p3 = Platform(pygame.image.load("resources/graphics/plat3.png"), 350, 130)
    p4 = Platform(pygame.image.load("resources/graphics/plat4.png"), 0, 100)
    p5 = Platform(pygame.image.load("resources/graphics/plat5.png"), 759, 100)
    p6 = Platform(pygame.image.load("resources/graphics/plat6.png"), 0, 312)
    p7 = Platform(pygame.image.load("resources/graphics/plat7.png"), 769, 312)
    p8 = Platform(pygame.image.load("resources/graphics/plat8.png"), 600, 288)
    all = [p1, p2, p3, p4, p5, p6, p7, p8]

player.add(player_bird)
platforms.add(Platforms.all)
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
            enemies, enemies_to_spawn = generate_enemies(image_sprites, enemies, spawn_points, enemies_to_spawn)
            next_spawn_time = current_time + 5000

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
        score.draw(screen, image_sprites["digits"])

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
