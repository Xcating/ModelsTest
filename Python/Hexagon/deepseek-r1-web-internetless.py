import pygame
import math
import sys

def point_to_segment_distance(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p

    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay

    t = (apx * abx + apy * aby) / (abx**2 + aby**2 + 1e-8)
    t = max(0.0， min(1.0, t))

    closest_x = ax + t * abx
    closest_y = ay + t * aby

    dx = px - closest_x
    dy = py - closest_y
    distance = math.hypot(dx, dy)

    return distance, (closest_x, closest_y)

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing Ball in Rotating Hexagon")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

center = (width//2, height//2)
hex_radius = 200
num_sides = 6
rotate_speed = 1
rotate_angle = 0

ball_radius = 15
ball_pos = [center[0], center[1]-100]
ball_velocity = [2, 0]
gravity = 0.2
restitution = 0.8
friction = 0.95

hex_vertices_local = []
for i in range(num_sides):
    theta = math.radians(i*60)
    x = hex_radius * math.cos(theta)
    y = hex_radius * math.sin(theta)
    hex_vertices_local.append((x, y))

hex_edges_normals = []
for i in range(num_sides):
    a = hex_vertices_local[i]
    b = hex_vertices_local[(i+1)%num_sides]
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = math.hypot(dy, -dx)
    normal = (dy/length, -dx/length) if length != 0 else (0,0)
    hex_edges_normals.append(normal)

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    rotate_angle = (rotate_angle + rotate_speed) % 360
    theta_rad = math.radians(rotate_angle)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)

    current_hex_vertices = []
    for x, y in hex_vertices_local:
        x_rot = x*cos_theta - y*sin_theta
        y_rot = x*sin_theta + y*cos_theta
        current_hex_vertices.append((center[0]+x_rot, center[1]+y_rot))

    ball_velocity[1] += gravity

    dx = ball_pos[0] - center[0]
    dy = ball_pos[1] - center[1]
    x_local = dx*cos_theta + dy*sin_theta
    y_local = -dx*sin_theta + dy*cos_theta

    collisions = []
    for i in range(num_sides):
        a = hex_vertices_local[i]
        b = hex_vertices_local[(i+1)%num_sides]
        normal = hex_edges_normals[i]

        distance, _ = point_to_segment_distance((x_local, y_local), a, b)
        vec_ax = x_local - a[0]
        vec_ay = y_local - a[1]
        dot_product = vec_ax*normal[0] + vec_ay*normal[1]

        if distance < ball_radius and dot_product < 0:
            collisions.append((distance, i))

    if collisions:
        collisions.sort()
        min_distance, i = collisions[0]
        normal = hex_edges_normals[i]

        move_distance = ball_radius - min_distance
        new_x_local = x_local - normal[0]*move_distance
        new_y_local = y_local - normal[1]*move_distance

        new_x_global = center[0] + new_x_local*cos_theta - new_y_local*sin_theta
        new_y_global = center[1] + new_x_local*sin_theta + new_y_local*cos_theta
        ball_pos = [new_x_global, new_y_global]

        vx, vy = ball_velocity
        v_local_x = vx*cos_theta + vy*sin_theta
        v_local_y = -vx*sin_theta + vy*cos_theta

        vn_dot = v_local_x*normal[0] + v_local_y*normal[1]
        vn_x = vn_dot*normal[0]
        vn_y = vn_dot*normal[1]
        vt_x = v_local_x - vn_x
        vt_y = v_local_y - vn_y

        vn_new_x = -vn_x * restitution
        vn_new_y = -vn_y * restitution
        vt_new_x = vt_x * friction
        vt_new_y = vt_y * friction

        v_new_local_x = vn_new_x + vt_new_x
        v_new_local_y = vn_new_y + vt_new_y

        v_new_global_x = v_new_local_x*cos_theta - v_new_local_y*sin_theta
        v_new_global_y = v_new_local_x*sin_theta + v_new_local_y*cos_theta
        ball_velocity = [v_new_global_x, v_new_global_y]

    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]

    screen.fill(BLACK)
    pygame.draw.polygon(screen, WHITE, current_hex_vertices, 2)
    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
