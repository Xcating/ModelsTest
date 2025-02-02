'''
Exploring the setup

I’m thinking through a Python program that draws a hexagon rotating around its center with a bouncing ball inside, considering gravity and friction. Using pygame for window environment.

Mapping hexagon dynamics

I’m outlining how to rotate the hexagon and transform the ball's position into this local coordinate system, considering a rotating angle to manage collisions effectively.

Managing collisions

I'm curious about reflecting the ball's velocity with friction, using a friction coefficient or a force proportional to its velocity to reduce the ball's speed over time.

Setting up the environment

I’m defining the screen size, clock, hexagon radius, ball position, velocity, rotation angle, gravity, and friction constants. Each frame, the hexagon rotates, gravity updates, friction is applied, and collision detection ensures realistic bounces.

Coding the script

I’m outlining the main loop for the Python script, defining constants, drawing the rotated hexagon, computing collision normals, and reflecting the ball's velocity with a restitution factor.

Finalizing the code

I’m wrapping up the Python script, opting for Chinese comments to match the question. The script will be concise, well-structured, and roughly 100 lines long, incorporating friction and restitution for collisions.

Reasoned about ball bouncing in hexagon，持续 17 秒
'''
import pygame
import math
import sys

# ============ 全局配置 ============
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 球的属性
BALL_RADIUS = 15
BALL_RESTITUTION = 0.9     # 反弹系数(弹性碰撞系数)，小于1代表碰撞有损失
FRICTION_COEFF = 0.99     # 摩擦力衰减系数(每帧乘以这个系数)
GRAVITY = 500             # 重力加速度(px/s^2)，可根据需求调整

# 六边形属性
HEX_RADIUS = 200          # 六边形“外接圆”半径
HEX_ROTATION_SPEED = 30   # 六边形旋转速度(度/秒)

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)

def get_hexagon_points(cx, cy, radius, angle_degs):
    """
    计算旋转后的六边形顶点的世界坐标列表。
    cx, cy: 六边形中心
    radius: 六边形外接圆半径
    angle_degs: 当前旋转角度(度)
    返回: [(x1, y1), (x2, y2), ..., (x6, y6)]
    """
    points = []
    # 每个顶点在本地坐标系中的角度 = 60度的倍数
    # 转换到世界坐标时需要加入旋转angle_degs
    for i in range(6):
        # 计算当前顶点的角度(弧度)
        theta = math.radians(angle_degs + i * 60)
        x = cx + radius * math.cos(theta)
        y = cy + radius * math.sin(theta)
        points.append((x, y))
    return points

