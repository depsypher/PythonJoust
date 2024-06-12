import pygame as pg


class Score:
    def __init__(self):
        self.score = 0
        self.eggs_collected = 0
        self.egg_points = [250, 500, 750, 1000]
        self.last_scored = 0

    def collect_egg(self, bonus):
        points = self.egg_points[min(self.eggs_collected, len(self.egg_points) - 1)]
        bonus_points = 500 if bonus else 0
        self.score += points + bonus_points
        self.eggs_collected += 1
        self.last_scored = pg.time.get_ticks()
        return points, bonus_points

    def kill(self, enemy):
        if enemy.enemy_type == 1:
            self.score += 500
        elif enemy.enemy_type == 2:
            self.score += 750
        elif enemy.enemy_type == 3:
            self.score += 1000

    def die(self):
        self.score += 50

    def reset(self):
        self.eggs_collected = 0

    def clear(self):
        self.score = 0
        self.eggs_collected = 0

    def draw(self, screen, digits):
        xpos = 210
        d = 10000000
        has_leading_digit = False
        while d >= 10:
            i = (self.score % d) // (d // 10)
            if i != 0 or d == 10 or has_leading_digit:
                screen.blit(digits[i], [xpos, 570])
                has_leading_digit = True
            d //= 10
            xpos += 17
