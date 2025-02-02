import pygame
import math
import random

# 初始化pygame
pygame.init()

# 设置屏幕大小
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# 设置颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 设置时钟
clock = pygame.time.Clock()

# 设置重力
gravity = 0.5

# 设置摩擦力
friction = 0.99

# 设置球的初始位置和速度
ball_radius = 15
ball_pos = [screen_width // 2, screen_height // 2]
ball_vel = [random.uniform(-5, 5), random.uniform(-5, 5)]

# 设置六边形的参数
hexagon_radius = 200
hexagon_center = [screen_width // 2, screen_height // 2]
hexagon_angle = 0
hexagon_rotation_speed = 0.01

# 计算六边形的顶点
def calculate_hexagon_points(center, radius, angle):
    points = []
    for i in range(6):
        x = center[0] + radius * math.cos(math.radians(60 * i + angle))
        y = center[1] + radius * math.sin(math.radians(60 * i + angle))
        points.append((x, y))
    return points

# 检测球是否与六边形的边碰撞
def check_collision(ball_pos, ball_radius, hexagon_points):
    for i in range(6):
        p1 = hexagon_points[i]
        p2 = hexagon_points[(i + 1) % 6]
        
        # 计算边的向量
        edge = (p2[0] - p1[0], p2[1] - p1[1])
        normal = (-edge[1], edge[0])
        length = math.hypot(normal[0], normal[1])
        normal = (normal[0] / length, normal[1] / length)
        
        # 计算球到边的距离
        ball_to_p1 = (ball_pos[0] - p1[0], ball_pos[1] - p1[1])
        distance = abs(ball_to_p1[0] * normal[0] + ball_to_p1[1] * normal[1])
        
        if distance < ball_radius:
            # 计算反射向量
            dot = ball_vel[0] * normal[0] + ball_vel[1] * normal[1]
            ball_vel[0] -= 2 * dot * normal[0]
            ball_vel[1] -= 2 * dot * normal[1]
            return True
    return False

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新六边形的旋转角度
    hexagon_angle += hexagon_rotation_speed
    if hexagon_angle >= 360:
        hexagon_angle -= 360

    # 计算六边形的顶点
    hexagon_points = calculate_hexagon_points(hexagon_center, hexagon_radius, hexagon_angle)

    # 更新球的速度和位置
    ball_vel[1] += gravity
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # 检测球是否与六边形的边碰撞
    if check_collision(ball_pos, ball_radius, hexagon_points):
        ball_vel[0] *= friction
        ball_vel[1] *= friction

    # 清屏
    screen.fill(BLACK)

    # 绘制六边形
    pygame.draw.polygon(screen, WHITE, hexagon_points, 2)

    # 绘制球
    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    # 更新屏幕
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

# 退出pygame
pygame.quit()
