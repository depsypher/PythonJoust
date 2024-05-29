import random

import pygame as pg

from egg import Egg
from actors import Character


class Enemy(Character):
    def __init__(self, sprites, start_pos, enemy_type: int):
        super().__init__()
        self.buzzard = sprites.buzzard
        if enemy_type == 0:
            self.mount = sprites.bounder
        else:
            self.mount = sprites.hunter
        self.spawn_images = sprites.spawn
        self.enemyType = enemy_type
        self.image = self.spawn_images[0]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.x = start_pos[0]
        self.y = start_pos[1]
        self.x_speed = random.randint(3, 10)
        if random.randint(0, 1) < 1:
            self.x_speed = -self.x_speed
            self.facing_right = False

        self.flapCount = 0
        self.alive = True

    def build_mount(self, buzzard, mount):
        surf = pg.Surface((60, 60), pg.SRCALPHA)
        surf.blit(mount, (18, 0))
        surf.blit(buzzard, (0, 0))
        self.mask = pg.mask.from_surface(surf)
        return surf

    def killed(self, eggs, egg_images, chars_small, killer, add_sprite, score):
        egg_x_speed = (self.x_speed + killer.x_speed) * 0.5
        egg_y_speed = (self.y_speed + killer.y_speed - 1) * 0.5
        add_sprite(eggs, Egg(egg_images, chars_small, self.x + 27, self.y + 21, egg_x_speed, egg_y_speed))
        score.kill(self)
        self.alive = False

    def update(self, current_time, keys, platforms, enemies):
        if current_time < self.next_update_time:
            return

        self.next_update_time = current_time + 50

        if self.spawning:
            self.frame += 1
            self.image = self.spawn_images[self.frame]
            if not self.facing_right:
                self.image = pg.transform.flip(self.image, True, False)

            self.next_update_time += 100
            self.rect.topleft = (self.x, self.y)
            if self.frame == 5:
                self.spawning = False
        else:
            # see if we need to accelerate
            if abs(self.x_speed) < self.targetXSpeed:
                self.x_speed += self.x_speed / abs(self.x_speed) / 2

            # work out if flapping...
            if self.flap < 1:
                if random.randint(0, 10) > 9 or self.y > 450:  # flap to avoid lava
                    self.y_speed -= 3
                    self.flap = 3
            else:
                self.flap -= 1

            self.velocity()

            if self.y > 570:  # hit lava
                self.kill()

            if self.x < -48:  # off the left. If enemy is dead then remove entirely
                if self.alive:
                    self.x = 900
                else:
                    self.kill()
            if self.x > 900:  # off the right. If enemy is dead then remove entirely
                if self.alive:
                    self.x = -48
                else:
                    self.kill()

            self.rect.topleft = (self.x, self.y)

            if self.alive:
                self.image = self.build_mount(self.buzzard[self.frame], self.mount[0])
            else:
                self.image = self.buzzard[self.frame]

            if self.x_speed < 0 or (self.x_speed == 0 and not self.facing_right):
                self.image = pg.transform.flip(self.image, True, False)
                self.facing_right = False
            else:
                self.facing_right = True

            for bird in pg.sprite.spritecollide(self, enemies, False, pg.sprite.collide_mask):
                if bird is not self:
                    self.bounce(bird)
                    bird.bounce(self)

            # check for platform collision
            self.walking = False

            # catch when it is walking between screens
            if (self.y == 109 or self.y == 295 or self.y == 491) and (self.x < 0 or self.x > 840):
                self.walking = True
                self.y_speed = 0
            else:
                collided_platforms = pg.sprite.spritecollide(self, platforms, False, pg.sprite.collide_mask)

                for collidedPlatform in collided_platforms:
                    self.bounce(collidedPlatform)

            self.rect.topleft = (self.x, self.y)
            self.animate(current_time)

    def bounce(self, collider):
        if collider.rect.left < self.rect.centerx < collider.rect.right and (
                collider.rect.centery > self.rect.centery):
            # coming in from the top?
            self.walking = True
            self.y_speed = 0
            self.y = collider.y - self.rect.height + 3
        elif self.y - self.y_speed > collider.rect.top and (
                collider.rect.left < self.rect.centerx < collider.rect.right):
            # colliding from bottom
            self.y += 3
            self.y_speed = 1
        elif self.rect.centerx < collider.rect.centerx:
            # colliding from left side
            self.x -= 3
            self.x_speed = -2
        elif self.rect.centerx > collider.rect.centerx:
            # colliding from right side
            self.x += 3
            self.x_speed = 2
