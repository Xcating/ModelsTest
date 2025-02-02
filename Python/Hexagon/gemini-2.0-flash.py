import pygame
import math
import numpy as np

# 初始化 Pygame
pygame.init()

# 设置显示窗口
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("六边形弹球")

# 定义颜色
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)

# 球的属性
ball_radius = 15
ball_position = np.array([screen_width / 2, screen_height / 2], dtype=float)
ball_velocity = np.array([2, 3], dtype=float)  # 初始速度
gravity = np.array([0, 0.5], dtype=float)    # 向下的重力
friction = 0.01                            # 摩擦力系数
bounce_damping = 0.8                       # 碰撞阻尼

# 六边形属性
hexagon_radius = 200
hexagon_center = np.array([screen_width / 2, screen_height / 2], dtype=float)
hexagon_rotation_speed = 0.01  # 速度（弧度/帧）
hexagon_angle = 0


def create_hexagon_vertices(center, radius, angle):
    """创建旋转六边形的顶点"""
    vertices = []
    for i in range(6):
        angle_rad = angle + 2 * math.pi * i / 6
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)
        vertices.append(np.array([x, y], dtype=float))
    return vertices


def draw_hexagon(vertices):
    """绘制六边形"""
    pygame.draw.polygon(screen, white, vertices, 2)


def collide_with_hexagon(ball_pos, ball_radius, hexagon_vertices):
    """检查球是否与六边形碰撞，如果碰撞则返回碰撞法线和碰撞深度"""
    min_depth = float('inf')
    collision_normal = np.array([0, 0], dtype=float)
    
    for i in range(6):
        start_vertex = hexagon_vertices[i]
        end_vertex = hexagon_vertices[(i + 1) % 6]

        # 边缘向量
        edge_vector = end_vertex - start_vertex

        # 将顶点与球心连接的向量
        ball_to_start = ball_pos - start_vertex

        # 计算正交的法向量
        edge_normal = np.array([-edge_vector[1], edge_vector[0]], dtype=float)
        edge_normal = edge_normal / np.linalg.norm(edge_normal)
        
        # 计算球心和边缘之间的距离
        distance = np.dot(ball_to_start, edge_normal)
        
        if distance < ball_radius:
          
          if ball_radius - distance < min_depth:
              min_depth = ball_radius - distance
              collision_normal = edge_normal

    if min_depth < float('inf'): #碰撞
      return collision_normal, min_depth 
    else:
      return None, None # 不碰撞

def handle_collision(ball_pos, ball_vel, collision_normal, depth):
    """处理碰撞：反射速度，并防止重叠"""
    
    # 分解球的速度分量为：垂直于碰撞面和沿着碰撞面
    normal_component = np.dot(ball_vel, collision_normal) * collision_normal
    tangent_component = ball_vel - normal_component

    # 反射速度向量
    new_velocity = tangent_component - (bounce_damping * normal_component)

    # 把球从碰撞面移出，避免球体在碰撞后继续进入多边形内
    ball_pos += collision_normal * depth
    
    return ball_pos, new_velocity

# 主循环
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. 更新球的位置和速度
    ball_velocity += gravity
    ball_position += ball_velocity
    
    # 应用摩擦力
    speed = np.linalg.norm(ball_velocity)
    if speed > 0:
      friction_force = -ball_velocity / speed * friction
      ball_velocity += friction_force

    # 2. 更新六边形角度
    hexagon_angle += hexagon_rotation_speed

    # 3. 创建六边形顶点
    hexagon_vertices = create_hexagon_vertices(hexagon_center, hexagon_radius, hexagon_angle)

    # 4. 检测与六边形的碰撞
    collision_normal, depth = collide_with_hexagon(ball_position, ball_radius, hexagon_vertices)
    
    # 5. 处理碰撞，调整速度和位置
    if collision_normal is not None:
      ball_position, ball_velocity = handle_collision(ball_position, ball_velocity, collision_normal, depth)
      
    # 6. 绘制
    screen.fill(black)
    draw_hexagon(hexagon_vertices)
    pygame.draw.circle(screen, blue, ball_position.astype(int), ball_radius)  # 使用整数坐标进行绘制
    
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)


pygame.quit()
