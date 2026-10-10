import pygame
import math
import random

WIDTH = 600
HEIGHT = 450
FLOOR_HEIGHT = 100

FLOOR_COLOR = (200, 200, 200)

SEG1_COLOR1 = (255, 0, 0)
SEG2_COLOR1 = (0, 255, 0)


JOINT_COLOR = (50, 50, 50)
TARGET_COLOR = (0, 0, 255)

SEG_THICKNESS = 6
JOINT_RADIUS = 10

ARM_START = (WIDTH / 2, HEIGHT - FLOOR_HEIGHT)
SEG1_LEN = 200.0
SEG2_LEN = 75.0

ROBOT_BASE = pygame.Rect((ARM_START[0] - 20, ARM_START[1] - 20), (40, 25))
FLOOR = pygame.Rect((0, HEIGHT - FLOOR_HEIGHT), (WIDTH, FLOOR_HEIGHT))

#JOINT LIMITS
ALPHA_MIN = math.radians(0)
ALPHA_MAX = math.radians(180)
BETA_MIN = math.radians(-150)
BETA_MAX = math.radians(150)

def setup_screen():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Elbow Room")

    font = pygame.font.Font("freesansbold.ttf", 24)

    return screen, font

def calculate_elbow_pos(alpha):
    x = SEG1_LEN * math.cos(alpha)
    y = SEG1_LEN * math.sin(alpha)

    return (ARM_START[0] + x, ARM_START[1] - y)

def calculate_tip_pos(elbow, alpha, beta):
    x = elbow[0] + SEG2_LEN * math.cos(alpha + beta)
    y = elbow[1] - SEG2_LEN * math.sin(alpha + beta)  # minus because screen y is flipped
    return (x, y)

def wrap_angle(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi

def solve_ik(target_pos, prefer_sign):
    x = target_pos[0] - ARM_START[0]
    y = ARM_START[1] - target_pos[1]

    num = x**2 + y**2 - SEG1_LEN**2 - SEG2_LEN**2
    den = 2 * SEG1_LEN * SEG2_LEN

    beta_magnitude = math.acos(max(-1, min(1, num / den)))

    final_config = None
    for sign in (prefer_sign, -prefer_sign):
        beta = beta_magnitude * sign

        num = SEG2_LEN * math.sin(beta)
        den = SEG1_LEN + SEG2_LEN * math.cos(beta)
        alpha = wrap_angle(math.atan2(y, x) - math.atan2(num, den))

        alpha_error = max(0, ALPHA_MIN - alpha, alpha - ALPHA_MAX)
        beta_error = max(0, BETA_MIN - beta, beta - BETA_MAX)
        error = alpha_error + beta_error

        # strict < so the preferred sign wins ties
        if final_config is None or error < final_config[0]:
            final_config = (error, alpha, beta)

    _, alpha, beta = final_config

    return (max(ALPHA_MIN, min(alpha, ALPHA_MAX)),
            max(BETA_MIN, min(beta, BETA_MAX)))


def draw_robot(screen, target_pos, prefer_sign):
    alpha, beta = solve_ik(target_pos, prefer_sign)
    elbow = calculate_elbow_pos(alpha)
    tip = calculate_tip_pos(elbow, alpha, beta)

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, FLOOR_COLOR, FLOOR)

    pygame.draw.line(screen, SEG1_COLOR1, ARM_START, elbow, SEG_THICKNESS)
    pygame.draw.line(screen, SEG2_COLOR1, elbow, tip, SEG_THICKNESS)

    pygame.draw.circle(screen, JOINT_COLOR, elbow, JOINT_RADIUS)
    pygame.draw.circle(screen, JOINT_COLOR, tip, JOINT_RADIUS)

    pygame.draw.circle(screen, TARGET_COLOR, target_pos, JOINT_RADIUS / 2)

    pygame.draw.rect(screen, JOINT_COLOR, ROBOT_BASE)

    return alpha, beta


pygame.init()

screen, font = setup_screen()

target = [344, 225]
elbow_sign = -1

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == 113:       #Ctrl + q stops the program
            running = False

        #Jump Controls
        if event.type == pygame.MOUSEBUTTONDOWN:
            target = [event.pos[0], event.pos[1]]

        #Course Controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                target[0] -= 1
            elif event.key == pygame.K_RIGHT:
                target[0] += 1
            elif event.key == pygame.K_UP:
                target[1] -= 1
            elif event.key == pygame.K_DOWN:
                target[1] += 1

        #Fine Controls
        if event.type == pygame.TEXTINPUT:
            if event.text == "a":
                target[0] -= 5
            elif event.text == "d":
                target[0] += 5
            elif event.text == "w":
                target[1] -= 5
            elif event.text == "s":
                target[1] += 5


    target = [max(0, min(target[0], WIDTH)), max(0, min(target[1], HEIGHT - FLOOR_HEIGHT))]

    calc_alpha, calc_beta = draw_robot(screen, target, elbow_sign)

    if calc_beta != 0:
        elbow_sign = 1 if calc_beta > 0 else -1

    pos_text = font.render(str(target), True, (255, 255, 255))
    textRect = pos_text.get_rect()
    textRect.center = (50, WIDTH - 80)
    screen.blit(pos_text, pos_text.get_rect())

    pygame.display.flip()

pygame.quit()