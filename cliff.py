import pygame as pg


class Cliff(pg.sprite.Sprite):
    def __init__(self, image, x, y, flames=None):
        pg.sprite.Sprite.__init__(self)

        self.flames = flames
        self.burning = -1
        self.next_update_time = 0

        if image is not None:
            self.image = image
            self.mask = pg.mask.from_surface(self.image)
        else:
            self.bottom_cliff = pg.image.load("resources/graphics/plat1.png")
            self.build_bottom_cliff()

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)

    def build_bottom_cliff(self):
        surf = pg.Surface((1020, 98), pg.SRCALPHA)

        width = 227 - (227 * self.burning / 100)
        pg.draw.rect(surf, (141, 73, 23), pg.Rect(217 - width, 0, width, 9))
        if self.burning > 100:
            surf.blit(self.flames[self.burning % 4], (217 - 18, 2 * (self.burning - 100)))
        elif self.burning < 100:
            surf.blit(self.flames[self.burning % 4], (217 - width - 18, 0))

        width = 276 - (276 * self.burning / 100)
        pg.draw.rect(surf, (141, 73, 23), pg.Rect(774, 0, width, 9))
        if self.burning > 100:
            surf.blit(self.flames[self.burning % 4], (774 - 12, 2 * (self.burning - 100)))
        elif self.burning < 100:
            surf.blit(self.flames[self.burning % 4], (774 + width - 12, 0))

        lava_height = 50
        lava_rect = [60, 98 - lava_height, 900, lava_height]
        pg.draw.rect(surf, (255, 0, 0), lava_rect)

        surf.blit(self.bottom_cliff, (216, 0))

        self.mask = pg.mask.from_surface(surf)
        self.image = surf

    def burn(self):
        if self.burning == -1:
            self.burning = 0

    def update(self, current_time):
        if current_time < self.next_update_time:
            return

        if self.burning < 30:
            self.next_update_time = current_time + 15
        else:
            self.next_update_time = current_time + 200

        if self.burning >= 0:
            self.build_bottom_cliff()
            self.burning += 1
            if self.burning > 100 + 50:
                self.burning = -2
