import math
import pygame
from sprites import robot, ball, goal
from sprites.robot import JOINT_RADIUS
import utils
import random

TOP_Y, BOTTOM_Y = 180, 310
TOP_LEFT_X, TOP_RIGHT_X = 15, 435
BOTTOM_LEFT_X, BOTTOM_RIGHT_X = 0, 450
EXCLUDE_X_MIN, EXCLUDE_X_MAX = 165, 275

def random_goal():
    while True:
        y = random.uniform(TOP_Y, BOTTOM_Y)
        x = random.uniform(BOTTOM_LEFT_X, BOTTOM_RIGHT_X)

        # Skip the excluded vertical band
        if EXCLUDE_X_MIN <= x <= EXCLUDE_X_MAX:
            continue

        # Check against the slanted sides
        t = (y - TOP_Y) / (BOTTOM_Y - TOP_Y)
        left = TOP_LEFT_X + t * (BOTTOM_LEFT_X - TOP_LEFT_X)
        right = TOP_RIGHT_X + t * (BOTTOM_RIGHT_X - TOP_RIGHT_X)

        if left <= x <= right:
            return int(x), int(y)

FLOOR_COLOR = (200, 200, 200)
FLOOR = pygame.Rect((0, utils.HEIGHT - utils.FLOOR_HEIGHT), (utils.WIDTH, utils.FLOOR_HEIGHT))

def draw_background():
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, FLOOR_COLOR, FLOOR)

def setup_screen():
    screen = pygame.display.set_mode((utils.WIDTH, utils.HEIGHT))
    pygame.display.set_caption("Elbow Room")

    font = pygame.font.Font("freesansbold.ttf", 24)

    return screen, font

pygame.init()
screen, font = setup_screen()
sim_clock = pygame.time.Clock()

target = [344, 225]
elbow_sign = -1
robot = robot.Robot(target, elbow_sign)

start_pos = [470, 225]
ball = ball.Ball(screen, start_pos, utils.HEIGHT - utils.FLOOR_HEIGHT)

top_left = random_goal()
goal = goal.Goal(screen, top_left)

running = True
holding_ball = False
while running:
    dt = sim_clock.tick(60) / 1000

    for event in pygame.event.get():
        
        if event.type == pygame.KEYDOWN:
            if event.key == 113: #Ctrl + q stops the program
                running = False
            elif event.key == 13 and math.dist(tip, ball.pos) <= JOINT_RADIUS + utils.BALL_RADIUS:
                holding_ball = not holding_ball

        #Jump Controls
        if event.type == pygame.MOUSEBUTTONDOWN and not goal.contains(event.pos):
            print(event)
            target = [event.pos[0], event.pos[1]]

    target = [max(0, min(target[0], utils.WIDTH)), max(0, min(target[1], utils.HEIGHT - utils.FLOOR_HEIGHT))]
    draw_background()
    old_pose = (robot.alpha, robot.beta)
    robot.update(target, dt)
    if holding_ball:
        # a held ball can't be pushed through the box walls: freeze the arm instead
        new_elbow = robot.calculate_elbow_pos(robot.alpha)
        new_tip = robot.calculate_tip_pos(new_elbow, robot.alpha, robot.beta)
        if goal.hits_wall(new_tip):
            robot.alpha, robot.beta = old_pose
    robot.draw(screen)
    ball.update(dt, holding_ball, robot)
    if not holding_ball:
        goal.collide_ball(ball)
    goal.update()

    if goal.scored(ball):
        win_text = font.render("Goal!", True, (255, 255, 255))
        screen.blit(win_text, win_text.get_rect(center=(utils.WIDTH // 2, 30)))
        pygame.display.flip()
        pygame.time.wait(1500)
        running = False

    elbow = robot.calculate_elbow_pos(robot.alpha)
    tip = robot.calculate_tip_pos(elbow, robot.alpha, robot.beta)

    pos_text = font.render(str(target), True, (255, 255, 255))
    textRect = pos_text.get_rect()
    textRect.center = (50, utils.WIDTH - 80)
    screen.blit(pos_text, pos_text.get_rect())

    pygame.display.flip() 