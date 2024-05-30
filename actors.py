import pygame as pg
import math


class Character(pg.sprite.Sprite):
    MAX_X_SPEED = 4
    MAX_RISING_SPEED = -6
    MAX_FALLING_SPEED = 10
    GRAVITY = 0.2

    VEL = {
        0: 0.8,
        1: 0.8,
        2: 0.8,
        3: 1.0,
        4: 1.7
    }

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.x = 389
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
        self.spawning = True

    def velocity(self):
        if not self.walking:
            self.y_speed += self.GRAVITY

        self.x_speed = max(self.x_speed, -self.MAX_X_SPEED)
        self.x_speed = min(self.x_speed, self.MAX_X_SPEED)
        self.y_speed = max(self.y_speed, self.MAX_RISING_SPEED)
        self.y_speed = min(self.y_speed, self.MAX_FALLING_SPEED)

        self.x += (self.x_speed * self.VEL[abs(math.floor(self.x_speed))])
        self.y += (self.y_speed * .6)

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
                    self.next_anim_time = current_time + 100 / abs(self.x_speed)
                    self.frame += 1
                    if self.frame > 3:
                        self.frame = 0
                    else:
                        self.frame = 3
        else:
            if self.flap > 0:
                self.frame = 5
            else:
                self.frame = 6


class Score:
    def __init__(self):
        self.score = 0
        self.eggs_collected = 0
        self.egg_points = [250, 500, 750, 1000]

    def collect_egg(self, bonus):
        points = self.egg_points[min(self.eggs_collected, len(self.egg_points) - 1)]
        bonus_points = 500 if bonus else 0
        self.score += points + bonus_points
        self.eggs_collected += 1
        return points, bonus_points

    def kill(self, enemy):
        if enemy.enemyType == 1:
            self.score += 500
        elif enemy.enemyType == 2:
            self.score += 750
        elif enemy.enemyType == 3:
            self.score += 1000

    def die(self):
        self.score += 50

    def reset(self):
        self.eggs_collected = 0

    def draw(self, screen, digits):
        xpos = 210
        d = 10000000
        has_leading_digit = False
        while d >= 10:
            i = (self.score % d) // (d // 10)
            if i != 0 or d == 10 or has_leading_digit:
                screen.blit(digits[i], [xpos, 570])
                has_leading_digit = True
            d //= 10
            xpos += 17


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
