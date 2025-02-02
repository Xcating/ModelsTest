'''
Crafting the simulation

Thinking through a Python program to model a ball bouncing in a rotating hexagon. Considering gravity, friction, and realistic wall collisions, I’m planning to use Pygame for the animation.

Mapping out the system

I'm honing in on how systematically adjusting friction influences the ball's speed, how to track collisions with a rotating hexagon, and ensuring the ball's bounce feels natural within this dynamic.

Adjusting for dynamics

I'm refining the collision response by considering the hexagon's rotation. By factoring in the wall's velocity at the collision point, I aim to ensure realistic and dynamic interactions for the ball.

Mapping the trajectory

I’m considering a simpler collision approach by rotating the coordinate system with the hexagon, while carefully analyzing the ball's trajectory under gravity and friction to ensure accurate movement.

Calculating collision

I'm digging into collision detection by identifying if the ball is within a safe zone and measuring the minimum distance to each hexagon wall, identifying potential bounces.

Transforming collision dynamics

I’m gathering info on how the hexagon's rotation changes the ball wall interaction, using reflection and factoring in the wall's velocity for a nuanced collision response.

Calculating wall velocity

OK, let me see. I'm considering the hexagon's rotation to estimate wall velocity at collision points. This will refine collision mechanics and enhance overall ball movement accuracy.

Integrating physical principles

I’m working on including gravity and friction in the collision dynamics, applying a damping factor to velocity and modeling friction as a force, ensuring continuous adjustment of the ball's movement.

Examining dynamic friction

I'm noting the challenge of simulating friction as a velocity-dependent force, considering air resistance as a subtle but persistent factor, ultimately applying a damping factor each frame.

Setting up the simulation

I'm using Pygame to model the simulation, organizing parameters like constants for gravity and friction, and aligning hexagon coordinates for dynamic movement within the window.

Tracking hexagon movement

I’m calculating hexagon rotation using angular speed and adjusting the ball's velocity, factoring in gravity and a damping factor to simulate continuous friction.

Pinpointing collisions and wall movement

I’m identifying collision points by checking distances to hexagon walls and considering the wall's velocity from rotation to enhance realism in the simulation.

Mapping the ball's motion

OK, let me see. I'm analyzing the ball's relative velocity to the hexagon wall, determining if it's moving inward, and figuring out the normal vector to assess collision dynamics.

Spotting inward normals

First, I’m pulling together the edge vector and identifying candidate normals. Then, I check which normal points inward by testing their dot products, leading to collision detection and velocity adjustments.

Ensuring collision handling

OK, let’s think it through: I’m thinking about handling collisions with multiple walls each frame to prevent the ball from getting stuck in a corner, while maintaining simulation accuracy.

Crafting the simulation

I’m pulling together classes and functions to simulate collisions and bounces. This includes computing relative velocities, handling complex collisions, and ensuring precise object movements within Pygame.

Simplifying calculations

I’m digging into using pygame.math.Vector2 to handle vector calculations for positions and velocities, streamlining the simulation code.

Setting simulation parameters

I’m finalizing the simulation setup, including ball and hexagon details, gravity, rotation, damping, and friction factors, ensuring realistic dynamics and computational efficiency.

Implementing friction dynamics

I’m working through simulating friction using 1 - friction * dt to achieve a more realistic velocity decay. This approach effectively replicates air resistance in the simulation.

Adjusting ball dynamics

I'm calculating collisions with hexagon walls, determining penetration depth and normal, and adjusting ball velocity to ensure it bounces off walls with the correct rebound.

Mapping out collision handling

I’m working through managing multiple collision detections each frame, applying continuous friction for energy loss, and ensuring accurate hexagon rotation and relative collisions.

Streamlining collision detection

I’m aiming to simplify collision responses by iteratively updating the ball's position and velocity for each edge, ensuring the simulation processes collisions more efficiently.

Reasoned about ball bouncing simulation，持续 32 秒 
'''
import pygame
import math
import sys

# -------------------------------
# 辅助函数：计算点到线段的最近点
# -------------------------------
def closest_point_on_segment(P, A, B):
    """
    给定点 P 和线段 AB，返回 P 在 AB 上的最近点。
    """
    AB = B - A
    if AB.length_squared() == 0:
        return A
    t = (P - A).dot(AB) / AB.length_squared()
    t = max(0, min(1, t))
    return A + AB * t

