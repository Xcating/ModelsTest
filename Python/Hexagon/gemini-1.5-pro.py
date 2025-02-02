import pygame
import math

# 初始化 Pygame
pygame.init()

# 屏幕尺寸
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing Ball in Rotating Hexagon")

# 颜色
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# 六边形参数
hex_center = (width // 2, height // 2)
hex_radius = 150
rotation_speed = 0.5  # 每帧旋转的度数

# 球参数
ball_radius = 15
ball_x = hex_center[0]
ball_y = hex_center[1] - hex_radius + ball_radius + 1
ball_vx = 5
ball_vy = 0
gravity = 0.2
friction = 0.99

# 计算六边形的顶点
def hexagon_vertices(center, radius, rotation):
    vertices = []
    for i in range(6):
        angle_deg = 60 * i + rotation
        angle_rad = math.radians(angle_deg)
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)
        vertices.append((x, y))
    return vertices

# 游戏循环
running = True
clock = pygame.time.Clock()
rotation = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新球的位置
    ball_vy += gravity
    ball_x += ball_vx
    ball_y += ball_vy

    # 旋转六边形
    rotation += rotation_speed

    # 获取旋转的六边形顶点
    hex_vertices_rotated = hexagon_vertices(hex_center, hex_radius, rotation)

    # 碰撞检测和反弹 (简化版 - 需要改进)
    for i in range(6):
        x1, y1 = hex_vertices_rotated[i]
        x2, y2 = hex_vertices_rotated[(i + 1) % 6]

        # 简化的碰撞检测：检查球是否在边界的外面
        dist_to_center = math.hypot(ball_x - hex_center[0], ball_y - hex_center[1])
        if dist_to_center > hex_radius - ball_radius:
            # 反转速度以模拟反弹 (这部分需要更精确的碰撞处理)
            ball_vx *= -friction
            ball_vy *= -friction

    # 绘制
    screen.fill(black)
    pygame.draw.polygon(screen, white, hex_vertices_rotated, 2)
    pygame.draw.circle(screen, red, (int(ball_x), int(ball_y)), ball_radius)

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

pygame.quit()
