import pygame as pg


class Cliff(pg.sprite.Sprite):
    def __init__(self, image, x, y):
        pg.sprite.Sprite.__init__(self)
        if image is not None:
            self.image = image
            self.mask = pg.mask.from_surface(self.image)
        else:
            bottom_cliff = pg.image.load("resources/graphics/plat1.png")
            surf = pg.Surface((900, 98), pg.SRCALPHA)
            surf.blit(bottom_cliff, (166, 0))
            pg.draw.rect(surf, (141, 73, 23), pg.Rect(0, 0, 166, 9))
            pg.draw.rect(surf, (141, 73, 23), pg.Rect(724, 0, 176, 9))
            self.mask = pg.mask.from_surface(surf)
            self.image = surf

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)
