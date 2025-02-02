'''
Crafting the ball simulation

I’m using Python and Pygame to create a realistic simulation of a ball inside a rotating hexagon, considering gravity, friction, and collision with rotating walls.

Tackling hexagon rotation

I’m simulating a ball inside a rotating hexagon in Pygame. I’m working out the hexagon's orientation and looking at collision detection with moving boundaries.

Adjusting my approach

I’m translating the ball's position to fit the hexagon's rotated frame. Calculating collisions and realistic bounces involves considering the ball's velocity relative to the rotating boundary.

Integrating rotational nuances

Combining rotational wall velocity with collision dynamics, I’m calculating the ball's relative velocity to derive realistic bounce outcomes. Reflecting the ball's velocity against the wall's approach is key.

Simulating dynamics

I'm mapping out how friction and gravity influence the ball's movement, adjusting tangential speed with a damping coefficient and incorporating a coefficient of restitution for realistic wall bounces.

Structuring the simulation

I’m outlining a Pygame-based simulation, detailing the ball's class and movement, collision detection with a rotating hexagon, and ensuring the ball remains within the hexagon's boundaries.

Handling collisions

I’m thinking through how to manage the ball's swift movements and multiple collisions with the hexagon's edges, ensuring accurate velocity reflections to keep it within boundaries.

Calculating collision dynamics

I’m thinking through the inner normal by rotating edge vectors 90 degrees and adjusting directions to pinpoint collision points. Velocity reflections are then calculated based on these interactions.

Honing collision response

I’m refining how friction and restitution affect a collision by tweaking the ball's tangential and normal velocities, ensuring a smoother simulation outcome.

Balancing restitution and friction

I’m setting restitution to 0.9 and friction to 0.98, updating relative velocities post-collision, and ensuring the ball stays positioned to prevent sticking.

Reasoned about ball bounce simulation，持续 17 秒
'''
import pygame, sys, math
from pygame.math import Vector2

# ------------------------------
# 参数设置
# ------------------------------
WIDTH, HEIGHT = 800, 600            # 窗口大小
FPS = 60                            # 帧率

# 六边形参数
HEX_RADIUS = 250                    # 六边形半径（从中心到顶点的距离）
hex_center = Vector2(WIDTH/2, HEIGHT/2)
hex_rotation_speed = math.radians(20)   # 每秒旋转角度（以弧度计）

# 小球参数
BALL_RADIUS = 10
ball_pos = Vector2(WIDTH/2, HEIGHT/2 - 100)
ball_vel = Vector2(120, 0)          # 初始速度（像素/秒）
gravity = Vector2(0, 300)           # 重力加速度（像素/秒^2）
air_friction = 0.999               # 每帧空气阻力衰减系数

# 碰撞物理参数
restitution = 0.9       # 法向反弹系数（能量损失）
wall_friction = 0.98    # 撞击时切向摩擦

# ------------------------------
# 工具函数：计算六边形顶点
# ------------------------------
def get_hexagon_vertices(center, radius, rotation):
    """返回旋转后的六边形顶点列表（顺时针或逆时针均可，只要内侧在多边形内部）"""
    vertices = []
    for i in range(6):
        angle = math.radians(60 * i) + rotation
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        vertices.append(Vector2(x, y))
    return vertices

