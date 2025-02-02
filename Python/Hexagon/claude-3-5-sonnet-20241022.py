import pygame
import math
import numpy as np

# 初始化Pygame
pygame.init()

# 设置窗口
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("旋转六边形中的弹跳球")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 物理参数
GRAVITY = 0.5
FRICTION = 0.99
BOUNCE_FACTOR = 0.7

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.vel_x = 0
        self.vel_y = 0

    def update(self):
        # 更新位置
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 应用重力
        self.vel_y += GRAVITY
        
        # 应用摩擦力
        self.vel_x *= FRICTION
        self.vel_y *= FRICTION

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)

class Hexagon:
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.angle = 0
        self.rotation_speed = 0.04

    def get_points(self):
        points = []
        for i in range(6):
            angle = self.angle + i * math.pi / 3
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            points.append((x, y))
        return points

    def draw(self, surface):
        points = self.get_points()
        pygame.draw.polygon(surface, WHITE, points, 2)

    def update(self):
        self.angle += self.rotation_speed

def check_collision(ball, hexagon):
    points = hexagon.get_points()
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % 6]
        
        # 计算球到线段的最短距离
        line_vec = np.array([p2[0] - p1[0], p2[1] - p1[1]])
        ball_to_p1 = np.array([ball.x - p1[0], ball.y - p1[1]])
        
        line_length = np.linalg.norm(line_vec)
        line_unit = line_vec / line_length
        
        projection_length = np.dot(ball_to_p1, line_unit)
        
        if 0 <= projection_length <= line_length:
            projection = p1 + line_unit * projection_length
            distance = np.linalg.norm(np.array([ball.x, ball.y]) - projection)
            
            if distance < ball.radius:
                # 计算法向量
                normal = np.array([-line_vec[1], line_vec[0]]) / line_length
                if np.dot(normal, ball_to_p1) < 0:
                    normal = -normal
                
                # 计算反弹
                velocity = np.array([ball.vel_x, ball.vel_y])
                reflection = velocity - 2 * np.dot(velocity, normal) * normal
                
                ball.vel_x = reflection[0] * BOUNCE_FACTOR
                ball.vel_y = reflection[1] * BOUNCE_FACTOR
                
                # 调整球的位置以防止卡在边界
                overlap = ball.radius - distance
                ball.x += normal[0] * overlap
                ball.y += normal[1] * overlap

# 创建对象
ball = Ball(WIDTH//2, HEIGHT//2, 10)
hexagon = Hexagon(WIDTH//2, HEIGHT//2, 200)

# 游戏主循环
running = True
clock = pygame.time.Clock()

while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 点击时给球一个随机初速度
            ball.vel_x = (pygame.mouse.get_pos()[0] - ball.x) * 0.1
            ball.vel_y = (pygame.mouse.get_pos()[1] - ball.y) * 0.1

    # 更新
    ball.update()
    hexagon.update()
    check_collision(ball, hexagon)

    # 绘制
    screen.fill(BLACK)
    hexagon.draw(screen)
    ball.draw(screen)
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

pygame.quit()
