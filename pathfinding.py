
import pygame as pg
from os import path
import heapq

vec = pg.math.Vector2


def draw_text(text, size, color, x, y, screen, font_name, align="topleft"):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(**{align: (x, y)})
    screen.blit(text_surface, text_rect)

class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        self.connections = [vec(1, 0), vec(-1, 0), vec(0, 1), vec(0, -1)]
        # comment/uncomment this for diagonals:
        self.connections += [vec(1, 1), vec(-1, 1), vec(1, -1), vec(-1, -1)]

    def in_bounds(self, node):
        return 0 <= node.x < self.width and 0 <= node.y < self.height

    def passable(self, node):
        return node not in self.walls

    def find_neighbors(self, node):
        neighbors = [node + connection for connection in self.connections]
        neighbors = filter(self.in_bounds, neighbors)
        neighbors = filter(self.passable, neighbors)
        return neighbors

    def draw(self):
        for wall in self.walls:
            rect = pg.Rect(wall * TILESIZE, (TILESIZE, TILESIZE))
            pg.draw.rect(screen, LIGHTGRAY, rect)

class WeightedGrid(SquareGrid):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.weights = {}

    def cost(self, from_node, to_node):
        if (vec(to_node) - vec(from_node)).length_squared() == 1:
            return self.weights.get(to_node, 0) + 10
        else:
            return self.weights.get(to_node, 0) + 14

    def draw(self):
        for wall in self.walls:
            rect = pg.Rect(wall * TILESIZE, (TILESIZE, TILESIZE))
            pg.draw.rect(screen, DARKPURPLE, rect)
        for tile in self.weights:
            x, y = tile
            rect = pg.Rect(x * TILESIZE + 3, y * TILESIZE + 3, TILESIZE - 3, TILESIZE - 3)
            pg.draw.rect(screen, FOREST, rect)

class PriorityQueue:
    def __init__(self):
        self.nodes = []

    def put(self, node, cost):
        heapq.heappush(self.nodes, (cost, node))

    def get(self):
        return heapq.heappop(self.nodes)[1]

    def empty(self):
        return len(self.nodes) == 0

def draw_grid():
    SIZE=WIDTH+HEIGHT
    for i in range(0, SIZE, TILESIZE):
        pg.draw.line(screen, CYAN, (i, 0), (i, SIZE))
        pg.draw.line(screen, CYAN, (0, i), (SIZE, i))

def draw_icons():
    start_center = (goal.x * TILESIZE + TILESIZE / 2, goal.y * TILESIZE + TILESIZE / 2)
    screen.blit(ball_img, ball_img.get_rect(center=start_center))
    goal_center = (start.x * TILESIZE + TILESIZE / 2, start.y * TILESIZE + TILESIZE / 2)
    screen.blit(goal_img, goal_img.get_rect(center=goal_center))

def vec2int(v):
    return (int(v.x), int(v.y))

def heuristic(a, b):
    # return abs(a.x - b.x) ** 2 + abs(a.y - b.y) ** 2
    return (abs(a.x - b.x) + abs(a.y - b.y)) * 10

def breadth_first_search(graph, start, end):
    frontier = PriorityQueue()
    frontier.put(vec2int(start), 0)
    path = {vec2int(start): None}
    cost = {vec2int(start): 0}
    while not frontier.empty():
        current = frontier.get()
        if current == end:
            break
        for next in graph.find_neighbors(vec(current)):
            next = vec2int(next)
            next_cost = cost[current] + graph.cost(current, next)
            if next not in cost or next_cost < cost[next]:
                cost[next] = next_cost
                frontier.put(next, cost)
                path[next] = vec(current) - vec(next)
    return path, cost

def a_star_search(graph, start, end):
    frontier = PriorityQueue()
    frontier.put(vec2int(start), 0)
    path = {vec2int(start): None}
    cost = {vec2int(start): 0}
    while not frontier.empty():
        current = frontier.get()
        if current == end:
            break
        for next in graph.find_neighbors(vec(current)):
            next = vec2int(next)
            next_cost = cost[current] + graph.cost(current, next)
            if next not in cost or next_cost < cost[next]:
                cost[next] = next_cost
                priority = next_cost + heuristic(end, vec(next))
                frontier.put(next, priority)
                path[next] = vec(current) - vec(next)
    return path, cost

def greedy_best_first_search(graph, start, end):
    frontier = PriorityQueue()
    frontier.put(vec2int(start), 0)
    path = {vec2int(start): None}
    cost = {vec2int(start): 0}
    while not frontier.empty():
        current = frontier.get()
        if current == end:
            break
        for next in graph.find_neighbors(vec(current)):
            next = vec2int(next)
            next_cost = cost[current] + graph.cost(current, next)
            if next not in cost or next_cost < cost[next]:
                cost[next] = next_cost
                priority = next_cost
                # priority = heuristic(end, vec(next))
                frontier.put(next, priority)
                path[next] = vec(current) - vec(next)
    return path, cost

