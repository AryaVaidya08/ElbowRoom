import math
import pygame
import utils

GOAL_COLOR = (0, 255, 0, 60)   # semi-transparent green (alpha 0-255)
WALL_COLOR = (200, 200, 200)
BOX_SIZE = 50
WALL_THICKNESS = 5
ZONE_HEIGHT = 25               # height of the green strip at the bottom
RESTITUTION = 0.85             # same bounce as the screen edges

class Goal(pygame.sprite.Sprite):
    def __init__(self, screen, top_left):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.top_left = top_left
        x, y = top_left
        t = WALL_THICKNESS

        # Walls (open top, so no top wall)
        self.left_wall = pygame.Rect(x, y, t, BOX_SIZE)
        self.right_wall = pygame.Rect(x + BOX_SIZE - t, y, t, BOX_SIZE)
        self.bottom_wall = pygame.Rect(x, y + BOX_SIZE - t, BOX_SIZE, t)
        self.walls = [self.left_wall, self.right_wall, self.bottom_wall]

        # Green zone: a strip resting on top of the bottom wall
        self.rectBox = pygame.Rect(
            x + t,
            y + BOX_SIZE - t - ZONE_HEIGHT,
            BOX_SIZE - 2 * t,
            ZONE_HEIGHT,
        )

        # Transparent surface for the zone, created once
        self.zone_surface = pygame.Surface(self.rectBox.size, pygame.SRCALPHA)
        self.zone_surface.fill(GOAL_COLOR)

        self.update()

    def update(self):
        # Zone first, walls on top
        self.screen.blit(self.zone_surface, self.rectBox.topleft)
        for wall in self.walls:
            pygame.draw.rect(self.screen, WALL_COLOR, wall)

    def collide_ball(self, ball):
        """Bounce the ball off the box walls (circle vs rect)."""
        r = utils.BALL_RADIUS
        for wall in self.walls:
            cx = max(wall.left, min(ball.pos[0], wall.right))
            cy = max(wall.top, min(ball.pos[1], wall.bottom))
            dx, dy = ball.pos[0] - cx, ball.pos[1] - cy
            dist = math.hypot(dx, dy)
            if dist >= r:
                continue

            # ball centre inside the wall: push out along the shallowest side
            if dist < 1e-9:
                gaps = {(-1, 0): ball.pos[0] - wall.left, (1, 0): wall.right - ball.pos[0],
                        (0, -1): ball.pos[1] - wall.top, (0, 1): wall.bottom - ball.pos[1]}
                (nx, ny), gap = min(gaps.items(), key=lambda kv: kv[1])
                ball.pos = [ball.pos[0] + nx * (gap + r), ball.pos[1] + ny * (gap + r)]
            else:
                nx, ny = dx / dist, dy / dist
                ball.pos = [cx + nx * r, cy + ny * r]

            vn = ball.vel[0] * nx + ball.vel[1] * ny
            if vn < 0:
                ball.vel = [ball.vel[0] - (1 + RESTITUTION) * vn * nx,
                            ball.vel[1] - (1 + RESTITUTION) * vn * ny]

    def hits_wall(self, pos):
        """True if a ball centred at pos would overlap any box wall."""
        r = utils.BALL_RADIUS
        for wall in self.walls:
            cx = max(wall.left, min(pos[0], wall.right))
            cy = max(wall.top, min(pos[1], wall.bottom))
            if math.hypot(pos[0] - cx, pos[1] - cy) < r:
                return True
        return False

    def scored(self, ball):
        """True once the ball's centre is inside the green zone."""
        return self.rectBox.collidepoint(ball.pos)

    def contains(self, pos):
        """True if pos is on a wall or in the green zone."""
        return self.rectBox.collidepoint(pos) or any(w.collidepoint(pos) for w in self.walls)
