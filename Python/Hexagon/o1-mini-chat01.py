import pygame
import math
import sys

# 初始化 Pygame
pygame.init()

# 屏幕尺寸
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("旋转六边形内弹跳的球")

clock = pygame.time.Clock()

# 六边形参数
hex_center = pygame.math.Vector2(WIDTH/2, HEIGHT/2)
hex_radius = 250  # 六边形外接圆半径
hex_sides = 6
rotation_angle = 0.0          # 当前六边形旋转角度（弧度）
angular_velocity = 0.01       # 六边形旋转角速度（正值为逆时针旋转）

# 小球参数
ball_radius = 10
ball_pos = pygame.math.Vector2(WIDTH/2, HEIGHT/2 - 100)
ball_vel = pygame.math.Vector2(3, 0)   # 初始速度
gravity = pygame.math.Vector2(0, 0.5)    # 重力加速度（向下）
air_friction = 0.999                   # 模拟空气阻力（每帧乘以该因子）

# 碰撞参数
restitution = 0.9      # 法向反弹系数（0~1，1为完全弹性碰撞）
collision_friction = 0.9  # 碰撞时切向速度的保留比例

def get_hexagon_vertices(center, radius, sides, angle_offset):
    """返回六边形各顶点的列表，每个顶点为 pygame.math.Vector2 对象"""
    vertices = []
    for i in range(sides):
        theta = angle_offset + (2 * math.pi * i) / sides
        x = center.x + radius * math.cos(theta)
        y = center.y + radius * math.sin(theta)
        vertices.append(pygame.math.Vector2(x, y))
    return vertices

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def resolve_collision_with_edge(ball_pos, ball_vel, ball_radius, edge_start, edge_end, hex_center, omega):
    """
    检查小球是否与一条边碰撞，如有碰撞则调整速度和位置。
    返回调整后 (ball_pos, ball_vel) 以及是否发生碰撞的标志。
    """
    edge_vec = edge_end - edge_start
    edge_length_sq = edge_vec.length_squared()
    if edge_length_sq == 0:
        return ball_pos, ball_vel, False

    # 计算球心到边起点的向量
    w = ball_pos - edge_start
    # 在边上的投影参数（限制在[0,1]内）
    t = clamp(w.dot(edge_vec) / edge_length_sq, 0, 1)
    closest_point = edge_start + edge_vec * t
    diff = ball_pos - closest_point
    dist = diff.length()

    if dist < ball_radius:
        # 计算穿透深度
        penetration = ball_radius - dist
        # 如果球心正好在边上，防止除零
        if dist != 0:
            collision_normal = diff.normalize()
        else:
            # 若重合则使用边的法向（稍微偏离即可）
            collision_normal = pygame.math.Vector2(-edge_vec.y, edge_vec.x).normalize()

        # 计算边的内侧法向
        # 内侧方向应当指向六边形中心，所以选择与 (center - edge_mid) 同向的法向
        edge_mid = (edge_start + edge_end) * 0.5
        inward_normal = pygame.math.Vector2(-edge_vec.y, edge_vec.x).normalize()
        if (hex_center - edge_mid).dot(inward_normal) < 0:
            inward_normal = -inward_normal

        # 为保证碰撞反弹方向正确，我们选择使球心从边外“弹回”的法向，
        # 如果 diff 与 inward_normal 夹角过大，则用 inward_normal 作为碰撞法向
        if collision_normal.dot(inward_normal) < 0.5:
            collision_normal = inward_normal

        # 计算当前边上碰撞点处由于六边形旋转产生的速度
        # 旋转六边形的刚体运动：给定角速度 omega，任一点的速度为 ω 叉 (point - center)
        # 对二维，叉乘结果为： v = (-omega * (y - cy), omega * (x - cx))
        rel_point = closest_point - hex_center
        wall_vel = pygame.math.Vector2(-omega * rel_point.y, omega * rel_point.x)

        # 计算相对速度（小球速度相对于边的速度）
        rel_vel = ball_vel - wall_vel

        # 仅当小球正朝向墙壁时才处理碰撞（v·n < 0）
        if rel_vel.dot(collision_normal) < 0:
            # 分解相对速度为法向分量和切向分量
            vn = collision_normal * rel_vel.dot(collision_normal)
            vt = rel_vel - vn

            # 反弹后，法向分量反向（乘以反弹系数），切向分量衰减（模拟摩擦）
            vn_after = -restitution * vn
            vt_after = collision_friction * vt

            rel_vel_after = vn_after + vt_after

            # 更新小球速度，加上墙壁的速度
            new_ball_vel = wall_vel + rel_vel_after

            # 修正小球位置，将其推出边界
            new_ball_pos = ball_pos + collision_normal * penetration

            return new_ball_pos, new_ball_vel, True

    return ball_pos, ball_vel, False

def main():
    global rotation_angle, ball_pos, ball_vel

    running = True
    while running:
        dt = clock.tick(60)  # 帧率60 FPS

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 更新六边形旋转角度
        rotation_angle += angular_velocity

        # 更新小球运动：加上重力，加上空气阻力
        ball_vel += gravity
        ball_vel *= air_friction
        ball_pos += ball_vel

        # 获取当前六边形顶点（随旋转更新）
        vertices = get_hexagon_vertices(hex_center, hex_radius, hex_sides, rotation_angle)

        # 对于六边形的每一条边，检测并处理碰撞
        # 注意：如果一次帧内小球可能同时与多个边发生穿透，建议多次迭代碰撞处理
        collision_happened = True
        iterations = 0
        while collision_happened and iterations < 5:
            collision_happened = False
            for i in range(hex_sides):
                start_point = vertices[i]
                end_point = vertices[(i+1) % hex_sides]
                new_pos, new_vel, collided = resolve_collision_with_edge(ball_pos, ball_vel, ball_radius, start_point, end_point, hex_center, angular_velocity)
                if collided:
                    ball_pos, ball_vel = new_pos, new_vel
                    collision_happened = True
            iterations += 1

        # 绘制背景
        screen.fill((30, 30, 30))

        # 绘制六边形边框
        points = [(v.x, v.y) for v in vertices]
        pygame.draw.polygon(screen, (200, 200, 200), points, 3)

        # 绘制小球
        pygame.draw.circle(screen, (255, 100, 100), (int(ball_pos.x), int(ball_pos.y)), ball_radius)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
