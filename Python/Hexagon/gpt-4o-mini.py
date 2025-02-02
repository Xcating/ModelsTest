import pygame
import math

# 初始化 Pygame
pygame.init()

# 屏幕设置
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing Ball in Rotating Hexagon")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 球的属性
ball_radius = 15
ball_pos = [width // 2, height // 2]
ball_vel = [2, 0]
gravity = 0.1
friction = 0.99

# 六边形的设置
hex_size = 200
hex_center = [width // 2, height // 2]
rotation_speed = 0.5
angle = 0

def draw_hexagon(surface, center, size, angle):
    points = []
    for i in range(6):
        theta = (math.pi / 3) * i + angle
        x = center[0] + size * math.cos(theta)
        y = center[1] + size * math.sin(theta)
        points.append((x, y))
    pygame.draw.polygon(surface, BLACK, points)

def check_collision(ball_pos, ball_vel, hex_center, angle):
    for i in range(6):
        # 计算当前墙壁的两个顶点
        theta1 = (math.pi / 3) * i + angle
        theta2 = (math.pi / 3) * (i + 1) + angle
        p1 = (hex_center[0] + hex_size * math.cos(theta1),
              hex_center[1] + hex_size * math.sin(theta1))
        p2 = (hex_center[0] + hex_size * math.cos(theta2),
              hex_center[1] + hex_size * math.sin(theta2))

        # 计算球到这条边的距离
        normal = (p2[1] - p1[1], p1[0] - p2[0])  # 边的法向量
        norm_length = math.sqrt(normal[0] ** 2 + normal[1] ** 2)
        normal = (normal[0] / norm_length, normal[1] / norm_length)

        # 球心到边的距离
        dist = ((ball_pos[0] - p1[0]) * normal[0] + (ball_pos[1] - p1[1]) * normal[1])

        if dist < ball_radius:
            # 反弹效果
            ball_vel[0] = -ball_vel[0] * 0.8
            ball_vel[1] = -ball_vel[1] * 0.8

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 清屏
    screen.fill(WHITE)

    # 绘制旋转六边形
    draw_hexagon(screen, hex_center, hex_size, angle)
    angle += rotation_speed * math.pi / 180  # 增加角度以实现旋转

    # 更新球的位置和速度
    ball_vel[1] += gravity  # 应用重力
    ball_pos[0] += ball_vel[0]  # 更新 x 位置
    ball_pos[1] += ball_vel[1]  # 更新 y 位置
    ball_vel[0] *= friction  # 应用摩擦

    # 碰撞检测
    check_collision(ball_pos, ball_vel, hex_center, angle)

    # 检查球是否在屏幕内
    if ball_pos[0] > width + ball_radius:
        ball_pos[0] = width + ball_radius
        ball_vel[0] = -ball_vel[0]
    elif ball_pos[0] < -ball_radius:
        ball_pos[0] = -ball_radius
        ball_vel[0] = -ball_vel[0]

    if ball_pos[1] > height + ball_radius:
        ball_pos[1] = height + ball_radius
        ball_vel[1] = -ball_vel[1]
    elif ball_pos[1] < -ball_radius:
        ball_pos[1] = -ball_radius
        ball_vel[1] = -ball_vel[1]

    # 绘制球
    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    # 更新屏幕
    pygame.display.flip()
    pygame.time.delay(16)

pygame.quit()
