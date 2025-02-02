import pygame
import math

# 初始化 Pygame
pygame.init()

# 设置窗口尺寸
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("弹跳球 - 旋转六边形")

# 颜色常量
BACKGROUND_COLOR = (0, 0, 0)
HEX_COLOR = (255, 255, 255)
BALL_COLOR = (255, 0, 0)

# 物理参数
GRAVITY = 0.5
RESTITUTION = 0.8
FRICTION = 0.95

class RotatingHexagon:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        self.rotation = 0
        self.rotation_speed = 1  # 度/帧

    def get_vertices(self):
        vertices = []
        for i in range(6):
            angle_deg = self.rotation + i * 60
            angle_rad = math.radians(angle_deg)
            x = self.center[0] + self.radius * math.cos(angle_rad)
            y = self.center[1] + self.radius * math.sin(angle_rad)
            vertices.append((x, y))
        return vertices

    def update(self):
        self.rotation = (self.rotation + self.rotation_speed) % 360

class BouncingBall:
    def __init__(self, position, radius):
        self.position = list(position)
        self.velocity = [0, 0]
        self.radius = radius

    def update(self, gravity):
        self.velocity[1] += gravity
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

    def handle_collision(self, edge, hex_center, rotation_speed):
        p1, p2 = edge
        # 计算边中点和法线方向
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        dx = hex_center[0] - mx
        dy = hex_center[1] - my
        length = math.hypot(dx, dy)
        if length == 0:
            return
        nx = dx / length
        ny = dy / length

        # 计算到边的距离
        px = self.position[0] - mx
        py = self.position[1] - my
        distance = px * nx + py * ny

        if distance < -self.radius:
            # 修正位置
            penetration = -distance - self.radius
            self.position[0] += penetration * nx
            self.position[1] += penetration * ny

            # 计算边线速度
            omega = math.radians(rotation_speed)
            edge_vel_x = -omega * (my - hex_center[1])
            edge_vel_y = omega * (mx - hex_center[0])

            # 计算相对速度
            rel_vel_x = self.velocity[0] - edge_vel_x
            rel_vel_y = self.velocity[1] - edge_vel_y

            # 分解速度
            normal_vel = (rel_vel_x * nx + rel_vel_y * ny)
            tangent_vel_x = rel_vel_x - normal_vel * nx
            tangent_vel_y = rel_vel_y - normal_vel * ny

            # 计算新速度
            new_rel_vel_x = -RESTITUTION * normal_vel * nx + FRICTION * tangent_vel_x
            new_rel_vel_y = -RESTITUTION * normal_vel * ny + FRICTION * tangent_vel_y

            self.velocity[0] = new_rel_vel_x + edge_vel_x
            self.velocity[1] = new_rel_vel_y + edge_vel_y

# 初始化对象
hexagon = RotatingHexagon((WIDTH//2, HEIGHT//2), 250)
ball = BouncingBall((WIDTH//2, HEIGHT//2), 20)

# 设置初始速度
ball.velocity = [5, -10]

# 主循环
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新对象状态
    hexagon.update()
    ball.update(GRAVITY)

    # 获取当前六边形顶点
    vertices = hexagon.get_vertices()
    edges = [(vertices[i], vertices[(i+1)%6]) for i in range(6)]

    # 处理碰撞
    for edge in edges:
        ball.handle_collision(edge, hexagon.center, hexagon.rotation_speed)

    # 绘制画面
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.polygon(screen, HEX_COLOR, vertices, 2)
    pygame.draw.circle(screen, BALL_COLOR, 
                      (int(ball.position[0]), int(ball.position[1])), 
                      ball.radius)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
