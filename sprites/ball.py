import pygame

BALL_COLOR = (255, 255, 0)
BALL_RADIUS = 10

class Ball(pygame.sprite.Sprite):
    def __init__(self, screen, start_pos):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.pos = start_pos
        self.vel = [0, 0]
        self.acel = [0, 6.7]

    def update(self, dt):
        #use acel to update vel
        self.vel = [self.vel[0] + self.acel[0] * dt, 
                    self.vel[1] + self.acel[1] * dt]

        #use vel to update pos
        self.pos = [self.pos[0] + self.vel[0] * dt, 
                    self.pos[1] + self.vel[1] * dt]

        if self.pos[0] + BALL_RADIUS >= self.screen.get_width() or self.pos[0] <= 0:
            self.vel[0] *= -0.5

        if self.pos[1] + BALL_RADIUS >= self.screen.get_height() or self.pos[1] <= 0:
            self.vel[1] *= -0.5

        print(f"[{str(round(self.pos[0], 3)).zfill(7)}, {str(round(self.pos[1], 3)).zfill(7)}] | [{str(round(self.vel[0], 3)).zfill(7)}, {str(round(self.vel[1], 3)).zfill(7)}]")

        self.draw()

    def draw(self):
        pygame.draw.circle(self.screen, BALL_COLOR, self.pos, BALL_RADIUS)