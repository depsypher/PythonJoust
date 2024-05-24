import pygame as pg

class Character(pg.sprite.Sprite):
    MAX_X_SPEED = 8
    MAX_RISING_SPEED = -6
    MAX_FALLING_SPEED = 10

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
        self.targetXSpeed = 10
        self.walking = True
        self.facing_right = True
        self.spawning = True

    def player_velocity(self):
        self.x += self.x_speed
        self.y += self.y_speed

        if not self.walking:
            self.y_speed += 0.2

        self.x_speed = max(self.x_speed, -self.MAX_X_SPEED)
        self.x_speed = min(self.x_speed, self.MAX_X_SPEED)
        self.y_speed = max(self.y_speed, self.MAX_RISING_SPEED)
        self.y_speed = min(self.y_speed, self.MAX_FALLING_SPEED)

        if self.y < 0:  # can't go off the top
            self.y = 0
            self.y_speed = 2

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
                self.frame = 6
            else:
                self.frame = 5


class Platform(pg.sprite.Sprite):
    def __init__(self, image, x, y):
        pg.sprite.Sprite.__init__(self)
        if image is not None:
            self.image = image
            self.mask = pg.mask.from_surface(self.image)
        else:
            surf = pg.Surface((185, 9), pg.SRCALPHA)
            pg.draw.rect(surf, (141, 73, 23), pg.Rect(0, 0, 185, 9))
            self.mask = pg.mask.from_surface(surf)
            self.image = surf

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)


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

    def die(self):
        self.score += 50

    def reset(self):
        self.eggs_collected = 0

    def draw(self, screen, digits):
        xpos = 222
        d = 10000000
        seen = False
        while d >= 10:
            i = (self.score % d) // (d // 10)
            if i != 0 or d == 10 or seen:
                screen.blit(digits[i], [xpos, 570])
                seen = True
            d //= 10
            xpos += 17


class Godmode(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.pic = pg.image.load("resources/graphics/god.png")
        self.image = self.pic
        self.on = False
        self.rect = self.image.get_rect()
        self.rect.topleft = (850, 0)
        self.timer = pg.time.get_ticks()

    def toggle(self, current_time):
        if current_time > self.timer:
            self.on = not self.on
            self.timer = current_time + 100