# -------------------------------
# 主程序入口
# -------------------------------
def main():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("旋转六边形内的弹跳小球")
    clock = pygame.time.Clock()

    # -------------------------------
    # 物理参数设置
    # -------------------------------
    ball_radius = 10
    # 初始位置设在屏幕中央，初始速度随意
    ball_pos = pygame.math.Vector2(WIDTH/2, HEIGHT/2)
    ball_vel = pygame.math.Vector2(200, -250)  # 单位：像素/秒

    gravity = pygame.math.Vector2(0, 500)  # 重力加速度，单位：像素/秒^2
    friction_coeff = 0.1  # 空气摩擦系数（每秒衰减比例），模拟空气阻力
    restitution = 0.9   # 碰撞回复系数（0为完全无弹性，1为完全弹性）

    # -------------------------------
    # 六边形参数
    # -------------------------------
    hex_center = pygame.math.Vector2(WIDTH/2, HEIGHT/2)
    hex_radius = 250  # 六边形的外接圆半径
    num_sides = 6
    rotation_angle = 0.0  # 初始旋转角度（弧度）
    rotation_speed = math.radians(30)  # 旋转角速度，30°/秒

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # 每帧的时间，单位：秒

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 更新六边形旋转角度
        rotation_angle += rotation_speed * dt

        # 更新小球物理（重力和空气摩擦）
        ball_vel += gravity * dt
        # 这里使用线性摩擦因子，每秒减少 friction_coeff 比例的速度
        ball_vel *= (1 - friction_coeff * dt)
        ball_pos += ball_vel * dt

        # -------------------------------
        # 计算六边形的顶点（按顺时针或逆时针排列均可）
        # -------------------------------
        vertices = []
        for i in range(num_sides):
            angle = rotation_angle + i * (2 * math.pi / num_sides)
            vertex = hex_center + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * hex_radius
            vertices.append(vertex)

        # -------------------------------
        # 检测并处理小球与六边形边界的碰撞
        # -------------------------------
        for i in range(num_sides):
            A = vertices[i]
            B = vertices[(i + 1) % num_sides]

            # 求球心到边 AB 的最近点
            cp = closest_point_on_segment(ball_pos, A, B)
            diff = ball_pos - cp
            dist = diff.length()

            if dist < ball_radius:
                # 计算碰撞法向量（指向六边形内部）
                if dist == 0:
                    # 避免除零（这里任取一个法向量，指向六边形中心）
                    n = (hex_center - cp).normalize()
                else:
                    n = diff.normalize()

                # 将法向量调整为指向内部：检查 cp 到 hex_center 的方向
                if (hex_center - cp).dot(n) < 0:
                    n = -n

                # 计算碰撞处六边形边界的瞬时速度
                # 六边形整体以 rotation_speed 绕中心旋转，所以 cp 的速度为：
                # v_wall = ω × r，其中 r = cp - hex_center
                r = cp - hex_center
                # 2D 旋转的叉乘效果： v_wall = (-ω * r.y, ω * r.x)
                wall_vel = pygame.math.Vector2(-rotation_speed * r.y, rotation_speed * r.x)

                # 计算小球相对于墙的相对速度
                rel_vel = ball_vel - wall_vel
                vn = rel_vel.dot(n)
                if vn < 0:  # 小球正朝向墙壁
                    # 反射相对于墙的速度
                    rel_vel = rel_vel - (1 + restitution) * vn * n
                    # 还原到绝对速度
                    ball_vel = rel_vel + wall_vel

                # 将小球挤出墙外，避免穿透（按法向量方向移动）
                penetration = ball_radius - dist
                ball_pos += n * penetration

        # -------------------------------
        # 绘制部分
        # -------------------------------
        screen.fill((30, 30, 30))  # 深色背景

        # 绘制旋转的六边形（连线）
        hex_points = [(v.x, v.y) for v in vertices]
        pygame.draw.polygon(screen, (200, 200, 200), hex_points, width=3)

        # 绘制小球
        pygame.draw.circle(screen, (255, 100, 100), (int(ball_pos.x), int(ball_pos.y)), ball_radius)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
