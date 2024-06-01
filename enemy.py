import random

import pygame as pg

from egg import Egg
from actors import Character


class Enemy(Character):
    def __init__(self, sprites, start_pos, enemy_type: int):
        super().__init__()
        self.audio_channel = pg.mixer.Channel(1)
        self.sounds = {
            "spawn": pg.mixer.Sound("resources/sound/spawn-enemy.ogg"),
        }
        self.buzzard = sprites.buzzard
        if enemy_type == 0:
            self.mount = sprites.bounder[0]
        else:
            self.mount = sprites.hunter[0]
        self.alive = True
        self.spawning = 20
        self.enemy_type = enemy_type
        self.image = self.buzzard[0]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.x = start_pos[0]
        self.y = start_pos[1]
        self.x_speed = 1
        self.target_x_speed = 3 if enemy_type == 0 else 4
        self.next_flap = 0
        if random.randint(0, 1) < 1:
            self.x_speed = -self.x_speed
            self.facing_right = False

    def update(self, current_time, delta, platforms, enemies):
        # if current_time < self.next_update_time:
        #     return
        # self.next_update_time = current_time + 30

        if self.spawning >= 0:
            if self.spawning == 20:
                self.audio_channel.stop()
                self.audio_channel.play(self.sounds["spawn"])

            self.image = self.build_spawn(self.buzzard[2], 20 - self.spawning)
            if not self.facing_right:
                self.image = pg.transform.flip(self.image, True, False)

            self.rect.topleft = (self.x, self.y)
            self.spawning -= 1
        else:
            speed = abs(self.x_speed)
            if speed < self.target_x_speed:
                self.x_speed += 1 if self.x_speed > 0 else -1

            # flap occasionally and to avoid lava
            self.flap -= 1
            if current_time > self.next_flap and random.randint(0, 10) > 5 or self.y > 450:
                self.y_speed -= 180
                self.next_flap = current_time + 250
                self.flap = 5

            self.walking = False
            self.velocity(delta)
            self.wrap(on_wrap=lambda: self.kill() if not self.alive else False)

            # head to nearest edge of screen if dead
            if not self.alive:
                speed = abs(self.x_speed)
                self.x_speed = -speed if self.x < 450 else speed

            self.rect.topleft = (self.x, self.y)
            self.bird_collision(enemies)
            self.platform_collision(platforms)
            self.rect.topleft = (self.x, self.y)

            self.animate(current_time)
            self.image = self.build_mount(self.buzzard[self.frame], self.mount)

            if self.x_speed < 0 or (self.x_speed == 0 and not self.facing_right):
                self.image = pg.transform.flip(self.image, True, False)
                self.facing_right = False
            else:
                self.facing_right = True

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

    def platform_collision(self, platforms):
        collided_platforms = pg.sprite.spritecollide(self, platforms, False, pg.sprite.collide_mask)
        for collidedPlatform in collided_platforms:
            self.bounce(collidedPlatform)
            if self.y > 559:  # hit lava
                self.kill()

    def bird_collision(self, enemies):
        for bird in pg.sprite.spritecollide(self, enemies, False, pg.sprite.collide_mask):
            if bird is not self:
                self.bounce(bird)
                bird.bounce(self)

    def build_mount(self, buzzard, mount):
        if self.alive:
            surf = pg.Surface((60, 60), pg.SRCALPHA)
            surf.blit(mount, (18, 0))
            surf.blit(buzzard, (0, 0))
            self.mask = pg.mask.from_surface(surf)
            return surf
        else:
            return self.buzzard[self.frame]

    def killed(self, eggs, egg_images, chars_small, killer, add_sprite, score):
        self.target_x_speed = 4
        egg_x_speed = (self.x_speed + killer.x_speed) * 0.5
        egg_y_speed = (self.y_speed + killer.y_speed - 1) * 0.5
        add_sprite(eggs, Egg(egg_images, chars_small, self.x + 27, self.y + 21, egg_x_speed, egg_y_speed))
        score.kill(self)
        self.alive = False
