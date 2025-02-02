'''
Setting up the scene

I’m planning a Python script with Pygame, crafting an animation of a ball bouncing within a rotating hexagon, incorporating gravity and friction effects.

Rotating the hexagon

I’m thinking about collision detection with a rotating hexagon. By defining it in local coordinates and rotating it incrementally, I can use vector math to check if the ball interacts with the hexagon's boundaries.

Mapping the process

I’m outlining a Pygame script to animate a ball in a rotating hexagon, highlighting gravity, friction, and collision detection with hexagon edges using points and normals from each line segment.

Adjusting ball behavior

OK, let me see. I’m piecing together collision handling by adjusting the ball's position and updating its velocity with gravity and friction, ensuring it bounces correctly off hexagon edges.

Translating assistance

I’m working on assembling a Pygame script in Chinese, creating an animation of a ball rebounding within a spinning hexagon with gravity and friction, covering every aspect from setup to collision handling.

Crafting the hexagon

I’m tweaking Pygame to animate a ball within a spinning hexagon, adjusting velocity with friction and gravity, and ensuring collision detection with hexagon edges each frame.

已推理，持续 2m 45s
'''
import pygame
import math
import sys

# ========== 参数全局设置 ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 重力加速度（像素/帧^2, 可根据需求调整）
GRAVITY = 0.5
# 摩擦力因子(每帧速度乘以该因子，略微衰减)
FRICTION_FACTOR = 0.999
# 弹性系数(球与墙碰撞时速度保留的比例)
RESTITUTION = 0.9

# 墙壁的旋转速度(弧度/帧)
ANGULAR_SPEED = 0.02

# 小球初始设置
BALL_RADIUS = 20
INITIAL_BALL_X = 0
INITIAL_BALL_Y = -100  # 稍微在屏幕中心上方
INITIAL_VX = 5
INITIAL_VY = 0

# ========== 初始化Pygame ==========
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("球在旋转六边形内弹跳 - 演示")
clock = pygame.time.Clock()

# ========== 准备六边形原始坐标(以(0,0)为中心) ==========
# 正六边形每条边与中心的距离(此值可自行调大/调小)
HEX_RADIUS = 200
# 计算六个顶点(正六边形每相邻顶点间夹角 60度)
original_hex_points = []
for i in range(6):
    angle = math.radians(60 * i)
    x = HEX_RADIUS * math.cos(angle)
    y = HEX_RADIUS * math.sin(angle)
    original_hex_points.append((x, y))

def rotate_point(x, y, theta):
    """ 以(0,0)为中心旋转坐标 (x,y) """
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    x_new = x * cos_t - y * sin_t
    y_new = x * sin_t + y * cos_t
    return x_new, y_new

def vector_length(vx, vy):
    return math.sqrt(vx*vx + vy*vy)

def normalize(vx, vy):
    """ 将向量归一化 """
    length = vector_length(vx, vy)
    if length == 0:
        return 0.0, 0.0
    return vx / length, vy / length

def reflect_velocity(ball_vx, ball_vy, nx, ny, restitution):
    """
    将速度 (ball_vx, ball_vy) 关于法线 (nx, ny) 进行反射,
    并乘以弹性系数 restitution
    """
    # 先将 (nx, ny) 归一化
    nx, ny = normalize(nx, ny)
    # 计算法线方向的分量
    v_dot_n = ball_vx * nx + ball_vy * ny
    # 反射后 = 原速度 - 2*(投影到法线上的分量)
    rx = ball_vx - 2 * v_dot_n * nx
    ry = ball_vy - 2 * v_dot_n * ny
    # 乘以弹性系数
    rx *= restitution
    ry *= restitution
    return rx, ry

def wall_point_velocity(rx, ry, omega):
    """
    计算墙壁某点速度:
    对半径向量 (rx, ry) 进行 垂直方向旋转 并乘以角速度
    2D中 "omega &times; r" 可视为在Z方向, 
    结果在XY平面计算等效 (vx = -omega * ry, vy = omega * rx)
    """
    vx = -omega * ry
    vy = omega * rx
    return vx, vy

