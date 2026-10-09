import pygame
import math

WIDTH = 600
HEIGHT = 450
FLOOR_HEIGHT = 100

FLOOR_COLOR = (200, 200, 200)

SEG1_COLOR = (255, 0, 0)
SEG2_COLOR = (0, 255, 0)
JOINT_COLOR = (50, 50, 50)
TARGET_COLOR = (0, 0, 255)

SEG_THICKNESS = 6
JOINT_RADIUS = 10

ARM_START = (WIDTH / 4, HEIGHT - FLOOR_HEIGHT)
SEG1_LEN = 100.0
SEG2_LEN = 50.0

ROBOT_BASE = pygame.Rect((ARM_START[0] - 20, ARM_START[1] - 20), (40, 25))
FLOOR = pygame.Rect((0, HEIGHT - FLOOR_HEIGHT), (WIDTH, FLOOR_HEIGHT))

def setup_screen():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Elbow Room")

    floor = pygame.Rect((0, HEIGHT - FLOOR_HEIGHT), (WIDTH, FLOOR_HEIGHT))
    pygame.draw.rect(screen, FLOOR_COLOR, floor)
    pygame.display.flip()

    return screen

def calculate_beta(end_pos):
    # Convert absolute screen coordinates to coordinates relative to the base
    x = end_pos[0] - ARM_START[0]
    y = ARM_START[1] - end_pos[1]  # Flip y-axis

    num = x**2 + y**2 - SEG1_LEN**2 - SEG2_LEN**2
    den = 2 * SEG1_LEN * SEG2_LEN

    return -math.acos(max(-1, min(1, num / den)))


def calculate_alpha(end_pos, beta):
    x = end_pos[0] - ARM_START[0]
    y = ARM_START[1] - end_pos[1]

    num = SEG2_LEN * math.sin(beta)
    den = SEG1_LEN + SEG2_LEN * math.cos(beta)

    return math.atan2(y, x) - math.atan2(num, den)


def calculate_elbow_pos(alpha):
    x = SEG1_LEN * math.cos(alpha)
    y = SEG1_LEN * math.sin(alpha)

    return (ARM_START[0] + x, ARM_START[1] - y)

def calculate_tip_pos(elbow, alpha, beta):
    x = elbow[0] + SEG2_LEN * math.cos(alpha + beta)
    y = elbow[1] - SEG2_LEN * math.sin(alpha + beta)  # minus because screen y is flipped
    return (x, y)

def draw_robot(screen, target_pos):
    beta = calculate_beta(target_pos)
    alpha = calculate_alpha(target_pos, beta)
    elbow = calculate_elbow_pos(alpha)
    tip = calculate_tip_pos(elbow, alpha, beta)

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, FLOOR_COLOR, FLOOR)

    pygame.draw.line(screen, SEG1_COLOR, ARM_START, elbow, SEG_THICKNESS)
    pygame.draw.line(screen, SEG2_COLOR, elbow, tip, SEG_THICKNESS)

    pygame.draw.circle(screen, JOINT_COLOR, elbow, JOINT_RADIUS)
    pygame.draw.circle(screen, JOINT_COLOR, tip, JOINT_RADIUS)

    pygame.draw.circle(screen, TARGET_COLOR, target_pos, JOINT_RADIUS / 2)

    pygame.draw.rect(screen, JOINT_COLOR, ROBOT_BASE)
    pygame.display.flip()


pygame.init()

screen = setup_screen()

end_pos = [294.65566742582274, 310.3362276988979]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == 113:       #Ctrl + q stops the program
            running = False

        #Course Controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                end_pos[0] -= 1
            elif event.key == pygame.K_RIGHT:
                end_pos[0] += 1
            elif event.key == pygame.K_UP:
                end_pos[1] -= 1
            elif event.key == pygame.K_DOWN:
                end_pos[1] += 1

        #Fine Controls
        if event.type == pygame.TEXTINPUT:
            if event.text == "a":
                end_pos[0] -= 3
            elif event.text == "d":
                end_pos[0] += 3
            elif event.text == "w":
                end_pos[1] -= 3
            elif event.text == "s":
                end_pos[1] += 3

    draw_robot(screen, end_pos)

pygame.quit()