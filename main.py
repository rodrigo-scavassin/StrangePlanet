import pygame as pg
import sys
from random import choice, random
from os import path
from settings import *
from sprites import *
from tilemap import *
from spritesheet import Spritesheet
import time

index = 0

def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)

class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        movie_folder = path.join(game_folder, 'movie')
        self.map_folder = path.join(game_folder, 'maps')
        self.title_font = path.join(img_folder, 'game_of_squids.TTF')
        self.hud_font = path.join(img_folder, 'ethnocentric.ttf')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        self.player_spritesheet = Spritesheet(PLAYER_IMG)
        self.player_s = [self.player_spritesheet.parse_sprite('player_s1.png'), self.player_spritesheet.parse_sprite('player_s2.png'),self.player_spritesheet.parse_sprite('player_s3.png')]
        self.player_sw = [self.player_spritesheet.parse_sprite('player_sw1.png'), self.player_spritesheet.parse_sprite('player_sw2.png'),self.player_spritesheet.parse_sprite('player_sw3.png')]
        self.player_w = [self.player_spritesheet.parse_sprite('player_w1.png'), self.player_spritesheet.parse_sprite('player_w2.png'),self.player_spritesheet.parse_sprite('player_w3.png')]
        self.player_nw = [self.player_spritesheet.parse_sprite('player_nw1.png'), self.player_spritesheet.parse_sprite('player_nw2.png'),self.player_spritesheet.parse_sprite('player_nw3.png')]
        self.player_n = [self.player_spritesheet.parse_sprite('player_n1.png'), self.player_spritesheet.parse_sprite('player_n2.png'),self.player_spritesheet.parse_sprite('player_n3.png')]
        self.player_ne = [self.player_spritesheet.parse_sprite('player_ne1.png'), self.player_spritesheet.parse_sprite('player_ne2.png'),self.player_spritesheet.parse_sprite('player_ne3.png')]
        self.player_e = [self.player_spritesheet.parse_sprite('player_e1.png'), self.player_spritesheet.parse_sprite('player_e2.png'),self.player_spritesheet.parse_sprite('player_e3.png')]
        self.player_se = [self.player_spritesheet.parse_sprite('player_se1.png'), self.player_spritesheet.parse_sprite('player_se2.png'),self.player_spritesheet.parse_sprite('player_se3.png')]
        self.player_img = self.player_s[index]
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))
        self.alien_imgs = [pg.image.load(path.join(img_folder, ALIEN_IMG[0])).convert_alpha(), pg.image.load(path.join(img_folder, ALIEN_IMG[1])).convert_alpha()]
        self.alien_img = self.alien_imgs[index]
        self.fireAlien_imgs = [pg.image.load(path.join(img_folder, FIRE_ALIEN_IMG[0])).convert_alpha(), pg.image.load(path.join(img_folder, FIRE_ALIEN_IMG[1])).convert_alpha()]
        self.fireAlien_img = self.fireAlien_imgs[index]
        self.boss_imgs = [pg.image.load(path.join(img_folder, BOSS_IMG[0])).convert_alpha(), pg.image.load(path.join(img_folder, BOSS_IMG[1])).convert_alpha()]
        self.boss_img = self.boss_imgs[index]
        self.spider_imgs = [pg.image.load(path.join(img_folder, SPIDER_IMG[0])).convert_alpha(), pg.image.load(path.join(img_folder, SPIDER_IMG[1])).convert_alpha()]
        self.spider_img = self.spider_imgs[index]
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        self.fireSplat = pg.image.load(path.join(img_folder, FIRE_SPLAT)).convert_alpha()
        self.fireSplat = pg.transform.scale(self.fireSplat, (64, 64))
        self.bossSplat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.bossSplat = pg.transform.scale(self.splat, (128, 128))
        self.spiderSplat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.spiderSplat = pg.transform.scale(self.splat, (128, 128))
        self.comet1_imgs = [pg.image.load(path.join(movie_folder, COMET1[0])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET1[1])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET1[2])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET1[3])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET1[4])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET1[5])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET1[6])).convert_alpha()]
        self.comet2_imgs = [pg.image.load(path.join(movie_folder, COMET2[0])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET2[1])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET2[2])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET2[3])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET2[4])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET2[5])).convert_alpha(), pg.image.load(path.join(movie_folder, COMET2[6])).convert_alpha()]
        self.intro_basic = pg.image.load(path.join(movie_folder, INTRO_BASIC)).convert_alpha()
        self.intro_basic = pg.transform.scale(self.intro_basic, (WIDTH, HEIGHT))
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
        self.radar_img = pg.image.load(path.join(img_folder, RADAR)).convert_alpha()
        self.tutorial_img = pg.image.load(path.join(img_folder, HOW_TO_PLAY)).convert_alpha()
        self.tutorial_img = pg.transform.scale(self.tutorial_img, (round(HEIGHT*1100/880), round(HEIGHT)))
        # efeito de luz
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()
        # som / músicas
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
        self.alien_cry_sounds = []
        for snd in ALIEN_CRY_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(1)
            self.alien_cry_sounds.append(s)
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
        self.alien_hit_sounds = []
        for snd in ALIEN_HIT_SOUNDS:
            self.alien_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))

    def new(self):
        # inicializa variaiveis para o inicio do jogo
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.lavas = pg.sprite.Group()
        self.aliens = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_folder, 'map.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'alien':
                Alien(self, obj_center.x, obj_center.y)
            if tile_object.name == 'fireAlien':
                FireAlien(self, obj_center.x, obj_center.y)
            if tile_object.name == 'boss':
                Boss(self, obj_center.x, obj_center.y)
            if tile_object.name == 'spider':
                Spider(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name == 'lava':
                Lava(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun']:
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.radarzin = False
        self.paused = False
        self.night = False
        self.godMode = False

    def run(self):
        # loop game
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0  # para funcionar com Python 2.x
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # Atualiza loop game
        self.all_sprites.update()
        self.camera.update(self.player)
        # game over?
        if len(self.aliens) == 0:
            self.playing = False
        # jogador colide com itens
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            if hit.type == 'leg' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(LEG_AMOUNT)
            if hit.type == 'eye' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(EYE_AMOUNT)
            if hit.type == 'shotgun':
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = 'shotgun'
        # inimigo colide com o jogador
        if not(self.godMode):
            hits = pg.sprite.spritecollide(self.player, self.aliens, False, collide_hit_rect)
            for hit in hits:
                if random() < 0.7:
                    choice(self.player_hit_sounds).play()


                # EFEITO CAMERA VERMELHA
                for i in range(0,2):
                    GB = min(255, max(0, round(255 * (1-0.8))))
                    self.screen.fill((255, GB, GB), special_flags = pg.BLEND_MULT)
                    pg.display.flip()
                    pg.time.wait(5)

                if (type(hit)==Alien):
                    self.player.health -= ALIEN_DAMAGE
                elif (type(hit)==FireAlien):
                    self.player.health -= FIRE_ALIEN_DAMAGE
                elif (type(hit)==Spider):
                    self.player.health -= SPIDER_DAMAGE
                else:
                    self.player.health -= BOSS_DAMAGE

                hit.vel = vec(0, 0)
                if self.player.health <= 0:
                    self.playing = False
            if hits:
                self.player.hit()
                self.player.pos += vec(ALIEN_KNOCKBACK, 0).rotate(-hits[0].rot)
        # projétil colide com inimigo
        hits = pg.sprite.groupcollide(self.aliens, self.bullets, False, True)
        for alien in hits:
            for bullet in hits[alien]:
                alien.health -= bullet.damage
                if (type(alien)==Boss and alien.health <= 0):
                    Item(self, alien.pos + vec(32, 32), 'leg')
                if (type(alien)==Spider and alien.health <= 0):
                    Item(self, alien.pos + vec(32, 32), 'eye')

            alien.vel = vec(0, 0)
    def draw_radar(self):
        s = pg.Surface((WIDTH,HEIGHT))  
        s.set_alpha(200)              
        s.fill((0,0,0))          
        self.screen.blit(s, (0,0))    

        self.radar_rect = self.radar_img.get_rect()
        self.screen.blit(self.radar_img, (WIDTH/2-599/2, HEIGHT/2-599/2))
        x,y = self.player.pos
        x_radplayer = ((x*599)/19200) + (WIDTH - 599)/2
        y_radplayer = ((y*599)/19200) + (HEIGHT - 599)/2

        pg.draw.rect(self.screen,RED,(x_radplayer,y_radplayer,10,10))

        pass
    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def render_fog(self):
        # Desenhar a máscara de luz (gradiente) na imagem esurecida
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)


    def draw(self):
        self.screen.blit(self.map_img, self.camera.apply(self.map))
        
        for sprite in self.all_sprites:
            if isinstance(sprite, Alien):
                sprite.draw_health()
            if isinstance(sprite, FireAlien):
                sprite.draw_health()
            if isinstance(sprite, Boss):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if isinstance(sprite, Spider):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            self.draw_grid()
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)
            for lava in self.lavas:
                pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(lava.rect), 1)
        if self.radarzin:
            self.draw_radar()

 
        if self.night:
            self.render_fog()
        # HUD
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        self.draw_text('Aliens: {}'.format(len(self.aliens)), self.hud_font, 30, WHITE,
                       WIDTH - 10, 10, align="topright")
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align="center")
        pg.display.flip()

    def events(self):
        global index
        game_folder = path.dirname(__file__)
        music_folder = path.join(game_folder, 'music')
        # detectar eventos
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:

                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_x:
                    self.radarzin = not self.radarzin
                if event.key == pg.K_q:
                    self.godMode = not self.godMode
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_k:
                    for alien in g.aliens:
                        alien.kill()
                if event.key == pg.K_n:
                    self.night = not self.night
                    # Tocar música noturna
                    if self.night:
                        pg.mixer.music.load(path.join(music_folder, NIGHT))
                        pg.mixer.music.play(loops=-1)
                    else:
                        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
                        pg.mixer.music.play(loops=-1)
                if event.key == pg.K_g:
                    if self.player.weapon == 'shotgun':
                        self.player.weapon = 'pistol'
                    else:
                        self.player.weapon = 'shotgun'

    def show_win_screen(self):
        self.screen.fill(BLACK)
        game_folder = path.dirname(__file__)
        music_folder = path.join(game_folder, 'music')
        pg.mixer.music.load(path.join(music_folder, WIN))
        pg.mixer.music.play(loops=1)
        self.draw_text("YOU SAVED THE GALAXY", self.title_font, 100, BLUE,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press any key to continue", self.title_font, 50, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))

    def show_go_screen(self):
        self.screen.fill(BLACK)
        game_folder = path.dirname(__file__)
        music_folder = path.join(game_folder, 'music')
        pg.mixer.music.load(path.join(music_folder, GAME_OVER))
        pg.mixer.music.play(loops=1)
        self.draw_text("GAME OVER", self.title_font, 180, RED,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press any key to continue", self.title_font, 50, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
    
    def show_start_screen(self):
        game_folder = path.dirname(__file__)
        music_folder = path.join(game_folder, 'music')
        pg.mixer.music.load(path.join(music_folder, INTRO))
        pg.mixer.music.play(loops=-1)
        intro_playing = True
        while intro_playing:
            aleatorio = choice([1,2,0,0,0,0,0,0,0])
            if aleatorio == 0:
                self.screen.blit(self.intro_basic, (0, 0))
                self.draw_text("STRANGE PLANET", self.title_font, 130, GREEN,
                        WIDTH / 2, HEIGHT / 2, align="center")
                self.draw_text("Press any key to start", self.title_font, 50, WHITE,
                        WIDTH / 2, HEIGHT * 3 / 4, align="center")
                pg.draw.rect(self.screen, BLACK, (0, 0, WIDTH/12,HEIGHT/8))
                pg.display.flip()
                time.sleep(1)
            elif aleatorio == 1:
                for comet in self.comet1_imgs:
                    self.screen.blit(pg.transform.scale(comet, (WIDTH, HEIGHT)), (0, 0))
                    self.draw_text("STRANGE PLANET", self.title_font, 130, GREEN,
                        WIDTH / 2, HEIGHT / 2, align="center")
                    self.draw_text("Press any key to start", self.title_font, 50, WHITE,
                        WIDTH / 2, HEIGHT * 3 / 4, align="center")
                    pg.draw.rect(self.screen, BLACK, (0, 0, WIDTH/12,HEIGHT/8))
                    pg.display.flip()
                    time.sleep(0.05)
            elif aleatorio == 2:
                for comet in self.comet2_imgs:
                    self.screen.blit(pg.transform.scale(comet, (WIDTH, HEIGHT)), (0, 0))
                    self.draw_text("STRANGE PLANET", self.title_font, 130, GREEN,
                        WIDTH / 2, HEIGHT / 2, align="center")
                    self.draw_text("Press any key to start", self.title_font, 50, WHITE,
                        WIDTH / 2, HEIGHT * 3 / 4, align="center")
                    pg.draw.rect(self.screen, BLACK, (0, 0, WIDTH/12,HEIGHT/8))
                    pg.display.flip()
                    time.sleep(0.05)

            
            for event in pg.event.get():
                if event.type == pg.KEYUP:
                    intro_playing = False
            
        self.screen.fill(BROWN)
        self.tutorial_rect = self.tutorial_img.get_rect()
        self.screen.blit(self.tutorial_img, (WIDTH/2-self.tutorial_rect.width/2, HEIGHT/2-self.tutorial_rect.height/2))
        pg.display.flip()
                        
        self.wait_for_key()

        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

# estanciar objeto do jogo
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    if len(g.aliens) == 0:
        g.show_win_screen()
    else:
        g.show_go_screen()