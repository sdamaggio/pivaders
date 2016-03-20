#!/usr/bin/env python2

# TODO:
# game should have only 1 level so remove other levels
# add a screen to input the god mode code (1380)
## make a digit selector that will change the digit with joystick input
## go trough 4 of them and then check code and start game in god mode
# once we win god mode game it should stay on that screen until next reset
# send signals to mega and check signals from mega

# show "insert 0 coin" before starting to play
# change spaceship color when god mode is on and add volume to sound
# add fake menu to integrate cheat code page?


# // Pin modes
# 
# #define INPUT            0
# #define OUTPUT           1
# #define PWM_OUTPUT       2
# #define GPIO_CLOCK       3
# #define SOFT_PWM_OUTPUT      4
# #define SOFT_TONE_OUTPUT     5
# #define PWM_TONE_OUTPUT      6
# 
# #define LOW          0
# #define HIGH             1
# 
# // Pull up/down/none
# 
# #define PUD_OFF          0
# #define PUD_DOWN         1
# #define PUD_UP           2
# 
# // PWM
# 
# #define PWM_MODE_MS     0
# #define PWM_MODE_BAL        1
# 
# // Interrupt levels
# 
# #define INT_EDGE_SETUP      0
# #define INT_EDGE_FALLING    1
# #define INT_EDGE_RISING     2
# #define INT_EDGE_BOTH       3




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

credits = 0
# add this in /boot/config.txt (remove first # on every row)
#
# # uncomment to force a specific HDMI mode (this will force VGA)
# hdmi_group=2
# hdmi_mode=8


# http://raspi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2
import wiringpi2 as GPIO
GPIO.wiringPiSetupPhys()

# Wiring Joystick + buttons:
# door signal   gpio23  pin 33  open when high
# coin signal   gpio22  pin 31  active high

pinUp = 38
pinRight = 32
pinLeft = 36
pinDown = 40
pinShoot = 35
pinReady = 37

pinWiringDoorOcto = 33 # door open when HIGH

pinWiringPlugA = 8
pinWiringPlugB = 10
pinWiringPlugC = 12
pinWiringPlugD = 16
pinWiringRed = 24
pinWiringGreen = 18
pinWiringBlue = 22
pinWiringYellow = 26

pinCoinCounter = 31

pinLedStripRed = 19
pinLedStripGreen = 21
pinLedStripBlue = 23

pinFan = 29 # gpio mode 21 out, gpio write 21 1 to shut them off


pinWiringTaskSolved = 3
pin3CoinsInserted = 5
pinSpaceInvadersSolved = 7
pinBellTaskSolved = 11 # LOW is solved!
# free communication to mega pin --> pin 13
pinReset = 15 #wire it with level converter

#GPIO pin setup
GPIO.pinMode(pinUp, 0)
GPIO.pullUpDnControl(pinUp, 2)
GPIO.pinMode(pinRight, 0)
GPIO.pullUpDnControl(pinRight, 2)
GPIO.pinMode(pinLeft, 0)
GPIO.pullUpDnControl(pinLeft, 2)
GPIO.pinMode(pinDown, 0)
GPIO.pullUpDnControl(pinDown, 2)
GPIO.pinMode(pinShoot, 0)
GPIO.pullUpDnControl(pinShoot, 2)
GPIO.pinMode(pinReady, 0)
GPIO.pullUpDnControl(pinReady, 2)
GPIO.pinMode(pinWiringTaskSolved, 0)
GPIO.pullUpDnControl(pinWiringTaskSolved, 2)

GPIO.pinMode(pinWiringDoorOcto, 0)

GPIO.pinMode(pinWiringPlugA, 1)
GPIO.pinMode(pinWiringPlugB, 1)
GPIO.pinMode(pinWiringPlugC, 1)
GPIO.pinMode(pinWiringPlugD, 1)
GPIO.digitalWrite(pinWiringPlugA, 0)
GPIO.digitalWrite(pinWiringPlugB, 0)
GPIO.digitalWrite(pinWiringPlugC, 0)
GPIO.digitalWrite(pinWiringPlugD, 0)
GPIO.pinMode(pinWiringRed, 0)
GPIO.pullUpDnControl(pinWiringRed, 1)
GPIO.pinMode(pinWiringGreen, 0)
GPIO.pullUpDnControl(pinWiringGreen, 1)
GPIO.pinMode(pinWiringBlue, 0)
GPIO.pullUpDnControl(pinWiringBlue, 1)
GPIO.pinMode(pinWiringYellow, 0)
GPIO.pullUpDnControl(pinWiringYellow, 1)

