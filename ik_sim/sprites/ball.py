import pygame
import utils

class Ball(pygame.sprite.Sprite):
    def __init__(self, screen, start_pos, floor_height):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.pos = start_pos
        self.floor_height = floor_height
        self.vel = [0, 0]
        self.acel = [0.0, 6.7]

    def update(self, dt, holding_ball, robot):
        if not holding_ball:
            self.acel = [0.0, 6.7]
            #use acel to update vel
            self.vel = [self.vel[0] + self.acel[0] * dt, 
                        self.vel[1] + self.acel[1] * dt]

            #use vel to update pos
            self.pos = [self.pos[0] + self.vel[0] * dt, 
                        self.pos[1] + self.vel[1] * dt]
        else:
            self.acel = [0.0, 0.0]
            self.vel = [0.0, 0.0]
            self.pos = [robot.tip[0], robot.tip[1]]

        if self.pos[0] + utils.BALL_RADIUS >= self.screen.get_width() or self.pos[0] <= 0:
            self.vel[0] *= -0.85

        if self.pos[1] + utils.BALL_RADIUS >= self.floor_height or self.pos[1] <= 0:
            self.vel[1] *= -0.85

        self.draw()

    def draw(self):
        pygame.draw.circle(self.screen, utils.BALL_COLOR, self.pos, utils.BALL_RADIUS)