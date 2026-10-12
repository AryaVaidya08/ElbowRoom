import pygame
from sprites import ball

WIDTH = 600
HEIGHT = 450

def setup_screen():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Elbow Room")

    font = pygame.font.Font("freesansbold.ttf", 24)

    return screen, font

pygame.init()
screen, font = setup_screen()
sim_clock = pygame.time.Clock()

start_pos = [470, 225]
ball = ball.Ball(screen, start_pos)

running = True

while running:
    dt = sim_clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == 113:       #Ctrl + q stops the program
            running = False

    screen.fill((0,0,0))
    ball.update(dt)
    pygame.display.flip() 