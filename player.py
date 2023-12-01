import random

import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, images):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.images = images["bird"]
        self.unmounted_images = images["player_unmounted"]
        self.spawn_images = images["spawn"]
        self.egg_images = images["egg"]
        self.frameNum = 2
        self.image = self.images[self.frameNum]
        self.rect = self.image.get_rect()
        self.next_update_time = 0
        self.next_anim_time = 0
        self.x = 415
        self.y = 350
        self.facingRight = True
        self.x_speed = 0
        self.y_speed = 0
        self.targetXSpeed = 10
        self.flap = False
        self.walking = True
        self.playerChannel = pygame.mixer.Channel(0)
        self.flap_sound = pygame.mixer.Sound("resources/sound/joustflaedit.wav")
        self.skid_sound = pygame.mixer.Sound("resources/sound/joustski.wav")
        self.bump_sound = pygame.mixer.Sound("resources/sound/joustthu.wav")
        self.egg_sound = pygame.mixer.Sound("resources/sound/joustegg.wav")
        self.lives = 4
        self.spawning = True
        self.alive = 2

    def update(self, current_time, keys, platforms, enemies, god, eggs, score):
        # Update every 30 milliseconds

        if self.next_update_time < current_time:
            self.next_update_time = current_time + 30
            if self.alive == 2:
                if self.spawning:
                    self.frameNum += 1
                    self.image = self.spawn_images[self.frameNum]
                    self.next_update_time += 100
                    self.rect.topleft = (self.x, self.y)
                    if self.frameNum == 5:
                        self.frameNum = 4
                        self.spawning = False
                else:
                    if keys[pygame.K_LEFT]:
                        if self.x_speed > -10:
                            self.x_speed -= 0.5
                    elif keys[pygame.K_RIGHT]:
                        if self.x_speed < 10:
                            self.x_speed += 0.5
                    if keys[pygame.K_SPACE]:
                        if not self.flap:
                            self.playerChannel.stop()
                            self.flap_sound.play(0)
                            if self.y_speed > -250:
                                self.y_speed -= 3
                            self.flap = True
                    else:
                        self.flap = False
                    self.x += self.x_speed
                    self.y += self.y_speed
                    if not self.walking:
                        self.y_speed += 0.4
                    if self.y_speed > 10:
                        self.y_speed = 10
                    if self.y_speed < -10:
                        self.y_speed = -10
                    if self.y < 0:
                        self.y = 0
                        self.y_speed = 2
                    if self.y > 570:
                        self.die()
                    if self.x < -48:
                        self.x = 900
                    if self.x > 900:
                        self.x = -48
                    self.rect.topleft = (self.x, self.y)

                    # check for enemy collision
                    collided_birds = pygame.sprite.spritecollide(self, enemies, False,
                                                                collided=pygame.sprite.collide_mask)
                    for bird in collided_birds:
                        # check each bird to see if above or below
                        if bird.y > self.y and bird.alive:
                            self.bounce(bird)
                            bird.killed(eggs, self.egg_images)
                            bird.bounce(self)
                            self.y_speed = -self.y_speed
                            score.score += 1000
                        elif bird.y < self.y - 5 and bird.alive and not god.on:
                            self.bounce(bird)
                            bird.bounce(self)
                            self.die()
                            break
                        elif bird.alive:
                            self.bounce(bird)
                            bird.bounce(self)

                    self.walking = False
                    if (((40 < self.y < 45) or (250 < self.y < 255)) and (
                            self.x < 0 or self.x > 860)):  # catch when it is walking between screens
                        self.walking = True
                        self.y_speed = 0
                    else:
                        collided = False
                        # check for platform collision
                        collided_platforms = pygame.sprite.spritecollide(self, platforms, False)

                        for collidedPlatform in collided_platforms:
                            collided = self.bounce(collidedPlatform)
                        if collided:
                            self.playerChannel.play(self.bump_sound)

                    collided_eggs = pygame.sprite.spritecollide(self, eggs, False)
                    for collided_egg in collided_eggs:
                        self.egg_sound.play(0)
                        score.score += 250
                        collided_egg.kill()

                    self.rect.topleft = (self.x, self.y)
                    if self.walking:
                        # if walking
                        if self.next_anim_time < current_time:
                            if self.x_speed != 0:
                                if (self.x_speed > 5 and keys[pygame.K_LEFT]) or (
                                        self.x_speed < -5 and keys[pygame.K_RIGHT]):

                                    if self.frameNum != 4:
                                        self.playerChannel.play(self.skid_sound)
                                    self.frameNum = 4
                                else:
                                    self.next_anim_time = current_time + 200 / abs(self.x_speed)
                                    self.frameNum += 1
                                    if self.frameNum > 3:
                                        self.frameNum = 0
                            elif self.frameNum == 4:
                                self.frameNum = 3
                                self.playerChannel.stop()

                        self.image = self.images[self.frameNum]
                    else:
                        if self.flap:
                            self.image = self.images[6]

                        else:
                            self.image = self.images[5]
                    if self.x_speed < 0 or (self.x_speed == 0 and self.facingRight == False):
                        self.image = pygame.transform.flip(self.image, True, False)
                        self.facingRight = False
                    else:
                        self.facingRight = True
            elif self.alive == 1:
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
                if not self.walking:
                    self.y_speed += 0.4
                if self.y_speed > 10:
                    self.y_speed = 10
                if self.y_speed < -10:
                    self.y_speed = -10
                if self.y < 0:  # can't go off the top
                    self.y = 0
                    self.y_speed = 2

                if self.x < -48:  # off the left. remove entirely
                    self.image = self.images[7]
                    self.alive = 0
                    self.next_update_time = current_time + 2000
                if self.x > 900:  # off the right. remove entirely
                    self.image = self.images[7]
                    self.alive = 0
                    self.next_update_time = current_time + 2000
                self.rect.topleft = (self.x, self.y)
                # check for platform collision
                collided_platforms = pygame.sprite.spritecollide(self, platforms, False)#,