### coin counter signal interrupt sensing
def coin_counted_event(channel):
    global credits
    credits += 1    

import RPi.GPIO as wiringpi
wiringpi.setmode(wiringpi.BOARD)
wiringpi.setup(pinCoinCounter, wiringpi.IN)  
wiringpi.add_event_detect(pinCoinCounter, wiringpi.FALLING, callback=coin_counted_event, bouncetime=300)

GPIO.pinMode(pinLedStripRed, 1)
GPIO.digitalWrite(pinLedStripRed, 0)
GPIO.pinMode(pinLedStripGreen, 1)
GPIO.digitalWrite(pinLedStripGreen, 0)
GPIO.pinMode(pinLedStripBlue, 1)
GPIO.digitalWrite(pinLedStripBlue, 0)

GPIO.pinMode(pinFan, 1)
GPIO.digitalWrite(pinFan, 0)

GPIO.pinMode(pinWiringTaskSolved, 1)
GPIO.digitalWrite(pinWiringTaskSolved, 1)
GPIO.pinMode(pin3CoinsInserted, 1)
GPIO.digitalWrite(pin3CoinsInserted, 1)
GPIO.pinMode(pinSpaceInvadersSolved, 1)
GPIO.digitalWrite(pinSpaceInvadersSolved, 1)
GPIO.pinMode(pinBellTaskSolved, 0) 
GPIO.pullUpDnControl(pinBellTaskSolved, 2) # TODO: remove for production
GPIO.pinMode(pinReset, 0)
GPIO.pullUpDnControl(pinReset, 2) # TODO: remove for production



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
        self.wiring_image = pygame.image.load('data/graphics/wiring_screen.jpg').convert()
        self.order_beer_image = pygame.image.load('data/graphics/order_beer_screen.jpg').convert()
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
        GameState.god_mode = False #GOD MODE SET IT HEREEEEEEEEEEEEEEEEEEEEEEEE

    def splash_screen(self): 
        global credits
        credits = 0
        #self.kill_all()           
        self.screen.blit(self.intro_screen, [0, 0])
        #self.screen.blit(self.intro_font.render("PIVADERS", 1, WHITE), (265, 120))
        #self.screen.blit(self.game_font.render("PRESS SPACE TO PLAY", 1, WHITE), (274, 191))
        self.screen.blit(self.game_font.render("INSERT "+str(3-credits)+" COINS TO PLAY", 1, WHITE), (274, 500))
        pygame.display.flip()
        #self.control()
        self.clock.tick(self.refresh_rate / 2)
        if credits >= 3:
            pygame.time.delay(2000)
            #self.start_game()
        pygame.time.delay(500)
        self.cheat_code_input_screen()

    def cheat_code_input_screen(self):
        digit_values=[0,0,0,0]
        selected_digit = 0
        code_entered = False

        while code_entered == False:
            self.joystick_digit_selector(digit_values, selected_digit)
                    
        raw_input("Press Enter when ready\n>")    

    def joystick_digit_selector(self, digit_values, selected_digit):
        self.screen.fill(BLACK)
        text = self.game_font.render("INSERT CHEAT CODE", 1, WHITE)
        self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 70))
        text = self.game_font.render("OK", 1, WHITE)
        self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 500))
    
        for i in range(0,4):
            digit_x = 80+(i*180)
            digit_y = 200
            digit_width = 100
            digit_height = 200
            
            if i==selected_digit:
                color = RED
            else:
                color = WHITE
            pygame.draw.rect(self.screen, color, pygame.Rect(digit_x, digit_y, digit_width, digit_height), 5) # remove last number to have filling inside instead of filling on the border
            pygame.draw.polygon(self.screen, color, [[digit_x, digit_y - 10], [digit_x+digit_width, digit_y - 10], [digit_x+(digit_width/2), digit_y-60]])
            pygame.draw.polygon(self.screen, color, [[digit_x, digit_y+digit_height + 10], [digit_x+digit_width, digit_y+digit_height + 10], [digit_x+(digit_width/2), digit_y+digit_height+60]])

            font = pygame.font.Font(None, 250)
            text = font.render(str(digit_values[i]), 1, WHITE)
            self.screen.blit(text, (digit_x+3, digit_y+10))
            pygame.display.flip()


    def main_loop(self):
        self.cheat_code_input_screen()


if __name__ == '__main__':
    pv = Game()
    pv.main_loop()
    

