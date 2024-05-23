import pygame as pg


class Egg(pg.sprite.Sprite):
    def __init__(self, egg_images, x, y, x_speed, y_speed):
        pg.sprite.Sprite.__init__(self)
        self.images = egg_images
        self.image = self.images[0]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.rect.topleft = (x, y)
        self.next_update_time = 0

    def update(self, current_time, platforms):
        if current_time < self.next_update_time:
            return

        self.next_update_time = current_time + 30

        self.y_speed += 0.4
        if self.y_speed > 10:
            self.y_speed = 10
        self.y += self.y_speed
        self.x += self.x_speed
        if -0.2 < self.x_speed < 0.2:
            self.x_speed = 0
        elif self.x_speed < 0:
            self.x_speed += 0.2
        else:
            self.x_speed -= 0.2

        if self.y > 570:  # hit lava
            self.kill()

        self.rect.topleft = (self.x, self.y)
        if (((40 < self.y < 45) or (250 < self.y < 255)) and (
                self.x < 0 or self.x > 860)):  # catch when it is rolling between screens
            self.y_speed = 0
        else:
            collided_platforms = pg.sprite.spritecollide(self, platforms, False, collided=pg.sprite.collide_mask)
            for collidedPlatform in collided_platforms:
                self.bounce(collidedPlatform)

        # wrap round screens
        if self.x < -48:
            self.x = 900
        if self.x > 900:
            self.x = -48

    def bounce(self, collider):
        if self.y < collider.y and ((collider.x - 40) < self.x < (collider.rect.right - 10)):
            # coming in from the top?
            self.y_speed = -abs(self.y_speed) * 0.25
            self.y = collider.y - self.rect.height + 1
        elif self.x < collider.x:
            # colliding from left side
            self.x -= 3
            self.x_speed = -2
        elif self.x > collider.rect.right + self.x_speed:
            # colliding from right side
            self.x += 3
            self.x_speed = 2
        elif self.y > collider.y:
            # colliding from bottom
            self.y = self.y + 10
            self.y_speed = 0
