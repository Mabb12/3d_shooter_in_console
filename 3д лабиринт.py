import sys
import math
import os
import time
import keyboard
from heapq import heappush, heappop

# Размеры лабиринта
MAZE_WIDTH = 11
MAZE_HEIGHT = 11

# # — стена, . — пустое пространство
maze = [
    ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
    ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
    ["#", ".", ".", "#", ".", ".", "#", "#", "#", "#", "#"],
    ["#", ".", ".", "#", ".", ".", ".", ".", ".", ".", "#"],
    ["#", ".", ".", "#", ".", ".", ".", ".", ".", ".", "#"],
    ["#", ".", ".", "#", ".", ".", ".", ".", ".", ".", "#"],
    ["#", ".", ".", "#", ".", ".", ".", ".", ".", ".", "#"],
    ["#", ".", ".", "#", ".", ".", ".", ".", ".", ".", "#"],
    ["#", ".", ".", "#", ".", ".", ".", ".", ".", "L", "#"],
    ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
]

# Позиция и направление игрока
player_x = 1.5
player_y = 1.5
player_angle = 0  # Направление взгляда
player_health = 100  # Хп

# Монстры
monsters = [
    {"x": 1.6, "y": 5.5, "alive": True},
    {"x": 4.5, "y": 6.5, "alive": True},
    {"x": 8.5, "y": 8.5, "alive": True},
    {"x": 9.5, "y": 9.5, "alive": True},
]

# Пуля
bullet = {"x": None, "y": None, "angle": None, "active": False}

# Параметры отображения
FOV = math.pi / 3  # Поле зрения
SCREEN_WIDTH = 80  # Ширина консоли
SCREEN_HEIGHT = 24  # Высота консоли

angle_step = FOV / SCREEN_WIDTH

# Текстура монстра
MONSTER_ART = [
    "   ▄████▄▄  ",
    "  ▄▀█▀▐└─┐  ",
    "  █▄▐▌▄█▄┘  ",
    "  └▄▄▄▄─┘   ",
    "▄██████████▄",
    "▒▒█▄████▄█▒▒",
    "  ███▀▀███  ",
    " ▄███  ███▄ ",
]

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(maze, start, goal):
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Возможные движения
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < len(maze) and 0 <= neighbor[1] < len(maze[0]):
                if maze[neighbor[0]][neighbor[1]] == "#":
                    continue  # Стена
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))
    return None  # Путь не найден

def move_monsters():
    global monsters, player_x, player_y
    player_pos = (int(player_y), int(player_x))  # Позиция игрока в сетке

    for monster in monsters:
        if monster["alive"]:
            monster_pos = (int(monster["y"]), int(monster["x"]))  # Позиция монстра в сетке
            path = a_star(maze, monster_pos, player_pos)
            if path and len(path) > 1:
                next_pos = path[1]  # Следующая позиция на пути
                monster["x"] = next_pos[1] + 0.1
                monster["y"] = next_pos[0] + 0.1

def check_player_damage():
    global player_x, player_y, player_health
    for monster in monsters:
        if monster["alive"]:
            dx = monster["x"] - player_x
            dy = monster["y"] - player_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 0.5:  #Если монстр рядом с игроком
                player_health -= 1
                print(f"Игрок получил урон! Здоровье: {player_health}")
                if player_health <= 0:
                    print("Игрок погиб!")
                    sys.exit()