if __name__ == '__main__':
    TILESIZE = 48
    GRIDWIDTH = 28
    GRIDHEIGHT = 15
    WIDTH = TILESIZE * GRIDWIDTH
    HEIGHT = TILESIZE * GRIDHEIGHT
    FPS = 60
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    FOREST = (34, 57, 10)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    YELLOW = (255, 255, 0)
    DARKGRAY = (40, 40, 40)
    DARKPURPLE = (100, 0, 100)
    MEDGRAY = (75, 75, 75)

    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    font_name = pg.font.match_font('hack')

    icon_dir = path.join(path.dirname(__file__))
    goal_img = pg.image.load(path.join(icon_dir, './Images/goal.png')).convert_alpha()
    goal_img = pg.transform.scale(goal_img, (50, 50))
    # home_img.fill((0, 255, 0, 255), special_flags=pg.BLEND_RGBA_MULT)
    ball_img = pg.image.load(path.join(icon_dir, './Images/ball.png'))
    ball_img = pg.transform.scale(ball_img, (50, 50))
    # cross_img.fill((255, 0, 0, 255), special_flags=pg.BLEND_RGBA_MULT)
    arrows = {}
    arrow_img = pg.image.load(path.join(icon_dir, './Images/arrowLeft.png')).convert_alpha()
    arrow_img = pg.transform.scale(arrow_img, (50, 50))
    for dir in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
        arrows[dir] = pg.transform.rotate(arrow_img, vec(dir).angle_to(vec(1, 0)))

    g = WeightedGrid(GRIDWIDTH, GRIDHEIGHT)
    walls = [(10, 7), (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7), (7, 7), (6, 7), (5, 7), (5, 5), (5, 6), (1, 6), (2, 6), (3, 6), (5, 10), (5, 11), (5, 12), (5, 9), (5, 8), (12, 8), (12, 9), (12, 10), (12, 11), (15, 14), (15, 13), (15, 12), (15, 11), (15, 10), (17, 7), (18, 7), (21, 7), (21, 6), (21, 5), (21, 4), (21, 3), (22, 5), (23, 5), (24, 5), (25, 5), (18, 10), (20, 10), (19, 10), (21, 10), (22, 10), (23, 10), (14, 4), (14, 5), (14, 6), (14, 0), (14, 1), (9, 2), (9, 1), (7, 3), (8, 3), (10, 3), (9, 3), (11, 3), (2, 5), (2, 4), (2, 3), (2, 2), (2, 0), (2, 1), (0, 11), (1, 11), (2, 11), (21, 2), (20, 11), (20, 12), (23, 13), (23, 14), (24, 10), (25, 10), (6, 12), (7, 12), (10, 12), (11, 12), (12, 12), (5, 3), (6, 3), (5, 4)]
    # walls = []
    for wall in walls:
        g.walls.append(vec(wall))
    terrain = [(11, 6), (12, 6), (13, 6), (14, 6), (15, 6), (10, 7), (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7), (16, 8), (15, 8), (14, 8), (13, 8), (12, 8), (11, 8), (10, 8), (11, 9), (12, 9), (13, 9), (14, 9), (15, 9), (11, 10), (12, 10), (13, 10), (14, 10), (15, 10), (12, 11), (13, 11), (14, 11), (12, 5), (13, 5), (14, 5), (11, 5), (15, 5), (12, 4), (13, 4), (14, 4)]
    terrain = []
    for tile in terrain:
        g.weights[tile] = 15

    goal = vec(14, 8)
    start = vec(20, 0)
    search_type = a_star_search
    path, c = search_type(g, goal, start)

    running = True
    while running:
            clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                    if event.key == pg.K_1:
                        search_type = a_star_search
                        path, c = search_type(g, goal, start)
                    if event.key == pg.K_2:
                        search_type = greedy_best_first_search
                        path, c = search_type(g, goal, start)
                    if event.key == pg.K_3:
                        search_type = breadth_first_search
                        path, c = search_type(g, goal, start)
                    if event.key == pg.K_m:
                        # dump the wall list for saving
                        print([(int(loc.x), int(loc.y)) for loc in g.walls])
                if event.type == pg.MOUSEBUTTONDOWN:
                    mpos = vec(pg.mouse.get_pos()) // TILESIZE
                    if event.button == 2:
                        if mpos in g.walls:
                            g.walls.remove(mpos)
                        else:
                            if mpos != start :
                                g.walls.append(mpos)
                    if event.button == 1:
                        if mpos in g.walls:
                            break
                        start = mpos
                    if event.button == 3:
                        goal = mpos
                    path, c = search_type(g, goal, start)

            # pg.display.set_caption("{:.2f}".format(clock.get_fps()))
            pg.display.set_caption("Path Finder")
            screen.fill(BLACK)
            # fill explored area
            for node in path:
                x, y = node
                rect = pg.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
                pg.draw.rect(screen, MEDGRAY, rect)
            draw_grid()
            g.draw()
            # draw path from start to goal
            current = start # + path[vec2int(start)]
            l = 0
            try:
                while current != goal:
                    if (current.x, current.y) in path:
                        v = path[(current.x, current.y)]
                    if v.length_squared() == 1:
                        l += 10
                    else:
                        l += 14
                    img = arrows[vec2int(v)]
                    x = current.x * TILESIZE + TILESIZE / 2
                    y = current.y * TILESIZE + TILESIZE / 2
                    r = img.get_rect(center=(x, y))
                    screen.blit(img, r)
                    # find next in path
                    current = current + path[vec2int(current)]
            except :
                pass
            draw_icons()
            draw_text(search_type.__name__, 30, WHITE, WIDTH - 10, HEIGHT - 10, screen, font_name, align="bottomright")
            draw_text('Path length:{}'.format(l), 30, WHITE, WIDTH - 10, HEIGHT - 45, screen, font_name, align="bottomright")
            pg.display.flip()
