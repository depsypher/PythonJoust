import random

import pygame

from egg import Egg


class Enemy(pygame.sprite.Sprite):
    def __init__(self, images, startPos, enemyType):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.images = images["enemy"]
        self.spawnimages = images["spawn"]
        self.unmountedimages = images["unmounted"]
        self.frameNum = 0
        self.enemyType = enemyType
        self.image = self.spawnimages[0]
        self.rect = self.image.get_rect()
        self.next_update_time = 0
        self.next_anim_time = 0
        self.x = startPos[0]
        self.y = startPos[1]
        self.flap = 0
        self.facingRight = True
        self.x_speed = random.randint(3, 10)
        self.targetXSpeed = 10
        self.yspeed = 0
        self.walking = True
        self.flapCount = 0
        self.spawning = True
        self.alive = True

    def killed(self, eggs, egg_images):
        # make an egg appear here
        eggs.add(Egg(egg_images, self.x, self.y + 30, self.x_speed, self.yspeed))
        self.alive = False

    def update(self, current_time, keys, platforms, god):
        if self.next_update_time < current_time:  # only update every 30 millis
            self.next_update_time = current_time + 50

            if self.spawning:
                self.frameNum += 1
                self.image = self.spawnimages[self.frameNum]
                self.next_update_time += 100
                self.rect.topleft = (self.x, self.y)
                if self.frameNum == 5:
                    self.spawning = False
            else:
                # see if we need to accelerate
                if abs(self.x_speed) < self.targetXSpeed:
                    self.x_speed += self.x_speed / abs(self.x_speed) / 2

                # work out if flapping...
                if self.flap < 1:
                    if random.randint(0, 10) > 8 or self.y > 450:  # flap to avoid lava
                        self.yspeed -= 3
                        self.flap = 3
                else:
                    self.flap -= 1

                self.x += self.x_speed
                self.y += self.yspeed

                if not self.walking:
                    self.yspeed += 0.4

                if self.yspeed > 10:
                    self.yspeed = 10
                if self.yspeed < -10:
                    self.yspeed = -10

                if self.y < 0:  # can't go off the top
                    self.y = 0
                    self.yspeed = 2

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

                # check for platform collision
                collided_platforms = pygame.sprite.spritecollide(self, platforms, False)#,
#                                                                collided=pygame.sprite.collide_mask)
                self.walking = False
                if ((40 < self.y < 45) or (220 < self.y < 225)) and (
                        self.x < 0 or self.x > 860):  # catch when it is walking between screens
                    self.walking = True
                    self.yspeed = 0
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
                if self.alive:
                    self.image = self.images[((self.enemyType * 7) + self.frameNum)]
                else:
                    # show the unmounted sprite
                    self.image = self.unmountedimages[self.frameNum]
                if self.x_speed < 0 or (self.x_speed == 0 and not self.facingRight):
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facingRight = False
                else:
                    self.facingRight = True

    def bounce(self, collider):
        collided = False
        if self.y < (collider.y - 20) and ((collider.x - 40) < self.x < (collider.rect.right - 10)):
            # coming in from the top?
            self.walking = True
            self.yspeed = 0
            self.y = collider.y - self.rect.height + 3
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
            self.yspeed = 0
        return collided
