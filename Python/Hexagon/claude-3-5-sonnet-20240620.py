import pygame
import math
import sys

# 初始化Pygame
pygame.init()

# 设置窗口大小
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("旋转六边形中的弹跳球")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 六边形参数
HEX_RADIUS = 200
HEX_CENTER = (WIDTH // 2, HEIGHT // 2)
ROTATION_SPEED = 0.5  # 弧度/秒

# 球参数
BALL_RADIUS = 10
ball_pos = [WIDTH // 2, HEIGHT // 2 - 100]
ball_vel = [0, 0]

# 物理参数
GRAVITY = 0.5
FRICTION = 0.99
BOUNCE_FACTOR = 0.8

# 计算六边形顶点
def get_hex_vertices(center, radius, rotation):
    vertices = []
    for i in range(6):
        angle = rotation + i * math.pi / 3
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices

# 检查球是否与线段碰撞
def line_circle_collision(p1, p2, circle_pos, circle_radius):
    x1, y1 = p1
    x2, y2 = p2
    cx, cy = circle_pos

    # 计算线段向量
    dx = x2 - x1
    dy = y2 - y1

    # 计算线段长度的平方
    length_sq = dx * dx + dy * dy

    # 计算球心到线段起点的向量
    t = ((cx - x1) * dx + (cy - y1) * dy) / length_sq

    # 找到线段上最近的点
    if t < 0:
        closest_point = (x1, y1)
    elif t > 1:
        closest_point = (x2, y2)
    else:
        closest_point = (x1 + t * dx, y1 + t * dy)

    # 计算最近点到球心的距离
    distance = math.sqrt((cx - closest_point[0])**2 + (cy - closest_point[1])**2)

    return distance <= circle_radius, closest_point

# 主游戏循环
clock = pygame.time.Clock()
rotation = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 更新旋转角度
    rotation += ROTATION_SPEED * clock.get_time() / 1000

    # 应用重力
    ball_vel[1] += GRAVITY

    # 更新球的位置
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # 应用摩擦力
    ball_vel[0] *= FRICTION
    ball_vel[1] *= FRICTION

    # 获取六边形顶点
    hex_vertices = get_hex_vertices(HEX_CENTER, HEX_RADIUS, rotation)

    # 检查碰撞
    for i in range(6):
        p1 = hex_vertices[i]
        p2 = hex_vertices[(i + 1) % 6]
        collision, closest_point = line_circle_collision(p1, p2, ball_pos, BALL_RADIUS)

        if collision:
            # 计算法线向量
            nx = ball_pos[0] - closest_point[0]
            ny = ball_pos[1] - closest_point[1]
            norm = math.sqrt(nx*nx + ny*ny)
            nx /= norm
            ny /= norm

            # 计算入射速度在法线方向上的分量
            vn = ball_vel[0] * nx + ball_vel[1] * ny

            # 应用反弹
            ball_vel[0] = (ball_vel[0] - 2 * vn * nx) * BOUNCE_FACTOR
            ball_vel[1] = (ball_vel[1] - 2 * vn * ny) * BOUNCE_FACTOR

            # 将球移出碰撞位置
            ball_pos[0] = closest_point[0] + nx * (BALL_RADIUS + 1)
            ball_pos[1] = closest_point[1] + ny * (BALL_RADIUS + 1)

    # 绘制
    screen.fill(BLACK)
    pygame.draw.polygon(screen, WHITE, hex_vertices, 2)
    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

    pygame.display.flip()
    clock.tick(60)
