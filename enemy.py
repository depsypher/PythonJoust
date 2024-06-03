import random
import sys

import pygame as pg

from util import LANES, play_sound
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

    def update(self, current_time, delta, platforms, enemies, state):
        if self.spawning >= 0:
            if self.spawning == 20:
                self.audio_channel.stop()
                play_sound(self.audio_channel, self.sounds['spawn'], state)

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
            if self.should_flap(current_time):
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

    def should_flap(self, current_time):
        if current_time < self.next_flap:
            return False
        if self.y > 540:
            return True

        nearest_lane = (LANES[0], sys.maxsize)
        for lane in LANES:
            d = pg.math.Vector2(self.x, self.y).distance_to((self.x, lane))
            if d < nearest_lane[1]:
                nearest_lane = (lane, d)

        return self.y > nearest_lane[0]

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

    def killed(self, eggs, sprites, killer, add_sprite, score):
        self.target_x_speed = 4
        egg_x_speed = (self.x_speed + killer.x_speed) * 0.5
        egg_y_speed = (self.y_speed + killer.y_speed - 1) * 0.5
        egg = Egg(sprites, self.x + 27, self.y + 21, egg_x_speed, egg_y_speed, add_sprite)
        add_sprite(eggs, egg)
        score.kill(self)
        self.alive = False


class Egg(Character):
    def __init__(self, sprites, x, y, x_speed, y_speed, add_sprite):
        super().__init__()
        self.egg_images = sprites.egg
        self.hatchling = sprites.hatchling
        self.chars_small = sprites.chars_small
        self.image = self.egg_images[0]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.last_y = y
        self.rect.topleft = (x, y)
        self.walking = False
        self.bonus = True   # until it hits a platform
        self.hatch = None
        self.add_sprite = add_sprite
        self.egg_state = {}

    def update(self, current_time, delta, platforms, eggs, enemies, sprites):
        self.velocity(delta)
        self.wrap()
        self.rect.topleft = (self.x, self.y)

        collided_platforms = pg.sprite.spritecollide(self, platforms, False, pg.sprite.collide_mask)
        for collidedPlatform in collided_platforms:
            self.bonus = False
            self.bounce(collidedPlatform)

        for collided_egg in pg.sprite.spritecollide(self, eggs, False, pg.sprite.collide_mask):
            if collided_egg is not self:
                self.bounce(collided_egg)

        self.animate_hatch(current_time, enemies, sprites)

        if -0.1 < self.x_speed < 0.1:
            if 890 <= self.x <= 1020:
                self.x_speed -= 1
            elif -100 <= self.x <= 0:
                self.x_speed += 1
            elif self.y == self.last_y and not self.hatch:
                self.hatch = current_time + 12000

        if self.y > 570:  # hit lava
            self.kill()
        self.last_y = self.y
        self.rect.topleft = (self.x, self.y)

    def bounce(self, collider):
        if self.y < collider.y and ((collider.x - 40) < self.x < (collider.rect.right - 10)):
            # egg is above collider
            self.x_speed *= 0.75
            self.y_speed = -abs(self.y_speed) * 0.5
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

    def animate_hatch(self, current_time, enemies, sprites):
        if self.hatch:
            step = 250
            if current_time > self.hatch + step * 10 + 1000:
                if not self.egg_state.get('hatched', False):
                    self.egg_state['hatched'] = True
                    self.add_sprite(enemies, Enemy(sprites, (self.x, self.y - 25), 0))
                    self.kill()
            elif current_time > self.hatch + step * 8 + 1000:
                self.image = self.hatchling[2]
            elif current_time > self.hatch + step * 7 + 1000:
                self.image = self.hatchling[1]
            elif current_time > self.hatch + step * 6 + 1000:
                if not self.egg_state.get('hatchling', False):
                    self.egg_state['hatchling'] = True
                    self.x -= 6
                    self.y -= 5
                self.image = self.hatchling[0]
            elif current_time > self.hatch + step * 5 + 1000:
                self.image = self.egg_images[3]
            elif current_time > self.hatch + step * 4:
                self.image = self.egg_images[0]
            elif current_time > self.hatch + step * 3:
                self.image = self.egg_images[2]
            elif current_time > self.hatch + step * 2:
                self.image = self.egg_images[0]
            elif current_time > self.hatch + step:
                self.image = self.egg_images[1]
            else:
                self.image = self.egg_images[0]

            self.mask = pg.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
