import pygame
import math

# 初始化Pygame
pygame.init()

# 常量
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
FRICTION = 0.99

# 六边形的相关设置
HEX_SIZE = 300
HEX_CENTER = (WIDTH // 2, HEIGHT // 2)
HEX_ROT_SPEED = 1  # 六边形旋转速度

# 球的相关设置
BALL_RADIUS = 15
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_velocity = [0, 0]

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in Rotating Hexagon")
clock = pygame.time.Clock()

def draw_hexagon(surface, center, size, angle):
    points = []
    for i in range(6):
        # 计算旋转后的点
        theta = math.radians(i * 60 + angle)
        x = center[0] + size * math.cos(theta)
        y = center[1] + size * math.sin(theta)
        points.append((x, y))
    pygame.draw.polygon(surface, WHITE, points, 3)

def check_collision(ball_pos, radius, hex_center, hex_size, angle):
    # 计算六边形的每个边
    points = []
    for i in range(6):
        theta = math.radians(i * 60 + angle)
        x = hex_center[0] + hex_size * math.cos(theta)
        y = hex_center[1] + hex_size * math.sin(theta)
        points.append((x, y))

    for i in range(6):
        p1 = points[i]
        p2 = points[(i + 1) % 6]
        # 计算边的法向量
        edge = (p2[0] - p1[0], p2[1] - p1[1])
        edge_length = math.sqrt(edge[0]**2 + edge[1]**2)

        # 归一化法向量
        normal = (-edge[1] / edge_length, edge[0] / edge_length)
        
        # 投影球到边的法向量
        ball_to_p1 = (ball_pos[0] - p1[0], ball_pos[1] - p1[1])
        if (normal[0] * ball_to_p1[0] + normal[1] * ball_to_p1[1]) < radius:
            return normal

    return None

# 主循环
running = True
angle = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新
    angle += HEX_ROT_SPEED
    ball_velocity[1] += GRAVITY
    
    # 更新球的位置
    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]
    
    # 检查碰撞
    collision_normal = check_collision(ball_pos, BALL_RADIUS, HEX_CENTER, HEX_SIZE, angle)
    if collision_normal:
        # 反弹
        ball_velocity[0] *= -1 * FRICTION
        ball_velocity[1] *= -1 * FRICTION
        
        # 调整位置，避免穿透
        overlap = BALL_RADIUS - (collision_normal[0] * (ball_pos[0] - HEX_CENTER[0] + 15) + 
                                   collision_normal[1] * (ball_pos[1] - HEX_CENTER[1] + 15))
        ball_pos[0] += collision_normal[0] * overlap
        ball_pos[1] += collision_normal[1] * overlap

    # 填充背景
    screen.fill(BLACK)
    
    # 画六边形
    draw_hexagon(screen, HEX_CENTER, HEX_SIZE, angle)
    
    # 画球
    pygame.draw.circle(screen, WHITE, (int(ball_pos[0])， int(ball_pos[1])), BALL_RADIUS)

    # 刷新显示
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
