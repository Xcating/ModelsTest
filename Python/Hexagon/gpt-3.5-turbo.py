import pygame
import sys
from pygame.locals import *
import math
import pygame
import sys
from pygame.locals import *
import math
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Ball Bouncing in Rotating Hexagon')

# 定义旋转六边形的参数
center = (width // 2, height // 2)  # 旋转中心
radius = 200  # 旋转半径
speed = 0.01  # 旋转速度
angle = 0  # 初始角度
class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = 0
        self.speed_y = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self):
        # 球体受重力和摩擦力的影响
        self.speed_y += 0.1  # 重力加速度
        self.y += self.speed_y

        # 检测球体和旋转六边形的碰撞
        angle_rad = math.radians(angle)
        px = self.x - center[0]
        py = self.y - center[1]
        rotated_x = px * math.cos(angle_rad) - py * math.sin(angle_rad) + center[0]
        rotated_y = px * math.sin(angle_rad) + py * math.cos(angle_rad) + center[1]

        if rotated_y + self.radius >= center[1] + 50:  # 旋转六边形的边界
            self.y = center[1] + 50 - self.radius
            self.speed_y *= -0.8  # 反弹并且速度衰减
ball = Ball(width // 2, 50, 10, (255, 0, 0))

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))

    angle += speed
    if angle >= 360:
        angle = 0

    # 绘制旋转六边形
    pygame.draw.polygon(screen, (0, 0, 0), [(center[0] + radius * math.cos(math.radians(a) + angle),
                                             center[1] + radius * math.sin(math.radians(a) + angle)) for a in
                                            range(0, 360, 60)], 5)

    ball.update()
    ball.draw(screen)

    pygame.display.flip()
