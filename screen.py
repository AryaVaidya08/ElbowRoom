import pygame
import math

WIDTH = 600
HEIGHT = 450
FLOOR_HEIGHT = 100

FLOOR_COLOR = (200, 200, 200)

SEG1_COLOR = (255, 0, 0)
SEG2_COLOR = (0, 255, 0)
JOINT_COLOR = (50, 50, 50)

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

def calculate_elbow_pos(alpha):
    #using polar coordinates
    x = SEG1_LEN * math.cos(alpha)
    y = SEG1_LEN * math.sin(alpha)
    print("elbow", x, y)
    return (ARM_START[0] + x, ARM_START[1] - y)

def calculate_end_pos(elbow, beta):
    x = SEG2_LEN * math.cos(beta)
    y = SEG2_LEN * math.sin(beta)
    print("end", x, y)    
    return (elbow[0] + x, elbow[1] - y)

def draw_robot(screen, alpha, beta):
    elbow = calculate_elbow_pos(alpha)
    end = calculate_end_pos(elbow, alpha + beta)

    print(ARM_START, elbow, end)

    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, FLOOR_COLOR, FLOOR)

    pygame.draw.line(screen, SEG1_COLOR, ARM_START, elbow, SEG_THICKNESS)
    pygame.draw.line(screen, SEG2_COLOR, elbow, end, SEG_THICKNESS)

    pygame.draw.circle(screen, JOINT_COLOR, elbow, JOINT_RADIUS)
    pygame.draw.circle(screen, JOINT_COLOR, end, JOINT_RADIUS)

    pygame.draw.rect(screen, JOINT_COLOR, ROBOT_BASE)
    pygame.display.flip()


pygame.init()

screen = setup_screen()

alpha_angle = 30
beta_angle = 60

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == 113:       #Ctrl + q stops the program
            running = False

        #Course Controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                beta_angle += 1
            elif event.key == pygame.K_RIGHT:
                beta_angle -= 1
            elif event.key == pygame.K_UP:
                alpha_angle += 1
            elif event.key == pygame.K_DOWN:
                alpha_angle -= 1

        #Fine Controls
        if event.type == pygame.TEXTINPUT:
            if event.text == "a":
                beta_angle += 3
            elif event.text == "d":
                beta_angle -= 3
            elif event.text == "w":
                alpha_angle += 3
            elif event.text == "s":
                alpha_angle -= 3

    draw_robot(screen, math.radians(alpha_angle), math.radians(beta_angle))

pygame.quit()