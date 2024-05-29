import random
import math
import pygame as pg

from enemy import Enemy
from actors import Character


class Player(Character):
    def __init__(self, sprites, add_sprite, state):
        super().__init__()
        self.frame = 2
        self.unmounted_images = sprites.ostrich
        self.mount = sprites.p1mount
        self.spawn_images = sprites.spawn
        self.egg_images = sprites.egg
        self.chars_small = sprites.chars_small
        self.poof_images = sprites.poof
        self.sounds = {
            "walk1": pg.mixer.Sound("resources/sound/walk1.ogg"),
            "walk2": pg.mixer.Sound("resources/sound/walk2.ogg"),
            "flap_up": pg.mixer.Sound("resources/sound/flap-up.ogg"),
            "flap_dn": pg.mixer.Sound("resources/sound/flap-dn.ogg"),
            "skid": pg.mixer.Sound("resources/sound/skid.ogg"),
            "bump": pg.mixer.Sound("resources/sound/bump.ogg"),
            "hit": pg.mixer.Sound("resources/sound/hit.ogg"),
            "egg": pg.mixer.Sound("resources/sound/egg.ogg"),
        }
        self.image = self.spawn_images[0]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.flap = 0
        self.playerChannel = pg.mixer.Channel(0)
        self.lives = 5
        self.alive = "spawning"
        self.skidding = 0
        self.spawning = 0
        self.x = 290
        self.y = 491
        self.next_accel_time = 0
        self.add_sprite = add_sprite
        self.alternate_walk = False
        self.poof = None
        self.score_badges = []
        self.state = state

    def build_mount(self, mount):
        if self.flap == 1:
            frame = 5
        elif self.flap == 2 or (self.flap == 0 and not self.walking):
            frame = 6
        else:
            frame = self.frame
        ostrich = self.unmounted_images[frame]
        surf = pg.Surface((60, 60), pg.SRCALPHA)
        surf.blit(mount, (12, 6 if self.skidding else 0))
        surf.blit(ostrich, (0, 0))
        self.mask = pg.mask.from_surface(surf)
