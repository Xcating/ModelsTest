import pygame
import math

# 初始化 Pygame
pygame.init()

# 设置屏幕尺寸
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# 定义颜色
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# 六边形参数
hexagon_radius = 200
hexagon_center = (screen_width // 2, screen_height // 2)
hexagon_rotation_speed = 0.01  # 弧度/帧

# 球的参数
ball_radius = 20
ball_position = [hexagon_center[0], hexagon_center[1] - hexagon_radius + ball_radius + 10]
ball_velocity = [0, 0]  # 初始速度
gravity = 0.5
friction = 0.99  # 摩擦系数（略小于 1 以使球最终停止）
bounce_factor = -0.7  # 反弹系数

# 六边形顶点计算函数
def calculate_hexagon_vertices(center, radius, rotation_angle):
    vertices = []
    for i in range(6):
        angle = rotation_angle + i * math.pi / 3
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        vertices.append([x, y])
    return vertices

# 游戏时钟
clock = pygame.time.Clock()

# 旋转角度
rotation_angle = 0

# 主循环
running = True
while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新旋转角度
    rotation_angle += hexagon_rotation_speed

    # 计算六边形顶点
    hexagon_vertices = calculate_hexagon_vertices(hexagon_center, hexagon_radius, rotation_angle)

    # 更新球的速度（重力）
    ball_velocity[1] += gravity

    # 更新球的位置
    ball_position[0] += ball_velocity[0]
    ball_position[1] += ball_velocity[1]

    # 碰撞检测（与六边形边）
    for i in range(6):
        v1 = hexagon_vertices[i]
        v2 = hexagon_vertices[(i + 1) % 6]

        # 计算从顶点到球的法线向量
        line_vector = [v2[0] - v1[0], v2[1] - v1[1]]
        ball_to_v1 = [ball_position[0] - v1[0], ball_position[1] - v1[1]]

        # 使用点积查找线向量的归一化
        magnitude = math.sqrt(line_vector[0] ** 2 + line_vector[1] ** 2)
        if magnitude == 0:
            continue # 避免被零除
        line_unit = [line_vector[0] / magnitude, line_vector[1] / magnitude]

        # 法线单位向量
        normal_unit = [line_unit[1], -line_unit[0]]

        # 将球到 v1 的向量投影到法线上
        projection = normal_unit[0] * ball_to_v1[0] + normal_unit[1] * ball_to_v1[1]

        # 如果球在墙后面（投影 < 0）且在墙附近（投影 < ball_radius）
        if projection < 0 and projection > -ball_radius:
            # 检查是否在边的范围内（使用点积）
            dot_product = line_unit[0] * ball_to_v1[0] + line_unit[1] * ball_to_v1[1]

            if 0 < dot_product < magnitude:
                # 碰撞！
                # 将速度投影到法线上
                velocity_projection = normal_unit[0] * ball_velocity[0] + normal_unit[1] * ball_velocity[1]

                # 反转并衰减法向速度分量
                ball_velocity[0] -= 2 * velocity_projection * normal_unit[0] * -bounce_factor
                ball_velocity[1] -= 2 * velocity_projection * normal_unit[1] * -bounce_factor

                # 纠正球的位置以防止其粘在墙上
                ball_position[0] += normal_unit[0] * (ball_radius - projection)
                ball_position[1] += normal_unit[1] * (ball_radius - projection)

    # 应用摩擦力
    ball_velocity[0] *= friction
    ball_velocity[1] *= friction

    # 清空屏幕
    screen.fill(black)

    # 绘制六边形
    pygame.draw.polygon(screen, white, hexagon_vertices, 2)

    # 绘制球
    pygame.draw.circle(screen, red, (int(ball_position[0]), int(ball_position[1])), ball_radius)

    # 更新显示
    pygame.display.flip()

    # 限制帧速率
    clock.tick(60)  # 60 帧每秒

# 退出 Pygame
pygame.quit()
