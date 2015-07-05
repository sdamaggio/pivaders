#!/usr/bin/env python2

# TODO:
# change spaceship color when gode mode is on
# and add volume to sound
#
#
#


import pygame, random, time

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ALIEN_SIZE = (30, 40)
ALIEN_SPACER = 20
BARRIER_ROW = 10
BARRIER_COLUMN = 4
BULLET_SIZE = (5, 10)
MISSILE_SIZE = (5, 5)
BLOCK_SIZE = (10, 10)
RES = (800, 600)

rightPressed = False
leftPressed = False


# add this in /boot/config.txt (remove first # on every row)
#
# # uncomment to force a specific HDMI mode (this will force VGA)
# hdmi_group=2
# hdmi_mode=8


# http://raspi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Wiring Joystick + buttons:
# UP            gpio22  pin 15
# RIGHT         gpio27  pin 13  move right
# LEFT          gpio18  pin 12  move left
# GREN BUTTON   gpio23  pin 16  shoot
# BLUE BUTTON   gpio24  pin 18  Esc
# GND           pin 11, 14, 6

# unused
# DOWN          gpio17  pin 11

pinUp = 22
pinRight = 27
pinLeft = 18
pinShoot = 23
pinEsc = 24
pinWiringSolved = 0

#GPIO pin setup
GPIO.setup(pinUp, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinRight, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinLeft, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinShoot, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinEsc, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinWiringSolved, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (64, 61)
        self.rect = self.image.get_rect()
        self.rect.x = (RES[0] / 2) - (self.size[0] / 2)
        self.rect.y = 520
        self.travel = 7
        self.speed = 1000 # NOTE: default 1000, 150 for god mode 
        self.time = pygame.time.get_ticks()

    def update(self):
        if GameState.god_mode == True:
            self.speed = 150;
            self.lives = 98;
        self.rect.x += GameState.vector * self.travel
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > RES[0] - self.size[0]:
            self.rect.x = RES[0] - self.size[0]


class Alien(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (ALIEN_SIZE)
        self.rect = self.image.get_rect()
        self.has_moved = [0, 0]
        self.vector = [1, 1]
        self.travel = [(ALIEN_SIZE[0] - 7), ALIEN_SPACER]
        self.speed = 700
        self.time = pygame.time.get_ticks()

    def update(self):
        if GameState.alien_time - self.time > self.speed:
            if self.has_moved[0] < 12:
                self.rect.x += self.vector[0] * self.travel[0]
                self.has_moved[0] += 1
            else:
                if not self.has_moved[1]:
                    self.rect.y += self.vector[1] * self.travel[1]
                self.vector[0] *= -1
                self.has_moved = [0, 0]
                self.speed -= 20
                if self.speed <= 100:
                    self.speed = 100
            self.time = GameState.alien_time


class Ammo(pygame.sprite.Sprite):
    def __init__(self, color, (width, height)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.speed = 0
        self.vector = 0

    def update(self):
        self.rect.y += self.vector * self.speed
        if self.rect.y < 0 or self.rect.y > RES[1]:
            self.kill()


class Block(pygame.sprite.Sprite):
    def __init__(self, color, (width, height)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()


class GameState:
    pass


class Game(object):
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()
        
        self.game_font = pygame.font.Font('data/Orbitracer.ttf', 28)
        self.intro_font = pygame.font.Font('data/Orbitracer.ttf', 72)
        
        self.screen = pygame.display.set_mode([RES[0], RES[1]], pygame.FULLSCREEN)
        
        self.time = pygame.time.get_ticks()
        self.refresh_rate = 20
        self.rounds_won = 0
        self.level_up = 50
        self.score = 0
        self.lives = 2
        
        self.player_group = pygame.sprite.Group()
        self.alien_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.missile_group = pygame.sprite.Group()
        self.barrier_group = pygame.sprite.Group()
        self.all_sprite_list = pygame.sprite.Group()
        
        #load images and sounds
        self.sys_overheat0 = pygame.image.load('data/graphics/system_overheating_0.png').convert_alpha()
        self.sys_overheat1 = pygame.image.load('data/graphics/system_overheating_1.png').convert_alpha()
        self.intro_screen = pygame.image.load('data/graphics/start_screen.jpg').convert()
        self.background = pygame.image.load('data/graphics/Space-Background.jpg').convert()
        pygame.display.set_caption('Pivaders - ESC to exit')
        pygame.mouse.set_visible(False)
        Alien.image = pygame.image.load('data/graphics/Spaceship16.png').convert_alpha() #was without _alpha
        Alien.image.set_colorkey(WHITE)        
        Player.image = pygame.image.load('data/graphics/ship_sheet_final.png').convert_alpha()
        self.animate_right = False
        self.animate_left = False
        self.explosion_sheet = pygame.image.load('data/graphics/explosion_new1.png').convert_alpha()
        self.explosion_image = self.explosion_sheet.subsurface(0, 0, 79, 96)
        self.alien_explosion_sheet = pygame.image.load('data/graphics/alien_explosion.png')
        self.alien_explode_graphics = self.alien_explosion_sheet.subsurface(0, 0, 94, 96)
        self.explode = False
        self.explode_pos = 0
        self.alien_explode = False
        self.alien_explode_pos = 0
        pygame.mixer.music.load('data/sound/10_Arpanauts.ogg')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.7)
        self.bullet_fx = pygame.mixer.Sound('data/sound/shoot.wav')
        self.explosion_fx = pygame.mixer.Sound('data/sound/invaderkilled.wav')
        self.explosion_fx.set_volume(0.5)
        self.explodey_alien = []
        
        # initialize GameState vars
        GameState.end_game = False
        GameState.start_screen = True
        GameState.vector = 0
        GameState.shoot_bullet = False
        GameState.god_mode = False

    def control(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameState.start_screen = False
                GameState.end_game = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if GameState.start_screen:
                    GameState.start_screen = False
                    GameState.end_game = True
                    self.kill_all()
                else:
                    GameState.start_screen = True
            if GPIO.input(pinEsc) == 0:
                if GameState.start_screen:
                    GameState.start_screen = False
                    GameState.end_game = True
                    self.kill_all()
                else:
                    GameState.start_screen = True
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_LEFT] or GPIO.input(pinLeft) == 0:
            self.animate_left = True
            self.animate_right = False
            if GameState.god_mode == False:
                GameState.vector = -1
            else:
                GameState.vector = -2                    
        elif self.keys[pygame.K_RIGHT] or GPIO.input(pinRight) == 0:
            self.animate_right = True
            self.animate_left = False
            if GameState.god_mode == False:
                GameState.vector = 1
            else:
                GameState.vector = 2 

        else:
            GameState.vector = 0
            self.animate_right = False
            self.animate_left = False
        if self.keys[pygame.K_SPACE] or GPIO.input(pinShoot) == 0 or GPIO.input(pinUp) == 0:
            if GameState.start_screen:
                GameState.start_screen = False
                self.lives = 2
                self.score = 0
                self.make_player()
                self.make_defenses()
                self.alien_wave(0)
            else:
                GameState.shoot_bullet = True
                self.bullet_fx.play()

    def player_explosion(self):
        if self.explode:
            if self.explode_pos < 8:
                self.explosion_image = self.explosion_sheet.subsurface(0, self.explode_pos * 96, 79, 96)
                self.explode_pos += 1
                self.screen.blit(self.explosion_image, [self.player.rect.x - 10, self.player.rect.y - 30])
            else:
                self.explode = False
                self.explode_pos = 0	

    def alien_explosion(self):
        if self.alien_explode:
            if self.alien_explode_pos < 9:
                self.alien_explode_graphics = self.alien_explosion_sheet.subsurface(
                    0, self.alien_explode_pos * 96, 94, 96)
                self.alien_explode_pos += 1
                self.screen.blit(self.alien_explode_graphics, [
                    int(self.explodey_alien[0]) - 50, int(self.explodey_alien[1]) - 60])
            else:
                self.alien_explode = False
                self.alien_explode_pos = 0
                self.explodey_alien = []

    def splash_screen(self):    
        # TODO: remove counter and replace for with "while GPIO.input(pinLeft) != 0:"
        #for count in range(0,5):
        #    self.screen.blit(self.sys_overheat0, [0, 0])
        #    pygame.display.flip()
        #    time.sleep(1.0)
        #    self.screen.blit(self.sys_overheat1, [0, 0])
        #    pygame.display.flip()
        #    time.sleep(1.0)
        #    self.control()
            
        while GameState.start_screen:
			self.kill_all()            
			self.screen.blit(self.intro_screen, [0, 0])
			#self.screen.blit(self.intro_font.render("PIVADERS", 1, WHITE), (265, 120))
			#self.screen.blit(self.game_font.render("PRESS SPACE TO PLAY", 1, WHITE), (274, 191))
			pygame.display.flip()
			self.control()
			self.clock.tick(self.refresh_rate / 2)		

    def make_player(self):
        self.player = Player()
        self.player_group.add(self.player)
        self.all_sprite_list.add(self.player)

    def refresh_screen(self):
        self.all_sprite_list.draw(self.screen)
        self.player_explosion()
        self.alien_explosion()
        self.refresh_scores()
        pygame.display.flip()
        self.screen.blit(self.background, [0, 0])
        self.clock.tick(self.refresh_rate)

    def refresh_scores(self):
        self.screen.blit(self.game_font.render("SCORE " + str(self.score), 1, WHITE), (10, 8))
        self.screen.blit(self.game_font.render("LIVES " + str(self.lives + 1), 1, RED), (355, 575))

    def alien_wave(self, speed):
        for column in range(BARRIER_COLUMN):
            for row in range(BARRIER_ROW):
                alien = Alien()
                alien.rect.y = 65 + (column * (ALIEN_SIZE[1] + ALIEN_SPACER))
                alien.rect.x = ALIEN_SPACER + (row * (ALIEN_SIZE[0] + ALIEN_SPACER))
                self.alien_group.add(alien)
                self.all_sprite_list.add(alien)
                alien.speed -= speed

    def make_bullet(self):
        if GameState.game_time - self.player.time > self.player.speed:
            if GameState.god_mode == False:
                bullet = Ammo(BLUE, BULLET_SIZE)
                bullet.vector = -1
                bullet.speed = 13
                bullet.rect.x = self.player.rect.x + 28
                bullet.rect.y = self.player.rect.y
                self.bullet_group.add(bullet)
                self.all_sprite_list.add(bullet)
                self.player.time = GameState.game_time
            else:	
                for cont in range(0, 11):
                    bullet = Ammo(YELLOW, BULLET_SIZE)
                    bullet.vector = -1
                    bullet.speed = 26                  

                    #if cont == 0:
                    #    bullet.rect.x = self.player.rect.x + 29 - 6
                    #    bullet.rect.y = self.player.rect.y - 80			
                    #if cont == 1:
                    #    bullet.rect.x = self.player.rect.x + 29 + 6				
                    #    bullet.rect.y = self.player.rect.y - 80
                    if cont == 2:
                        bullet.rect.x = self.player.rect.x + 29 - 6
                        bullet.rect.y = self.player.rect.y - 40        
                    if cont == 3:
                        bullet.rect.x = self.player.rect.x + 29 + 6          
                        bullet.rect.y = self.player.rect.y - 20
                    if cont == 4:
                        bullet.rect.x = self.player.rect.x + 29 - 6            
                        bullet.rect.y = self.player.rect.y 
                    if cont == 5:
                        bullet.rect.x = self.player.rect.x + 29 + 6         
                        bullet.rect.y = self.player.rect.y + 20
                    #if cont == 6:
                    #    bullet.rect.x = self.player.rect.x + 29 - 6          
                    #    bullet.rect.y = self.player.rect.y + 40
                    #if cont == 7:
                    #    bullet.rect.x = self.player.rect.x + 29 + 6        
                    #    bullet.rect.y = self.player.rect.y + 40
                    #if cont == 8:
                    #    bullet.rect.x = self.player.rect.x + 29 - 6          
                    #    bullet.rect.y = self.player.rect.y + 80
                    #if cont == 9:
                    #    bullet.rect.x = self.player.rect.x + 29 + 6      
                    #    bullet.rect.y = self.player.rect.y + 80

                    self.bullet_group.add(bullet)
                    self.all_sprite_list.add(bullet)
                    self.player.time = GameState.game_time
        GameState.shoot_bullet = False

    def make_missile(self):
        if len(self.alien_group):
            shoot = random.random()
            if shoot <= 0.25: # def: 0.05
                shooter = random.choice([
                    alien for alien in self.alien_group])
                missile = Ammo(RED, MISSILE_SIZE)
                missile.vector = 1
                missile.rect.x = shooter.rect.x + 15
                missile.rect.y = shooter.rect.y + 40
                missile.speed = 18 # def: 10
                self.missile_group.add(missile)
                self.all_sprite_list.add(missile)

    def make_barrier(self, columns, rows, spacer):
        for column in range(columns):
            for row in range(rows):
                barrier = Block(WHITE, (BLOCK_SIZE))
                barrier.rect.x = 55 + (200 * spacer) + (row * 10)
                barrier.rect.y = 450 + (column * 10)
                self.barrier_group.add(barrier)
                self.all_sprite_list.add(barrier)

    def make_defenses(self):
        for spacing, spacing in enumerate(xrange(4)):
            self.make_barrier(3, 9, spacing)

    def kill_all(self):
        for items in [self.bullet_group, self.player_group,
                      self.alien_group, self.missile_group, self.barrier_group]:
            for i in items:
                i.kill()

    def is_dead(self):
        if self.lives < 0:
            self.screen.blit(self.game_font.render("The war is lost! You scored: " + str(self.score), 1, RED), (250, 15))
            self.rounds_won = 0
            self.refresh_screen()
            self.level_up = 50
            self.explode = False
            self.alien_explode = False
            pygame.time.delay(3000)
            return True

    def defenses_breached(self):
        for alien in self.alien_group:
            if alien.rect.y > 410:
                self.screen.blit(self.game_font.render("The aliens have breached Earth defenses!", 1, RED), (180, 15))
                self.refresh_screen()
                self.level_up = 50
                self.explode = False
                self.alien_explode = False
                pygame.time.delay(3000)
                return True

    def win_round(self):
        if len(self.alien_group) < 1:
            self.rounds_won += 1
            self.screen.blit(self.game_font.render("You won round " + str(self.rounds_won) + "  but the battle rages on", 1, RED), (200, 15))
            self.refresh_screen()
            pygame.time.delay(3000)
            return True

    def next_round(self):
        self.explode = False
        self.alien_explode = False
        for actor in [self.missile_group, self.barrier_group, self.bullet_group]:
            for i in actor:
                i.kill()
        self.alien_wave(self.level_up)
        self.make_defenses()
        self.level_up += 50

    def calc_collisions(self):
        pygame.sprite.groupcollide(self.missile_group, self.barrier_group, True, True)
        pygame.sprite.groupcollide(self.bullet_group, self.barrier_group, True, True)

        for z in pygame.sprite.groupcollide(self.bullet_group, self.alien_group, True, True):
            self.alien_explode = True
            self.explodey_alien.append(z.rect.x)
            self.explodey_alien.append(z.rect.y)
            self.score += 10
            self.explosion_fx.play()

        if pygame.sprite.groupcollide(
                self.player_group, self.missile_group, False, True):
            self.lives -= 1
            self.explode = True
            self.explosion_fx.play()

    def main_loop(self):
        while not GameState.end_game:
            while not GameState.start_screen:
                GameState.game_time = pygame.time.get_ticks()
                GameState.alien_time = pygame.time.get_ticks()
                self.control()
                self.make_missile()
                self.calc_collisions()
                self.refresh_screen()
                if self.is_dead() or self.defenses_breached():
                    GameState.start_screen = True
                for actor in [self.player_group, self.bullet_group, self.alien_group, self.missile_group]:
                    for i in actor:
                        i.update()
                if GameState.shoot_bullet:
                    self.make_bullet()
                if self.win_round():
                    self.next_round()
            self.splash_screen()
        pygame.quit()


if __name__ == '__main__':
    pv = Game()
    pv.main_loop()