#        return self.mask.to_surface(setcolor=(255, 0, 0))  # show mask for debugging
        return surf

    def update(self, current_time, keys, platforms, enemies, eggs, score, state):
        if self.spawning == 0:
            self.alive = "mounted"

        if self.poof is not None and self.poof.alive():
            self.poof.update(current_time)

        for badge in self.score_badges:
            badge.update(current_time, lambda b: self.score_badges.remove(b))

        if self.alive == "spawning":
            self.next_update_time += 100
            self.spawning -= 1
            self.frame = 5 if self.frame == 6 else self.frame + 1
            self.image = self.spawn_images[self.frame]
            self.rect.topleft = (self.x, self.y)
            if self.frame >= 5 and (keys[pg.K_LEFT] or keys[pg.K_RIGHT] or keys[pg.K_SPACE]):
                self.spawning = 0
                self.alive = "mounted"
                self.do_mounted(current_time, eggs, enemies, state['god'], keys, platforms, score)
        elif self.alive == "mounted" or self.alive == "skidding":
            self.do_mounted(current_time, eggs, enemies, state['god'], keys, platforms, score)
        elif self.alive == "unmounted":
            self.do_unmounted(current_time, platforms)
        else:
            self.respawn()

    def do_mounted(self, current_time, eggs, enemies, god, keys, platforms, score):
        if self.skidding > 0:
            if self.skidding == 1:
                self.x_speed = 0
                self.next_accel_time = current_time + 400
            else:
                slow = -1 if self.x_speed > 0 else 1
                if self.skidding == 20:
                    self.x_speed += slow * 3
                elif self.skidding == 10:
                    self.x_speed += slow * 2
                elif self.skidding == 5:
                    self.x_speed += slow
            self.skidding -= 1
        elif self.walking and ((self.x_speed > 3 and keys[pg.K_LEFT]) or (self.x_speed < -3 and keys[pg.K_RIGHT])):
            self.playerChannel.play(self.sounds["skid"])
            self.frame = 4
            self.skidding = 30
        elif keys[pg.K_LEFT]:
            if self.walking:
                if current_time > self.next_accel_time:
                    self.next_accel_time = current_time + 120
                    self.x_speed -= 1
            else:
                self.facing_right = False
        elif keys[pg.K_RIGHT]:
            if self.walking:
                if current_time > self.next_accel_time:
                    self.next_accel_time = current_time + 120
                    self.x_speed += 1
            else:
                self.facing_right = True

        if keys[pg.K_SPACE]:
            self.skidding = 0
            self.walking = False

            if self.flap == 0:
                if keys[pg.K_LEFT] and current_time > self.next_accel_time:
                    self.next_accel_time = current_time + 120
                    self.x_speed -= 1
                if keys[pg.K_RIGHT] and current_time > self.next_accel_time:
                    self.next_accel_time = current_time + 120
                    self.x_speed += 1

                self.y_speed -= 3
                self.playerChannel.stop()
                self.sounds["flap_dn"].play(0)
                self.flap = 2
            else:
                self.flap = 1
        else:
            if self.flap == 1:
                self.playerChannel.stop()
                self.sounds["flap_up"].play(0)
            self.flap = 0

        if self.walking and self.x_speed != 0:
            self.facing_right = self.x_speed > 0

        self.velocity()

        if self.x < -48:
            self.x = 900
        if self.x > 900:
            self.x = -48

        self.rect.topleft = (self.x, self.y)

        # check for enemy collision
        for enemy in pg.sprite.spritecollide(self, enemies, False, pg.sprite.collide_mask):
            if enemy.alive:
                if self.y < enemy.y:
                    enemy.killed(eggs, self.egg_images, self.chars_small, self, self.add_sprite, score)
                    self.bounce(enemy)
                    enemy.bounce(self)
                elif self.y - 5 > enemy.y:
                    self.bounce(enemy)
                    enemy.bounce(self)
                    if not god.on:
                        score.reset()
                        self.die(score)
                    break
                else:
                    self.bounce(enemy)
                    enemy.bounce(self)

        # catch when it is walking between screens
        if (self.y == 109 or self.y == 295) and (self.x < 0 or self.x > 840):
            self.walking = True
            self.y_speed = 0
        else:
            collided = False
            collided_platforms = pg.sprite.spritecollide(self, platforms, False, pg.sprite.collide_mask)

            for collidedPlatform in collided_platforms:
                if self.y < 559:
                    collided = self.bounce(collidedPlatform)

            if not collided:
                self.walking = False

            if self.y > 559:
                score.reset()
                self.die(score)

        collided_eggs = pg.sprite.spritecollide(self, eggs, False, pg.sprite.collide_mask)
        for collided_egg in collided_eggs:
            self.sounds["egg"].play(0)
            bonus = collided_egg.bonus
            points = score.collect_egg(bonus)[0]
            badge = ScoreBadge(self.chars_small, collided_egg.x, collided_egg.y - 16, points, bonus)
            self.add_sprite(None, badge)
            self.score_badges.append(badge)
            collided_egg.kill()

        if self.walking:
            if current_time > self.next_anim_time:
                if self.x_speed != 0:
                    if self.skidding > 0:
                        self.frame = 4
                    else:
                        speed = abs(self.x_speed) * self.VEL[abs(math.floor(self.x_speed))]
                        ms = (8.0 / speed) * 15
                        self.next_anim_time = current_time + ms
                        self.frame += 1
                        if self.frame > 3:
                            self.frame = 0
                    if self.frame == 2:
                        self.sounds["walk1"].play(0) if self.alternate_walk else self.sounds["walk2"].play(0)
                        self.alternate_walk = not self.alternate_walk
                else:
                    self.frame = 3
                    self.playerChannel.stop()

        self.rect.topleft = (self.x, self.y)
        self.image = self.build_mount(self.mount)

        if not self.facing_right:
            self.image = pg.transform.flip(self.image, True, False)
            self.mask = pg.mask.from_surface(self.image)

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

        self.velocity()

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
        collided_platforms = pg.sprite.spritecollide(self, platforms, False, pg.sprite.collide_mask)

        for collidedPlatform in collided_platforms:
            collided = self.bounce(collidedPlatform)

        if not collided:
            self.walking = False

        self.rect.topleft = (self.x, self.y)
        self.animate(current_time)
        self.image = self.unmounted_images[self.frame]
        if self.x_speed < 0 or (self.x_speed == 0 and not self.facing_right):
            self.image = pg.transform.flip(self.image, True, False)
            self.facing_right = False
        else:
            self.facing_right = True

    def bounce(self, collider):
        collided = False
        enemy = True if type(collider) is Enemy else False
        if not enemy and self.walking and (self.y > collider.y - 40):
            collided = True
            self.x += -21 if self.x_speed > 0 else 21
            self.x_speed = -self.x_speed
            self.playerChannel.play(self.sounds["bump"])
        elif collider.rect.left < self.rect.centerx < collider.rect.right and (
                collider.rect.centery > self.rect.centery):
            # coming in from the top?
            if enemy:
                self.y_speed = max(-self.y_speed, -6)
                self.y = collider.y - 25
                self.playerChannel.play(self.sounds["hit"])
            else:
                collided = True
                if collider.rect.left + 10 < self.rect.centerx < collider.rect.right - 10:
                    if not self.walking:
                        self.walking = True

                    self.y = collider.y - self.rect.height + 1
                    self.flap = 0
                    self.y_speed = 0
                else:
                    self.y_speed = -2
        elif self.y - self.y_speed > collider.rect.top and (
                collider.rect.left < self.rect.centerx < collider.rect.right):
            # player is below collider
            collided = True
            self.playerChannel.play(self.sounds["bump"])
            self.y = self.y + 10
            self.y_speed = -self.y_speed
        elif self.rect.centerx < collider.rect.centerx:
            # player is to left of collider
            collided = True
            if enemy:
                self.playerChannel.play(self.sounds["hit"])
                self.y_speed = max(-self.y_speed, -3)
                self.x_speed = max(-self.x_speed, -3)
            elif self.rect.bottom > collider.rect.bottom:
                self.playerChannel.play(self.sounds["bump"])
                self.x = self.x - (2 * abs(self.x_speed))
                self.x_speed = -3
        elif self.rect.centerx > collider.rect.centerx:
            # player is to right of collider
            collided = True
            if enemy:
                self.playerChannel.play(self.sounds["hit"])
                self.y_speed = max(-self.y_speed, -3)
                self.x_speed = min(-self.x_speed, 3)
            elif self.rect.bottom > collider.rect.bottom:
                self.playerChannel.play(self.sounds["bump"])
                self.x = self.x + (2 * abs(self.x_speed))
                self.x_speed = 3

        return collided

    def die(self, score):
        self.lives -= 1
        self.spawning = 20
        self.alive = "unmounted"
        self.poof = Poof(self.poof_images, self.x, self.y - 20)
        self.add_sprite(None, self.poof)
        score.die()

    def respawn(self):
        self.frame = 1
        self.x = 389
        self.y = 491
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.facing_right = True
        self.x_speed = 0
        self.y_speed = 0
        self.flap = 0
        self.walking = True
        self.skidding = False
        self.alive = "spawning"


