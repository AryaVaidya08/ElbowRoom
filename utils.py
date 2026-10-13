import math

WIDTH = 500
HEIGHT = 450
FLOOR_HEIGHT = 100

BALL_COLOR = (255, 255, 0)
BALL_RADIUS = 10

def wrap_angle(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi