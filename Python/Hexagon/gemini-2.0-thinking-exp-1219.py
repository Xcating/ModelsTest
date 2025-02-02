import pygame
import math

# 初始化 Pygame
pygame.init()

# 屏幕尺寸
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("弹跳球")

# 颜色
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# 六边形参数
hexagon_radius = 200
hexagon_x = screen_width // 2
hexagon_y = screen_height // 2
hexagon_rotation_speed = 0.02  # 弧度/帧
hexagon_angle = 0

# 球参数
ball_radius = 15
ball_x = hexagon_x + hexagon_radius / 2
ball_y = hexagon_y
ball_speed_x = 5
ball_speed_y = 0
gravity = 0.5
friction = 0.01
elasticity = 0.8  # 弹性系数
rotation_effect_factor = 0.1 # 旋转影响因子


def calculate_hexagon_points(angle):
    points = []
    for i in range(6):
        x = hexagon_x + hexagon_radius * math.cos(angle + 2 * math.pi * i / 6)
        y = hexagon_y + hexagon_radius * math.sin(angle + 2 * math.pi * i / 6)
        points.append((int(x), int(y)))
    return points

def draw_hexagon(points):
    pygame.draw.polygon(screen, white, points, 2)

def rotate_point(point, center, angle):
    """围绕中心点旋转一个点"""
    ox, oy = center
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def point_segment_distance_sq(point, segment_p1, segment_p2):
    """计算点到线段的平方距离"""
    x, y = point
    x1, y1 = segment_p1
    x2, y2 = segment_p2

    l2 = ((x1 - x2) ** 2 + (y1 - y2) ** 2)
    if l2 == 0.0:
        return (x - x1) ** 2 + (y - y1) ** 2   # 如果 p1 == p2 返回点到 p1 的距离

    t = ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / l2
    t = max(0, min(1, t)) # 限制 t 在 [0, 1] 之间
    projection_x = x1 + t * (x2 - x1)
    projection_y = y1 + t * (y2 - y1)

    return (x - projection_x) ** 2 + (y - projection_y) ** 2


def point_segment_distance(point, segment_p1, segment_p2):
    """计算点到线段的距离"""
    return math.sqrt(point_segment_distance_sq(point, segment_p1, segment_p2))

def segment_normal(segment_p1, segment_p2):
    """计算线段的法向量 (单位向量，指向外侧)"""
    x1, y1 = segment_p1
    x2, y2 = segment_p2
    dx = x2 - x1
    dy = y2 - y1
    normal_x = -dy
    normal_y = dx
    length = math.sqrt(normal_x**2 + normal_y**2)
    return normal_x / length, normal_y / length


def handle_collision(ball_x, ball_y, ball_speed_x, ball_speed_y, hexagon_points):
    """处理球与六边形墙壁的碰撞"""
    new_ball_speed_x = ball_speed_x
    new_ball_speed_y = ball_speed_y

    collision = False

    for i in range(6):
        p1 = hexagon_points[i]
        p2 = hexagon_points[(i + 1) % 6]

        distance_sq = point_segment_distance_sq((ball_x, ball_y), p1, p2)


        if distance_sq <= ball_radius**2: # 碰撞发生
            collision = True
            normal_x, normal_y = segment_normal(p1, p2)


            # 反射速度向量
            dot_product = ball_speed_x * normal_x + ball_speed_y * normal_y
            new_ball_speed_x -= 2 * dot_product * normal_x
            new_ball_speed_y -= 2 * dot_product * normal_y

            # 应用旋转墙壁的影响
            segment_vector_x = p2[0] - p1[0]
            segment_vector_y = p2[1] - p1[1]
            segment_length = math.sqrt(segment_vector_x**2 + segment_vector_y**2)
            tangent_x = segment_vector_x / segment_length
            tangent_y = segment_vector_y / segment_length


            wall_tangential_speed = hexagon_radius * hexagon_rotation_speed # 墙壁切向速度大小
            # 切向速度方向取决于旋转方向和法线方向，这里简化处理，直接将旋转速度投影到切线方向上，并根据法线方向判断正负
            tangential_speed_component = wall_tangential_speed * (normal_x * tangent_y - normal_y * tangent_x) # 叉积的z分量，用于判断方向


            new_ball_speed_x += rotation_effect_factor * tangential_speed_component * tangent_x
            new_ball_speed_y += rotation_effect_factor * tangential_speed_component * tangent_y


            # 应用弹性系数
            new_ball_speed_x *= elasticity
            new_ball_speed_y *= elasticity

            # 将球推离墙壁，避免粘连 (简单的分离方法)
            distance_to_move = ball_radius - point_segment_distance((ball_x, ball_y), p1, p2)
            ball_x += distance_to_move * normal_x
            ball_y += distance_to_move * normal_y


            break # 一次碰撞只处理一个面


    return ball_x, ball_y, new_ball_speed_x, new_ball_speed_y, collision


# 游戏循环
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 清屏
    screen.fill(black)

    # 计算旋转的六边形顶点
    hexagon_angle += hexagon_rotation_speed
    hexagon_points = calculate_hexagon_points(hexagon_angle)


    # 绘制六边形
    draw_hexagon(hexagon_points)

    # 更新球的位置
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # 重力
    ball_speed_y += gravity

    # 摩擦力 (简单的线性摩擦)
    ball_speed_x *= (1 - friction)
    ball_speed_y *= (1 - friction)


    # 碰撞检测和处理
    ball_x, ball_y, ball_speed_x, ball_speed_y, collision_occurred = handle_collision(ball_x, ball_y, ball_speed_x, ball_speed_y, hexagon_points)


    # 绘制球
    pygame.draw.circle(screen, red, (int(ball_x), int(ball_y)), ball_radius)


    # 更新显示
    pygame.display.flip()

    # 控制帧率
    clock.tick(60) # 每秒 60 帧

pygame.quit()
