import pygame
import math
import sys

# 初始化 Pygame
pygame.init()

# 设置窗口尺寸和标题
WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("旋转六边形内的弹跳球")

# 设置颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 设置帧率
FPS = 60
clock = pygame.time.Clock()

# 物理参数
GRAVITY = 500  # 像素每秒²
FRICTION = 0.99  # 摩擦因子
ELASTICITY = 0.9  # 弹性系数

# 球的参数
BALL_RADIUS = 15
BALL_COLOR = RED

# 六边形参数
HEXAGON_RADIUS = 200
HEXAGON_COLOR = WHITE
ROTATION_SPEED = math.radians(30)  # 每秒旋转30度

class Ball:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, GRAVITY)
    
    def update(self, dt):
        # 更新速度和位置
        self.vel += self.acc * dt
        self.vel *= FRICTION
        self.pos += self.vel * dt
    
    def draw(self, surface):
        pygame.draw.circle(surface, BALL_COLOR, (int(self.pos.x), int(self.pos.y)), BALL_RADIUS)

class Hexagon:
    def __init__(self, center, radius):
        self.center = pygame.math.Vector2(center)
        self.radius = radius
        self.angle = 0  # 当前旋转角度
        self.vertices = self.calculate_vertices()
    
    def calculate_vertices(self):
        vertices = []
        for i in range(6):
            angle = self.angle + math.pi / 3 * i
            x = self.center.x + self.radius * math.cos(angle)
            y = self.center.y + self.radius * math.sin(angle)
            vertices.append(pygame.math.Vector2(x, y))
        return vertices
    
    def rotate(self, dt):
        self.angle += ROTATION_SPEED * dt
        self.vertices = self.calculate_vertices()
    
    def draw(self, surface):
        pygame.draw.polygon(surface, HEXAGON_COLOR, [(v.x, v.y) for v in self.vertices], 2)

    def get_edges(self):
        edges = []
        for i in range(6):
            start = self.vertices[i]
            end = self.vertices[(i + 1) % 6]
            edges.append((start, end))
        return edges

def detect_collision(ball, hexagon):
    for edge_start, edge_end in hexagon.get_edges():
        edge = edge_end - edge_start
        edge_length = edge.length()
        edge_dir = edge.normalize()

        # 计算从边起点到球的向量
        to_ball = ball.pos - edge_start

        # 计算距离
        proj_length = to_ball.dot(edge_dir)
        proj_length = max(0, min(edge_length, proj_length))
        closest_point = edge_start + edge_dir * proj_length
        distance = (ball.pos - closest_point).length()

        if distance < BALL_RADIUS:
            # 计算法线
            normal = (ball.pos - closest_point).normalize()

            # 墙壁的切向量
            tangent = pygame.math.Vector2(-normal.y, normal.x)

            # 墙壁的速度（由于旋转）
            wall_velocity = tangent * ROTATION_SPEED * hexagon.radius

            # 球的速度相对于墙壁
            relative_velocity = ball.vel - wall_velocity

            # 分离速度分量
            vel_along_normal = relative_velocity.dot(normal)

            if vel_along_normal < 0:
                # 反弹
                ball.vel -= (1 + ELASTICITY) * vel_along_normal * normal

                # 摩擦力
                vel_tangent = relative_velocity.dot(tangent)
                ball.vel -= vel_tangent * tangent * (1 - FRICTION)
                
                # 将球的位置调整到不与墙壁重叠
                overlap = BALL_RADIUS - distance
                ball.pos += normal * overlap

def main():
    # 创建球和六边形
    ball = Ball(WIDTH / 2, HEIGHT / 2)
    hexagon = Hexagon(center=(WIDTH / 2, HEIGHT / 2), radius=HEXAGON_RADIUS)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000  # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 更新六边形的旋转
        hexagon.rotate(dt)

        # 更新球的位置
        ball.update(dt)

        # 检测并响应碰撞
        detect_collision(ball, hexagon)

        # 绘制
        WINDOW.fill(BLACK)
        hexagon.draw(WINDOW)
        ball.draw(WINDOW)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
