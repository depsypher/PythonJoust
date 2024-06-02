import pygame as pg
import random
from loader import load_sprite

RED = (255, 0, 0)
BROWN = (141, 73, 23)


class Cliff(pg.sprite.Sprite):
    def __init__(self, image, x, y, flames=None):
        pg.sprite.Sprite.__init__(self)

        self.flames = flames
        self.burning = -1
        self.next_update_time = 0

        if image is not None:
            self.bottom_cliff = None
            self.image = image
            self.mask = pg.mask.from_surface(self.image)
        else:
            self.lava_bubble = (-1, 0)
            self.bottom_cliff = load_sprite(0, 19, 190, 30, 3, 0, 1, "resources/graphics/spritesheet.png")[0]
            self.build_bottom_cliff(0)

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)
        self.born = 0

    def build_bottom_cliff(self, age):
        surf = pg.Surface((1020, 98), pg.SRCALPHA)

        if self.burning != -2:
            cliff_left = 217
            width = 227 - (227 * self.burning / 100)
            pg.draw.rect(surf, BROWN, pg.Rect(cliff_left - width, 0, width, 9))
            if self.burning > 100:
                surf.blit(self.flames[self.burning % 4], (cliff_left - 18, 2 * (self.burning - 100)))
            elif self.burning < 100:
                surf.blit(self.flames[self.burning % 4], (cliff_left - width - 18, 0))

            cliff_right = 780
            width = 276 - (276 * self.burning / 100)
            pg.draw.rect(surf, BROWN, pg.Rect(cliff_right, 0, width, 9))
            if self.burning > 100:
                surf.blit(self.flames[self.burning % 4], (cliff_right - 12, 2 * (self.burning - 100)))
            elif self.burning < 100:
                surf.blit(self.flames[self.burning % 4], (cliff_right + width - 12, 0))

        lava_height = min(age / 100, 50)
        lava_rect = [60, 98 - lava_height, 900, lava_height]
        pg.draw.rect(surf, RED, lava_rect)

        lava_bubble_index = self.lava_bubble[0]
        if lava_bubble_index >= 0:
            x = self.lava_bubble[1]
            y = (98 - lava_height - 3) + 3 * lava_bubble_index
            if lava_bubble_index == 0:
                pg.draw.rect(surf, RED, [x - 6, y, 6, 3])
                pg.draw.rect(surf, RED, [x + 6, y, 6, 3])
            else:
                pg.draw.rect(surf, RED, [x, y - 3, 6, 3])
                pg.draw.rect(surf, (0, 0, 0), [x, y, 6, 3])
            self.lava_bubble = (self.lava_bubble[0] - 1, self.lava_bubble[1])

        surf.blit(self.bottom_cliff, (210, 0))

        self.mask = pg.mask.from_surface(surf)
        self.image = surf

    def burn(self):
        if self.burning == -1:
            self.burning = 0

    def update(self, current_time):
        if current_time < self.next_update_time or not self.bottom_cliff:
            return

        if self.born == 0:
            self.born = current_time

        age = 0 if self.born == 0 else current_time - self.born

        if self.burning < 30:
            self.next_update_time = current_time + 15
        else:
            self.next_update_time = current_time + 200

        if self.burning >= 0:
            self.build_bottom_cliff(age)
            self.burning += 1
            if self.burning > 100 + 50:
                self.burning = -2
        elif self.bottom_cliff and 4500 < age < 10500:
            self.build_bottom_cliff(age - 4500)
            self.next_update_time = current_time + 100
        elif age > 10500:
            if self.lava_bubble[0] < 0 and random.randint(0, 10) > 5:
                x = random.randint(60, 220) if random.randint(0, 1) < 1 else random.randint(732, 890)
                self.lava_bubble = (2, x)

            self.build_bottom_cliff(age)
            self.next_update_time = current_time + 250
