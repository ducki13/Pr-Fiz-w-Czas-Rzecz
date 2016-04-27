#!/usr/bin/python
#-*- coding: utf-8 -*-

import pygame
import random

pygame.init()

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)


display_width = 1200
display_height = 700

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Gra w fizyke')

#clock: controls frames per second
clock = pygame.time.Clock()

#fps: frames per second
framesPerSecond = 30
#speed of replacement
change = 5


class SceneObject:

    def __init__(self, pict, width, height, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.pict = pygame.image.load(pict)
        self.width = width
        self.height = height
        self.ground = y
        self.old_x = x

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def is_within_me(self, x, y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def display(self):
        gameDisplay.blit(self.pict, (self.x, self.y))

    def print_position(self):
        print("x: " + str(self.x) + "  y: " + str(self.y))


class Rabbit(SceneObject):

    vx = 0.0
    vy = 0.0
    dt = 1.0/3
    a = 50.0
    g = 10.0
    mi = 5.0
    max_speed = 20.0
    k = 0.0005

    def set_x(self, x):
        self.old_x = self.x
        self.x = x
        if self.x < 0.0:
            self.x = 0.0
        elif self.x > display_width - self.width:
            self.x = display_width - self.width

    def set_y(self, y):
        self.y = y

    def revert_x(self):
        self.x = self.old_x

    def set_vx(self, vx):
        self.vx = vx

    def set_vy(self, vy):
        self.vy = vy

    def set_horizontal_speed(self, speed):
        self.set_vx(speed)
        if 0.0 < self.vx < 5.0:
            self.vx = 0.0
        elif -5.0 < self.vx < 0.0:
            self.vx = 0.0

    def set_vertical_speed(self, speed):
        self.set_vy(speed)

    def air_resistance(self):
        self.set_vx(self.vx - self.k * self.vx)
        self.set_x(self.x + self.vx * self.dt)

    def jump(self, check_constraints):
        self.set_vy(self.vy + self.g * self.dt)
        self.set_y(self.y + self.vy * self.dt)
        if check_constraints:
            if self.y > self.ground:
                self.y = self.ground

    def run_right(self):
        self.set_vx(self.vx + self.a * self.dt)
        self.set_x(self.x + self.vx * self.dt)
        self.vx = min(self.vx, self.max_speed)

    def run_right_in_air(self):
        self.air_resistance()

    def decrease_speed_right(self):
        self.set_vx(self.vx - self.mi * self.g * self.dt)
        self.set_x(self.x + self.vx * self.dt)
        if self.vx < 5.0:
            self.vx = 0.0

    def run_left(self):
        self.set_vx(self.vx - self.a * self.dt)
        self.set_x(self.x + self.vx * self.dt)
        self.vx = max(self.vx, -self.max_speed)

    def run_left_in_air(self):
        self.air_resistance()

    def decrease_speed_left(self):
        self.set_vx(self.vx + self.mi * self.g * self.dt)
        self.set_x(self.x + self.vx * self.dt)
        if -5.0 < self.vx:
            self.vx = 0.0

    def is_on_ground(self):
        return abs(self.y - self.ground) <= 2.0

    def is_in_hole(self, hole):
        return self.is_on_ground() and (hole.x <= self.x <= hole.x + hole.width
                                        or hole.x <= self.x + self.width <= hole.x + hole.width)

    def fall_into_hole(self):
        self.jump(False)

    def collide_with_side_of(self, obj):
        return (obj.x <= self.x <= obj.x + obj.width or obj.x <= self.x + self.width <= obj.x + obj.width)\
            and self.y + self.height > obj.y

    def is_on(self, obj):
        return (obj.x <= self.x <= obj.x + obj.width or obj.x <= self.x + self.width <= obj.x + obj.width)\
            and self.y + self.height <= obj.y


class Scene(SceneObject):

    def is_visible(self, obj):
        return self.is_within_me(obj.x, obj.y)

    #displays all objects on the scene
    def draw(self, objects):
        gameDisplay.fill(white) #paint background in white

        for obj in objects:
            obj.display()

        pygame.display.update()


def text_objects(text, font, color = black):
    u"""Zwraca powierzchnie z napisanym na niej tekstem
    oraz prostokąt w którym zawiera się tekst.
    Jeśli nie wybierzemy koloru tekstu, to będzie czarny."""
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()


def message_display(text):
    u"""Wyświetla zadany tekst na ekranie."""
    largeText = pygame.font.Font('freesansbold.ttf', 115)
    # Dość skoplikowany sposób by wybrać czcionkę 'freesansbold.ttf'
    # o rozmiarze 115.
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((display_width / 2.0), (display_height / 2.0))
    # Centrujemy tekst.
    gameDisplay.blit(TextSurf, TextRect)
    # Zobacz linia 343.

    pygame.display.update()


def crash():
    message_display('Game Over')


def game_loop():

    #objects
    rabbit = Rabbit('krolikmaly.jpg', 79.0, 88.0, display_width * 0.45, display_height * 0.7)
    scene = Scene('Tlo.png', display_width, display_height, 0.0, 0.0)
    hole = SceneObject('Dziura.jpg', 90.0, 96.0, display_width * 0.65, display_height * 0.8)
    platform = SceneObject('Platforma.jpg', 140.0, 96.0, display_width * 0.15, display_height * 0.695)

    is_down_left = False
    is_down_right = False

    play_game = True
    while play_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play_game = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if rabbit.is_on_ground():
                        rabbit.set_horizontal_speed(0.0)
                        is_down_left = True
                        rabbit.run_left()

                if event.key == pygame.K_RIGHT:
                    if rabbit.is_on_ground():
                        rabbit.set_horizontal_speed(0.0)
                        is_down_right = True
                        rabbit.run_right()

                if event.key == pygame.K_UP:
                    if rabbit.is_on_ground():
                        rabbit.set_vertical_speed(-50.0)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    is_down_left = False
                if event.key == pygame.K_RIGHT:
                    is_down_right = False

        rabbit.jump(True)

        #move right
        if is_down_right and rabbit.vx >= 0.0 and rabbit.is_on_ground():
            rabbit.run_right()

        #move left
        if is_down_left and rabbit.vx <= 0.0 and rabbit.is_on_ground():
            rabbit.run_left()

        #stop right
        if not is_down_right and rabbit.vx > 0.0 and rabbit.is_on_ground():
            rabbit.decrease_speed_right()

        #move right in the air
        if not rabbit.is_on_ground() and rabbit.vx > 0.0:
            rabbit.run_right_in_air()

        #stop left
        if not is_down_left and rabbit.vx < 0.0 and rabbit.is_on_ground():
            rabbit.decrease_speed_left()

        #move left in the air
        if not rabbit.is_on_ground() and rabbit.vx < 0.0:
            rabbit.run_left_in_air()

        if rabbit.is_on(platform):
            print("Wygrales!")
            play_game = False

        if rabbit.collide_with_side_of(platform):
            rabbit.set_vx(0.0)
            rabbit.revert_x()

        scene.draw([scene, hole, platform, rabbit])

        if rabbit.is_in_hole(hole):
            rabbit.set_horizontal_speed(0.0)
            rabbit.set_vertical_speed(0.0)
            while rabbit.x + rabbit.width/2.0 < hole.x + hole.width/2.0:
                rabbit.run_right()
            while rabbit.x + rabbit.width/2.0 > hole.x + hole.width/2.0:
                rabbit.run_left()
            while scene.is_visible(rabbit):
                rabbit.fall_into_hole()
                scene.draw([scene, hole, platform, rabbit])
            crash()
            play_game = False

        #count of frames per second
        clock.tick(framesPerSecond)

Game = True

while Game:
    game_loop()
    Game = False
    answer = raw_input('Do you want play again? ')
    
    if answer == 'y':
        Game = True
    
pygame.quit()
quit()
