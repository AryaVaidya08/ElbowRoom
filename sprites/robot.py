import pygame
import math
from utils import wrap_angle

WIDTH = 600
HEIGHT = 450
FLOOR_HEIGHT = 100

SEG1_COLOR1 = (255, 0, 0)
SEG2_COLOR1 = (0, 255, 0)

JOINT_COLOR = (50, 50, 50)
TARGET_COLOR = (0, 0, 255)

SEG_THICKNESS = 6
JOINT_RADIUS = 7

ARM_START = (WIDTH / 2, HEIGHT - FLOOR_HEIGHT)
SEG1_LEN = 200.0
SEG2_LEN = 75.0

ROBOT_BASE = pygame.Rect((ARM_START[0] - 20, ARM_START[1] - 20), (40, 25))

ALPHA_MIN = math.radians(0)
ALPHA_MAX = math.radians(180)
BETA_MIN = math.radians(-165)
BETA_MAX = math.radians(165)

MAX_SPEED = 2

class Robot(pygame.sprite.Sprite):
    def __init__(self, target, elbow_sign):
        pygame.sprite.Sprite.__init__(self)
        self.target = target
        self.elbow_sign = elbow_sign

        self.alpha, self.beta = self.solve_ik(target, self.elbow_sign)

    def update(self, new_target, dt):
        self.target = new_target

        # keep the current elbow orientation so the arm doesn't flip mid-motion
        if self.beta != 0:
            self.elbow_sign = 1 if self.beta > 0 else -1

        alpha_goal, beta_goal = self.solve_ik(self.target, self.elbow_sign)
        self.alpha, self.beta = self.move_toward(self.alpha, self.beta, alpha_goal, beta_goal, dt)

    def move_toward(self, alpha, beta, alpha_goal, beta_goal, dt):
        da = alpha_goal - alpha
        db = beta_goal - beta
        dist = max(abs(da), abs(db))

        if dist < 1e-9:
            return alpha_goal, beta_goal

        scale = min(1.0, MAX_SPEED * dt / dist)
        return alpha + da * scale, beta + db * scale

    def calculate_elbow_pos(self, alpha):
        x = SEG1_LEN * math.cos(alpha)
        y = SEG1_LEN * math.sin(alpha)

        return (ARM_START[0] + x, ARM_START[1] - y)

    def calculate_tip_pos(self, elbow, alpha, beta):
        x = elbow[0] + SEG2_LEN * math.cos(alpha + beta)
        y = elbow[1] - SEG2_LEN * math.sin(alpha + beta)  # minus because screen y is flipped
        return (x, y)

    def solve_ik(self, target_pos, prefer_sign):
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

    def draw(self, screen):
        elbow = self.calculate_elbow_pos(self.alpha)
        tip = self.calculate_tip_pos(elbow, self.alpha, self.beta)

        pygame.draw.line(screen, SEG1_COLOR1, ARM_START, elbow, SEG_THICKNESS)
        pygame.draw.line(screen, SEG2_COLOR1, elbow, tip, SEG_THICKNESS)

        pygame.draw.circle(screen, JOINT_COLOR, elbow, JOINT_RADIUS)
        pygame.draw.circle(screen, JOINT_COLOR, tip, JOINT_RADIUS)

        pygame.draw.circle(screen, TARGET_COLOR, self.target, JOINT_RADIUS / 2)

        pygame.draw.rect(screen, JOINT_COLOR, ROBOT_BASE)