import pygame
from sprites import robot

WIDTH = 600
HEIGHT = 450

FLOOR_HEIGHT = 100
FLOOR_COLOR = (200, 200, 200)
FLOOR = pygame.Rect((0, HEIGHT - FLOOR_HEIGHT), (WIDTH, FLOOR_HEIGHT))

def draw_background():
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, FLOOR_COLOR, FLOOR)

def setup_screen():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Elbow Room")

    font = pygame.font.Font("freesansbold.ttf", 24)

    return screen, font

pygame.init()
screen, font = setup_screen()
sim_clock = pygame.time.Clock()

target = [344, 225]
elbow_sign = -1
robot = robot.Robot(target, elbow_sign)



running = True
while running:
    dt = sim_clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == 113:       #Ctrl + q stops the program
            running = False

        #Jump Controls
        if event.type == pygame.MOUSEBUTTONDOWN:
            target = [event.pos[0], event.pos[1]]

    target = [max(0, min(target[0], WIDTH)), max(0, min(target[1], HEIGHT - FLOOR_HEIGHT))]

    draw_background()
    robot.update(target, dt)
    robot.draw(screen)

    pos_text = font.render(str(target), True, (255, 255, 255))
    textRect = pos_text.get_rect()
    textRect.center = (50, WIDTH - 80)
    screen.blit(pos_text, pos_text.get_rect())

    pygame.display.flip() 