class Poof(pg.sprite.Sprite):
    def __init__(self, poof, x, y):
        super().__init__()
        self.poof = poof
        self.image = self.poof[0]
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)
        self.animation_index = 0
        self.next_animate = 0

    def update(self, current_time):
        if current_time < self.next_animate:
            return
        self.next_animate = current_time + 200

        if self.animation_index < len(self.poof):
            self.image = self.poof[self.animation_index]
            self.rect = self.image.get_rect()
            self.rect.topleft = (self.x, self.y)
            self.animation_index += 1
        else:
            self.kill()


class ScoreBadge(pg.sprite.Sprite):
    def __init__(self, chars_small, x, y, points, bonus=False):
        super().__init__()
        self.chars_small = chars_small
        self.image = self.chars_small[0]
        self.rect = self.image.get_rect()
        self.points = points
        self.bonus = bonus
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)
        self.animation_index = 0
        self.ttl = 0

    def build_score(self):
        surf = pg.Surface((45, 33), pg.SRCALPHA)
        index = 0
        if self.bonus:
            surf.blit(self.chars_small[5], (0, 0))
            surf.blit(self.chars_small[0], (12, 0))
            surf.blit(self.chars_small[0], (24, 0))
            mask = pg.mask.from_surface(surf)
            surf = mask.to_surface(setcolor=(0, 255, 0))

        for digit in str(self.points):
            d = int(digit)
            surf.blit(self.chars_small[d], (12 * index, 18))
            index += 1

        return surf

    def update(self, current_time, remove_badge):
        if self.ttl == 0:
            self.ttl = current_time + 500

        if current_time > self.ttl:
            remove_badge(self)
            self.kill()
        else:
            self.image = self.build_score()
            self.rect = self.image.get_rect()
            self.rect.topleft = (self.x, self.y)
