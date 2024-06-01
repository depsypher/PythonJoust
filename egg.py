import pygame as pg

import actors


class Egg(actors.Character):
    def __init__(self, egg_images, chars_small, x, y, x_speed, y_speed):
        super().__init__()
        self.egg_images = egg_images
        self.chars_small = chars_small
        self.image = self.egg_images[0]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.rect.topleft = (x, y)
        self.walking = False
        self.bonus = True   # until it hits a platform

    def update(self, current_time, delta, platforms):
        self.velocity(delta)
        self.wrap()
        self.rect.topleft = (self.x, self.y)
        collided_platforms = pg.sprite.spritecollide(self, platforms, False, pg.sprite.collide_mask)
        for collidedPlatform in collided_platforms:
            self.bonus = False
            self.bounce(collidedPlatform)

        if self.y > 570:  # hit lava
            self.kill()
        self.rect.topleft = (self.x, self.y)

    def bounce(self, collider):
        if self.y < collider.y and ((collider.x - 40) < self.x < (collider.rect.right - 10)):
            # egg is above collider
            self.x_speed *= 0.5
            self.y_speed = -abs(self.y_speed) * 0.25
            self.y = collider.y - self.rect.height + 1
        elif self.x < collider.x:
            # egg is left of collider
            self.x -= 3
            self.x_speed = -self.x_speed + 1
        elif self.x > collider.rect.right + self.x_speed:
            # egg is right of collider
            self.x += 3
            self.x_speed = -self.x_speed + 1
        elif self.y > collider.y:
            # egg is below collider
            self.y = self.y + 10
            self.y_speed = 0
