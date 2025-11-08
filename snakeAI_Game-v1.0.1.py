# 文件名: user_game_main.py
# 依赖: pygame, numpy
# 运行: python user_game_main.py

import sys
import random
import time
import numpy as np
import pygame
from pygame import mixer

# ---------------------------
# 游戏主类
# ---------------------------
class SnakeGame:
    def __init__(self, seed=0, board_size=50, silent_mode=False):
        """
        初始化游戏
        seed: 随机种子
        board_size: 棋盘边长（格子数）
        silent_mode: True 时不初始化 pygame 显示（便于无界面测试）
        """
        # 设置棋盘的大小，表示棋盘边长（格子数）
        self.board_size = board_size

        # 计算总的格子数，棋盘上的格子总数 = 边长的平方
        self.grid_size = self.board_size ** 2

        # 设置每个格子的像素大小，影响游戏的视觉表现
        self.cell_size = 20

        # 计算整个棋盘的宽度和高度，基于棋盘的格子数和每个格子的像素大小
        self.width = self.height = self.board_size * self.cell_size

        # 设置边框的大小，用于容纳其他显示元素，如按钮、分数等
        self.border_size = 40

        # 计算显示区域的宽度，包括边框和控制面板的空白区域
        self.display_width = self.width + 2 * self.border_size + 240

        # 计算显示区域的高度，包括顶部/底部边框、分数条
        self.display_height = self.height + 2 * self.border_size + 40

        self.silent_mode = silent_mode
        if not silent_mode:
            pygame.init()
            pygame.display.set_caption("贪吃蛇（可接入 AI）")
            self.screen = pygame.display.set_mode((self.display_width, self.display_height))
            self.font = pygame.font.SysFont("SimHei", 24)
            self.large_font = pygame.font.SysFont("SimHei", 30)

            # 尝试加载声音文件（若不存在则忽略）
            try:
                mixer.init()
                self.sound_eat = mixer.Sound("sound/eat.wav")
                self.sound_game_over = mixer.Sound("sound/game_over.wav")
                self.sound_count = mixer.Sound("sound/count.wav")
            except Exception:
                self.sound_eat = None
                self.sound_game_over = None
                self.sound_count = None
        else:
            self.screen = None
            self.font = None
            self.large_font = None
            self.sound_eat = None
            self.sound_game_over = None
            self.sound_count = None

        self.snake = None
        self.non_snake = None
        self.direction = None
        self.score = 0
        self.food = None
        self.seed_value = seed
        random.seed(seed)  # 设置随机种子
        np.random.seed(seed)

        self.reset()

    def reset(self):
        """重置游戏：生成初始蛇与食物"""
        # 使蛇位于中心并朝下（3 节）
        mid = self.board_size // 2
        # 玩家蛇
        self.snake = [(mid + i, mid) for i in range(1, -2, -1)]
        self.non_snake = set((r, c) for r in range(self.board_size) for c in range(self.board_size) if (r, c) not in self.snake)
        self.direction = "DOWN"          # 玩家蛇初始方向
        self.food = self._generate_food()
        self.score = 0
        self.death_reason = None

    def reset_opponent_mode(self):
        """重置对抗模式游戏状态"""
        # 使蛇位于中心并朝下（3 节）
        mid = self.board_size // 2
        # 玩家蛇
        self.snake = [(mid + i, mid) for i in range(1, -2, -1)]
        # 对抗蛇
        self.opponent_snake = [(mid + i + 5, mid) for i in range(1, -2, -1)]  # 让对抗蛇在另一位置
        # 合并两条蛇的位置到non_snake集合
        all_snake_positions = set(self.snake + self.opponent_snake)
        self.non_snake = set((r, c) for r in range(self.board_size) for c in range(self.board_size) if (r, c) not in all_snake_positions)
        self.direction = "DOWN"          # 玩家蛇初始方向
        self.opponent_direction = "UP"   # 对抗蛇初始方向（与玩家相反）
        self.opponent_dead = False       # 对抗蛇死亡状态标记
        self.death_reason = None         # 死亡原因记录
        self.food = self._generate_food()
        self.score = 0

    def step(self, action):
        """
        执行一步：
        action: -1（不变/无输入），或 0:UP,1:LEFT,2:RIGHT,3:DOWN
        返回: done(bool), info(dict)
        """
        if action != -1:
            self._update_direction(action)

        # 当前蛇头位置
        row, col = self.snake[0]
        if self.direction == "UP":
            row -= 1
        elif self.direction == "DOWN":
            row += 1
        elif self.direction == "LEFT":
            col -= 1
        elif self.direction == "RIGHT":
            col += 1

        # 先假定没有死亡
        done = False
        self.death_reason = None

        # 吃到食物判定
        if (row, col) == self.food:
            food_obtained = True
            self.score += 10
            if self.sound_eat:
                try:
                    self.sound_eat.play()
                except Exception:
                    pass
            # 吃到食物时，立即添加新头部（不删除尾部）
            self.snake.insert(0, (row, col))
            self.non_snake.discard((row, col))
        else:
            food_obtained = False
            # 移除尾格并放入空格集合
            self.non_snake.add(self.snake.pop())
            # 非食物情况，添加新头部
            self.snake.insert(0, (row, col))
            self.non_snake.discard((row, col))

        # ---- 撞墙 / 撞自己判定 ----
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            done = True
            self.death_reason = "撞墙死亡"
        elif (row, col) in self.snake[1:]:  # 检查是否撞到自己身体（排除新头部）
            done = True
            self.death_reason = "撞到自己"

        # ---- 如果死亡 ----
        if done:
            if self.sound_game_over:
                try:
                    self.sound_game_over.play()
                except Exception:
                    pass
        else:
            # 吃到食物则生成新食物
            if food_obtained:
                self.food = self._generate_food()

        info = {
            "snake_size": len(self.snake),
            "snake_head_pos": np.array(self.snake[0]),
            "prev_snake_head_pos": np.array(self.snake[1]) if len(self.snake) > 1 else np.array(self.snake[0]),
            "food_pos": np.array(self.food),
            "food_obtained": food_obtained,
            "death_reason": self.death_reason
        }

        return done, info

    def step_opponent_mode(self, action):
        """
        对抗模式中执行玩家蛇的移动
        action: -1（不变/无输入），或 0:UP,1:LEFT,2:RIGHT,3:DOWN
        返回: done(bool), info(dict)
        """
        if action != -1:
            self._update_direction(action)

        # 当前蛇头位置
        row, col = self.snake[0]
        if self.direction == "UP":
            row -= 1
        elif self.direction == "DOWN":
            row += 1
        elif self.direction == "LEFT":
            col -= 1
        elif self.direction == "RIGHT":
            col += 1

        # 先假定没有死亡
        done = False
        self.death_reason = None

        # 先添加新头部（无论是否吃到食物）
        self.snake.insert(0, (row, col))
        self.non_snake.discard((row, col))

        # 吃到食物判定
        if (row, col) == self.food:
            food_obtained = True
            self.score += 10
            if self.sound_eat:
                try:
                    self.sound_eat.play()
                except Exception:
                    pass
        else:
            food_obtained = False
            # 移除尾格并放入空格集合（如果蛇长度>1）
            if len(self.snake) > 1:
                self.non_snake.add(self.snake.pop())

        # ---- 撞墙 / 撞自己 / 撞对抗蛇判定 ----
        # 撞自己时排除新添加的头部
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            done = True
            self.death_reason = "撞墙死亡"
        elif (row, col) in self.snake[1:]:  # 检查是否撞到自己的身体（排除新头部）
            done = True
            self.death_reason = "撞到自己"
        elif (row, col) in self.opponent_snake:
            done = True
            self.death_reason = "撞到对抗蛇"

        # ---- 如果死亡 ----
        if done:
            if self.sound_game_over:
                try:
                    self.sound_game_over.play()
                except Exception:
                    pass
        else:
            # 吃到食物则生成新食物
            if food_obtained:
                self.food = self._generate_food()

        info = {
            "snake_size": len(self.snake),
            "snake_head_pos": np.array(self.snake[0]),
            "prev_snake_head_pos": np.array(self.snake[1]) if len(self.snake) > 1 else np.array(self.snake[0]),
            "food_pos": np.array(self.food),
            "food_obtained": food_obtained,
            "death_reason": self.death_reason
        }

        return done, info

    def opponent_step(self, action):
        """处理对抗蛇的移动逻辑"""
        # 如果对抗蛇已经死亡，则不再移动
        if hasattr(self, 'opponent_dead') and self.opponent_dead:
            return True, {"death_reason": self.death_reason}

        if action != -1:
            self._update_opponent_direction(action)

        # 当前对抗蛇头位置
        row, col = self.opponent_snake[0]
        # 根据方向计算新位置
        if self.opponent_direction == "UP":
            row -= 1
        elif self.opponent_direction == "DOWN":
            row += 1
        elif self.opponent_direction == "LEFT":
            col -= 1
        elif self.opponent_direction == "RIGHT":
            col += 1

        done = False
        death_reason = None

        # 先添加新头部（无论是否吃到食物）
        self.opponent_snake.insert(0, (row, col))

        # 碰撞检测
        # 撞自己时排除新添加的头部
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            done = True
            death_reason = "对抗蛇撞墙死亡"
        elif (row, col) in self.opponent_snake[1:]:  # 撞自己（排除新头部）
            done = True
            death_reason = "对抗蛇撞到自己"
        elif (row, col) in self.snake:  # 撞玩家蛇
            done = True
            death_reason = "对抗蛇撞到玩家蛇"

        # 如果发生碰撞，标记对抗蛇为死亡状态
        if done:
            self.opponent_dead = True
            self.death_reason = death_reason
            print(f"对抗蛇死亡：{death_reason}")
            return done, {"death_reason": death_reason}

        # 未死亡且没吃到食物时移除尾部
        if (row, col) != self.food:
            if len(self.opponent_snake) > 1:
                self.opponent_snake.pop()
        else:
            # 吃到食物
            self.food = self._generate_food()          # 生成新食物

        return done, {"death_reason": death_reason}

    def respawn_opponent(self):
        """重新部署对抗蛇"""
        mid = self.board_size // 2
        # 在不同位置重新生成对抗蛇
        self.opponent_snake = [(mid + i - 5, mid - 5) for i in range(1, -2, -1)]
        self.opponent_direction = "DOWN"
        self.opponent_dead = False
        
        # 更新non_snake集合
        all_snake_positions = set(self.snake + self.opponent_snake)
        self.non_snake = set((r, c) for r in range(self.board_size) for c in range(self.board_size) if (r, c) not in all_snake_positions)

    def _update_direction(self, action):
        """根据 action 更新方向（避免直接往回走）"""
        if action == 0 and self.direction != "DOWN":
            self.direction = "UP"
        elif action == 1 and self.direction != "RIGHT":
            self.direction = "LEFT"
        elif action == 2 and self.direction != "LEFT":
            self.direction = "RIGHT"
        elif action == 3 and self.direction != "UP":
            self.direction = "DOWN"

    def _update_opponent_direction(self, action):
        """根据 action 更新对抗蛇方向（避免直接往回走）"""
        if action == 0 and self.opponent_direction != "DOWN":
            self.opponent_direction = "UP"
        elif action == 1 and self.opponent_direction != "RIGHT":
            self.opponent_direction = "LEFT"
        elif action == 2 and self.opponent_direction != "LEFT":
            self.opponent_direction = "RIGHT"
        elif action == 3 and self.opponent_direction != "UP":
            self.opponent_direction = "DOWN"

    def _generate_food(self):
        """随机在空格里生成食物（若无可用空格则返回 (0,0)）"""
        if len(self.non_snake) > 0:
            return random.sample(list(self.non_snake), 1)[0]
        else:
            return (0, 0)

    # ---------------------------
    # 绘图与 UI
    # ---------------------------
    def draw_board(self, draw_opponent=False):
        """绘制棋盘边框、蛇、食物"""
        # 背景
        self.screen.fill((0, 0, 0))

        # 绘制边框（白线）
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (self.border_size - 2, self.border_size - 2, self.width + 4, self.height + 4), 2)

        self.draw_snake()  # 绘制玩家的蛇
        
        # 只在对抗模式下绘制对抗蛇
        if draw_opponent and hasattr(self, 'opponent_snake') and not hasattr(self, 'opponent_dead') or (hasattr(self, 'opponent_dead') and not self.opponent_dead):
            self.draw_opponent_snake()

        # 绘制食物（红色方块）
        if len(self.snake) < self.grid_size:
            r, c = self.food
            pygame.draw.rect(self.screen, (255, 0, 0),
                             (c * self.cell_size + self.border_size, r * self.cell_size + self.border_size,
                              self.cell_size, self.cell_size))

    def draw_opponent_snake(self):
        """绘制对抗蛇（包括头部和眼睛）"""
        head_r, head_c = self.opponent_snake[0]
        head_x = head_c * self.cell_size + self.border_size
        head_y = head_r * self.cell_size + self.border_size

        # 绘制蛇头（红色的头）
        pygame.draw.polygon(self.screen, (255, 0, 0), [
            (head_x + self.cell_size // 2, head_y),
            (head_x + self.cell_size, head_y + self.cell_size // 2),
            (head_x + self.cell_size // 2, head_y + self.cell_size),
            (head_x, head_y + self.cell_size // 2)
        ])

        # 眼睛
        eye_size = 3
        eye_offset = self.cell_size // 4
        pygame.draw.circle(self.screen, (255, 255, 255), (head_x + eye_offset, head_y + eye_offset), eye_size)
        pygame.draw.circle(self.screen, (255, 255, 255), (head_x + self.cell_size - eye_offset, head_y + eye_offset), eye_size)

        # 绘制身体
        for i, (r, c) in enumerate(self.opponent_snake[1:]):
            body_x = c * self.cell_size + self.border_size
            body_y = r * self.cell_size + self.border_size
            color = (255, 50, 50)  # 红色身体
            pygame.draw.rect(self.screen, color, (body_x, body_y, self.cell_size, self.cell_size), border_radius=5)

    def draw_snake(self):
        """绘制蛇（头、眼、身体渐变）"""
        # 头坐标换算为像素
        head_r, head_c = self.snake[0]
        head_x = head_c * self.cell_size + self.border_size
        head_y = head_r * self.cell_size + self.border_size

        # 头（蓝色多边形）
        pygame.draw.polygon(self.screen, (100, 100, 255), [
            (head_x + self.cell_size // 2, head_y),
            (head_x + self.cell_size, head_y + self.cell_size // 2),
            (head_x + self.cell_size // 2, head_y + self.cell_size),
            (head_x, head_y + self.cell_size // 2)
        ])

        # 眼睛
        eye_size = 3
        eye_offset = self.cell_size // 4
        pygame.draw.circle(self.screen, (255, 255, 255), (head_x + eye_offset, head_y + eye_offset), eye_size)
        pygame.draw.circle(self.screen, (255, 255, 255), (head_x + self.cell_size - eye_offset, head_y + eye_offset), eye_size)

        # 身体渐变（绿到暗）
        color_list = np.linspace(255, 100, max(len(self.snake)-1,1), dtype=np.uint8)
        i = 0
        for r, c in self.snake[1:]:
            body_x = c * self.cell_size + self.border_size
            body_y = r * self.cell_size + self.border_size
            pygame.draw.rect(self.screen, (0, int(color_list[i]), 0),
                             (body_x, body_y, self.cell_size, self.cell_size), border_radius=5)
            i += 1

    def draw_side_panel(self, ai_connected, show_ai=True):
        """
        在右侧绘制控制面板：
        - 分数、长度
        - AI 连接按钮（可点击）
        - AI 当前状态（已连接/未连接）
        """
        panel_x = self.width + self.border_size + 20
        panel_y = self.border_size

        # 标题
        title_surf = self.large_font.render("控制面板", True, (220, 220, 220))
        self.screen.blit(title_surf, (panel_x, panel_y))

        panel_y += 60

        # 分数显示
        score_surf = self.font.render(f"分数: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surf, (panel_x, panel_y))
        panel_y += 30
        size_surf = self.font.render(f"蛇长: {len(self.snake)}", True, (255, 255, 255))
        self.screen.blit(size_surf, (panel_x, panel_y))
        panel_y += 40

        # 只在普通模式下显示AI相关内容
        if show_ai:
            # AI 状态显示
            status_text = "已连接" if ai_connected else "已断开"
            status_color = (100, 255, 100) if ai_connected else (255, 100, 100)
            status_surf = self.font.render(f"AI 状态: {status_text}", True, status_color)
            self.screen.blit(status_surf, (panel_x, panel_y))
            panel_y += 40

            # 绘制按钮（Connect/Disconnect）
            self.ai_button_rect = pygame.Rect(panel_x, panel_y, 160, 36)
            mouse_pos = pygame.mouse.get_pos()
            hovering = self.ai_button_rect.collidepoint(mouse_pos)
            button_color = (200, 200, 200) if not hovering else (255, 255, 255)
            pygame.draw.rect(self.screen, button_color, self.ai_button_rect, border_radius=6)
            btn_text = "断开 AI" if ai_connected else "接通 AI"
            btn_surf = self.font.render(btn_text, True, (20, 20, 20))
            btn_rect = btn_surf.get_rect(center=self.ai_button_rect.center)
            self.screen.blit(btn_surf, btn_rect)

    def render(self, ai_connected=False, draw_opponent=False, show_ai=True):
        """综合绘制函数：棋盘 + 右侧面板"""
        self.draw_board(draw_opponent)
        self.draw_side_panel(ai_connected, show_ai)
        pygame.display.flip()

    # ---------------------------
    # 辅助方法（鼠标判断等）
    # ---------------------------
    def is_mouse_on_rect(self, rect):
        """判断鼠标是否在给定 rect 上（rect 为 pygame.Rect）"""
        return rect.collidepoint(pygame.mouse.get_pos())

# ---------------------------
# AI 行为接口
# ---------------------------
def get_ai_action(game, is_opponent=False):
    """
    智能AI策略：支持控制对抗蛇
    is_opponent: True=控制红色对抗蛇，False=控制绿色玩家蛇
    """
    import random
    import numpy as np
    from collections import deque

    # 根据控制对象选择蛇的信息
    if is_opponent:
        snake = game.opponent_snake
        direction = game.opponent_direction
    else:
        snake = game.snake
        direction = game.direction

    head = np.array(snake[0])
    food = np.array(game.food)
    body = set(snake)
    board = game.board_size

    dirs = {
        0: (-1, 0),  # 上
        1: (0, -1),  # 左
        2: (0, 1),   # 右
        3: (1, 0)    # 下
    }

    opposite = {"UP": 3, "DOWN": 0, "LEFT": 2, "RIGHT": 1}
    opposite_dir = opposite.get(direction, -1)  # 使用对应蛇的当前方向

    def is_valid(pos):
        r, c = pos
        return 0 <= r < board and 0 <= c < board and (r, c) not in body

    # ----------------------------------------------------------------------
    # 🧩 BFS寻找从蛇头到食物的安全路径
    # ----------------------------------------------------------------------
    def bfs_path(start, goal):
        queue = deque([(start, [])])
        visited = {tuple(start)}

        while queue:
            (r, c), path = queue.popleft()
            if (r, c) == tuple(goal):
                return path  # 返回方向序列

            for d, (dr, dc) in dirs.items():
                nr, nc = r + dr, c + dc
                if (0 <= nr < board and 0 <= nc < board
                        and (nr, nc) not in body
                        and (nr, nc) not in visited):
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [d]))
        return None

    path = bfs_path(tuple(head), tuple(food))

    # ----------------------------------------------------------------------
    # 🧭 如果有安全路径，走第一步
    # ----------------------------------------------------------------------
    if path:
        if path[0] != opposite_dir:
            return path[0]
        
    

    # ----------------------------------------------------------------------
    # 🧱 若无安全路径，则选"最大空间方向"
    # ----------------------------------------------------------------------
    def flood_fill_space(start):
        """计算从某个方向出发的可行空间大小"""
        q = deque([start])
        seen = {start}
        while q:
            r, c = q.popleft()
            for dr, dc in dirs.values():
                nr, nc = r + dr, c + dc
                if 0 <= nr < board and 0 <= nc < board and (nr, nc) not in body and (nr, nc) not in seen:
                    seen.add((nr, nc))
                    q.append((nr, nc))
        return len(seen)

    best_dir = None
    best_space = -1

    for d, (dr, dc) in dirs.items():
        nr, nc = head[0] + dr, head[1] + dc
        if is_valid((nr, nc)) and d != opposite_dir:
            space = flood_fill_space((nr, nc))
            if space > best_space:
                best_space = space
                best_dir = d

    if best_dir is not None:
        return best_dir

    # ----------------------------------------------------------------------
    # 🌀 实在无路：随机选一条不反向的安全路
    # ----------------------------------------------------------------------
    safe_moves = [
        d for d, (dr, dc) in dirs.items()
        if is_valid((head[0] + dr, head[1] + dc)) and d != opposite_dir
    ]
    if safe_moves:
        return random.choice(safe_moves)

    # 没路就随机（必死）
    return random.choice([0, 1, 2, 3])

# ---------------------------
# 普通模式主函数
# ---------------------------
def main_normal():
    """普通模式主函数：玩家可自行控制或AI接管"""
    seed = random.randint(0, int(1e9))
    game = SnakeGame(seed=seed, silent_mode=False)

    # 初始化
    clock = pygame.time.Clock()
    update_interval = 0.2  # 游戏更新间隔（秒）
    last_update = time.time()

    action = -1
    game_state = "welcome"  # 初始游戏状态：欢迎界面
    ai_connected = False    # AI 开关（由右侧按钮控制）
    ai_control = False      # 当前是否由 AI 控制
    countdown_snd = game.sound_count

    # 画面上用于鼠标点击检测的隐藏文本
    start_button_surf = game.font.render("START", True, (0, 0, 0))
    retry_button_surf = game.font.render("RETRY", True, (0, 0, 0))

    # 欢迎界面
    def draw_welcome():
        game.screen.fill((0, 0, 0))
        margin_top = 50  # 顶部边距
        spacing = 40     # 行间距
        btn_margin_top = 60  # 按钮与文字间距

        # 标题
        title = game.large_font.render("SNAKE GAME", True, (255, 255, 255))
        title_rect = title.get_rect(center=(game.display_width // 2, margin_top + title.get_height() // 2))
        game.screen.blit(title, title_rect)

        # 信息文本
        info1 = game.font.render("方向键控制蛇（↑↓←→）", True, (200, 200, 200))
        info2 = game.font.render("右侧面板可接通/断开 AI（AI 接通后自动控制）", True, (200, 200, 200))
        game.screen.blit(info1, (game.display_width // 2 - info1.get_width() // 2, title_rect.bottom + spacing))
        game.screen.blit(info2, (game.display_width // 2 - info2.get_width() // 2, title_rect.bottom + spacing + info1.get_height() + 5))

        # START 按钮
        btn_width, btn_height = 140, 40
        btn_rect = pygame.Rect(0, 0, btn_width, btn_height)
        btn_rect.centerx = game.display_width // 2
        btn_rect.top = title_rect.bottom + spacing + info1.get_height() + info2.get_height() + btn_margin_top
        pygame.draw.rect(game.screen, (100, 100, 100), btn_rect, border_radius=6)

        text_s = game.font.render("开始游戏", True, (255, 255, 255))
        text_rect = text_s.get_rect(center=btn_rect.center)
        game.screen.blit(text_s, text_rect)

        game.start_button_rect = btn_rect
        pygame.display.flip()

    # 游戏结束界面
    def draw_game_over():
        game.screen.fill((0, 0, 0))
        margin_top = 60
        spacing = 40
        btn_margin_top = 30
        btn_spacing = 10

        # 标题
        title = game.large_font.render("游戏结束", True, (255, 255, 255))
        title_rect = title.get_rect(center=(game.display_width // 2, margin_top))
        game.screen.blit(title, title_rect)

        # 分数显示
        score_text = game.font.render(f"最终分数: {game.score}", True, (200, 200, 200))
        score_rect = score_text.get_rect(center=(game.display_width // 2, title_rect.bottom + spacing))
        game.screen.blit(score_text, score_rect)

        # 蛇身长度
        length = len(game.snake)
        length_text = game.font.render(f"蛇身长度: {length} 格", True, (200, 255, 200))
        length_rect = length_text.get_rect(center=(game.display_width // 2, score_rect.bottom + spacing // 2))
        game.screen.blit(length_text, length_rect)



        # 绘制蛇形展示区域
        s_area_width, s_area_height = 400, 300
        s_area_x = (game.display_width - s_area_width) // 2
        s_area_y = length_rect.bottom + 50
        pygame.draw.rect(game.screen, (30, 30, 30), (s_area_x, s_area_y, s_area_width, s_area_height), border_radius=12)

        # ---------------------------
        # 在展示区域绘制蛇（S型折叠）
        # ---------------------------
        cell = 10  # 每个方格像素
        cols = s_area_width // cell
        rows = s_area_height // cell

        # 生成一条“展示用”的S型蛇（不使用原坐标，只展示长度）
        display_snake = []
        direction = 1  # 1 向右, -1 向左
        row = 0
        count = 0

        for i in range(length):
            col = (i % (cols - 2)) + 1 if direction == 1 else (cols - 2 - (i % (cols - 2)))
            display_snake.append((row + 1, col))
            if (i + 1) % (cols - 2) == 0:
                row += 2
                direction *= -1
                if row + 1 >= rows:
                    break  # 超出展示区则停止

        # 绘制蛇头（蓝色菱形）
        if display_snake:
            head_r, head_c = display_snake[0]
            head_x = s_area_x + head_c * cell
            head_y = s_area_y + head_r * cell
            pygame.draw.polygon(game.screen, (100, 100, 255), [
                (head_x + cell // 2, head_y),
                (head_x + cell, head_y + cell // 2),
                (head_x + cell // 2, head_y + cell),
                (head_x, head_y + cell // 2)
            ])
            # 眼睛
            eye_size = 2
            pygame.draw.circle(game.screen, (255, 255, 255), (head_x + 3, head_y + 3), eye_size)
            pygame.draw.circle(game.screen, (255, 255, 255), (head_x + cell - 3, head_y + 3), eye_size)

        # 身体颜色渐变（绿→深绿）
        color_list = np.linspace(255, 80, max(len(display_snake) - 1, 1), dtype=np.uint8)
        for i, (r, c) in enumerate(display_snake[1:], start=0):
            body_x = s_area_x + c * cell
            body_y = s_area_y + r * cell
            pygame.draw.rect(game.screen, (0, int(color_list[i]), 0),
                            (body_x, body_y, cell, cell), border_radius=3)



        # 按钮设置
        btn_width, btn_height = 200, 50
        btn_spacing = 15
        
        # 再来一次按钮 - 放置在蛇形展示区域下方
        retry_btn = pygame.Rect(0, 0, btn_width, btn_height)
        retry_btn.centerx = game.display_width // 2
        retry_btn.top = s_area_y + s_area_height + btn_margin_top
        
        # 美化按钮
        pygame.draw.rect(game.screen, (120, 120, 120), retry_btn, border_radius=10)
        pygame.draw.rect(game.screen, (150, 150, 150), retry_btn, 2, border_radius=10)

        retry_text = game.font.render("再来一次", True, (255, 255, 255))
        retry_text_rect = retry_text.get_rect(center=retry_btn.center)
        game.screen.blit(retry_text, retry_text_rect)

        # 返回菜单按钮
        menu_btn = pygame.Rect(0, 0, btn_width, btn_height)
        menu_btn.centerx = game.display_width // 2
        menu_btn.top = retry_btn.bottom + btn_spacing
        pygame.draw.rect(game.screen, (150, 150, 180), menu_btn, border_radius=10)
        pygame.draw.rect(game.screen, (180, 180, 210), menu_btn, 2, border_radius=10)

        menu_text = game.font.render("返回菜单", True, (255, 255, 255))
        menu_text_rect = menu_text.get_rect(center=menu_btn.center)
        game.screen.blit(menu_text, menu_text_rect)

        # 退出游戏按钮
        exit_btn = pygame.Rect(0, 0, btn_width, btn_height)
        exit_btn.centerx = game.display_width // 2
        exit_btn.top = menu_btn.bottom + btn_spacing
        pygame.draw.rect(game.screen, (220, 70, 70), exit_btn, border_radius=10)
        pygame.draw.rect(game.screen, (180, 50, 50), exit_btn, 2, border_radius=10)

        exit_text = game.font.render("退出游戏", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=exit_btn.center)
        game.screen.blit(exit_text, exit_text_rect)

        game.retry_button_rect = retry_btn
        game.menu_button_rect = menu_btn
        game.exit_button_rect = exit_btn
        pygame.display.flip()

    # 主循环
    running = True
    while running:
        for event in pygame.event.get():
            # 退出
            if event.type == pygame.QUIT:
                running = False
                break

            # 鼠标点击事件
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 欢迎界面点击开始按钮
                if game_state == "welcome" and hasattr(game, "start_button_rect"):
                    if game.start_button_rect.collidepoint(event.pos):
                        # 倒计时 3 秒
                        for i in range(3, 0, -1):
                            game.screen.fill((0, 0, 0))
                            cnt_surf = game.large_font.render(str(i), True, (255, 255, 255))
                            game.screen.blit(cnt_surf, (game.display_width // 2 - cnt_surf.get_width() // 2,
                                                        game.display_height // 2 - cnt_surf.get_height() // 2))
                            pygame.display.flip()
                            if countdown_snd:
                                try:
                                    countdown_snd.play()
                                except:
                                    pass
                            pygame.time.wait(700)
                        action = -1
                        game_state = "running"
                        last_update = time.time()

                # 游戏结束界面按钮点击
                elif game_state == "game_over":
                    if hasattr(game, "retry_button_rect") and game.retry_button_rect.collidepoint(event.pos):
                        # 倒计时 3 秒
                        for i in range(3, 0, -1):
                            game.screen.fill((0, 0, 0))
                            cnt_surf = game.large_font.render(str(i), True, (255, 255, 255))
                            game.screen.blit(cnt_surf, (game.display_width // 2 - cnt_surf.get_width() // 2,
                                                        game.display_height // 2 - cnt_surf.get_height() // 2))
                            pygame.display.flip()
                            if countdown_snd:
                                try:
                                    countdown_snd.play()
                                except:
                                    pass
                            pygame.time.wait(700)
                        game.reset()
                        action = -1
                        game_state = "running"
                        last_update = time.time()
                    elif hasattr(game, "menu_button_rect") and game.menu_button_rect.collidepoint(event.pos):
                        # 返回菜单
                        pygame.quit()
                        main_gui()
                    elif hasattr(game, "exit_button_rect") and game.exit_button_rect.collidepoint(event.pos):
                        # 退出游戏
                        pygame.quit()
                        sys.exit()

                # AI 按钮点击
                elif game_state == "running" and hasattr(game, "ai_button_rect"):
                    if game.ai_button_rect.collidepoint(event.pos):
                        ai_connected = not ai_connected
                        ai_control = ai_connected  # 接通AI后立即开始控制

            # 键盘事件（玩家手动控制）
            if event.type == pygame.KEYDOWN and game_state == "running":
                # 玩家控制优先级高于AI控制
                # 当玩家按下方向键时，立即执行移动并重置AI控制标志
                # 同时设置ai_connected = False，使AI状态显示从绿色变为红色
                if event.key == pygame.K_UP:
                    action = 0
                    ai_control = False  # 确保玩家按下方向键时获得控制权
                    ai_connected = False  # 自动禁用AI连接，使状态显示为红色
                elif event.key == pygame.K_LEFT:
                    action = 1
                    ai_control = False
                    ai_connected = False
                elif event.key == pygame.K_RIGHT:
                    action = 2
                    ai_control = False
                    ai_connected = False
                elif event.key == pygame.K_DOWN:
                    action = 3
                    ai_control = False
                    ai_connected = False
                # WASD键控制
                elif event.key == pygame.K_w:
                    action = 0
                    ai_control = False  # 确保玩家按下方向键时获得控制权
                    ai_connected = False  # 自动禁用AI连接，使状态显示为红色
                elif event.key == pygame.K_a:
                    action = 1
                    ai_control = False
                    ai_connected = False
                elif event.key == pygame.K_d:
                    action = 2
                    ai_control = False
                    ai_connected = False
                elif event.key == pygame.K_s:
                    action = 3
                    ai_control = False
                    ai_connected = False
                # 按键后立即执行移动，不等待更新周期
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, 
                                pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                    # 立即执行移动
                    done, info = game.step(action)
                    game.render(ai_connected, draw_opponent=False, show_ai=True)
                    # 重置动作，避免连续移动
                    action = -1
                elif event.key == pygame.K_x:
                    # 切换 AI 控制
                    ai_control = not ai_control
                    if ai_control:
                        ai_connected = True

        # 游戏运行状态
        if game_state == "welcome":
            draw_welcome()
            clock.tick(20)
            continue
        if game_state == "game_over":
            draw_game_over()
            clock.tick(20)
            continue

        # 游戏步骤更新
        now = time.time()
        if now - last_update >= update_interval:
            last_update = now  # 更新时间
            
            if game_state == "running":
                # 玩家控制绿色蛇
                # 即使没有新的键盘输入，蛇也会保持当前方向移动
                if ai_connected and ai_control:
                    chosen_action = get_ai_action(game, is_opponent=False)  # 获取AI控制动作
                else:
                    # 对于玩家控制，action为-1时保持当前方向
                    chosen_action = action
                
                done, info = game.step(chosen_action)
                game.render(ai_connected, draw_opponent=False, show_ai=True)
                
                # 重置玩家动作，这样蛇会继续按照当前方向移动
                # 只有当玩家按下方向键时，action才会改变
                action = -1

            # 检查游戏是否结束
            if done:
                game_state = "game_over"

        clock.tick(60)

    pygame.quit()
    sys.exit()

# ---------------------------
# 对抗模式主函数
# ---------------------------
def main_opponent():
    """对抗模式主函数：玩家控制绿色蛇，AI控制红色蛇"""
    seed = random.randint(0, int(1e9))
    game = SnakeGame(seed=seed, silent_mode=False)

    # 初始化对抗模式游戏状态
    game.reset_opponent_mode()

    # 初始化
    clock = pygame.time.Clock()
    update_interval = 0.2  # 游戏更新间隔（秒）
    last_update = time.time()

    action = -1
    game_state = "welcome"  # 初始游戏状态：欢迎界面
    countdown_snd = game.sound_count

    # 欢迎界面
    def draw_welcome():
        game.screen.fill((0, 0, 0))
        margin_top = 50  # 顶部边距
        spacing = 40     # 行间距
        btn_margin_top = 60  # 按钮与文字间距

        # 标题
        title = game.large_font.render("对抗模式", True, (255, 255, 255))
        title_rect = title.get_rect(center=(game.display_width // 2, margin_top + title.get_height() // 2))
        game.screen.blit(title, title_rect)

        # 信息文本
        info1 = game.font.render("方向键或WASD控制绿色蛇（↑↓←→ / W A S D）", True, (200, 200, 200))
        info2 = game.font.render("小心红色AI蛇！碰到就会死亡！", True, (200, 200, 200))
        info3 = game.font.render("目标：达到1000积分！", True, (200, 200, 200))
        game.screen.blit(info1, (game.display_width // 2 - info1.get_width() // 2, title_rect.bottom + spacing))
        game.screen.blit(info2, (game.display_width // 2 - info2.get_width() // 2, title_rect.bottom + spacing + info1.get_height() + 5))
        game.screen.blit(info3, (game.display_width // 2 - info3.get_width() // 2, title_rect.bottom + spacing + info1.get_height() + info2.get_height() + 10))

        # START 按钮
        btn_width, btn_height = 140, 40
        btn_rect = pygame.Rect(0, 0, btn_width, btn_height)
        btn_rect.centerx = game.display_width // 2
        btn_rect.top = title_rect.bottom + spacing + info1.get_height() + info2.get_height() + info3.get_height() + btn_margin_top
        pygame.draw.rect(game.screen, (100, 100, 100), btn_rect, border_radius=6)

        text_s = game.font.render("开始游戏", True, (255, 255, 255))
        text_rect = text_s.get_rect(center=btn_rect.center)
        game.screen.blit(text_s, text_rect)

        game.start_button_rect = btn_rect
        pygame.display.flip()

    # 游戏结束界面
    def draw_game_over():
        game.screen.fill((0, 0, 0))
        margin_top = 60
        spacing = 40
        btn_margin_top = 30
        btn_spacing = 10

        # 标题
        if game.score >= 1000:
            title = game.large_font.render("恭喜胜利！", True, (255, 255, 255))
        else:
            title = game.large_font.render("游戏结束", True, (255, 255, 255))
        title_rect = title.get_rect(center=(game.display_width // 2, margin_top))
        game.screen.blit(title, title_rect)

        # 分数显示
        score_text = game.font.render(f"最终分数: {game.score}", True, (200, 200, 200))
        score_rect = score_text.get_rect(center=(game.display_width // 2, title_rect.bottom + spacing))
        game.screen.blit(score_text, score_rect)

        # 蛇身长度
        length = len(game.snake)
        length_text = game.font.render(f"蛇身长度: {length} 格", True, (200, 255, 200))
        length_rect = length_text.get_rect(center=(game.display_width // 2, score_rect.bottom + spacing // 2))
        game.screen.blit(length_text, length_rect)

        # 死亡原因
        reason_rect = None
        if hasattr(game, 'death_reason') and game.death_reason:
            reason_text = game.font.render(f"死亡原因: {game.death_reason}", True, (255, 200, 200))
            reason_rect = reason_text.get_rect(center=(game.display_width // 2, length_rect.bottom + spacing // 2))
            game.screen.blit(reason_text, reason_rect)

        # 绘制蛇形展示区域
        s_area_width, s_area_height = 400, 300
        s_area_x = (game.display_width - s_area_width) // 2
        if reason_rect:
            s_area_y = reason_rect.bottom + 50
        else:
            s_area_y = length_rect.bottom + 50
        pygame.draw.rect(game.screen, (30, 30, 30), (s_area_x, s_area_y, s_area_width, s_area_height), border_radius=12)

        # ---------------------------
        # 在展示区域绘制蛇（S型折叠）
        # ---------------------------
        cell = 10  # 每个方格像素
        cols = s_area_width // cell
        rows = s_area_height // cell

        # 生成一条"展示用"的S型蛇（不使用原坐标，只展示长度）
        display_snake = []
        direction = 1  # 1 向右, -1 向左
        row = 0
        count = 0

        for i in range(length):
            col = (i % (cols - 2)) + 1 if direction == 1 else (cols - 2 - (i % (cols - 2)))
            display_snake.append((row + 1, col))
            if (i + 1) % (cols - 2) == 0:
                row += 2
                direction *= -1
                if row + 1 >= rows:
                    break  # 超出展示区则停止

        # 绘制蛇头（蓝色菱形）
        if display_snake:
            head_r, head_c = display_snake[0]
            head_x = s_area_x + head_c * cell
            head_y = s_area_y + head_r * cell
            pygame.draw.polygon(game.screen, (100, 100, 255), [
                (head_x + cell // 2, head_y),
                (head_x + cell, head_y + cell // 2),
                (head_x + cell // 2, head_y + cell),
                (head_x, head_y + cell // 2)
            ])
            # 眼睛
            eye_size = 2
            pygame.draw.circle(game.screen, (255, 255, 255), (head_x + 3, head_y + 3), eye_size)
            pygame.draw.circle(game.screen, (255, 255, 255), (head_x + cell - 3, head_y + 3), eye_size)

        # 身体颜色渐变（绿→深绿）
        color_list = np.linspace(255, 80, max(len(display_snake) - 1, 1), dtype=np.uint8)
        for i, (r, c) in enumerate(display_snake[1:], start=0):
            body_x = s_area_x + c * cell
            body_y = s_area_y + r * cell
            pygame.draw.rect(game.screen, (0, int(color_list[i]), 0),
                            (body_x, body_y, cell, cell), border_radius=3)

        # 按钮设置
        btn_width, btn_height = 200, 50
        btn_spacing = 15
        
        # 再来一次按钮 - 放置在蛇形展示区域下方
        retry_btn = pygame.Rect(0, 0, btn_width, btn_height)
        retry_btn.centerx = game.display_width // 2
        retry_btn.top = s_area_y + s_area_height + btn_margin_top
        # 美化按钮
        pygame.draw.rect(game.screen, (120, 120, 120), retry_btn, border_radius=10)
        pygame.draw.rect(game.screen, (150, 150, 150), retry_btn, 2, border_radius=10)

        retry_text = game.font.render("再来一次", True, (255, 255, 255))
        retry_text_rect = retry_text.get_rect(center=retry_btn.center)
        game.screen.blit(retry_text, retry_text_rect)

        # 返回菜单按钮
        menu_btn = pygame.Rect(0, 0, btn_width, btn_height)
        menu_btn.centerx = game.display_width // 2
        menu_btn.top = retry_btn.bottom + btn_spacing
        pygame.draw.rect(game.screen, (150, 150, 180), menu_btn, border_radius=10)
        pygame.draw.rect(game.screen, (180, 180, 210), menu_btn, 2, border_radius=10)

        menu_text = game.font.render("返回菜单", True, (255, 255, 255))
        menu_text_rect = menu_text.get_rect(center=menu_btn.center)
        game.screen.blit(menu_text, menu_text_rect)

        # 退出游戏按钮
        exit_btn = pygame.Rect(0, 0, btn_width, btn_height)
        exit_btn.centerx = game.display_width // 2
        exit_btn.top = menu_btn.bottom + btn_spacing
        pygame.draw.rect(game.screen, (220, 70, 70), exit_btn, border_radius=10)
        pygame.draw.rect(game.screen, (180, 50, 50), exit_btn, 2, border_radius=10)

        exit_text = game.font.render("退出游戏", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=exit_btn.center)
        game.screen.blit(exit_text, exit_text_rect)

        game.retry_button_rect = retry_btn
        game.menu_button_rect = menu_btn
        game.exit_button_rect = exit_btn
        pygame.display.flip()

    # 主循环
    running = True
    while running:
        for event in pygame.event.get():
            # 退出
            if event.type == pygame.QUIT:
                running = False
                break

            # 鼠标点击事件
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 欢迎界面点击开始按钮
                if game_state == "welcome" and hasattr(game, "start_button_rect"):
                    if game.start_button_rect.collidepoint(event.pos):
                        # 倒计时 3 秒
                        for i in range(3, 0, -1):
                            game.screen.fill((0, 0, 0))
                            cnt_surf = game.large_font.render(str(i), True, (255, 255, 255))
                            game.screen.blit(cnt_surf, (game.display_width // 2 - cnt_surf.get_width() // 2,
                                                        game.display_height // 2 - cnt_surf.get_height() // 2))
                            pygame.display.flip()
                            if countdown_snd:
                                try:
                                    countdown_snd.play()
                                except:
                                    pass
                            pygame.time.wait(700)
                        action = -1
                        game_state = "running"
                        last_update = time.time()

                # 游戏结束界面按钮点击
                elif game_state == "game_over":
                    if hasattr(game, "retry_button_rect") and game.retry_button_rect.collidepoint(event.pos):
                        # 倒计时 3 秒
                        for i in range(3, 0, -1):
                            game.screen.fill((0, 0, 0))
                            cnt_surf = game.large_font.render(str(i), True, (255, 255, 255))
                            game.screen.blit(cnt_surf, (game.display_width // 2 - cnt_surf.get_width() // 2,
                                                        game.display_height // 2 - cnt_surf.get_height() // 2))
                            pygame.display.flip()
                            if countdown_snd:
                                try:
                                    countdown_snd.play()
                                except:
                                    pass
                            pygame.time.wait(700)
                        game.reset_opponent_mode()  # 使用对抗模式专用的重置方法
                        action = -1
                        game_state = "running"
                        last_update = time.time()
                    elif hasattr(game, "menu_button_rect") and game.menu_button_rect.collidepoint(event.pos):
                        # 返回菜单
                        pygame.quit()
                        main_gui()
                    elif hasattr(game, "exit_button_rect") and game.exit_button_rect.collidepoint(event.pos):
                        # 退出游戏
                        pygame.quit()
                        sys.exit()

            # 键盘事件（玩家手动控制）
            if event.type == pygame.KEYDOWN and game_state == "running":
                if event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_w:
                    action = 0
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a or event.key == pygame.K_a:
                    action = 1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d or event.key == pygame.K_d:
                    action = 2
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s or event.key == pygame.K_s:
                    action = 3
                    
                # 按键后立即执行移动，不等待更新间隔
                if action != -1:
                    # 立即执行玩家动作
                    game.step_opponent_mode(action)
                    # 立即渲染画面
                    game.render(ai_connected=False, draw_opponent=True, show_ai=False)
                    # 重置动作以避免连续移动
                    action = -1

        # 游戏运行状态
        if game_state == "welcome":
            draw_welcome()
            clock.tick(20)
            continue
        if game_state == "game_over":
            draw_game_over()
            clock.tick(20)
            continue

        # 游戏步骤更新
        now = time.time()
        if now - last_update >= update_interval:
            last_update = now  # 更新时间
            
            if game_state == "running":
                # 玩家控制绿色蛇
                chosen_action = action
                done, info = game.step_opponent_mode(chosen_action)

                # 对抗模式下AI控制红色蛇
                if not game.opponent_dead:
                    opponent_action = get_ai_action(game, is_opponent=True)
                    done_opponent, info_opponent = game.opponent_step(opponent_action)
                    
                    # 如果对抗蛇死亡，重新部署
                    if done_opponent:
                        print("红色蛇死亡，重新部署...")
                        # 延迟一小段时间再重新部署，让玩家能看到死亡效果
                        pygame.time.wait(500)
                        game.respawn_opponent()
                else:
                    # 如果对抗蛇已经死亡，等待重新部署
                    pass

                game.render(ai_connected=False, draw_opponent=True, show_ai=False)
                
                # 重置玩家动作
                action = -1

                # 检查胜利条件（1000积分）
                if game.score >= 1000:
                    print("恭喜胜利！达到1000积分！")
                    game_state = "game_over"

            # 检查游戏是否结束
            if done:
                game_state = "game_over"

        clock.tick(60)

    pygame.quit()
    sys.exit()

# ---------------------------
# 主入口
# ---------------------------
def main_gui():
    """图形界面模式选择"""
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("贪吃蛇游戏 - 选择模式")
    font = pygame.font.SysFont("SimHei", 30)
    large_font = pygame.font.SysFont("SimHei", 40)
    
    clock = pygame.time.Clock()
    running = True
    
    # 绘制模式选择界面
    def draw_mode_selection():
        screen.fill((0, 0, 0))
        
        # 标题
        title = large_font.render("选择游戏模式", True, (255, 255, 255))
        title_rect = title.get_rect(center=(300, 100))
        screen.blit(title, title_rect)
        
        # 按钮设置
        btn_width, btn_height = 240, 60
        btn_spacing = 20
        bottom_margin = 50  # 底部边距
        
        # 计算按钮起始位置，确保有足够的底部边距
        total_buttons_height = (btn_height + btn_spacing) * 3 - btn_spacing
        start_y = (400 - total_buttons_height - bottom_margin) // 2
        
        # 普通模式按钮
        btn_rect1 = pygame.Rect((600 - btn_width) // 2, start_y, btn_width, btn_height)
        # 美化按钮：添加边框和渐变效果
        pygame.draw.rect(screen, (120, 220, 120), btn_rect1, border_radius=12)
        pygame.draw.rect(screen, (80, 200, 80), btn_rect1, 3, border_radius=12)
        text1 = font.render("普通模式", True, (0, 0, 0))
        text_rect1 = text1.get_rect(center=btn_rect1.center)
        screen.blit(text1, text_rect1)
        
        # 对抗模式按钮
        btn_rect2 = pygame.Rect((600 - btn_width) // 2, start_y + btn_height + btn_spacing, btn_width, btn_height)
        pygame.draw.rect(screen, (120, 120, 220), btn_rect2, border_radius=12)
        pygame.draw.rect(screen, (80, 80, 200), btn_rect2, 3, border_radius=12)
        text2 = font.render("对抗模式", True, (0, 0, 0))
        text_rect2 = text2.get_rect(center=btn_rect2.center)
        screen.blit(text2, text_rect2)
        
        # 退出游戏按钮
        btn_rect3 = pygame.Rect((600 - btn_width) // 2, start_y + (btn_height + btn_spacing) * 2, btn_width, btn_height)
        pygame.draw.rect(screen, (220, 70, 70), btn_rect3, border_radius=12)
        pygame.draw.rect(screen, (180, 50, 50), btn_rect3, 3, border_radius=12)
        text3 = font.render("退出游戏", True, (255, 255, 255))
        text_rect3 = text3.get_rect(center=btn_rect3.center)
        screen.blit(text3, text_rect3)
        
        pygame.display.flip()
        return btn_rect1, btn_rect2, btn_rect3
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                btn_rect1, btn_rect2, btn_rect3 = draw_mode_selection()
                if btn_rect1.collidepoint(event.pos):
                    pygame.quit()
                    main_normal()
                elif btn_rect2.collidepoint(event.pos):
                    pygame.quit()
                    main_opponent()
                elif btn_rect3.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        
        draw_mode_selection()
        clock.tick(30)

def main():
    """游戏主入口，提供模式选择"""
    # 默认直接进入图形界面模式以便验证功能
    main_gui()
    
    # 保留原始选择逻辑作为注释
    """
    print("===== 贪吃蛇游戏 =====\n")
    print("请选择游戏模式:")
    print("1. 普通模式")
    print("2. 对抗模式")
    print("3. 图形界面模式（显示模式选择界面）")
    
    choice = input("请输入选择 (1-3): ")
    
    if choice == "1":
        main_normal()
    elif choice == "2":
        main_opponent()
    elif choice == "3":
        main_gui()
    else:
        print("无效的选择，默认进入普通模式")
        main_normal()
    """

if __name__ == "__main__":
    main()