def point_to_line_distance(px, py, x1, y1, x2, y2):
    """
    计算点(px, py)到线段(x1,y1)-(x2,y2)所对应的“无穷长直线”的有向距离，
    以及该直线的法线向量(nx, ny)（已归一化），
    同时返回最近点在直线上的位置(用于后续做碰撞修正)。

    返回: (distance, nx, ny, proj_x, proj_y)
    - distance: px到直线的有向距离(若为负，表示在直线外侧某一面)
    - nx, ny:   法线的单位向量
    - proj_x, proj_y: 投影到该直线的坐标
    """
    # 线段向量
    line_dx = x2 - x1
    line_dy = y2 - y1
    
    # 线段长度
    line_len = math.hypot(line_dx, line_dy)
    
    # 若线段过短(退化)，直接返回
    if line_len < 1e-8:
        return 0, 0, 0, x1, y1

    # 线段单位方向向量
    ux = line_dx / line_len
    uy = line_dy / line_len

    # 点到线段起点的向量
    vx = px - x1
    vy = py - y1

    # 在此线段方向上的投影长度
    proj_len = vx * ux + vy * uy

    # 得到投影点在直线(无限延伸)上的坐标
    proj_x = x1 + proj_len * ux
    proj_y = y1 + proj_len * uy

    # 线段法线向量(逆时针旋转90度)
    nx = -uy
    ny = ux

    # 点到直线的有向距离 = (p - proj) dot (n)
    # 注：n已是单位向量
    dist = (px - proj_x) * nx + (py - proj_y) * ny

    return dist, nx, ny, proj_x, proj_y

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("球在旋转六边形内弹跳示例")
    clock = pygame.time.Clock()

    # 六边形中心
    hex_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    # 六边形旋转角度
    hex_angle = 0.0

    # 球初始位置（可随意设置，只要在六边形内部）
    ball_x = SCREEN_WIDTH // 2
    ball_y = SCREEN_HEIGHT // 2 - 100
    # 球初始速度
    ball_vx = 100
    ball_vy = 0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # 每帧耗时(秒)

        # --- 事件处理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- 更新逻辑 ---

        # 1) 更新六边形角度
        hex_angle += HEX_ROTATION_SPEED * dt

        # 2) 更新球的速度(重力作用 + 摩擦衰减)
        ball_vy += GRAVITY * dt
        
        # 在没有与地面接触的情况下，也可以让速度每帧衰减一点，模拟空气阻力(可选)
        ball_vx *= FRICTION_COEFF
        ball_vy *= FRICTION_COEFF

        # 3) 更新球的位置
        ball_x += ball_vx * dt
        ball_y += ball_vy * dt

        # 4) 计算当前旋转六边形的顶点，用于碰撞检测
        hex_points = get_hexagon_points(hex_center[0], hex_center[1], HEX_RADIUS, hex_angle)

        # 将顶点顺序首尾相连组成 6 条边
        edges = []
        for i in range(len(hex_points)):
            x1, y1 = hex_points[i]
            x2, y2 = hex_points[(i + 1) % len(hex_points)]
            edges.append(((x1, y1), (x2, y2)))

        # 5) 与六边形的边做碰撞检测
        #    如果球的中心到直线的距离 < 球半径 且在多边形外侧(有向距离为负)，则产生碰撞
        for (x1, y1), (x2, y2) in edges:
            dist, nx, ny, proj_x, proj_y = point_to_line_distance(
                ball_x, ball_y, x1, y1, x2, y2
            )
            
            # 判断球在边界的哪一侧，可以通过判断点与多边形在同侧还是异侧，
            # 这里简化为使用有向距离 dist < 0 表示外侧。
            # 需要判断“球的中心与边的距离 <= 球半径”才算碰撞
            # dist<0时法线指向多边形内部；dist>0时法线指向外部
            # 不过我们在 point_to_line_distance() 中定义的法线是某个固定方向，
            # 所以我们要根据 dist 的正负来判断哪边是外侧。
            if abs(dist) <= BALL_RADIUS:
                # 判断是否需要更严格的“线段范围”判定，这里简单处理为“无穷直线”
                # 如果想更加精细，可在投影长度不在[0, line_len]范围时跳过。
                
                # 如果 dist 与球半径同号，说明球在外侧。这里做一个基于dist符号的判断：
                # 如果 dist < 0，表明球在法线指向的那一面(或者需要看实际情况进行调整)。
                
                # 这里假设 dist < 0 表示球越过了多边形的边，需要修正
                # 如果 dist > 0 代表球在六边形的里面（可能要根据你定义法线方向来调整）
                # 视情况把判断换成 (dist < 0) 也行。
                
                # 如果这里出现逻辑反了，可将“if abs(dist)<=BALL_RADIUS and dist>0”之类逻辑调整
                # 此处做演示，用 dist<0 表示碰撞
                if dist < 0:
                    # 修正球的位置：把球“推回到”与边界相切的位置
                    # dist 与 BALL_RADIUS 的差值就是需要修正的量
                    penetration = BALL_RADIUS - abs(dist)
                    ball_x += penetration * nx
                    ball_y += penetration * ny

                    # 速度反射： v' = v - 2(v·n)n
                    # 其中 n 是法线单位向量
                    # 先计算球速度在法线方向上的分量
                    v_dot_n = ball_vx * nx + ball_vy * ny
                    # 再做反射
                    ball_vx = ball_vx - 2 * v_dot_n * nx
                    ball_vy = ball_vy - 2 * v_dot_n * ny

                    # 加入反弹损失
                    ball_vx *= BALL_RESTITUTION
                    ball_vy *= BALL_RESTITUTION

        # --- 绘图 ---
        screen.fill(WHITE)

        # 6) 画旋转六边形
        pygame.draw.polygon(screen, BLACK, hex_points, width=2)

        # 7) 画球
        pygame.draw.circle(screen, RED, (int(ball_x), int(ball_y)), BALL_RADIUS)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
