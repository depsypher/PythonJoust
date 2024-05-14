import pygame


class Character(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x = 415
        self.y = 350
        self.x_speed = 0
        self.y_speed = 0
        self.flap = 0
        self.frameNum = 0
        self.next_update_time = 0
        self.next_anim_time = 0
        self.targetXSpeed = 10
        self.walking = True
        self.facingRight = True
        self.spawning = True

    def player_velocity(self):
        if not self.walking:
            self.y_speed += 0.4
        if self.y_speed > 10:
            self.y_speed = 10
        if self.y_speed < -10:
            self.y_speed = -10
        if self.y < 0:  # can't go off the top
            self.y = 0
            self.y_speed = 2

    def animate(self, current_time):
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


class Platform(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = image
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)
        self.right = self.rect.right
        self.top = self.rect.top


class Godmode(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.pic = pygame.image.load("resources/graphics/god.png")
        self.image = self.pic
        self.on = False
        self.rect = self.image.get_rect()
        self.rect.topleft = (850, 0)
        self.timer = pygame.time.get_ticks()

    def toggle(self, current_time):
        if current_time > self.timer:
            self.on = not self.on
            self.timer = current_time + 1000
