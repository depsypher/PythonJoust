import pygame as pg


class Message(pg.sprite.Sprite):
    def __init__(self, text, chars, x, y, duration, color=None):
        pg.sprite.Sprite.__init__(self)
        self.chars = chars
        self.text = text
        self.image = chars[0]
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)
        self.ttl = 0
        self.duration = duration
        self.color = color

    def draw_text(self):
        count = len(self.text)
        surf = pg.Surface((count * 20, 21), pg.SRCALPHA)

        text_width = 0
        for char in self.text:
            code = ord(char)
            char_index = 49             # default to space
            if 65 <= code <= 90:
                char_index = code - 55  # A-Z at index 10 to 35
            elif 48 <= code <= 57:
                char_index = code - 48  # 0-9 at index 0-9
            elif code == 33:
                char_index = 40         # !
            surf.blit(self.chars[char_index], (text_width, 0))
            char_width = 25 if char in ['M', 'W'] else 18
            char_width = 12 if char in ['I'] else char_width
            text_width += char_width

        if self.color is not None:
            mask = pg.mask.from_surface(surf)
            surf = mask.to_surface(setcolor=self.color)
        return surf

    def update(self, current_time, remove_message):
        if self.ttl == 0:
            self.ttl = current_time + self.duration

        if current_time > self.ttl:
            remove_message(self)
            self.kill()
        else:
            self.image = self.draw_text()
            self.rect = self.image.get_rect()
            self.rect.topleft = (self.x, self.y)



