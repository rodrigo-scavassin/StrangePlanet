import pygame as pg
from random import uniform, choice, randint, random
from settings import *
from tilemap import collide_hit_rect
import pytweening as tween
from itertools import chain
import math
vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.weapon = 'pistol'
        self.damaged = False
        self.index = 0

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
            self.index = (self.index + 0.05) % 3
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
            self.index = (self.index + 0.05) % 3
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
            self.index = (self.index + 0.1) % 3
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
            self.index = (self.index + 0.05) % 3
        if keys[pg.K_SPACE]:
            self.shoot()

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + BARREL_OFFSET.rotate(-self.rot) + vec(0, -48)
            self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                spread = uniform(-WEAPONS[self.weapon]['spread'], WEAPONS[self.weapon]['spread'])
                Bullet(self.game, pos, dir.rotate(spread), WEAPONS[self.weapon]['damage'])
                snd = choice(self.game.weapon_sounds[self.weapon])
                if snd.get_num_channels() > 2:
                    snd.stop()
                snd.play()
            MuzzleFlash(self.game, pos)

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 4)

    def update(self):
        if self.rot <= 22.5 or self.rot > 337.5:
            self.image = self.game.player_e[math.trunc(self.index)]
        if self.rot <= 67.5 and self.rot > 22.5:
            self.image = self.game.player_ne[math.trunc(self.index)]
        if self.rot <= 112.5 and self.rot > 67.5:
            self.image = self.game.player_n[math.trunc(self.index)]
        if self.rot <= 157.5 and self.rot > 112.5:
            self.image = self.game.player_nw[math.trunc(self.index)]
        if self.rot <= 202.5 and self.rot > 157.5:
            self.image = self.game.player_w[math.trunc(self.index)]
        if self.rot <= 247.5 and self.rot > 202.5:
            self.image = self.game.player_sw[math.trunc(self.index)]
        if self.rot <= 292.5 and self.rot > 247.5:
            self.image = self.game.player_s[math.trunc(self.index)]
        if self.rot <= 337.5 and self.rot > 292.5:
            self.image = self.game.player_se[math.trunc(self.index)]

        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.image, 0)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        if self.game.godMode:
            self.pos += self.vel * 3 * self.game.dt
        else:
            self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        if not(self.game.godMode):
            collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        if not(self.game.godMode):
            collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = (self.hit_rect.centerx, self.hit_rect.centery-48)
        if not(self.game.godMode):
            self.collide_with_lava(self.game.lavas, self.game)

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH
    
    def collide_with_lava(self, group, game):
        if pg.sprite.spritecollide(self, group, False, collide_hit_rect):
            self.health -= LAVA_DAMAGE

            if (self.health <= 0):
               game.playing = False

class Alien(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = ALIEN_LAYER
        self.groups = game.all_sprites, game.aliens
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.images = game.alien_imgs
        self.image = game.alien_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = ALIEN_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = ALIEN_HEALTH
        self.speed = choice(ALIEN_SPEEDS)
        self.target = game.player
        self.index = 0

    def avoid_aliens(self):
        for alien in self.game.aliens:
            if alien != self:
                dist = self.pos - alien.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < DETECT_RADIUS**2:
            if random() < 0.002:
                choice(self.game.alien_cry_sounds).play()
            self.index = (self.index + 0.1) % 2
            self.rot = target_dist.angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.images[math.trunc(self.index)], 0)
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_aliens()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        if self.health <= 0:
            choice(self.game.alien_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))
    def draw_health(self):
        if (self.health > 0.6 * ALIEN_HEALTH):
            col = GREEN
        elif (self.health > 0.3 * ALIEN_HEALTH):
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / ALIEN_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < ALIEN_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)

## Não consegui fazer herança. Vou simplesmente copiar a classe

class FireAlien(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = FIRE_ALIEN_LAYER
        self.groups = game.all_sprites, game.aliens
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.images = game.fireAlien_imgs
        self.image = game.fireAlien_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = FIRE_ALIEN_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = FIRE_ALIEN_HEALTH
        self.speed = choice(FIRE_ALIEN_SPEEDS)
        self.target = game.player
        self.index = 0

    def avoid_aliens(self):
        for alien in self.game.aliens:
            if alien != self:
                dist = self.pos - alien.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < DETECT_RADIUS**2:
            if random() < 0.002:
                choice(self.game.alien_cry_sounds).play()
            self.index = (self.index + 0.1) % 2
            self.rot = target_dist.angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.images[math.trunc(self.index)], 0)
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_aliens()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        if self.health <= 0:
            choice(self.game.alien_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.fireSplat, self.pos - vec(32, 32))

    def draw_health(self):
        if (self.health > 0.6 * FIRE_ALIEN_HEALTH):
            col = GREEN
        elif (self.health > 0.3 * FIRE_ALIEN_HEALTH):
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / FIRE_ALIEN_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < FIRE_ALIEN_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class Boss(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = BOSS_LAYER
        self.groups = game.all_sprites, game.aliens
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.images = game.boss_imgs
        self.image = game.boss_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = BOSS_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = BOSS_HEALTH
        self.speed = choice(BOSS_SPEEDS)
        self.target = game.player
        self.index = 0

    def avoid_aliens(self):
        for alien in self.game.aliens:
            if alien != self:
                dist = self.pos - alien.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < BOSS_DETECT_RADIUS**2:
            if random() < 0.002:
                choice(self.game.alien_cry_sounds).play()
            self.index = (self.index + 0.1) % 2
            self.rot = target_dist.angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.images[math.trunc(self.index)], 0)
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_aliens()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        if self.health <= 0:
            choice(self.game.alien_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.bossSplat, self.pos - vec(32, 32))

    def draw_health(self):
        if (self.health > 0.6 * BOSS_HEALTH):
            col = GREEN
        elif (self.health > 0.3 * BOSS_HEALTH):
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / BOSS_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < BOSS_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class Spider(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = SPIDER_LAYER
        self.groups = game.all_sprites, game.aliens
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.images = game.spider_imgs
        self.image = game.spider_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = SPIDER_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = SPIDER_HEALTH
        self.speed = choice(SPIDER_SPEEDS)
        self.target = game.player
        self.index = 0

    def avoid_aliens(self):
        for alien in self.game.aliens:
            if alien != self:
                dist = self.pos - alien.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < SPIDER_DETECT_RADIUS**2:
            if random() < 0.002:
                choice(self.game.alien_cry_sounds).play()
            self.index = (self.index + 0.1) % 2
            self.rot = target_dist.angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.images[math.trunc(self.index)], 0)
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_aliens()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        if self.health <= 0:
            choice(self.game.alien_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.spiderSplat, self.pos - vec(32, 32))

    def draw_health(self):
        if (self.health > 0.6 * SPIDER_HEALTH):
            col = GREEN
        elif (self.health > 0.3 * SPIDER_HEALTH):
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / SPIDER_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < SPIDER_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage
        self.hit_rect = BULLET_HIT_RECT

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']:
            self.kill()

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Lava(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.lavas
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()
        self.hit_rect = BULLET_HIT_RECT

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1
        self.hit_rect = ITEM_HIT_RECT

    def update(self):
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1
