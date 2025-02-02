import pygame
import sys
import math

# 初始化pygame
pygame.init()

# 设置屏幕大小
screen_width, screen_height = 600, 400
screen = pygame.display.set_mode((screen_width, screen_height))

# 设置标题
pygame.display.set_caption("Bouncing Ball Inside Rotating Hexagon")

# 定义颜色
white = (255, 255, 255)
black = (0, 0, 0)

# 设置变量
clock = pygame.time.Clock()
hexagon_speed = 0.02  # 六边形的旋转速度
friction = 0.99
gravity = 0.1

# 球的属性
ball_pos = [300, 200]
ball_vel = [2, -1]
ball_radius = 15

# 六边形的属性
hexagon_radius = 150
hexagon_angle = 0

def draw_hexagon(surface, center, size, angle):
    points = []
    for i in range(6):
        theta = angle + math.radians(i * 60)
        x = center[0] + size * math.cos(theta)
        y = center[1] + size * math.sin(theta)
        points.append((x, y))
    pygame.draw.polygon(surface, white, points, 3)

def move_ball():
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]
    ball_vel[1] += gravity  # Gravity

    # 模拟摩擦力
    ball_vel[0] *= friction
    ball_vel[1] *= friction

# 主循环
def point_to_line_dist(px, py, x1, y1, x2, y2):
    # Calculate the distance from point (px, py) to the line defined by points (x1, y1) and (x2, y2)
    line_mag = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    param = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / float(line_mag**2)
    if param < 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2), False
    elif param > 1:
        return math.sqrt((px - x2)**2 + (py - y2)**2), False
    else:
        x = x1 + param * (x2 - x1)
        y = y1 + param * (y2 - y1)
        return math.sqrt((px - x)**2 + (py - y)**2), True

def reflect_ball(px, py, vx, vy, x1, y1, x2, y2):
    # Reflect the ball velocity based on the line defined by (x1, y1) and (x2, y2)
    line_dx = x2 - x1
    line_dy = y2 - y1
    normal = pygame.math.Vector2(-line_dy, line_dx).normalize()
    incident = pygame.math.Vector2(vx, vy)
    reflected = incident.reflect(normal)
    return reflected.x, reflected.y

running = True
while running:
    screen.fill(black)

    # 绘制旋转的六边形
    draw_hexagon(screen, (screen_width//2, screen_height//2), hexagon_radius, hexagon_angle)
    hexagon_angle += hexagon_speed

    # 移动球
    move_ball()

    # 检测与六边形边的碰撞
    hex_points = [(math.cos(math.radians(1 + i * 60)) * hexagon_radius + screen_width//2,
                math.sin(math.radians(1 + i * 60)) * hexagon_radius + screen_height//2) for i in range(6)]

    for i in range(6):
        start_point = hex_points[i]
        end_point = hex_points[(i + 1) % 6]  # Ensure the last point connects back to the first
        dist, within_segment = point_to_line_dist(ball_pos[0], ball_pos[1], start_point[0], start_point[1], end_point[0], end_point[1])
        if dist < ball_radius and within_segment:
            # Calculate reflection
            ball_vel[0], ball_vel[1] = reflect_ball(ball_pos[0], ball_pos[1], ball_vel[0], ball_vel[1], start_point[0], start_point[1], end_point[0], end_point[1])
            # Move ball out of collision
            while dist < ball_radius:
                ball_pos[0] += ball_vel[0] * 0.1
                ball_pos[1] += ball_vel[1] * 0.1
                dist, within_segment = point_to_line_dist(ball_pos[0], ball_pos[1], start_point[0], start_point[1], end_point[0], end_point[1])
    
    # 绘制球
    pygame.draw.circle(screen, white, [int(ball_pos[0]), int(ball_pos[1])], ball_radius)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