#                                                                collided=pygame.sprite.collide_mask)
                self.walking = False
                if (((40 < self.y < 45) or (220 < self.y < 225)) and (
                        self.x < 0 or self.x > 860)):  # catch when it is walking between screens
                    self.walking = True
                    self.y_speed = 0
                else:
                    for collidedPlatform in collided_platforms:
                        self.bounce(collidedPlatform)
                self.rect.topleft = (self.x, self.y)
                if self.walking:
                    if self.next_anim_time < current_time:
                        if self.x_speed != 0:
                            self.next_anim_time = current_time + 100 / abs(self.x_speed)
                            self.frameNum += 1
                            if self.frameNum > 3:
                                self.frameNum = 0
                            else:
                                self.frameNum = 3
                else:
                    if self.flap > 0:
                        self.frameNum = 6
                    else:
                        self.frameNum = 5
                self.image = self.unmounted_images[self.frameNum]
                if self.x_speed < 0 or (self.x_speed == 0 and not self.facingRight):
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facingRight = False
                else:
                    self.facingRight = True
            else:
                # player respawn
                self.respawn()

    def bounce(self, collider):
        collided = False
        if self.y < (collider.y - 20) and (((collider.x - 40) < self.x < (collider.rect.right - 10))):
            # coming in from the top?
            self.walking = True
            self.y_speed = 0
            self.y = collider.y - self.rect.height + 1
        elif self.x < collider.x:
            # colliding from left side
            collided = True
            self.x = self.x - 10
            self.x_speed = -2
        elif self.x > collider.rect.right - 50:
            # colliding from right side
            collided = True
            self.x = self.x + 10
            self.x_speed = 2
        elif self.y > collider.y:
            # colliding from bottom
            collided = True
            self.y = self.y + 10
            self.y_speed = 0

        if collided:
            self.playerChannel.play(self.bump_sound)

        return collided

    def die(self):
        self.lives -= 1
        self.alive = 1

    def respawn(self):
        self.frameNum = 1
        self.image = self.images[self.frameNum]
        self.rect = self.image.get_rect()
        self.x = 415
        self.y = 350
        self.facingRight = True
        self.x_speed = 0
        self.y_speed = 0
        self.flap = False
        self.walking = True
        self.spawning = True
        self.alive = 2