def closest_point_on_segment(px, py, x1, y1, x2, y2):
    """
    计算点 (px, py) 到线段 (x1,y1)-(x2,y2) 的最近点
    返回 (cx, cy) 为线段上距离 (px, py) 最近的点坐标
    """
    # 线段向量
    seg_vx = x2 - x1
    seg_vy = y2 - y1
    # 点到线段起点向量
    pt_vx = px - x1
    pt_vy = py - y1

    seg_len_sq = seg_vx * seg_vx + seg_vy * seg_vy
    if seg_len_sq == 0:
        # 避免线段退化成一个点
        return x1, y1

    t = (pt_vx * seg_vx + pt_vy * seg_vy) / seg_len_sq
    # 限制 t 在 [0, 1]
    t = max(0, min(1, t))

    cx = x1 + seg_vx * t
    cy = y1 + seg_vy * t
    return cx, cy

def main():
    # 小球初始状态
    ball_x = INITIAL_BALL_X
    ball_y = INITIAL_BALL_Y
    ball_vx = INITIAL_VX
    ball_vy = INITIAL_VY

    # 六边形旋转角度
    theta = 0.0

    running = True
    while running:
        dt = clock.tick(FPS)  # 帧间隔(ms)
        dt_sec = dt / 1000.0  # 换算成秒可做更精准的物理计算(当前简化用帧为单位)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 1) 旋转角度更新
        theta += ANGULAR_SPEED

        # 2) 重力 & 摩擦力
        #    (在这里将 dt_sec 视为1帧，忽略更高精度)
        ball_vy += GRAVITY
        ball_vx *= FRICTION_FACTOR
        ball_vy *= FRICTION_FACTOR

        # 3) 更新小球位置
        ball_x += ball_vx
        ball_y += ball_vy

        # 4) 旋转后的六边形顶点
        hex_points = []
        for (ox, oy) in original_hex_points:
            rx, ry = rotate_point(ox, oy, theta)
            hex_points.append((rx, ry))

        # 5) 碰撞检测(对六条边)
        for i in range(6):
            # 当前顶点
            x1, y1 = hex_points[i]
            # 下一顶点(首尾相连)
            x2, y2 = hex_points[(i+1) % 6]

            # 找到球心到该线段的最近点
            cx, cy = closest_point_on_segment(ball_x, ball_y, x1, y1, x2, y2)
            dx = ball_x - cx
            dy = ball_y - cy
            dist_sq = dx*dx + dy*dy
            if dist_sq <= BALL_RADIUS*BALL_RADIUS:
                dist = math.sqrt(dist_sq)
                if dist == 0:
                    # 防止出现除0
                    dist = 0.001
                # 法线方向
                nx = dx / dist
                ny = dy / dist

                # —————————— 考虑旋转墙壁的速度 ——————————
                # 1) 线段中点到中心的大概向量(可用碰撞点到中心替代)
                #    以便估计碰撞点相对于中心的半径向量
                rx_coll = cx
                ry_coll = cy
                # 2) 墙壁碰撞点的速度
                vw_x, vw_y = wall_point_velocity(rx_coll, ry_coll, ANGULAR_SPEED)
                # 3) 小球与墙壁的相对速度
                rel_vx = ball_vx - vw_x
                rel_vy = ball_vy - vw_y
                # 4) 对相对速度做反射(法线)
                new_rel_vx, new_rel_vy = reflect_velocity(rel_vx, rel_vy, nx, ny, RESTITUTION)
                # 5) 小球最终速度 = 墙壁速度 + 反射后的相对速度
                ball_vx = vw_x + new_rel_vx
                ball_vy = vw_y + new_rel_vy

                # 碰撞修正：把球推离墙壁，避免粘住
                overlap = BALL_RADIUS - dist
                ball_x += nx * overlap
                ball_y += ny * overlap

        # ========== 绘制部分 ==========
        screen.fill((30, 30, 30))  # 背景深灰

        # 先把六边形顶点变换到屏幕坐标(中心在屏幕中心)
        screen_hex_points = []
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        for (rx, ry) in hex_points:
            scr_x = center_x + rx
            scr_y = center_y + ry
            screen_hex_points.append((scr_x, scr_y))

        # 画旋转六边形
        pygame.draw.polygon(screen, (0, 180, 240), screen_hex_points, width=2)

        # 画小球(注意小球在屏幕中心需要平移)
        draw_ball_x = center_x + ball_x
        draw_ball_y = center_y + ball_y
        pygame.draw.circle(screen, (255, 50, 50), (int(draw_ball_x), int(draw_ball_y)), BALL_RADIUS)

        # 显示
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
