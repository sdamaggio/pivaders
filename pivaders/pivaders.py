#!/usr/bin/env python2

# TODO:
# reset
# change spaceship color when god mode is on
# and add volume to sound

# to disable screen-sleep run this command:
# setterm -powersave off -blank 0

# // Pin modes pinMode()
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
# // Pull up/down/none pullUpDnControl()
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
#
#
#
#
# in order to run this script at startup with root privileges:
# -add a line in sudo nano /etc/rc.local: sudo python /home/pi/.../script.py &
# -sudo chown root script.sh
# -sudo chmod +s script.sh
#



import pygame, random, time
import os, sys, signal

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

credits = 3
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
pinFirstGameLost = 5 # LOW is solved!
pinSpaceInvadersSolved = 7 # LOW is solved!
pinBellTaskSolved = 11 # LOW is solved!
pinInfinityMirrorOn = 15 # LOW is solved!
pinReset = 13 #wire it with level converter

#GPIO pin setup
GPIO.pinMode(pinUp, 0) # 
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
wiringpi.add_event_detect(pinCoinCounter, wiringpi.FALLING, callback=coin_counted_event, bouncetime=800) # old value was 300

GPIO.pinMode(pinLedStripRed, 1)
GPIO.digitalWrite(pinLedStripRed, 0)
GPIO.pinMode(pinLedStripGreen, 1)
GPIO.digitalWrite(pinLedStripGreen, 0)
GPIO.pinMode(pinLedStripBlue, 1)
GPIO.digitalWrite(pinLedStripBlue, 0)

GPIO.pinMode(pinFan, 1)
GPIO.digitalWrite(pinFan, 1)