# ------------------------------
# 碰撞检测和响应：球与一条边
# ------------------------------
def collide_ball_edge(ball_pos, ball_vel, ball_radius, A, B, center, omega):
    """
    检查小球与边AB是否碰撞，若碰撞则更新速度和位置
    参数：
      ball_pos: Vector2 球中心位置
      ball_vel: Vector2 球速度（单位：像素/秒）
      ball_radius: 球半径
      A, B: Vector2 边的两个端点
      center: Vector2 六边形中心，用于确定“内侧”方向
      omega: 当前六边形的角速度（弧度/秒）
    返回：(new_ball_pos, new_ball_vel, collided)
    """
    edge = B - A
    edge_len_sq = edge.length_squared()
    if edge_len_sq == 0:
        return ball_pos, ball_vel, False

    # 求球心到直线的投影参数 t
    t = (ball_pos - A).dot(edge) / edge_len_sq
    # 限制 t 在 [0,1] 内，得到边上的最近点
    t = max(0, min(1, t))
    nearest = A + t * edge
    dist_vec = ball_pos - nearest
    dist = dist_vec.length()

    if dist >= ball_radius:
        return ball_pos, ball_vel, False  # 未碰撞

    # 碰撞发生：计算边的内侧法向
    # 先构造边的法向 candidate = (edge.y, -edge.x)
    n = Vector2(edge.y, -edge.x)
    # 判断 n 是否指向六边形内部：若 (center - A) 与 n 夹角大于 90° 则反向
    if (center - A).dot(n) < 0:
        n = -n
    n = n.normalize()

    # 计算墙面局部运动速度：由于六边形绕中心旋转，
    # 任一点 p（此处取最近碰撞点）处的速度为 v_wall = omega x (p - center)
    # 在二维中： v_wall = omega * (- (p - center).y, (p - center).x)
    r = nearest - center
    v_wall = Vector2(-omega * r.y, omega * r.x)

    # 计算相对碰撞速度
    v_rel = ball_vel - v_wall

    # 分解相对速度为法向和切向分量
    v_rel_n = n * v_rel.dot(n)
    v_rel_t = v_rel - v_rel_n

    # 碰撞反应：反转法向分量，并加入能量损失；切向分量乘以摩擦系数
    v_rel_n_new = -restitution * v_rel_n
    v_rel_t_new = wall_friction * v_rel_t
    v_rel_new = v_rel_n_new + v_rel_t_new

    new_ball_vel = v_rel_new + v_wall

    # 为防止穿透，将球位置调整到刚好在碰撞面上
    penetration = ball_radius - dist
    new_ball_pos = ball_pos + n * penetration

    return new_ball_pos, new_ball_vel, True

# ------------------------------
# 主程序
# ------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("球在旋转六边形内弹跳")
    clock = pygame.time.Clock()

    # 初始六边形旋转角度
    hex_rotation = 0

    # 使用局部变量保存小球的位置和速度
    pos = ball_pos.copy()
    vel = ball_vel.copy()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000  # 帧时间（秒）

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ------------------------------
        # 更新物理：重力、空气阻力
        # ------------------------------
        vel += gravity * dt
        vel *= air_friction  # 连续空气阻力
        pos += vel * dt

        # 更新六边形的旋转角度
        hex_rotation += hex_rotation_speed * dt
        # 获取当前旋转六边形顶点
        hex_vertices = get_hexagon_vertices(hex_center, HEX_RADIUS, hex_rotation)

        # ------------------------------
        # 检测小球与六边形各边的碰撞
        # ------------------------------
        collision_happened = False
        # 六边形边按顶点顺序依次连接，注意最后一条边为最后一个顶点到第一个顶点
        for i in range(len(hex_vertices)):
            A = hex_vertices[i]
            B = hex_vertices[(i+1) % len(hex_vertices)]
            pos, vel, collided = collide_ball_edge(pos, vel, BALL_RADIUS, A, B, hex_center, hex_rotation_speed)
            if collided:
                collision_happened = True
                # 若有碰撞，可考虑只响应一次；这里继续检测所有边（对于极端情况可能有多个碰撞）
                # 可添加 break 以只响应第一个碰撞
                # break

        # ------------------------------
        # 绘制
        # ------------------------------
        screen.fill((30, 30, 30))

        # 绘制六边形
        pygame.draw.polygon(screen, (200, 200, 200), [(v.x, v.y) for v in hex_vertices], width=3)

        # 绘制小球
        pygame.draw.circle(screen, (255, 100, 100), (int(pos.x), int(pos.y)), BALL_RADIUS)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
