#!/usr/bin/env python3

import pygame
import datetime
import math
import random


class Tank(pygame.sprite.Sprite):
    def __init__(self, position, turret_direction):
        super().__init__()
        self.position = position
        self.turret_direction = turret_direction
        self.image = pygame.transform.scale(TANK_BODY, (50, 40)).convert_alpha()
        self.rect = self.image.get_rect()
        self.hit_at = None

        self.last_update = datetime.datetime.now()

    def update(self):
        now = datetime.datetime.now()
        self.rect.center = self.position

        self.consider_removing()

    def was_hit_by(self, missile, player_list):
        self.image = pygame.transform.scale(TANK_FLAMES, (50, 40)).convert_alpha()

        if not self.hit_at:
            self.hit_at = datetime.datetime.now()
            return  True

        return False

    def consider_removing(self):
        dying = False
        if self.hit_at is not None and datetime.datetime.now() > (self.hit_at + datetime.timedelta(seconds=2)):
            dying = True

        if dying:
            self.kill()

        return dying

class Missile(pygame.sprite.Sprite):
    def __init__(self, position, direction, speed):
        super().__init__()

        self.birthday = datetime.datetime.now()

        pygame.mixer.Sound.play(LAUNCH)

        self.direction = ((direction/10.0) + math.pi) * -1
        self.position = \
                position[0] + (math.sin(self.direction) * 1), \
                position[1] + (math.cos(self.direction) * 1)

        self.speed = speed / 5.0
        self.gravity_pulled = 0

        self.image = MISSILE
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position

        self.last_update = datetime.datetime.now()

    def update(self):
        self.gravity_pulled += 0.007
        now = datetime.datetime.now()
        diff = now - self.last_update
        step = diff.microseconds / 5000.0

        self.position = \
            self.position[0] + (math.sin(self.direction) * self.speed*0.3*step), \
            self.position[1] + (math.cos(self.direction) * self.speed*0.3*step) + self.gravity_pulled

        self.rect.center = tuple(int(n) for n in self.position)
        self.last_update = now

    def has_hit(self, player, missile_list):
        pygame.mixer.Sound.play(EXPLOSION)
        self.kill()

    def consider_removing(self, wh: pygame.SurfaceType):
        dying = False
        if not -100 < self.position[0] < (wh[0]+100):
            dying = True
        if not -10000 < self.position[1] < (wh[1]+100):
            dying = True

        if dying:
            self.kill()

        return dying

def update_text(font, inventory, speed, direction, score, color):
    surface = font.render("[{:>30}]   speed:{:3}  angle:{:3}  score: {}".format("<"*min(inventory, 30), speed, direction/10.0, score), True, color)
    rect = surface.get_rect()
    rect.topleft = (20, 20)
    return surface, rect

def main():
    pygame.key.set_repeat(1, 100)

    last_missile_addition = datetime.datetime.now()
    missile_addition_frequency = datetime.timedelta(milliseconds=2700)
    missile_max = 30

    screen = pygame.display.set_mode((1200, 800))
    running = True
    playing = True

    speed = 50
    direction = 450
    old_speed, old_direction = -1, -1

    player_list = pygame.sprite.Group()
    self_player = Tank((100, 500), 0)
    player_list.add(self_player)
    for _ in range(10):
        player_list.add(Tank((random.randint(50, 1150), random.randint(50, 750)), 0))

    missile_list = pygame.sprite.Group()

    clock = pygame.time.Clock()

    score = 0
    inventory = 10

    status_font = pygame.font.SysFont('dejavusansmono', 24)
    status_text = update_text(status_font, inventory, speed, direction, score, PLAYING_COLOR)

    while running:
        text_dirty = False
        if speed != old_speed or direction != old_direction:
            old_speed, old_direction = speed, direction
            text_dirty = True

        if datetime.datetime.now() > last_missile_addition + missile_addition_frequency:
            if inventory < missile_max:
                last_missile_addition = datetime.datetime.now()
                inventory += 1
                text_dirty = True

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                print(event.button)

            if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            else:
                if playing:
                    if event.type == pygame.MOUSEMOTION:
                        pass
                    elif (event.type == pygame.KEYUP and event.key == pygame.K_SPACE) or (event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT):
                        if inventory > 0:
                            missile_list.add(Missile((110, 490), math.radians(direction), speed))
                            inventory -= 1
                            text_dirty = True
                    elif (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) or (event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_WHEELDOWN):
                        if speed < 80:
                            speed += 1
                            text_dirty = True
                    elif (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN) or (event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_WHEELUP):
                        if speed > 30:
                            speed -= 1
                            text_dirty = True
                    elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT) or (event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_X2):
                        direction = (direction + 3600 - 3) % 3600
                        if direction < -900:
                            direction = -900
                        text_dirty = True
                    elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) or (event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_X1):
                        direction = (direction + 3600 + 3) % 3600
                        if direction > 900:
                            direction = 900
                        text_dirty = True

        missles_old_enough = datetime.datetime.now() - datetime.timedelta(milliseconds=80)
        for missile in missile_list.sprites():
            if missile.birthday > missles_old_enough:
                continue
            if missile.consider_removing(screen.get_size()):
                continue
            for player in pygame.sprite.spritecollide(missile, player_list, False):
                missile.has_hit(player, missile_list)
                if player.was_hit_by(missile, player_list):
                    if player == self_player:
                        playing = False
                    else:
                        score += 1
                    text_dirty = True

        if text_dirty:
            status_text = update_text(status_font, inventory, speed, direction, score, PLAYING_COLOR if playing else GAME_OVER_COLOR)

        screen.fill((102, 178, 255))
        screen.blit(*status_text)

        missile_list.update()
        player_list.update()
        missile_list.draw(screen)
        player_list.draw(screen)

        clock.tick(180)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":

    pygame.init()
    TANK_BODY = pygame.image.load("resources/tank_body_drawing.png")
    TANK_BODY.set_colorkey((255, 0, 0))
    TANK_FLAMES = pygame.image.load("resources/tank_fire_drawing.png")
    TANK_FLAMES.blit(TANK_BODY, (0, 0))
    MISSILE = pygame.image.load("resources/dot.png")
    LAUNCH = pygame.mixer.Sound("resources/launch.wav")
    EXPLOSION = pygame.mixer.Sound("resources/explosion.wav")

    PLAYING_COLOR = (255, 255, 255)
    GAME_OVER_COLOR = (255, 96, 96)

    main()