def next_level():
    print("Вы перешли на следующий уровень")
    time.sleep(2)
    global maze, monsters, player_x, player_y, player_angle, player_health
    player_health = 100  
    player_x, player_y = 1.5, 1.5  # Сброс позиции игрока
    player_angle = 0  # Сброс угла

    # Новая карта
    maze = [
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
        ["#", ".", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", ".", "#"],
        ["#", ".", "#", ".", ".", ".", ".", ".", ".", ".", ".", "#", ".", "#"],
        ["#", ".", "#", ".", "#", "#", "#", "#", "#", "#", ".", "#", ".", "#"],
        ["#", ".", "#", ".", "#", ".", ".", ".", ".", "#", ".", "#", ".", "#"],
        ["#", ".", "#", ".", "#", ".", "#", "#", ".", "#", ".", "#", ".", "#"],
        ["#", ".", "#", ".", "#", ".", "#", ".", ".", ".", ".", "#", ".", "#"],
        ["#", ".", "#", ".", "#", ".", "#", "#", "#", "#", "#", "#", ".", "#"],
        ["#", ".", "#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
        ["#", ".", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", ".", "#"],
        ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ]

    monsters = [
        {"x": 1.5, "y": 5.5, "alive": True},
        {"x": 5.5, "y": 5.5, "alive": True},
        {"x": 8.5, "y": 8.5, "alive": True},
        {"x": 12.5, "y": 12.5, "alive": True},
        {"x": 10.5, "y": 10.5, "alive": True},
    ]

def cast_ray(angle):
    ray_dir_x = math.cos(angle)
    ray_dir_y = math.sin(angle)

    # Начальная позиция луча
    ray_x = player_x
    ray_y = player_y

    # Шаг для проверки пересечения с сеткой
    delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else 1e30
    delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else 1e30

    # Направление шага
    step_x = 1 if ray_dir_x > 0 else -1
    step_y = 1 if ray_dir_y > 0 else -1

    # Расстояние до следующего пересечения с сеткой
    side_dist_x = (int(ray_x) + (1 if ray_dir_x > 0 else 0) - ray_x) * delta_dist_x
    side_dist_y = (int(ray_y) + (1 if ray_dir_y > 0 else 0) - ray_y) * delta_dist_y

    while True:
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            ray_x += step_x
            side = 0  # Горизонтальное пересечение
        else:
            side_dist_y += delta_dist_y
            ray_y += step_y
            side = 1  # Вертикальное пересечение

        # Если игрок со стеной коснулся
        if maze[int(ray_y)][int(ray_x)] == "#":
            break

    # Расстояние до стены
    if side == 0:
        return abs((ray_x - player_x) / ray_dir_x) if ray_dir_x != 0 else 1e30
    else:
        return abs((ray_y - player_y) / ray_dir_y) if ray_dir_y != 0 else 1e30

def can_move(new_x, new_y):
    for dx in [-0.1, 0.1]:
        for dy in [-0.1, 0.1]:
            if maze[int(new_y + dy)][int(new_x + dx)] == "#":
                return False
    return True

def move_bullet():
    global bullet
    if bullet["active"]:
        # Двигает пулю вперед
        bullet["x"] += math.cos(bullet["angle"]) * 0.5
        bullet["y"] += math.sin(bullet["angle"]) * 0.5

        # Столкновение со стеной пули
        if maze[int(bullet["y"])][int(bullet["x"])] == "#":
            bullet["active"] = False  # Пуля исчезает при столкновении со стеной

        # Столкновение с монстром
        for monster in monsters:
            if monster["alive"]:
                dx = monster["x"] - bullet["x"]
                dy = monster["y"] - bullet["y"]
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < 0.5:  # Пуля попала в монстра
                    monster["alive"] = False
                    bullet["active"] = False
                    print("Монстр уничтожен!")

def render():
    screen = [[' ' for _ in range(SCREEN_WIDTH)] for _ in range(SCREEN_HEIGHT)]

    for x in range(SCREEN_WIDTH):
        ray_angle = player_angle - FOV / 2 + x * angle_step
        distance = cast_ray(ray_angle)

        # Корректировка расстояния
        distance *= math.cos(player_angle - ray_angle)

        # Высота стены на экране
        wall_height = int(SCREEN_HEIGHT / (distance + 0.0001))

        # Яркость стены
        if distance < 2:
            wall_char = "█"  # Близко — белый
        elif distance < 4:
            wall_char = "▓"  # Средняя яркость
        elif distance < 8:
            wall_char = "▒"  # Средняя темнота
        elif distance < 16:
            wall_char = "░"  # Далеко — серый
        else:
            wall_char = " "  # Очень далеко — ничего не видно

        # Отрисовка столбца
        for y in range(SCREEN_HEIGHT):
            if y < (SCREEN_HEIGHT - wall_height) // 2:
                screen[y][x] = " "  # Пустое пространство над стеной
            elif y < (SCREEN_HEIGHT + wall_height) // 2:
                screen[y][x] = wall_char  # Стена
            else:
                screen[y][x] = "."  # Пустое пространство под стеной

    # Отрисовка монстров
    for monster in monsters:
        if monster["alive"]:
            dx = monster["x"] - player_x
            dy = monster["y"] - player_y
            distance_to_monster = math.sqrt(dx * dx + dy * dy)
            angle_to_monster = math.atan2(dy, dx) - player_angle

            # Нормализует угол
            if angle_to_monster < -math.pi:
                angle_to_monster += 2 * math.pi
            if angle_to_monster > math.pi:
                angle_to_monster -= 2 * math.pi

            if abs(angle_to_monster) < FOV / 2:
                # Проверка на монстра за стеной
                ray_distance = cast_ray(math.atan2(dy, dx))
                if ray_distance < distance_to_monster:
                    continue  # Монстр за стеной

                screen_x = int((angle_to_monster + FOV / 2) / FOV * SCREEN_WIDTH)
                screen_y = (SCREEN_HEIGHT + wall_height) // 4

                # Масштабирование монстра
                scale = max(1, int(distance_to_monster))
                scaled_art = [line[::scale] for line in MONSTER_ART[::scale]]

                # Отрисовка
                for i, line in enumerate(scaled_art):
                    for j, char in enumerate(line):
                        if 0 <= screen_x + j < SCREEN_WIDTH and 0 <= screen_y + i < SCREEN_HEIGHT:
                            screen[screen_y + i][screen_x + j] = char

    # Отрисовка пули (не работает)
    if bullet["active"]:
        bullet_screen_x = int((math.atan2(bullet["y"] - player_y, bullet["x"] - player_x) - player_angle + FOV / 2) / FOV * SCREEN_WIDTH)
        bullet_screen_y = SCREEN_HEIGHT // 2
        if 0 <= bullet_screen_x < SCREEN_WIDTH and 0 <= bullet_screen_y < SCREEN_HEIGHT:
            screen[bullet_screen_y][bullet_screen_x] = "*"

    # Вывод
    os.system('cls' if os.name == 'nt' else 'clear')
    for row in screen:
        print("".join(row))

def shoot():
    global monsters

    # Попал ли игрок в монстра
    for monster in monsters:
        if monster["alive"]:
            dx = monster["x"] - player_x
            dy = monster["y"] - player_y
            distance = math.sqrt(dx * dx + dy * dy)

            # Угол до монстра
            angle_to_monster = math.atan2(dy, dx) - player_angle

            if angle_to_monster < -math.pi:
                angle_to_monster += 2 * math.pi
            if angle_to_monster > math.pi:
                angle_to_monster -= 2 * math.pi

            if abs(angle_to_monster) < 0.1 and distance < 2:
                monster["alive"] = False
                print("Монстр уничтожен!")

def check_stairs():
    global player_x, player_y
    if maze[int(player_y)][int(player_x)] == "L":
        next_level()

def main():
    global player_x, player_y, player_angle, player_health

    while True:
        # Обработка нажатий клавиш
        if keyboard.is_pressed('w'):  # Движение вперед
            new_x = player_x + math.cos(player_angle) * 0.2
            new_y = player_y + math.sin(player_angle) * 0.2
            if can_move(new_x, new_y):  # Нет ли стены
                player_x, player_y = new_x, new_y
        if keyboard.is_pressed('s'):  # Движение назад
            new_x = player_x - math.cos(player_angle) * 0.2
            new_y = player_y - math.sin(player_angle) * 0.2
            if can_move(new_x, new_y):  
                player_x, player_y = new_x, new_y
        if keyboard.is_pressed('a'):  # Поворот влево
            player_angle -= 0.1
        if keyboard.is_pressed('d'):  # Поворот вправо
            player_angle += 0.1
        if keyboard.is_pressed(' '):  # Стрельба
            shoot()

        # Движение монстров
        move_monsters()

        # Проверка урона игроку
        check_player_damage()

        # Проверка, находится ли игрок на лестнице
        check_stairs()

        # Рендер кадра
        render()
        time.sleep(0.03)  

if __name__ == "__main__":
    main()