import pygame as pg
import math
import random

YELLOW = (255, 255, 85)
GREY = (153, 153, 169)
WHITE = (255, 255, 255)

WALK_ANIM_SPEED = {
    1: 140,
    2: 80,
    3: 40,
    4: 15
}


class Character(pg.sprite.Sprite):
    MAX_X_SPEED = 4
    MAX_RISING_SPEED = -360
    MAX_FALLING_SPEED = 600
    GRAVITY = 650

    VEL = {
        0: 48,
        1: 48,
        2: 48,
        3: 60,
        4: 102,
    }

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.x = 290
        self.y = 491
        self.x_speed = 0
        self.y_speed = 0
        self.flap = 0
        self.frame = 0
        self.next_update_time = 0
        self.next_anim_time = 0
        self.target_x_speed = 8
        self.walking = True
        self.facing_right = True
        self.spawning = 0

    def velocity(self, delta):
        if not self.walking:
            self.y_speed += self.GRAVITY * delta

        self.x_speed = max(self.x_speed, -self.MAX_X_SPEED)
        self.x_speed = min(self.x_speed, self.MAX_X_SPEED)
        self.y_speed = max(self.y_speed, self.MAX_RISING_SPEED)
        self.y_speed = min(self.y_speed, self.MAX_FALLING_SPEED)

        self.x += (self.x_speed * self.VEL[abs(math.floor(self.x_speed))]) * delta
        self.y += (self.y_speed * .6) * delta

        if self.y < 0:  # can't go off the top
            self.y = 0
            self.y_speed = 2

    def wrap(self, on_wrap=None):
        if self.x < -52:
            self.x = 882
            if on_wrap:
                on_wrap()
        if self.x > 898:
            self.x = -45
            if on_wrap:
                on_wrap()

    def animate(self, current_time):
        if self.walking:
            if self.next_anim_time < current_time:
                if self.x_speed != 0:
                    self.next_anim_time = current_time + WALK_ANIM_SPEED.get(abs(self.x_speed), 0)
                    self.frame += 1
                    if self.frame > 3:
                        self.frame = 0
        else:
            if self.flap > 0:
                self.frame = 5
            else:
                self.frame = 6

    def build_spawn(self, bird, index):
        y = 60 - index * 3
        colors = [YELLOW, GREY, WHITE]
        color1 = colors[random.randint(0, 2)]
        color2 = colors[random.randint(0, 2)]

        surf1 = pg.Surface((60, 60), pg.SRCALPHA)
        surf1.blit(self.mount, (12, y))
        mask = pg.mask.from_surface(surf1)
        surf1 = mask.to_surface(setcolor=color1)

        surf2 = pg.Surface((60, 60), pg.SRCALPHA)
        surf2.blit(bird, (0, y))
        mask = pg.mask.from_surface(surf2)
        surf2 = mask.to_surface(setcolor=color2, unsetcolor=(0, 0, 0, 0))

        result = pg.Surface((60, 60), pg.SRCALPHA)
        result.blit(surf1, (0, 0))
        result.blit(surf2, (0, 0))
        return result


class GodMode(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("resources/graphics/god.png")
        self.on = False
        self.rect = self.image.get_rect()
        self.rect.topleft = (850, 0)
        self.timer = pg.time.get_ticks()

    def toggle(self, current_time):
        if current_time > self.timer:
            self.on = not self.on
            self.timer = current_time + 100
