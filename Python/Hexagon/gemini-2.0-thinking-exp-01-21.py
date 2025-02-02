import pygame
import math

# 初始化 Pygame
pygame.init()

# 屏幕尺寸
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("旋转六边形内的弹跳球")

# 颜色
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)

# 球的属性
ball_radius = 15
ball_pos = [screen_width // 2, screen_height // 2 - 100]  # 初始位置略高于中心
ball_vel = [5, 5]  # 初始速度
gravity = 0.5
friction = 0.01
ball_color = red

# 六边形的属性
hexagon_center = [screen_width // 2, screen_height // 2]
hexagon_radius = 200
hexagon_rotation_speed = 0.02  # 弧度/帧
hexagon_angle = 0
hexagon_color = white

# 辅助函数：计算六边形的顶点
def calculate_hexagon_vertices(center, radius, angle):
    vertices = []
    for i in range(6):
        angle_rad = math.radians(60 * i) + angle
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)
        vertices.append([int(x), int(y)])
    return vertices

# 辅助函数：点到线段的距离
def distance_point_segment(point, segment_start, segment_end):
    """计算点到线段的最短距离"""
    x0, y0 = point
    x1, y1 = segment_start
    x2, y2 = segment_end

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:  # 线段退化为点
        return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)

    t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx**2 + dy**2)
    t = max(0, min(1, t))  # 限制 t 在 [0, 1] 范围内

    closest_x = x1 + t * dx
    closest_y = y1 + t * dy

    return math.sqrt((x0 - closest_x)**2 + (y0 - closest_y)**2), [closest_x, closest_y]

# 辅助函数：向量反射
def reflect_vector(velocity, normal):
    """根据法向量反射速度向量"""
    # 向量的点积
    dot_product = velocity[0] * normal[0] + velocity[1] * normal[1]
    # 反射公式：v_reflected = v - 2 * (v · n) * n
    reflected_x = velocity[0] - 2 * dot_product * normal[0]
    reflected_y = velocity[1] - 2 * dot_product * normal[1]
    return [reflected_x, reflected_y]


# 游戏主循环
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新六边形角度
    hexagon_angle += hexagon_rotation_speed

    # 计算旋转后的六边形顶点
    hexagon_vertices = calculate_hexagon_vertices(hexagon_center, hexagon_radius, hexagon_angle)

    # 应用重力
    ball_vel[1] += gravity

    # 应用摩擦力 (简化版本，直接减速)
    ball_vel[0] *= (1 - friction)
    ball_vel[1] *= (1 - friction)


    # 更新球的位置
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # 碰撞检测和反弹
    collided = False
    for i in range(6):
        start_point = hexagon_vertices[i]
        end_point = hexagon_vertices[(i + 1) % 6]

        distance, closest_point = distance_point_segment(ball_pos, start_point, end_point)

        if distance <= ball_radius:
            collided = True

            # 计算碰撞点的法向量 (垂直于线段)
            segment_vector = [end_point[0] - start_point[0], end_point[1] - start_point[1]]
            normal_vector = [-segment_vector[1], segment_vector[0]] # 旋转90度得到法向量

            # 归一化法向量
            normal_magnitude = math.sqrt(normal_vector[0]**2 + normal_vector[1]**2)
            if normal_magnitude != 0: # 避免除以零
                normal_vector = [normal_vector[0] / normal_magnitude, normal_vector[1] / normal_magnitude]


            # 反弹球的速度
            ball_vel = reflect_vector(ball_vel, normal_vector)

            # 稍微调整球的位置，防止卡在墙里
            push_out_vector = [n * (ball_radius - distance + 1) for n in normal_vector] # +1 避免正好等于半径时也推出去
            ball_pos[0] += push_out_vector[0]
            ball_pos[1] += push_out_vector[1]


    # 边界碰撞 (屏幕边界) -  作为额外的边界，即使六边形旋转出屏幕
    if ball_pos[0] - ball_radius < 0:
        ball_pos[0] = ball_radius
        ball_vel[0] = -ball_vel[0]
    elif ball_pos[0] + ball_radius > screen_width:
        ball_pos[0] = screen_width - ball_radius
        ball_vel[0] = -ball_vel[0]

    if ball_pos[1] - ball_radius < 0:
        ball_pos[1] = ball_radius
        ball_vel[1] = -ball_vel[1]
    elif ball_pos[1] + ball_radius > screen_height:
        ball_pos[1] = screen_height - ball_radius
        ball_vel[1] = -ball_vel[1]


    # 绘制
    screen.fill(black)

    # 绘制六边形
    pygame.draw.polygon(screen, hexagon_color, hexagon_vertices, 2) # 2 是线宽

    # 绘制球
    pygame.draw.circle(screen, ball_color, [int(ball_pos[0]), int(ball_pos[1])], ball_radius)

    # 更新屏幕
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

pygame.quit()
