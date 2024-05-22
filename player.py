import random

import pygame

from enemy import Enemy
from actors import Character


class Player(Character):
    def __init__(self, images):
        super().__init__()
        self.frame = 2
        self.mounted_images = images["bird"]
        self.unmounted_images = images["player_unmounted"]
        self.spawn_images = images["spawn"]
        self.egg_images = images["egg"]
        self.flap_sound = pygame.mixer.Sound("resources/sound/joustflaedit.ogg")
        self.skid_sound = pygame.mixer.Sound("resources/sound/joustski.ogg")
        self.bump_sound = pygame.mixer.Sound("resources/sound/joustthu.ogg")
        self.egg_sound = pygame.mixer.Sound("resources/sound/joustegg.ogg")
        self.image = self.mounted_images[self.frame]
        self.rect = self.image.get_rect()
        self.flap = False
        self.playerChannel = pygame.mixer.Channel(0)
        self.lives = 5
        self.alive = "spawning"
        self.skidding = 0
        self.spawning = 20
        self.next_accel_time = 0

    def update(self, current_time, keys, platforms, enemies, god, eggs, score):
        if current_time < self.next_update_time:
            return

        # Update every 30 milliseconds
        self.next_update_time = current_time + 30

        if self.spawning == 0:
            self.alive = "mounted"

        if self.alive == "spawning":
            self.next_update_time += 100
            self.rect.topleft = (self.x, self.y)
            self.spawning -= 1
            self.frame = 5 if self.frame == 6 else self.frame + 1
            self.image = self.spawn_images[self.frame]
            if self.frame >= 5 and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_SPACE]):
                self.spawning = 0
                self.alive = "mounted"
                self.do_mounted(current_time, eggs, enemies, god, keys, platforms, score)
        elif self.alive == "mounted" or self.alive == "skidding":
            self.do_mounted(current_time, eggs, enemies, god, keys, platforms, score)
        elif self.alive == "unmounted":
            self.do_unmounted(current_time, platforms)
        else:
            self.respawn()

    def do_mounted(self, current_time, eggs, enemies, god, keys, platforms, score):
        if self.skidding > 0:
            if self.skidding == 1:
                self.x_speed = 0
            self.skidding -= 1
        elif keys[pygame.K_LEFT]:
            self.facing_right = False
            if self.walking and current_time > self.next_accel_time:
                self.next_accel_time = current_time + 30 * 10
                self.x_speed -= 1.5#0.1 if self.x_speed > -3.0 else 0.8
        elif keys[pygame.K_RIGHT]:
            self.facing_right = True
            if self.walking and current_time > self.next_accel_time:
                self.next_accel_time = current_time + 30 * 10
                self.x_speed += 1.5#0.1 if self.x_speed < 3.0 else 0.8

        if keys[pygame.K_SPACE]:
            self.skidding = 0
            self.walking = False

            if not self.flap:
                if keys[pygame.K_LEFT]:
                    if self.x_speed > -1.5:
                        self.x_speed -= 1.5
                    else:
                        self.x_speed -= 3.0
                    # self.x_speed -= 0.7 if self.x_speed > -2.5 else 1.3

                if keys[pygame.K_RIGHT]:
                    if self.x_speed < 1.5:
                        self.x_speed += 1.5
                    else:
                        self.x_speed += 3.0
                        # self.x_speed += 0.7 if self.x_speed < 2.5 else 1.3

                self.y_speed -= 3
                self.playerChannel.stop()
                self.flap_sound.play(0)
                self.flap = True
        else:
            self.flap = False

        self.player_velocity()

        if self.y > 570:
            score.reset()
            self.die(score)

        if self.x < -48:
            self.x = 900
        if self.x > 900:
            self.x = -48

        self.rect.topleft = (self.x, self.y)

        # check for enemy collision
        for bird in pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_mask):
            # check each bird to see if above or below
            if bird.y > self.y and bird.alive:
                bird.killed(eggs, self.egg_images, self)
                self.bounce(bird)
                bird.bounce(self)
                score.score += 1000
            elif bird.y < self.y - 5 and bird.alive and not god.on:
                self.bounce(bird)
                bird.bounce(self)
                score.reset()
                self.die(score)
                break
            elif bird.alive:
                self.bounce(bird)
                bird.bounce(self)

        collided = False
        collided_platforms = pygame.sprite.spritecollide(
            self, platforms, False, pygame.sprite.collide_mask)

        for collidedPlatform in collided_platforms:
            collided = self.bounce(collidedPlatform)

        if not collided:
            self.walking = False

        collided_eggs = pygame.sprite.spritecollide(self, eggs, False, pygame.sprite.collide_mask)
        for collided_egg in collided_eggs:
            self.egg_sound.play(0)
            score.collect_egg()
            collided_egg.kill()

        self.rect.topleft = (self.x, self.y)
        if self.walking:
            if self.next_anim_time < current_time:
                if self.x_speed != 0:
                    if self.skidding > 0:
                        self.frame = 4
                    elif (self.x_speed > 6 and keys[pygame.K_LEFT]) or (
                            self.x_speed < -6 and keys[pygame.K_RIGHT]):
                        self.playerChannel.play(self.skid_sound)
                        self.facing_right = True if self.x_speed > 0 else False
                        self.frame = 4
                        self.skidding = 13
                    else:
                        ms = (8.0 / abs(self.x_speed)) * 45
                        self.next_anim_time = current_time + ms
                        self.frame += 1
                        if self.frame > 3:
                            self.frame = 0
                else:
                    self.frame = 3
                    self.playerChannel.stop()

            self.image = self.mounted_images[self.frame]
        else:
            self.image = self.mounted_images[6 if self.flap else 5]

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def do_unmounted(self, current_time, platforms):
        # unmounted player, lone bird
        # see if we need to accelerate
        if abs(self.x_speed) < self.targetXSpeed:
            if abs(self.x_speed) > 0:
                self.x_speed += self.x_speed / abs(self.x_speed) / 2
            else:
                self.x_speed += 0.5
        # work out if flapping...
        if self.flap < 1:
            if random.randint(0, 10) > 8 or self.y > 450:  # flap to avoid lava
                self.y_speed -= 3
                self.flap = 3
        else:
            self.flap -= 1
        self.x = self.x + self.x_speed
        self.y = self.y + self.y_speed
        self.player_velocity()
        if self.x < -48:  # off the left. remove entirely
            self.image = self.unmounted_images[7]
            self.alive = "dead"
            self.next_update_time = current_time + 2000
        if self.x > 900:  # off the right. remove entirely
            self.image = self.unmounted_images[7]
            self.alive = "dead"
            self.next_update_time = current_time + 2000
        self.rect.topleft = (self.x, self.y)

        # check for platform collision
        collided = False
        collided_platforms = pygame.sprite.spritecollide(
            self, platforms, False, collided=pygame.sprite.collide_mask)

        for collidedPlatform in collided_platforms:
            collided = self.bounce(collidedPlatform)

        if not collided:
            self.walking = False

        self.rect.topleft = (self.x, self.y)
        self.animate(current_time)
        self.image = self.unmounted_images[self.frame]
        if self.x_speed < 0 or (self.x_speed == 0 and not self.facing_right):
            self.image = pygame.transform.flip(self.image, True, False)
            self.facing_right = False
        else:
            self.facing_right = True

    def bounce(self, collider):
        collided = False
        enemy = True if type(collider) is Enemy else False
        if not enemy and self.walking and (self.y > collider.y - 40):
            self.x -= self.x_speed * 2
            self.x_speed = -self.x_speed
            self.playerChannel.play(self.bump_sound)
        elif self.y < (collider.y - 20) and ((collider.x - 40) < self.x < (collider.rect.right - 10)):
            # coming in from the top?
            if enemy:
                self.y_speed = max(-self.y_speed, -6)
                self.y = collider.y - self.rect.height - 1
                self.playerChannel.play(self.bump_sound)
            else:
                collided = True
                self.walking = True
                self.y_speed = 0
                self.y = collider.y - self.rect.height + 1
        elif self.x < collider.x:
            # colliding from left side
            collided = True
            self.playerChannel.play(self.bump_sound)
            self.x = self.x - 10
            self.x_speed = -5
        elif self.x > collider.rect.right - 50:
            # colliding from right side
            collided = True
            self.playerChannel.play(self.bump_sound)
            self.x = self.x + 10
            self.x_speed = 5
        elif self.y > collider.y:
            # colliding from bottom
            collided = True
            self.playerChannel.play(self.bump_sound)
            self.y = self.y + 10
            self.y_speed = -self.y_speed

        return collided

    def die(self, score):
        self.lives -= 1
        self.spawning = 20
        self.alive = "unmounted"
        score.die()

    def respawn(self):
        self.frame = 1
        self.image = self.mounted_images[self.frame]
        self.rect = self.image.get_rect()
        self.x = 389
        self.y = 491
        self.facing_right = True
        self.x_speed = 0
        self.y_speed = 0
        self.flap = False
        self.walking = True
        self.skidding = False
        self.alive = "spawning"
