import random

import pygame

from egg import Egg
from actors import Character


class Enemy(Character):
    def __init__(self, sprites, start_pos, enemy_type):
        super().__init__()
        self.buzzard = sprites.buzzard
        if enemy_type == 0:
            self.mount = sprites.bounder
        else:
            self.mount = sprites.hunter
        self.spawn_images = sprites.spawn
        self.enemyType = enemy_type
        self.image = self.spawn_images[0]
        self.mask = pygame.mask.from_surface(self.image)
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
        surf = pygame.Surface((60, 60))
        surf.blit(mount, (18, 0))
        surf.blit(buzzard, (0, 0))
        surf.set_colorkey(pygame.color.Color('Black'))
        self.mask = pygame.mask.from_surface(surf)
        return surf

    def killed(self, eggs, egg_images, killer):
        eggs.add(Egg(egg_images, self.x, self.y + 20, self.x_speed + killer.x_speed, self.y_speed + killer.y_speed - 1))
        self.alive = False

    def update(self, current_time, keys, platforms, enemies):
        if current_time < self.next_update_time:
            return

        self.next_update_time = current_time + 50

        if self.spawning:
            self.frame += 1
            self.image = self.spawn_images[self.frame]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

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
                if random.randint(0, 10) > 8 or self.y > 450:  # flap to avoid lava
                    self.y_speed -= 3
                    self.flap = 3
            else:
                self.flap -= 1

            self.player_velocity()

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
                self.image = pygame.transform.flip(self.image, True, False)
                self.facing_right = False
            else:
                self.facing_right = True

            for bird in pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_mask):
                if bird is not self:
                    self.bounce(bird)
                    bird.bounce(self)

            # check for platform collision
            self.walking = False
            if ((40 < self.y < 45) or (220 < self.y < 225)) and (
                    self.x < 0 or self.x > 860):  # catch when it is walking between screens
                self.walking = True
                self.y_speed = 0
            else:
                collided_platforms = pygame.sprite.spritecollide(
                    self, platforms, False, pygame.sprite.collide_mask)

                for collidedPlatform in collided_platforms:
                    self.bounce(collidedPlatform)

            self.rect.topleft = (self.x, self.y)
            self.animate(current_time)

    def bounce(self, collider):
        if self.y < (collider.y - 20) and ((collider.x - 40) < self.x < (collider.rect.right - 10)):
            # coming in from the top?
            self.walking = True
            self.y_speed = 0
            self.y = collider.y - self.rect.height + 3
        elif self.x < collider.x:
            # colliding from left side
            self.x = self.x - 10
            self.x_speed = -2
        elif self.x > collider.rect.right - 50:
            # colliding from right side
            self.x = self.x + 10
            self.x_speed = 2
        elif self.y > collider.y:
            # colliding from bottom
            self.y = self.y + 10
            self.y_speed = 0