GPIO.pinMode(pinWiringTaskSolved, 1)
GPIO.digitalWrite(pinWiringTaskSolved, 1)
GPIO.pinMode(pinFirstGameLost, 1)
GPIO.digitalWrite(pinFirstGameLost, 1)
GPIO.pinMode(pinSpaceInvadersSolved, 1)
GPIO.digitalWrite(pinSpaceInvadersSolved, 1)
GPIO.pinMode(pinBellTaskSolved, 0) 
GPIO.pinMode(pinInfinityMirrorOn, 0)
GPIO.pinMode(pinReset, 0)
print("pivaders: pin initialization complete!")


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)



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
            self.speed = 150
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
        
        self.game_font = pygame.font.Font('/home/pi/DEV/pivaders/pivaders/data/Orbitracer.ttf', 28)
        self.game_font_medium = pygame.font.Font('/home/pi/DEV/pivaders/pivaders/data/Orbitracer.ttf', 48)
        self.intro_font = pygame.font.Font('/home/pi/DEV/pivaders/pivaders/data/Orbitracer.ttf', 72)
        
        self.screen = pygame.display.set_mode([RES[0], RES[1]], pygame.FULLSCREEN)
        
        self.time = pygame.time.get_ticks()
        self.refresh_rate = 20
        self.rounds_won = 0
        self.level_up = 50
        self.score = 0
        self.lives = 10
        
        self.player_group = pygame.sprite.Group()
        self.alien_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.missile_group = pygame.sprite.Group()
        self.barrier_group = pygame.sprite.Group()
        self.all_sprite_list = pygame.sprite.Group()
        
        #load images and sounds
        self.sys_overheat0 = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/system_overheating_0.png').convert_alpha()
        self.sys_overheat1 = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/system_overheating_1.png').convert_alpha()
        self.wiring_image = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/wiring_screen.png').convert_alpha()
        self.not_cool_enough_image = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/not_cool_enough.png').convert_alpha()
        self.morse_code = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/morse_code.png').convert_alpha()
        self.intro_screen = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/start_screen.jpg').convert()
        self.background = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/Space-Background.jpg').convert()
        pygame.display.set_caption('Pivaders - ESC to exit')
        pygame.mouse.set_visible(False)
        Alien.image = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/Spaceship16.png').convert_alpha() #was without _alpha
        Alien.image.set_colorkey(WHITE)        
        Player.image = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/ship_sheet_final.png').convert_alpha()
        self.animate_right = False
        self.animate_left = False
        self.explosion_sheet = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/explosion_new1.png').convert_alpha()
        self.explosion_image = self.explosion_sheet.subsurface(0, 0, 79, 96)
        self.alien_explosion_sheet = pygame.image.load('/home/pi/DEV/pivaders/pivaders/data/graphics/alien_explosion.png')
        self.alien_explode_graphics = self.alien_explosion_sheet.subsurface(0, 0, 94, 96)
        self.explode = False
        self.explode_pos = 0
        self.alien_explode = False
        self.alien_explode_pos = 0
        pygame.mixer.music.load('/home/pi/DEV/pivaders/pivaders/data/sound/10_Arpanauts.ogg')
        pygame.mixer.music.set_volume(0.7)
        self.bullet_fx = pygame.mixer.Sound('/home/pi/DEV/pivaders/pivaders/data/sound/shoot.wav')
        self.explosion_fx = pygame.mixer.Sound('/home/pi/DEV/pivaders/pivaders/data/sound/invaderkilled.wav')
        self.explosion_fx.set_volume(0.5)
        self.explodey_alien = []
        
        # initialize GameState vars
        GameState.end_game = False
        GameState.start_screen = True
        GameState.vector = 0
        GameState.shoot_bullet = False
        GameState.god_mode = False 
        GameState.has_played_once = False

    def control(self):
        if GPIO.digitalRead(pinReset) == 0:
            print("about to exit")
            os.system("sleep 10 && sudo python /home/pi/DEV/pivaders/pivaders/pivaders.py &")
            print("reboot sequence executed! good bye")
            #self.kill_all()
            sys.exit(0)
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
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_LEFT] or GPIO.digitalRead(pinLeft) == 0:
            self.animate_left = True
            self.animate_right = False
            if GameState.god_mode == False:
                GameState.vector = -1
            else:
                GameState.vector = -2                    
        elif self.keys[pygame.K_RIGHT] or GPIO.digitalRead(pinRight) == 0:
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
        if self.keys[pygame.K_SPACE]: 
            if GameState.start_screen:
                start_game()
        if GameState.start_screen == False and (GPIO.digitalRead(pinShoot) == 0 or GPIO.digitalRead(pinUp) == 0):
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

    def is_wiring_solved(self):
        # activate each plug one at a time and check if the corresponding input is triggered accordingly
        wiring_solved = True
        GPIO.digitalWrite(pinWiringPlugA, 1)
        if GPIO.digitalRead(pinWiringRed) == 0:
            wiring_solved = False
        GPIO.digitalWrite(pinWiringPlugA, 0)
        GPIO.digitalWrite(pinWiringPlugB, 1)
        if GPIO.digitalRead(pinWiringGreen) == 0:
            wiring_solved = False
        GPIO.digitalWrite(pinWiringPlugB, 0)
        GPIO.digitalWrite(pinWiringPlugC, 1)
        if GPIO.digitalRead(pinWiringBlue) == 0:
            wiring_solved = False
        GPIO.digitalWrite(pinWiringPlugC, 0)
        GPIO.digitalWrite(pinWiringPlugD, 1)
        if GPIO.digitalRead(pinWiringYellow) == 0:
            wiring_solved = False
        GPIO.digitalWrite(pinWiringPlugD, 0)
        return wiring_solved

    def splash_screen(self): 
        while GameState.start_screen:
            self.kill_all()           
            self.screen.blit(self.intro_screen, [0, 0])
            #self.screen.blit(self.intro_font.render("PIVADERS", 1, WHITE), (265, 120))
            #self.screen.blit(self.game_font.render("PRESS SPACE TO PLAY", 1, WHITE), (274, 191))
            font = pygame.font.Font('/home/pi/DEV/pivaders/pivaders/data/Orbitracer.ttf', 26)
            
            if GameState.has_played_once == False:
                if credits >= 3:
                    self.screen.blit(self.game_font.render("PRESS STRIKE! TO START", 1, WHITE), (274, 500))
                    if GPIO.digitalRead(pinShoot) == 0:
                        self.start_game()
                else:
                    self.screen.blit(self.game_font.render("INSERT "+str(3-credits)+" COINS TO PLAY", 1, WHITE), (274, 500))

            elif GameState.has_played_once == True and GPIO.digitalRead(pinInfinityMirrorOn) == 0:
                text = font.render("press Ready and Strike to enter a cheat code", 1, WHITE)
                self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 20))
                if GPIO.digitalRead(pinReady) == 0 and GPIO.digitalRead(pinShoot) == 0:
                    self.cheat_code_input_screen()           

            if GameState.god_mode == True:
                self.screen.blit(self.game_font.render("PRESS STRIKE! TO START", 1, WHITE), (274, 500))
                if GPIO.digitalRead(pinShoot) == 0:
                    self.start_game()

            pygame.display.flip()
            self.control()
            self.clock.tick(self.refresh_rate / 2)

    def overheat_screen(self):
        while GPIO.digitalRead(pinWiringDoorOcto) == 0: #while wiring lid is closed show the screen
            self.screen.blit(self.sys_overheat0, [0, 0])
            pygame.display.flip()
            pygame.time.delay(1000)
            self.screen.blit(self.sys_overheat1, [0, 0])
            pygame.display.flip()
            pygame.time.delay(1000)
            self.control()

    def wiring_screen(self):
        global credits
        credits = 0 #reset coin count, from now on any inserted coin will be counted
        while self.is_wiring_solved() == False:       # while wiring is not solved, show the screen
            self.screen.blit(self.wiring_image, [0, 0])
            pygame.display.flip()
            pygame.time.delay(200)
            self.control()
        GPIO.digitalWrite(pinWiringTaskSolved, 0)
        GPIO.digitalWrite(pinFan, 0)        

    def order_beer_screen(self): # screen for bell bar task
        while GPIO.digitalRead(pinShoot) == 1 and GPIO.digitalRead(pinReady) == 1:                
            self.screen.blit(self.not_cool_enough_image, [0, 0])
            pygame.display.flip()
            pygame.time.delay(200)
            self.control()

        while GPIO.digitalRead(pinBellTaskSolved) == 1: # while beer is not ordered, show the screen
            self.screen.blit(self.morse_code, [0, 0])
            pygame.display.flip()
            pygame.time.delay(200)
            self.control()

        # when bell task is solved play backgroun music
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.7)

    def cheat_code_input_screen(self):
        digit_values=[0,0,0,0]
        digit_solution=[1,3,8,0]
        selected_digit = 0
        code_entered = False

        while code_entered == False:
            if GPIO.digitalRead(pinRight) == 0 and selected_digit < 4:
                    selected_digit += 1
            elif GPIO.digitalRead(pinLeft) == 0 and selected_digit > 0:
                selected_digit += -1
            elif selected_digit == 4:
                if GPIO.digitalRead(pinShoot) == 0:
                    code_entered = True
            elif GPIO.digitalRead(pinUp) == 0 and digit_values[selected_digit] < 9:
                digit_values[selected_digit] += 1
            elif GPIO.digitalRead(pinDown) == 0 and digit_values[selected_digit] > 0:
                digit_values[selected_digit] += -1                            
            self.draw_joystick_digit_selector(digit_values, selected_digit)
            pygame.time.delay(100)

        if digit_values == digit_solution:            
            for i in range(0,5):
                # delete bottom part of the screen
                pygame.draw.rect(self.screen, BLACK, pygame.Rect(0, 470, 2000, 2000))
                pygame.display.flip()
                pygame.time.delay(200)

                font = pygame.font.Font('/home/pi/DEV/pivaders/pivaders/data/Orbitracer.ttf', 60)
                text = font.render("GOD MODE ACTIVATED!", 1, YELLOW)
                self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 500))
                pygame.display.flip()
                pygame.time.delay(600)

            GameState.god_mode = True            
            
        else:
            for i in range(0,2):
                # delete central part of the screen
                pygame.draw.rect(self.screen, BLACK, pygame.Rect(0, 470, 2000, 2000))
                pygame.display.flip()
                pygame.time.delay(200)

                font = pygame.font.Font('/home/pi/DEV/pivaders/pivaders/data/Orbitracer.ttf', 48)
                text = font.render("INVALID CODE", 1, YELLOW)
                self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 500))
                pygame.display.flip()
                pygame.time.delay(1000)

    def draw_joystick_digit_selector(self, digit_values, selected_digit):
        self.screen.fill(BLACK)
        text = self.game_font.render("INSERT CHEAT CODE", 1, WHITE)
        self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 70))
            
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

            font = pygame.font.Font(None, 54)
            if selected_digit == 4:                
                text = font.render("OK", 1, RED)
            else:
                text = font.render("OK", 1, WHITE)
            self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 500))

            font = pygame.font.Font(None, 250)
            text = font.render(str(digit_values[i]), 1, WHITE)
            self.screen.blit(text, (digit_x+3, digit_y+10))
        pygame.display.flip()

    def portal_screen(self):
        self.screen.blit(self.sys_overheat0, [0, 0])
        pygame.display.flip()
        pygame.time.delay(1000)
        self.screen.blit(self.sys_overheat1, [0, 0])
        pygame.display.flip()
        pygame.time.delay(1000)

        self.screen.fill(BLACK)
        font = pygame.font.Font('/home/pi/DEV/pivaders/pivaders/data/Orbitracer.ttf', 48)
        text = font.render("You think you won the battle??", 1, WHITE)
        self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 200))

        text = font.render("Enter the portal and meet us face to face!!", 1, WHITE)
        self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 300))

        pygame.display.flip()
        while True:
            self.control()

    def start_game(self):        
        GameState.start_screen = False
        if GameState.god_mode:
            self.lives = 98
        else:
            self.lives = 10
        self.score = 0
        self.make_player()
        self.make_defenses()
        self.alien_wave(0)

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
        # self.screen.blit(self.game_font.render("CREDITS " + str(credits), 1, WHITE), (680, 8)) TODO: fix credits display or remove

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
            GPIO.digitalWrite(pinFirstGameLost, 0);
            self.rounds_won = 0
            self.refresh_screen()
            self.level_up = 50
            self.explode = False
            self.alien_explode = False

            self.screen.fill(BLACK)
            pygame.draw.rect(self.screen, RED, pygame.Rect(170, 210, self.screen.get_width()-(2*170), self.screen.get_height()-(2*210)), 10)
            text=self.game_font_medium.render("The war is lost!", 1, RED)
            self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 240))

            text=self.game_font_medium.render("You scored: " + str(self.score), 1, RED)
            self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 320))

            pygame.display.update(160, 200, self.screen.get_width()-(2*160), self.screen.get_height()-(2*200))
            pygame.time.delay(10000)
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
            #self.rounds_won += 1         
            GPIO.digitalWrite(pinSpaceInvadersSolved, 0)   
            font = pygame.font.Font('/home/pi/DEV/pivaders/pivaders/data/Orbitracer.ttf', 60)
            text = font.render("YOU WON!! Your score is " + str(self.score), 1, BLUE)
            self.screen.blit(text, (text.get_rect(centerx=self.screen.get_width()/2).x, 250))
            # self.screen.blit(self.game_font.render("YOU WON!! Your score is " + str(self.score) , 1, RED), (200, 15))
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
        self.overheat_screen()
        self.wiring_screen()        
        self.order_beer_screen()
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
                    GameState.has_played_once = True
                for actor in [self.player_group, self.bullet_group, self.alien_group, self.missile_group]:
                    for i in actor:
                        i.update()
                if GameState.shoot_bullet:
                    self.make_bullet()
                if self.win_round() and GameState.god_mode==True:
                    self.portal_screen()
            self.splash_screen()
        pygame.quit()

if __name__ == '__main__':
    pv = Game()
    pv.main_loop()
    


# COIN TEST CODE, WORKING WITH MANUAL CONTACT BUT NOT COIN ACCEPTER
#
#import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(31, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#
#def printFunction(channel):
#    print("Button 1 pressed!")
#
#GPIO.add_event_detect(31, GPIO.BOTH, callback=printFunction, bouncetime=300)
#
#
#while True:
#    if 0==1:
#        print("sbagliato")    
#
#GPIO.cleanup()
#print("closing")
#
