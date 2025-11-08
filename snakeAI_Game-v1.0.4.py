# 文件名: user_game_main.py
# 贪吃蛇游戏主程序
# 依赖: pygame
# 运行: python user_game_main.py

# 导入必要的模块
import sys
import random
import time
import pygame
from pygame import mixer
import numpy as np

# ---------------------------
# 游戏主类
# ---------------------------
class SnakeGame:
    def __init__(self, seed=0, board_size=50, silent_mode=False):
        """
        初始化贪吃蛇游戏
        
        参数:
            seed: 随机种子，用于复现游戏状态
            board_size: 棋盘边长（格子数）
            silent_mode: True 时不初始化 pygame 显示（便于无界面测试）
        """
        # 随机数设置
        random.seed(seed)
        
        # 游戏配置参数
        self.board_size = board_size    # 棋盘边长（格子数）
        self.cell_size = 20            # 每个格子的像素大小
        self.border_size = 40          # 边框大小
        
        # 计算尺寸相关变量
        self.width = self.board_size * self.cell_size  # 棋盘宽度
        self.height = self.width                       # 棋盘高度（正方形）
        self.grid_size = self.board_size ** 2          # 总格子数
        
        # 显示窗口尺寸
        self.display_width = 1060  # 固定窗口宽度
        self.display_height = 860  # 固定窗口高度
        
        # 游戏状态初始化
        self.silent_mode = silent_mode
        
        # 初始化显示和音频
        if not silent_mode:
            pygame.init()
            pygame.display.set_caption("贪吃蛇（可接入 AI）")
            self.screen = pygame.display.set_mode((self.display_width, self.display_height))
            # 使用字体列表，确保中文字体能正确加载
            chinese_fonts = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial Unicode MS", "Microsoft YaHei"]
            self.font = pygame.font.SysFont(chinese_fonts, 24)
            self.large_font = pygame.font.SysFont(chinese_fonts, 30)

            # 尝试加载声音文件（静默失败）
            try:
                mixer.init()
                # 设置默认音量
                mixer.music.set_volume(0.3)  # 背景音乐音量30%
                
                # 加载音效
                self.sound_eat = mixer.Sound("sound/eat.wav")
                self.sound_game_over = mixer.Sound("sound/game_over.wav")
                self.sound_count = mixer.Sound("sound/count.wav")
                
                # 设置音效音量
                if self.sound_eat:
                    self.sound_eat.set_volume(0.6)  # 吃食物音效音量60%
                if self.sound_game_over:
                    self.sound_game_over.set_volume(0.8)  # 游戏结束音效音量80%
                if self.sound_count:
                    self.sound_count.set_volume(0.5)  # 倒计时音效音量50%
                
                # 初始化背景音乐状态
                self.bgm_playing = False
                    
            except Exception as e:
                # 记录错误但继续运行
                print(f"音效初始化失败: {e}")
                self.sound_eat = None
                self.sound_game_over = None
                self.sound_count = None
                self.bgm_playing = False
        else:
            self.screen = None
            self.font = None
            self.large_font = None
            self.sound_eat = None
            self.sound_game_over = None
            self.sound_count = None
            
        # 游戏速度设置
        self.speed = 30  # 默认游戏速度

        self.snake = None
        self.non_snake = None
        self.direction = None
        self.score = 0
        self.food = None
        self.seed_value = seed
        random.seed(seed)  # 设置随机种子
        np.random.seed(seed)
        
        # 背景音乐控制标志
        self.bgm_enabled = True  # 默认启用背景音乐

        self.reset()

    def reset(self):
        """重置游戏状态（普通模式）
        
        初始化玩家蛇、食物位置和游戏状态变量。
        """
        # 计算棋盘中心点
        mid = self.board_size // 2
        
        # 初始化玩家蛇（3节，位于中心）
        self.snake = [(mid + i, mid) for i in range(1, -2, -1)]
        self.snake_set = set(self.snake)  # 用于快速碰撞检测
        self.direction = "DOWN"          # 玩家蛇初始方向
        
        # 初始化游戏状态
        self.score = 0
        self.death_reason = None
        self.game_start_time = time.time()  # 初始化游戏开始时间
        
        # 更新可用位置集合
        self._update_available_positions()
        
        # 生成初始食物
        self.food = self._generate_food()
    
    def reset_three_snake_mode(self):
        """重置影子模式游戏状态
        
        初始化玩家蛇、AI1蛇（影子）、AI2蛇（影子）、食物位置和游戏状态变量。
        AI蛇完全模仿玩家的移动和蛇身长度，AI就是影子，AI死亡玩家也会死亡。
        """
        # 计算棋盘中心点
        mid = self.board_size // 2
        
        # 初始化玩家蛇（3节，位于中心）
        self.snake = [(mid + i, mid) for i in range(1, -2, -1)]
        self.snake_set = set(self.snake)
        self.direction = "DOWN"          # 玩家蛇初始方向
        
        # 初始化AI1蛇（3节，位于玩家左侧）
        self.ai1_snake = [(mid + i, mid - 5) for i in range(1, -2, -1)]
        self.ai1_snake_set = set(self.ai1_snake)
        self.ai1_direction = "DOWN"       # AI1蛇初始方向（与玩家相同）
        self.ai1_dead = False
        
        # 初始化AI2蛇（3节，位于玩家右侧）
        self.ai2_snake = [(mid + i, mid + 5) for i in range(1, -2, -1)]
        self.ai2_snake_set = set(self.ai2_snake)
        self.ai2_direction = "DOWN"       # AI2蛇初始方向（与玩家相同）
        self.ai2_dead = False
        
        # 初始化游戏状态
        self.score = 0
        self.ai1_score = 0
        self.ai2_score = 0
        self.death_reason = None
        self.game_start_time = time.time()  # 初始化游戏开始时间
        
        # 更新可用位置集合（排除三条蛇的位置）
        all_snake_positions = set(self.snake + self.ai1_snake + self.ai2_snake)
        self.non_snake = set((r, c) for r in range(self.board_size) for c in range(self.board_size) if (r, c) not in all_snake_positions)
        
        # 生成初始食物
        self.food = self._generate_food()

    def play_bgm(self):
        """播放背景音乐
        
        尝试播放背景音乐，如果文件不存在则静默失败。
        """
        if self.bgm_enabled and not self.bgm_playing:
            try:
                # 尝试加载并播放背景音乐（循环播放）
                mixer.music.load("sound/victory.wav")  # 使用现有的victory.wav作为背景音乐
                mixer.music.play(-1)  # -1表示循环播放
                self.bgm_playing = True
            except Exception:
                # 如果背景音乐文件不存在或无法播放，静默失败
                pass
    
    def pause_bgm(self):
        """暂停背景音乐"""
        if self.bgm_playing:
            try:
                mixer.music.pause()
                self.bgm_playing = False
            except Exception:
                pass
    
    def resume_bgm(self):
        """恢复播放背景音乐"""
        if self.bgm_enabled and not self.bgm_playing:
            try:
                mixer.music.unpause()
                self.bgm_playing = True
            except Exception:
                pass
    
    def draw_game_over_screen(self):
        """绘制游戏结束界面"""
        # 绘制深蓝色渐变背景
        for y in range(self.display_height):
            r = int(0)
            g = int(10)
            b = int(30 - 20 * y / self.display_height)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.display_width, y))
            
        margin_top = 60
        spacing = 35
        btn_spacing = 10

        # 标题 - 根据分数显示不同内容和颜色
        if self.score >= 1000:
            title_text = "恭喜胜利！"
            title_color = (255, 255, 100)  # 金黄色标题
            shadow_color = (180, 180, 0)   # 深黄色阴影
        else:
            title_text = "游戏结束"
            title_color = (255, 255, 255)  # 白色标题
            shadow_color = (150, 150, 150) # 灰色阴影
            
        # 标题阴影效果
        title_shadow = self.large_font.render(title_text, True, shadow_color)
        title = self.large_font.render(title_text, True, title_color)
        title_rect = title.get_rect(center=(self.display_width // 2, margin_top))
        
        # 绘制阴影和标题
        shadow_offset = 2
        self.screen.blit(title_shadow, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
        self.screen.blit(title, title_rect)

        # 分数显示 - 使用更醒目的颜色和更大的字体
        score_text = self.font.render(f"最终分数: {self.score}", True, (255, 255, 150))
        score_rect = score_text.get_rect(center=(self.display_width // 2, title_rect.bottom + spacing))
        self.screen.blit(score_text, score_rect)

        # 蛇身长度
        length = len(self.snake)
        length_text = self.font.render(f"蛇身长度: {length} 格", True, (200, 255, 200))
        length_rect = length_text.get_rect(center=(self.display_width // 2, score_rect.bottom + spacing // 2))
        self.screen.blit(length_text, length_rect)

        # 死亡原因
        reason_rect = None
        if hasattr(self, 'death_reason') and self.death_reason:
            reason_text = self.font.render(f"死亡原因: {self.death_reason}", True, (255, 200, 200))
            reason_rect = reason_text.get_rect(center=(self.display_width // 2, length_rect.bottom + spacing // 2))
            self.screen.blit(reason_text, reason_rect)

        # 绘制按钮
        button_width = 200
        button_height = 60
        button_y = self.display_height // 2
        
        # 重试按钮
        retry_button_rect = pygame.Rect(
            (self.display_width - button_width) // 2,
            button_y,
            button_width,
            button_height
        )
        pygame.draw.rect(self.screen, (0, 150, 0), retry_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (0, 255, 0), retry_button_rect, 2, border_radius=10)
        retry_text = self.font.render("重试", True, (255, 255, 255))
        retry_text_rect = retry_text.get_rect(center=retry_button_rect.center)
        self.screen.blit(retry_text, retry_text_rect)

        # 菜单按钮
        menu_button_rect = pygame.Rect(
            (self.display_width - button_width) // 2,
            button_y + button_height + btn_spacing,
            button_width,
            button_height
        )
        pygame.draw.rect(self.screen, (100, 100, 150), menu_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (150, 150, 255), menu_button_rect, 2, border_radius=10)
        menu_text = self.font.render("返回菜单", True, (255, 255, 255))
        menu_text_rect = menu_text.get_rect(center=menu_button_rect.center)
        self.screen.blit(menu_text, menu_text_rect)

        # 退出按钮
        exit_button_rect = pygame.Rect(
            (self.display_width - button_width) // 2,
            button_y + 2 * (button_height + btn_spacing),
            button_width,
            button_height
        )
        pygame.draw.rect(self.screen, (150, 0, 0), exit_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 0, 0), exit_button_rect, 2, border_radius=10)
        exit_text = self.font.render("退出游戏", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
    
    def stop_bgm(self):
        """停止背景音乐"""
        if self.bgm_playing:
            try:
                mixer.music.stop()
                self.bgm_playing = False
            except Exception:
                pass
                
    def reset_opponent_mode(self):
        """重置游戏状态（对抗模式）
        
        初始化玩家蛇、对抗蛇、食物位置和游戏状态变量。
        """
        # 计算棋盘中心点
        mid = self.board_size // 2
        
        # 初始化玩家蛇（3节，位于中心）
        self.snake = [(mid + i, mid) for i in range(1, -2, -1)]
        self.snake_set = set(self.snake)
        self.direction = "DOWN"          # 玩家蛇初始方向
        
        # 初始化对抗蛇（3节，位于对角位置避免与玩家蛇重叠）
        self.opponent_snake = [(mid - i - 5, mid - 5) for i in range(1, -2, -1)]
        self.opponent_snake_set = set(self.opponent_snake)
        self.opponent_direction = "UP"   # 对抗蛇初始方向（与玩家相反）
        self.opponent_dead = False       # 对抗蛇死亡状态标记
        
        # 初始化游戏状态
        self.score = 0
        self.opponent_score = 0
        self.death_reason = None
        self.game_start_time = time.time()  # 初始化游戏开始时间
        
        # 更新可用位置集合（排除两条蛇的位置）
        self._update_available_positions()
        
        # 生成初始食物
        self.food = self._generate_food()
        
    def _update_available_positions(self):
        """更新所有非蛇体位置的集合
        
        用于路径查找和食物生成时的位置有效性检查。
        """
        # 创建所有可能的位置集合
        all_positions = set((r, c) for r in range(self.board_size) 
                          for c in range(self.board_size))
        
        # 移除玩家蛇占据的位置
        available = all_positions - self.snake_set
        
        # 移除对抗蛇占据的位置（如果存在）
        if hasattr(self, 'opponent_snake_set'):
            available -= self.opponent_snake_set
        
        self.non_snake = available

    def step(self, action):
        """
        执行游戏的一步移动（普通模式）
        
        参数:
            action: -1（不变/无输入），或 0:UP, 1:LEFT, 2:RIGHT, 3:DOWN
            
        返回:
            tuple: (done, info) - done表示游戏是否结束，info包含游戏状态信息
        """
        # 更新方向（如果有新的动作输入）
        if action != -1:
            self._update_direction(action)

        # 计算新的蛇头位置
        row, col = self.snake[0]  # 当前蛇头位置
        if self.direction == "UP":
            row -= 1
        elif self.direction == "DOWN":
            row += 1
        elif self.direction == "LEFT":
            col -= 1
        elif self.direction == "RIGHT":
            col += 1
        
        new_head = (row, col)

        # 初始化状态变量
        done = False
        self.death_reason = None
        food_obtained = False

        # 处理蛇的移动和碰撞检测
        if new_head == self.food:
            # 吃到食物的情况
            food_obtained = True
            self.score += 10
            
            # 播放进食音效（静默失败）
            if self.sound_eat:
                try:
                    self.sound_eat.play()
                except Exception:
                    pass
                    
            # 添加新头部（不删除尾部，蛇长度增加）
            self.snake.insert(0, new_head)
            self.snake_set.add(new_head)
            self.non_snake.discard(new_head)
            
            # 添加吃到食物时的视觉反馈标记
            if not hasattr(self, 'food_effect_timer'):
                self.food_effect_timer = 0
                self.last_food_position = None
            self.last_food_position = new_head  # 记录吃到食物的位置
            self.food_effect_timer = 3  # 持续3帧的视觉效果
        else:
            # 没吃到食物的情况
            # 移除尾格并更新位置集合
            tail = self.snake.pop()
            if tail in self.snake_set:  # 确保tail存在于集合中再移除
                self.snake_set.remove(tail)
            self.non_snake.add(tail)
            
            # 添加新头部
            self.snake.insert(0, new_head)
            self.snake_set.add(new_head)
            self.non_snake.discard(new_head)

        # 检查碰撞条件
        # 1. 撞墙检测
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            done = True
            self.death_reason = "撞墙死亡"
        # 2. 撞到自己检测（检查蛇头是否与身体其他部分碰撞）
        elif len(self.snake) > 1 and new_head in self.snake[1:]:
            done = True
            self.death_reason = "撞到自己"

        # 处理游戏结束逻辑
        if done:
            # 播放游戏结束音效（静默失败）
            if self.sound_game_over:
                try:
                    self.sound_game_over.play()
                except Exception:
                    pass
        else:
            # 吃到食物时生成新食物
            if food_obtained:
                self.food = self._generate_food()

        # 构建并返回游戏状态信息
        info = {
            "snake_size": len(self.snake),
            "snake_head_pos": self.snake[0],  # 直接使用元组，避免不必要的转换
            "prev_snake_head_pos": self.snake[1] if len(self.snake) > 1 else self.snake[0],
            "food_pos": self.food,
            "food_obtained": food_obtained,
            "death_reason": self.death_reason
        }

        return done, info

    def step_opponent_mode(self, action):
        """
        执行游戏的一步移动（对抗模式）
        
        参数:
            action: -1（不变/无输入），或 0:UP, 1:LEFT, 2:RIGHT, 3:DOWN
            
        返回:
            tuple: (done, info) - done表示游戏是否结束，info包含游戏状态信息
        """
        # 更新方向（如果有新的动作输入）
        if action != -1:
            self._update_direction(action)

        # 计算新的蛇头位置
        row, col = self.snake[0]  # 当前蛇头位置
        if self.direction == "UP":
            row -= 1
        elif self.direction == "DOWN":
            row += 1
        elif self.direction == "LEFT":
            col -= 1
        elif self.direction == "RIGHT":
            col += 1
        
        new_head = (row, col)

        # 初始化状态变量
        done = False
        self.death_reason = None
        food_obtained = False

        # 先添加新头部（无论是否吃到食物）
        self.snake.insert(0, new_head)
        self.snake_set.add(new_head)
        self.non_snake.discard(new_head)

        # 检查是否吃到食物
        if new_head == self.food:
            food_obtained = True
            self.score += 10
            
            # 播放进食音效（静默失败）
            if self.sound_eat:
                try:
                    self.sound_eat.play()
                except Exception:
                    pass
                    
            # 添加吃到食物时的视觉反馈标记
            if not hasattr(self, 'food_effect_timer'):
                self.food_effect_timer = 0
                self.last_food_position = None
            self.last_food_position = new_head  # 记录吃到食物的位置
            self.food_effect_timer = 3  # 持续3帧的视觉效果
        else:
            # 没吃到食物时移除尾部（如果蛇长度>1）
            food_obtained = False
            if len(self.snake) > 1:
                tail = self.snake.pop()
                if tail in self.snake_set:  # 确保tail存在于集合中再移除
                    self.snake_set.remove(tail)
                self.non_snake.add(tail)

        # 检查碰撞条件
        # 1. 撞墙检测
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            done = True
            self.death_reason = "撞墙死亡"
        # 2. 撞到自己检测（检查蛇头是否与身体其他部分碰撞）
        elif len(self.snake) > 1 and new_head in self.snake[1:]:
            done = True
            self.death_reason = "撞到自己"
        # 3. 撞到对抗蛇检测
        elif new_head in self.opponent_snake_set:
            done = True
            self.death_reason = "撞到对抗蛇"

        # 处理游戏结束逻辑
        if done:
            # 播放游戏结束音效（静默失败）
            if self.sound_game_over:
                try:
                    self.sound_game_over.play()
                except Exception:
                    pass
        else:
            # 吃到食物时生成新食物
            if food_obtained:
                self.food = self._generate_food()

        # 构建并返回游戏状态信息（移除numpy依赖）
        info = {
            "snake_size": len(self.snake),
            "snake_head_pos": self.snake[0],  # 直接使用元组
            "prev_snake_head_pos": self.snake[1] if len(self.snake) > 1 else self.snake[0],
            "food_pos": self.food,
            "food_obtained": food_obtained,
            "death_reason": self.death_reason
        }

        return done, info

    def opponent_step(self, action):
        """
        处理对抗蛇的移动逻辑（增强版）
        
        参数:
            action: -1（不变/无输入），或 0:UP, 1:LEFT, 2:RIGHT, 3:DOWN
            
        返回:
            tuple: (done, info) - done表示对抗蛇是否死亡，info包含死亡原因
        """
        # 如果对抗蛇已经死亡，则不再移动
        if hasattr(self, 'opponent_dead') and self.opponent_dead:
            return True, {"death_reason": self.death_reason}

        # 更新移动方向（如果有新的动作输入）
        if action != -1:
            self._update_opponent_direction(action)

        # 计算新的对抗蛇头位置
        row, col = self.opponent_snake[0]  # 当前对抗蛇头位置
        if self.opponent_direction == "UP":
            row -= 1
        elif self.opponent_direction == "DOWN":
            row += 1
        elif self.opponent_direction == "LEFT":
            col -= 1
        elif self.opponent_direction == "RIGHT":
            col += 1
        
        new_head = (row, col)

        # 初始化状态变量
        done = False
        death_reason = None

        # 先添加新头部（无论是否吃到食物）
        self.opponent_snake.insert(0, new_head)
        self.opponent_snake_set.add(new_head)

        # 检查碰撞条件
        # 1. 撞墙检测
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            done = True
            death_reason = "对抗蛇撞墙死亡"
        # 2. 撞到自己检测（排除刚添加的头部）
        elif new_head in self.opponent_snake_set and new_head != self.opponent_snake[0]:
            done = True
            death_reason = "对抗蛇撞到自己"
        # 3. 撞到玩家蛇检测
        elif new_head in self.snake_set:
            done = True
            death_reason = "对抗蛇撞到玩家蛇"

        # 处理对抗蛇死亡逻辑
        if done:
            self.opponent_dead = True
            self.death_reason = death_reason
            # 为玩家增加额外奖励分数
            self.score += 50  # 击败对抗蛇的奖励
            
            # 播放对抗蛇死亡音效（如果有）
            if hasattr(self, 'sound_crash') and self.sound_crash:
                try:
                    self.sound_crash.play()
                except Exception:
                    pass
            
            return done, {"death_reason": death_reason}

        # 处理移动后的蛇身更新
        if new_head != self.food:
            # 没吃到食物时移除尾部（如果蛇长度>1）
            if len(self.opponent_snake) > 1:
                tail = self.opponent_snake.pop()
                self.opponent_snake_set.remove(tail)
        else:
            # 吃到食物，生成新食物
            self.opponent_score += 10
            
            # 播放对抗蛇进食音效（如果有）
            if hasattr(self, 'sound_eat') and self.sound_eat:
                try:
                    # 调整音量或使用不同音效区分玩家和对抗蛇
                    pygame.mixer.Sound.set_volume(self.sound_eat, 0.5)
                    self.sound_eat.play()
                    pygame.mixer.Sound.set_volume(self.sound_eat, 1.0)  # 恢复原音量
                except Exception:
                    pass
            
            self.food = self._generate_food()
        
        # 更新non_snake集合，确保游戏状态一致性
        self._update_available_positions()

        return done, {"death_reason": death_reason}

    def respawn_opponent(self):
        """重新部署对抗蛇"""
        mid = self.board_size // 2
        
        # 尝试最多10次生成有效的对抗蛇位置
        for _ in range(10):
            # 随机选择一个远离玩家的区域
            # 使用边界检查确保位置有效
            opponent_row = random.randint(2, self.board_size - 5)
            opponent_col = random.randint(2, self.board_size - 5)
            
            # 创建对抗蛇（3节）
            new_opponent_snake = [(opponent_row + i, opponent_col) for i in range(1, -2, -1)]
            new_opponent_set = set(new_opponent_snake)
            
            # 检查是否与玩家蛇重叠或越界
            valid_position = True
            for pos in new_opponent_snake:
                r, c = pos
                # 检查是否在棋盘内
                if r < 0 or r >= self.board_size or c < 0 or c >= self.board_size:
                    valid_position = False
                    break
                # 检查是否与玩家蛇重叠
                if pos in self.snake_set:
                    valid_position = False
                    break
            
            if valid_position:
                # 有效位置，更新对抗蛇
                self.opponent_snake = new_opponent_snake
                self.opponent_snake_set = new_opponent_set
                self.opponent_direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
                self.opponent_dead = False
                
                # 重新计算non_snake集合，确保准确性
                self.non_snake = set((r, c) for r in range(self.board_size) for c in range(self.board_size) 
                                  if (r, c) not in self.snake_set and (r, c) not in self.opponent_snake_set and (r, c) != self.food)
                return
        
        # 如果多次尝试都失败，使用安全的默认位置
        self.opponent_snake = [(max(2, mid - 3), max(2, mid - 5)), 
                              (max(2, mid - 4), max(2, mid - 5)), 
                              (max(2, mid - 5), max(2, mid - 5))]
        self.opponent_snake_set = set(self.opponent_snake)
        self.opponent_direction = "UP"
        self.opponent_dead = False
        
        # 重新计算non_snake集合
        self.non_snake = set((r, c) for r in range(self.board_size) for c in range(self.board_size) 
                          if (r, c) not in self.snake_set and (r, c) not in self.opponent_snake_set and (r, c) != self.food)

    def _update_direction(self, action):
        """
        根据用户操作更新玩家蛇的移动方向
        
        参数:
            action: 0:UP, 1:LEFT, 2:RIGHT, 3:DOWN
        
        说明:
            实现了180度转向限制，防止蛇直接反向移动
        """
        # 使用条件判断直接更新方向，避免不必要的嵌套
        if action == 0 and self.direction != "DOWN":  # 向上且不与当前方向冲突
            self.direction = "UP"
        elif action == 1 and self.direction != "RIGHT":  # 向左且不与当前方向冲突
            self.direction = "LEFT"
        elif action == 2 and self.direction != "LEFT":  # 向右且不与当前方向冲突
            self.direction = "RIGHT"
        elif action == 3 and self.direction != "UP":  # 向下且不与当前方向冲突
            self.direction = "DOWN"

    def _update_opponent_direction(self, action):
        """
        根据输入更新对抗蛇的移动方向
        
        参数:
            action: 0:UP, 1:LEFT, 2:RIGHT, 3:DOWN
        
        说明:
            实现了180度转向限制，防止对抗蛇直接反向移动
        """
        # 使用条件判断直接更新方向，避免不必要的嵌套
        if action == 0 and self.opponent_direction != "DOWN":  # 向上且不与当前方向冲突
            self.opponent_direction = "UP"
        elif action == 1 and self.opponent_direction != "RIGHT":  # 向左且不与当前方向冲突
            self.opponent_direction = "LEFT"
        elif action == 2 and self.opponent_direction != "LEFT":  # 向右且不与当前方向冲突
            self.opponent_direction = "RIGHT"
        elif action == 3 and self.opponent_direction != "UP":  # 向下且不与当前方向冲突
            self.opponent_direction = "DOWN"
            
    def step_three_snake_mode(self, action):
        """
        影子模式的游戏逻辑步骤
        AI蛇完全模仿玩家的移动和蛇身长度，AI就是影子，AI死亡玩家也死亡
        玩家吃到食物增长蛇身，AI也会增长蛇身
        
        参数:
            action: -1（不变/无输入），或 0:UP, 1:LEFT, 2:RIGHT, 3:DOWN
            
        返回:
            tuple: (done, info) - done表示游戏是否结束，info包含游戏状态信息
        """
        # 确保AI蛇的生命状态属性存在并设置为True
        if not hasattr(self, 'ai1_alive'):
            self.ai1_alive = True
        if not hasattr(self, 'ai2_alive'):
            self.ai2_alive = True
        
        # 初始化状态变量
        done = False
        self.death_reason = None
        food_obtained = False
        
        # 1. 处理玩家蛇的移动 - 传统蛇形移动方式
        if action != -1:
            self._update_direction(action)
        
        # 计算新的蛇头位置
        row, col = self.snake[0]  # 当前蛇头位置
        if self.direction == "UP":
            row -= 1
        elif self.direction == "DOWN":
            row += 1
        elif self.direction == "LEFT":
            col -= 1
        elif self.direction == "RIGHT":
            col += 1
        
        new_head = (row, col)
        
        # 先添加新头部（无论是否吃到食物）
        self.snake.insert(0, new_head)
        if hasattr(self, 'snake_set'):
            self.snake_set.add(new_head)
            self.non_snake.discard(new_head)
        
        # 检查碰撞条件（玩家蛇）
        # 1. 撞墙检测
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            done = True
            self.death_reason = "玩家蛇撞墙死亡！"
        # 2. 撞自己检测
        elif new_head in self.snake[1:]:
            done = True
            self.death_reason = "玩家蛇咬到自己！"
        # 3. 撞AI蛇检测
        elif hasattr(self, 'ai1_snake') and new_head in self.ai1_snake:
            done = True
            self.death_reason = "玩家蛇撞到AI1蛇！"
        elif hasattr(self, 'ai2_snake') and new_head in self.ai2_snake:
            done = True
            self.death_reason = "玩家蛇撞到AI2蛇！"
        
        # 2. 处理食物逻辑
        if not done and hasattr(self, 'food') and new_head == self.food:
            food_obtained = True
            self.score += 10
            # 记录最后食物位置用于视觉效果
            if hasattr(self, 'non_snake'):
                # 从可用位置集合中移除旧食物位置
                self.non_snake.discard(self.food)
            # 生成新食物
            self.food = self._generate_food()
        else:
            # 如果没吃到食物，移除尾部（保持蛇长度不变）
            tail = self.snake.pop()
            if hasattr(self, 'snake_set'):
                self.snake_set.discard(tail)
                self.non_snake.add(tail)
        
        # 3. 处理AI蛇的移动 - AI蛇完全模仿玩家移动（作为影子）
        if hasattr(self, 'ai1_snake') and hasattr(self, 'ai2_snake') and not done:
            # 3.1 计算AI1蛇的新位置（位于玩家左侧一定距离）
            shadow_offset1 = -5  # AI1位于玩家左侧5格
            new_ai1_snake = []
            
            for i, (r, c) in enumerate(self.snake):
                # 复制玩家蛇的形状，但水平位置偏移
                new_c = c + shadow_offset1
                # 确保在边界内
                new_c = max(0, min(new_c, self.board_size - 1))
                new_ai1_snake.append((r, new_c))
            
            # 3.2 计算AI2蛇的新位置（位于玩家右侧一定距离）
            shadow_offset2 = 5  # AI2位于玩家右侧5格
            new_ai2_snake = []
            
            for i, (r, c) in enumerate(self.snake):
                # 复制玩家蛇的形状，但水平位置偏移
                new_c = c + shadow_offset2
                # 确保在边界内
                new_c = max(0, min(new_c, self.board_size - 1))
                new_ai2_snake.append((r, new_c))
            
            # 检查AI蛇的碰撞
            # AI1蛇碰撞检测
            ai1_dead = False
            # 检查AI1蛇是否撞墙
            for (r, c) in new_ai1_snake:
                if r < 0 or r >= self.board_size or c < 0 or c >= self.board_size:
                    ai1_dead = True
                    break
            # 检查AI1蛇是否咬自己
            if not ai1_dead and len(set(new_ai1_snake)) != len(new_ai1_snake):
                ai1_dead = True
            # 检查AI1蛇是否撞玩家蛇
            if not ai1_dead and any(pos in self.snake for pos in new_ai1_snake):
                ai1_dead = True
            # 检查AI1蛇是否撞AI2蛇
            if not ai1_dead and any(pos in new_ai2_snake for pos in new_ai1_snake):
                ai1_dead = True
            
            # AI2蛇碰撞检测
            ai2_dead = False
            # 检查AI2蛇是否撞墙
            for (r, c) in new_ai2_snake:
                if r < 0 or r >= self.board_size or c < 0 or c >= self.board_size:
                    ai2_dead = True
                    break
            # 检查AI2蛇是否咬自己
            if not ai2_dead and len(set(new_ai2_snake)) != len(new_ai2_snake):
                ai2_dead = True
            # 检查AI2蛇是否撞玩家蛇
            if not ai2_dead and any(pos in self.snake for pos in new_ai2_snake):
                ai2_dead = True
            # 检查AI2蛇是否撞AI1蛇
            if not ai2_dead and any(pos in new_ai1_snake for pos in new_ai2_snake):
                ai2_dead = True
            
            # 更新AI蛇的生命状态
            self.ai1_alive = not ai1_dead
            self.ai2_alive = not ai2_dead
            
            # 如果任何一条AI蛇死亡，玩家也死亡
            if ai1_dead or ai2_dead:
                done = True
                if ai1_dead and ai2_dead:
                    self.death_reason = "两条影子蛇都死亡了！"
                elif ai1_dead:
                    self.death_reason = "左侧影子蛇死亡了！"
                else:
                    self.death_reason = "右侧影子蛇死亡了！"
            else:
                # 更新AI蛇的位置
                # 先从non_snake中移除旧位置
                if hasattr(self, 'non_snake'):
                    for pos in self.ai1_snake:
                        self.non_snake.add(pos)
                    for pos in self.ai2_snake:
                        self.non_snake.add(pos)
                
                # 更新AI蛇的位置
                self.ai1_snake = new_ai1_snake
                self.ai2_snake = new_ai2_snake
                
                # 从non_snake中添加新位置
                if hasattr(self, 'non_snake'):
                    for pos in self.ai1_snake:
                        self.non_snake.discard(pos)
                    for pos in self.ai2_snake:
                        self.non_snake.discard(pos)
        
        # 返回游戏状态
        info = {
            "death_reason": self.death_reason,
            "score": self.score,
            "food_obtained": food_obtained,
            "ai1_alive": self.ai1_alive,
            "ai2_alive": self.ai2_alive
        }
        
        return done, info

    def _generate_food(self):
        """随机在空格里生成食物（若无可用空格则返回 (0,0)）"""
        if len(self.non_snake) > 0:
            # 将集合转换为列表后再随机选择
            non_snake_list = list(self.non_snake)
            return non_snake_list[0] if len(non_snake_list) == 1 else random.choice(non_snake_list)
        else:
            return (0, 0)

    # ---------------------------
    # 绘图与 UI
    # ---------------------------
    def draw_board(self, draw_opponent=False):
        """
        绘制游戏界面，包括棋盘、蛇和食物
        
        参数:
            draw_opponent: 是否绘制对抗蛇
        """
        # 绘制深蓝色渐变背景
        for y in range(self.screen.get_height()):
            # 从深蓝到稍微亮一点的蓝色渐变
            r = max(0, int(10 - 5 * y / self.screen.get_height()))
            g = max(0, int(15 - 8 * y / self.screen.get_height()))
            b = max(20, int(30 + 10 * y / self.screen.get_height()))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen.get_width(), y))

        # 绘制游戏区域背景
        pygame.draw.rect(self.screen, (10, 15, 30),
                         (self.border_size, self.border_size, self.width, self.height),
                         border_radius=5)
        
        # 绘制棋盘网格线（浅灰色，半透明）和灰色对角线填充
        grid_color = (50, 50, 70, 100)
        # 绘制两条主对角线上的格子填充灰色
        diagonal_color = (40, 40, 60, 150)  # 灰色填充颜色
        for r in range(self.board_size):
            for c in range(self.board_size):
                # 判断是否在主对角线上（左上到右下）或副对角线上（右上到左下）
                if r == c or r + c == self.board_size - 1:
                    # 计算格子的左上角坐标
                    start_x = self.border_size + c * self.cell_size
                    start_y = self.border_size + r * self.cell_size
                    # 填充整个格子为灰色
                    pygame.draw.rect(self.screen, diagonal_color,
                                  (start_x, start_y, self.cell_size, self.cell_size))
        
        # 绘制网格线
        for i in range(1, self.board_size):
            # 垂直线
            x = self.border_size + i * self.cell_size
            pygame.draw.line(self.screen, grid_color, 
                           (x, self.border_size), 
                           (x, self.border_size + self.height),
                           1)
            # 水平线
            y = self.border_size + i * self.cell_size
            pygame.draw.line(self.screen, grid_color, 
                           (self.border_size, y), 
                           (self.border_size + self.width, y),
                           1)

        # 绘制棋盘边框（白色双线，增强视觉效果）
        # 外边框
        pygame.draw.rect(self.screen, (150, 150, 180),
                         (self.border_size - 3, self.border_size - 3, self.width + 6, self.height + 6), 2)
        # 内边框
        pygame.draw.rect(self.screen, (200, 200, 255),
                         (self.border_size - 1, self.border_size - 1, self.width + 2, self.height + 2), 1)

        # 绘制玩家蛇
        self.draw_snake()
        
        # 绘制对抗蛇（仅在对抗模式且对抗蛇未死亡时）
        opponent_alive = hasattr(self, 'opponent_snake') and (
            not hasattr(self, 'opponent_dead') or not self.opponent_dead
        )
        if draw_opponent and opponent_alive:
            self.draw_opponent_snake()
        
        # 绘制AI1蛇（影子模式）
        ai1_alive = hasattr(self, 'ai1_snake') and (not hasattr(self, 'ai1_dead') or not self.ai1_dead)
        if ai1_alive:
            self.draw_ai_3snake('ai1')
        
        # 绘制AI2蛇（影子模式）
        ai2_alive = hasattr(self, 'ai2_snake') and (not hasattr(self, 'ai2_dead') or not self.ai2_dead)
        if ai2_alive:
            self.draw_ai_3snake('ai2')

        # 绘制食物 - 使用更吸引人的样式，带有立体感和脉动效果
        if len(self.snake) < self.grid_size:
            r, c = self.food
            food_x = c * self.cell_size + self.border_size
            food_y = r * self.cell_size + self.border_size
            
            # 添加脉动动画效果
            if not hasattr(self, 'food_pulse_timer'):
                self.food_pulse_timer = 0
            self.food_pulse_timer = (self.food_pulse_timer + 1) % 60
            pulse_factor = 1.0 + 0.1 * abs(30 - self.food_pulse_timer) / 30
            
            # 计算食物大小
            base_size = self.cell_size * 0.8
            current_size = base_size * pulse_factor
            offset = (self.cell_size - current_size) // 2
            
            # 食物阴影（增加立体感）
            shadow_offset = 2
            pygame.draw.circle(self.screen, (150, 10, 10),
                              (food_x + self.cell_size // 2 + shadow_offset, 
                               food_y + self.cell_size // 2 + shadow_offset),
                              current_size // 2)
            
            # 食物主体（渐变色圆形）
            # 创建径向渐变效果的surface
            food_surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            center = (self.cell_size // 2, self.cell_size // 2)
            radius = int(current_size // 2)
            
            # 从中心到边缘的径向渐变
            for i in range(radius, 0, -1):
                intensity = 255 - (radius - i) * 255 // radius
                color = (255, intensity // 5, intensity // 5)
                pygame.draw.circle(food_surf, color, center, i)
            
            # 将渐变效果绘制到屏幕
            self.screen.blit(food_surf, (food_x, food_y))
            
            # 食物高光（增加光泽感）
            highlight_size = max(1, current_size // 4)
            pygame.draw.circle(self.screen, (255, 255, 255),
                              (food_x + self.cell_size // 2 - offset, 
                               food_y + self.cell_size // 2 - offset),
                              highlight_size)
            
            # 食物细节点缀（装饰效果）
            decor_size = max(1, current_size // 8)
            decor_positions = [
                (food_x + self.cell_size // 4, food_y + self.cell_size // 4),
                (food_x + self.cell_size * 3 // 4, food_y + self.cell_size // 4),
                (food_x + self.cell_size // 4, food_y + self.cell_size * 3 // 4),
                (food_x + self.cell_size * 3 // 4, food_y + self.cell_size * 3 // 4)
            ]
            
            for pos in decor_positions:
                pygame.draw.circle(self.screen, (255, 255, 255, 180), pos, decor_size)
        
        # 绘制吃到食物时的视觉反馈效果
        if hasattr(self, 'food_effect_timer') and self.food_effect_timer > 0 and hasattr(self, 'last_food_position') and self.last_food_position:
            # 计算效果的屏幕坐标
            r, c = self.last_food_position
            effect_x = c * self.cell_size + self.border_size
            effect_y = r * self.cell_size + self.border_size
            
            # 根据计时器计算效果大小和透明度
            size_factor = 1.0 + (3 - self.food_effect_timer) * 0.3
            opacity = 255 - (3 - self.food_effect_timer) * 85
            
            # 创建一个临时的surface用于绘制带透明度的效果
            effect_surf = pygame.Surface((self.cell_size * 2, self.cell_size * 2), pygame.SRCALPHA)
            
            # 绘制食物效果的外环（带有渐变效果）
            for i in range(5):
                current_size = int(self.cell_size * size_factor * (1 - i * 0.15))
                current_opacity = int(opacity * (1 - i * 0.2))
                pygame.draw.circle(
                    effect_surf,
                    (255, 255, 50, current_opacity),  # 黄色带透明度
                    (self.cell_size, self.cell_size),
                    current_size // 2
                )
            
            # 将效果绘制到屏幕上
            self.screen.blit(effect_surf, (effect_x - self.cell_size // 2, effect_y - self.cell_size // 2))
            
            # 减少计时器
            self.food_effect_timer -= 1

    def draw_opponent_snake(self):
        """绘制对抗蛇（包括头部和眼睛）"""
        head_r, head_c = self.opponent_snake[0]
        head_x = head_c * self.cell_size + self.border_size
        head_y = head_r * self.cell_size + self.border_size

        # 绘制蛇头（深红色调，更有质感）
        snake_head_color = (180, 0, 0)  # 更深的红色
        pygame.draw.polygon(self.screen, snake_head_color, [
            (head_x + self.cell_size // 2, head_y),
            (head_x + self.cell_size, head_y + self.cell_size // 2),
            (head_x + self.cell_size // 2, head_y + self.cell_size),
            (head_x, head_y + self.cell_size // 2)
        ])
        
        # 添加头部光泽效果
        highlight_color = (220, 80, 80)
        highlight_points = [
            (head_x + self.cell_size // 2, head_y + self.cell_size // 5),
            (head_x + self.cell_size * 0.8, head_y + self.cell_size // 2),
            (head_x + self.cell_size // 2, head_y + self.cell_size * 0.4),
            (head_x + self.cell_size * 0.2, head_y + self.cell_size // 2)
        ]
        pygame.draw.polygon(self.screen, highlight_color, highlight_points)

        # 眼睛 - 根据当前方向调整眼睛位置，增强视觉反馈
        eye_size = max(2, self.cell_size // 12)  # 根据单元格大小动态调整
        eye_offset = self.cell_size // 4
        
        # 根据移动方向调整眼睛位置，让蛇看起来朝移动方向看
        if self.opponent_direction == "UP":
            eye1_pos = (head_x + eye_offset, head_y + eye_offset)
            eye2_pos = (head_x + self.cell_size - eye_offset, head_y + eye_offset)
        elif self.opponent_direction == "DOWN":
            eye1_pos = (head_x + eye_offset, head_y + self.cell_size - eye_offset)
            eye2_pos = (head_x + self.cell_size - eye_offset, head_y + self.cell_size - eye_offset)
        elif self.opponent_direction == "LEFT":
            eye1_pos = (head_x + eye_offset, head_y + eye_offset)
            eye2_pos = (head_x + eye_offset, head_y + self.cell_size - eye_offset)
        else:  # RIGHT
            eye1_pos = (head_x + self.cell_size - eye_offset, head_y + eye_offset)
            eye2_pos = (head_x + self.cell_size - eye_offset, head_y + self.cell_size - eye_offset)
        
        # 绘制眼睛和瞳孔
        pygame.draw.circle(self.screen, (255, 255, 255), eye1_pos, eye_size)
        pygame.draw.circle(self.screen, (255, 255, 255), eye2_pos, eye_size)
        pygame.draw.circle(self.screen, (0, 0, 0), eye1_pos, eye_size // 2)
        pygame.draw.circle(self.screen, (0, 0, 0), eye2_pos, eye_size // 2)
        
        # 绘制身体部分
        for i, (r, c) in enumerate(self.opponent_snake[1:]):
            body_x = c * self.cell_size + self.border_size
            body_y = r * self.cell_size + self.border_size
            # 使用稍微浅一点的红色表示身体
            body_color = (200, 50, 50)
            pygame.draw.rect(self.screen, body_color, (body_x, body_y, self.cell_size, self.cell_size), border_radius=5)
    
    def draw_ai_3snake(self, ai_type):
        """
        绘制AI蛇（影子模式）
        
        参数:
            ai_type: 'ai1' 或 'ai2'
        """
        # 根据AI类型选择蛇的属性
        if ai_type == 'ai1':
            snake = self.ai1_snake
            direction = self.ai1_direction
            # AI1蛇使用蓝色
            head_color = (0, 150, 255)
            body_color = (0, 100, 255)
        else:  # ai2
            snake = self.ai2_snake
            direction = self.ai2_direction
            # AI2蛇使用紫色
            head_color = (150, 0, 255)
            body_color = (100, 0, 255)
        
        # 绘制蛇身
        for i, (r, c) in enumerate(snake):
            x = c * self.cell_size + self.border_size
            y = r * self.cell_size + self.border_size
            
            # 蛇头特殊绘制
            if i == 0:
                # 绘制蛇头（多边形）
                pygame.draw.polygon(self.screen, head_color, [
                    (x + self.cell_size // 2, y),
                    (x + self.cell_size, y + self.cell_size // 2),
                    (x + self.cell_size // 2, y + self.cell_size),
                    (x, y + self.cell_size // 2)
                ])
                
                # 添加头部光泽效果
                highlight_color = (min(head_color[0] + 40, 255), min(head_color[1] + 40, 255), min(head_color[2] + 40, 255))
                highlight_points = [
                    (x + self.cell_size // 2, y + self.cell_size // 5),
                    (x + self.cell_size * 0.8, y + self.cell_size // 2),
                    (x + self.cell_size // 2, y + self.cell_size * 0.4),
                    (x + self.cell_size * 0.2, y + self.cell_size // 2)
                ]
                pygame.draw.polygon(self.screen, highlight_color, highlight_points)
                
                # 绘制眼睛（根据移动方向调整位置）
                eye_size = max(2, self.cell_size // 12)
                eye_offset = self.cell_size // 4
                
                if direction == "UP":
                    eye1_pos = (x + eye_offset, y + eye_offset)
                    eye2_pos = (x + self.cell_size - eye_offset, y + eye_offset)
                elif direction == "DOWN":
                    eye1_pos = (x + eye_offset, y + self.cell_size - eye_offset)
                    eye2_pos = (x + self.cell_size - eye_offset, y + self.cell_size - eye_offset)
                elif direction == "LEFT":
                    eye1_pos = (x + eye_offset, y + eye_offset)
                    eye2_pos = (x + eye_offset, y + self.cell_size - eye_offset)
                else:  # RIGHT
                    eye1_pos = (x + self.cell_size - eye_offset, y + eye_offset)
                    eye2_pos = (x + self.cell_size - eye_offset, y + self.cell_size - eye_offset)
                
                # 绘制眼睛和瞳孔
                pygame.draw.circle(self.screen, (255, 255, 255), eye1_pos, eye_size)
                pygame.draw.circle(self.screen, (255, 255, 255), eye2_pos, eye_size)
                pygame.draw.circle(self.screen, (0, 0, 0), eye1_pos, eye_size // 2)
                pygame.draw.circle(self.screen, (0, 0, 0), eye2_pos, eye_size // 2)
            else:
                # 绘制蛇身
                pygame.draw.rect(self.screen, body_color, (x, y, self.cell_size, self.cell_size), border_radius=5)
        
        # 绘制蛇身体（渐变效果）
        snake_to_draw = self.ai1_snake if ai_type == 'ai1' else self.ai2_snake
        for i, (r, c) in enumerate(snake_to_draw[1:]):
            segment_x = c * self.cell_size + self.border_size
            segment_y = r * self.cell_size + self.border_size
            
            # 根据位置计算渐变色（立方函数，更自然的过渡）
            total_segments = len(snake_to_draw) - 1
            if total_segments > 0:
                progress = 1 - (i / total_segments)
                # 使用立方函数让颜色变化更自然
                progress_cubed = progress ** 3
                
                # 蓝色/紫色渐变：从头部附近的亮色到尾部的暗色
                if ai_type == 'ai1':
                    # 蓝色渐变
                    blue_intensity = int(150 + 105 * progress_cubed)
                    red_green = int(50 + 50 * progress_cubed)
                else:
                    # 紫色渐变
                    red_intensity = int(100 + 100 * progress_cubed)
                    blue_intensity = int(100 + 100 * progress_cubed)
                    green_intensity = int(20 + 30 * progress_cubed)
                
                # 添加一点随机性使身体更有趣
                random_offset = random.randint(-5, 5)
                if ai_type == 'ai1':
                    # 蓝色渐变颜色
                    segment_color = (max(30, min(200, red_green + random_offset)), 
                                    max(0, min(50, red_green + random_offset)), 
                                    max(0, min(255, blue_intensity + random_offset)))
                else:
                    # 紫色渐变颜色
                    segment_color = (max(30, min(200, red_intensity + random_offset)), 
                                    max(0, min(50, green_intensity + random_offset)), 
                                    max(0, min(200, blue_intensity + random_offset)))
                
                # 绘制带圆角的矩形身体
                rect = pygame.Rect(segment_x + 2, segment_y + 2, 
                                  self.cell_size - 4, self.cell_size - 4)
                pygame.draw.rect(self.screen, segment_color, rect, border_radius=5)
                
                # 添加高光效果
                highlight_rect = pygame.Rect(segment_x + 3, segment_y + 3, 
                                          self.cell_size - 8, self.cell_size // 3)
                highlight_color = (min(255, segment_color[0] + 40), 
                                  min(255, segment_color[1] + 40), 
                                  min(255, segment_color[2] + 40))
                pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=2)
            
            # 尾部尖端处理
            if i == total_segments - 1 and total_segments > 1:
                prev_r, prev_c = snake_to_draw[-2]
                # 确定尾部方向
                if prev_r < r:  # 尾部向下
                    pygame.draw.polygon(self.screen, segment_color, [
                        (segment_x + self.cell_size // 2, segment_y),
                        (segment_x, segment_y + self.cell_size),
                        (segment_x + self.cell_size, segment_y + self.cell_size)
                    ])
                elif prev_r > r:  # 尾部向上
                    pygame.draw.polygon(self.screen, segment_color, [
                        (segment_x + self.cell_size // 2, segment_y + self.cell_size),
                        (segment_x, segment_y),
                        (segment_x + self.cell_size, segment_y)
                    ])
                elif prev_c < c:  # 尾部向右
                    pygame.draw.polygon(self.screen, segment_color, [
                        (segment_x, segment_y + self.cell_size // 2),
                        (segment_x + self.cell_size, segment_y),
                        (segment_x + self.cell_size, segment_y + self.cell_size)
                    ])
                else:  # 尾部向左
                    pygame.draw.polygon(self.screen, segment_color, [
                        (segment_x + self.cell_size, segment_y + self.cell_size // 2),
                        (segment_x, segment_y),
                        (segment_x, segment_y + self.cell_size)
                    ])
            # 删除错误的眼睛绘制代码

        # 绘制身体 - 使用渐变效果，与玩家蛇风格一致
        # 这部分代码已经在上面实现，此处为重复代码，需要删除
            
            # 删除重复代码

    def draw_snake(self):
        """绘制蛇（头、眼、身体渐变）"""
        # 头坐标换算为像素
        head_r, head_c = self.snake[0]
        head_x = head_c * self.cell_size + self.border_size
        head_y = head_r * self.cell_size + self.border_size

        # 头（蓝色多边形）- 使用更深的蓝色，添加光泽效果
        head_color = (80, 120, 255)
        pygame.draw.polygon(self.screen, head_color, [
            (head_x + self.cell_size // 2, head_y),
            (head_x + self.cell_size, head_y + self.cell_size // 2),
            (head_x + self.cell_size // 2, head_y + self.cell_size),
            (head_x, head_y + self.cell_size // 2)
        ])
        
        # 添加蛇头光泽效果
        gloss_points = [
            (head_x + self.cell_size // 3, head_y + self.cell_size // 4),
            (head_x + self.cell_size // 2, head_y + self.cell_size // 3),
            (head_x + 2 * self.cell_size // 3, head_y + self.cell_size // 4),
            (head_x + self.cell_size // 2, head_y + self.cell_size // 2)
        ]
        pygame.draw.polygon(self.screen, (150, 180, 255), gloss_points)

        # 眼睛 - 根据当前方向调整眼睛位置，增强视觉反馈
        eye_size = max(3, self.cell_size // 6)
        pupil_size = max(1, eye_size // 2)
        eye_offset = self.cell_size // 4
        
        # 根据移动方向调整眼睛位置，让蛇看起来朝移动方向看
        if self.direction == "UP":
            eye_y_offset = -eye_offset
            eye_x_offset1 = -eye_offset
            eye_x_offset2 = eye_offset
        elif self.direction == "DOWN":
            eye_y_offset = eye_offset
            eye_x_offset1 = -eye_offset
            eye_x_offset2 = eye_offset
        elif self.direction == "LEFT":
            eye_x_offset1 = -eye_offset
            eye_x_offset2 = -eye_offset
            eye_y_offset1 = -eye_offset
            eye_y_offset2 = eye_offset
        else:  # RIGHT
            eye_x_offset1 = eye_offset
            eye_x_offset2 = eye_offset
            eye_y_offset1 = -eye_offset
            eye_y_offset2 = eye_offset
        
        # 绘制眼睛
        if self.direction in ["LEFT", "RIGHT"]:
            # 左眼
            pygame.draw.circle(self.screen, (255, 255, 255), 
                              (head_x + self.cell_size // 2 + eye_x_offset1, 
                               head_y + self.cell_size // 2 + eye_y_offset1), 
                              eye_size)
            # 左眼瞳孔
            pygame.draw.circle(self.screen, (0, 0, 0), 
                              (head_x + self.cell_size // 2 + eye_x_offset1 + 
                               (eye_x_offset1 // abs(eye_x_offset1) if eye_x_offset1 != 0 else 0) * 2, 
                               head_y + self.cell_size // 2 + eye_y_offset1), 
                              pupil_size)
            # 右眼
            pygame.draw.circle(self.screen, (255, 255, 255), 
                              (head_x + self.cell_size // 2 + eye_x_offset2, 
                               head_y + self.cell_size // 2 + eye_y_offset2), 
                              eye_size)
            # 右眼瞳孔
            pygame.draw.circle(self.screen, (0, 0, 0), 
                              (head_x + self.cell_size // 2 + eye_x_offset2 + 
                               (eye_x_offset2 // abs(eye_x_offset2) if eye_x_offset2 != 0 else 0) * 2, 
                               head_y + self.cell_size // 2 + eye_y_offset2), 
                              pupil_size)
        else:  # UP, DOWN
            # 左眼
            pygame.draw.circle(self.screen, (255, 255, 255), 
                              (head_x + self.cell_size // 2 + eye_x_offset1, 
                               head_y + self.cell_size // 2 + eye_y_offset), 
                              eye_size)
            # 左眼瞳孔
            pygame.draw.circle(self.screen, (0, 0, 0), 
                              (head_x + self.cell_size // 2 + eye_x_offset1, 
                               head_y + self.cell_size // 2 + eye_y_offset + 
                               (eye_y_offset // abs(eye_y_offset) if eye_y_offset != 0 else 0) * 2), 
                              pupil_size)
            # 右眼
            pygame.draw.circle(self.screen, (255, 255, 255), 
                              (head_x + self.cell_size // 2 + eye_x_offset2, 
                               head_y + self.cell_size // 2 + eye_y_offset), 
                              eye_size)
            # 右眼瞳孔
            pygame.draw.circle(self.screen, (0, 0, 0), 
                              (head_x + self.cell_size // 2 + eye_x_offset2, 
                               head_y + self.cell_size // 2 + eye_y_offset + 
                               (eye_y_offset // abs(eye_y_offset) if eye_y_offset != 0 else 0) * 2), 
                              pupil_size)

        # 身体渐变（增强视觉效果）
        body_length = len(self.snake) - 1
        for i, (r, c) in enumerate(self.snake[1:]):
            body_x = c * self.cell_size + self.border_size
            body_y = r * self.cell_size + self.border_size
            
            # 计算渐变颜色 - 更平滑的渐变效果
            progress = i / max(body_length, 1)
            # 使用立方函数使渐变更自然
            green_intensity = int(255 - (155 * progress * progress * progress))
            
            # 根据不同部分使用微妙的颜色变化
            if i == 0:  # 靠近头部的第一节
                color = (50, green_intensity, 50)
            else:
                # 身体部分使用稍微不同的绿色色调
                green_variation = random.randint(-15, 15)  # 添加一点随机性
                color = (0, max(50, min(255, green_intensity + green_variation)), 0)
            
            # 绘制身体段，使用更大的圆角
            pygame.draw.rect(self.screen, color, 
                           (body_x, body_y, self.cell_size, self.cell_size), 
                           border_radius=max(4, self.cell_size // 3))
            
            # 添加身体高光效果
            highlight_rect = pygame.Rect(
                body_x + self.cell_size // 4,
                body_y + self.cell_size // 4,
                self.cell_size // 2,
                self.cell_size // 4
            )
            highlight_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=2)
            
            # 尾部特殊处理
            if i == body_length - 1:
                # 尾部尖端效果
                tail_center_x = body_x + self.cell_size // 2
                tail_center_y = body_y + self.cell_size // 2
                # 确定尾部方向
                if i > 0:
                    prev_r, prev_c = self.snake[-2]
                    if prev_r < r:  # 尾部向下
                        pygame.draw.polygon(self.screen, color, [
                            (tail_center_x - self.cell_size // 3, tail_center_y - self.cell_size // 4),
                            (tail_center_x + self.cell_size // 3, tail_center_y - self.cell_size // 4),
                            (tail_center_x, tail_center_y + self.cell_size // 2)
                        ])
                    elif prev_r > r:  # 尾部向上
                        pygame.draw.polygon(self.screen, color, [
                            (tail_center_x - self.cell_size // 3, tail_center_y + self.cell_size // 4),
                            (tail_center_x + self.cell_size // 3, tail_center_y + self.cell_size // 4),
                            (tail_center_x, tail_center_y - self.cell_size // 2)
                        ])
                    elif prev_c < c:  # 尾部向右
                        pygame.draw.polygon(self.screen, color, [
                            (tail_center_x - self.cell_size // 4, tail_center_y - self.cell_size // 3),
                            (tail_center_x - self.cell_size // 4, tail_center_y + self.cell_size // 3),
                            (tail_center_x + self.cell_size // 2, tail_center_y)
                        ])
                    elif prev_c > c:  # 尾部向左
                        pygame.draw.polygon(self.screen, color, [
                            (tail_center_x + self.cell_size // 4, tail_center_y - self.cell_size // 3),
                            (tail_center_x + self.cell_size // 4, tail_center_y + self.cell_size // 3),
                            (tail_center_x - self.cell_size // 2, tail_center_y)
                        ])

    def draw_side_panel(self, ai_connected, show_ai=True):
        """
        在右侧绘制控制面板：
        - 分数、长度
        - 对抗模式下显示对抗蛇信息
        - AI 连接按钮和状态
        """
        panel_x = self.width + self.border_size + 20
        panel_y = self.border_size
        panel_width = 200

        # 绘制面板背景（半透明，增强视觉层次感）
        panel_bg_rect = pygame.Rect(panel_x - 10, panel_y, panel_width, 400)
        pygame.draw.rect(self.screen, (30, 30, 30, 180), panel_bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 80, 80), panel_bg_rect, border_radius=10, width=1)

        # 标题
        title_surf = self.large_font.render("控制面板", True, (220, 220, 220))
        self.screen.blit(title_surf, (panel_x, panel_y))

        panel_y += 60

        # 玩家蛇信息
        score_surf = self.font.render(f"玩家分数: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surf, (panel_x, panel_y))
        panel_y += 25
        size_surf = self.font.render(f"蛇长: {len(self.snake)}", True, (255, 255, 255))
        self.screen.blit(size_surf, (panel_x, panel_y))
        panel_y += 25
        
        # 显示当前等级/速度信息
        speed_level = max(1, int(self.speed / 5))
        speed_surf = self.font.render(f"速度等级: {speed_level}", True, (200, 200, 255))
        self.screen.blit(speed_surf, (panel_x, panel_y))
        panel_y += 35

        # 对抗模式信息（如果存在对抗蛇）
        if hasattr(self, 'opponent_snake'):
            # 显示对抗蛇分数和状态
            opponent_status = "存活" if (not hasattr(self, 'opponent_dead') or not self.opponent_dead) else "已死亡"
            opponent_status_color = (255, 100, 100) if opponent_status == "已死亡" else (200, 200, 200)
            
            opponent_title_surf = self.font.render("对抗蛇信息:", True, (220, 100, 100))
            self.screen.blit(opponent_title_surf, (panel_x, panel_y))
            panel_y += 25
            
            # 对抗蛇分数
            opponent_score = getattr(self, 'opponent_score', 0)
            opponent_score_surf = self.font.render(f"分数: {opponent_score}", True, (255, 255, 255))
            self.screen.blit(opponent_score_surf, (panel_x + 10, panel_y))
            panel_y += 25
            
            # 对抗蛇状态
            opponent_status_surf = self.font.render(f"状态: {opponent_status}", True, opponent_status_color)
            self.screen.blit(opponent_status_surf, (panel_x + 10, panel_y))
            panel_y += 35

        # 只在普通模式下显示AI相关内容
        if show_ai:
            # AI 状态显示
            status_text = "已连接" if ai_connected else "已断开"
            status_color = (100, 255, 100) if ai_connected else (255, 100, 100)
            status_surf = self.font.render(f"AI 状态: {status_text}", True, status_color)
            self.screen.blit(status_surf, (panel_x, panel_y))
            panel_y += 40

            # 绘制按钮（Connect/Disconnect）- 改进视觉效果
            self.ai_button_rect = pygame.Rect(panel_x, panel_y, 160, 36)
            mouse_pos = pygame.mouse.get_pos()
            hovering = self.ai_button_rect.collidepoint(mouse_pos)
            
            # 按钮背景和边框效果
            bg_color = (100, 180, 255) if ai_connected else (100, 255, 150)
            hover_color = (150, 210, 255) if ai_connected else (150, 255, 200)
            border_color = (200, 200, 200)
            
            button_color = hover_color if hovering else bg_color
            pygame.draw.rect(self.screen, button_color, self.ai_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, self.ai_button_rect, border_radius=8, width=2)
            
            # 按钮文字
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

# 导入必要的库
import heapq
from collections import deque, defaultdict
import random

# ---------------------------
# AI 行为接口
# ---------------------------
def get_ai_action(game, is_opponent=False):
    """
    智能AI策略：支持控制对抗蛇
    优化版本：集成A*搜索、智能空间评估、循环检测和长期生存策略
    对抗模式增强：添加攻击玩家、包围、食物竞争和防御策略
    is_opponent: True=控制红色对抗蛇，False=控制绿色玩家蛇
    """
    # 根据控制对象选择蛇的信息
    if is_opponent:
        snake = game.opponent_snake
        direction = game.opponent_direction
        # 使用现有的opponent_snake_set提高性能
        if hasattr(game, 'opponent_snake_set'):
            body = game.opponent_snake_set
        else:
            body = set(snake)
        # 获取对抗蛇特定的信息
        if hasattr(game, 'opponent_score'):
            score = game.opponent_score
        else:
            score = len(snake) - 3  # 默认初始长度为3
        
        # 获取玩家蛇信息（对抗模式特有）
        if hasattr(game, 'snake'):
            player_snake = game.snake
            player_head = player_snake[0] if player_snake else None
            player_body = set(player_snake) if player_snake else set()
        else:
            player_snake = []
            player_head = None
            player_body = set()
    else:
        snake = game.snake
        direction = game.direction
        # 使用现有的snake_set提高性能
        if hasattr(game, 'snake_set'):
            body = game.snake_set
        else:
            body = set(snake)
        score = game.score
        
        # 非对抗模式时初始化玩家相关变量
        player_snake = []
        player_head = None
        player_body = set()
    


    head = snake[0]
    food = game.food
    board = game.board_size
    snake_length = len(snake)
    
    # 计算游戏进度百分比
    board_area = board * board
    game_progress = snake_length / board_area

    # 方向映射
    dirs = {
        0: (-1, 0),  # 上
        1: (0, -1),  # 左
        2: (0, 1),   # 右
        3: (1, 0)    # 下
    }

    # 方向名称映射
    dir_names = {
        0: "UP",
        1: "LEFT",
        2: "RIGHT",
        3: "DOWN"
    }

    opposite = {"UP": 3, "DOWN": 0, "LEFT": 2, "RIGHT": 1}
    opposite_dir = opposite.get(direction, -1)  # 使用对应蛇的当前方向

    # 检查位置是否有效
    def is_valid(pos):
        r, c = pos
        return 0 <= r < board and 0 <= c < board and (r, c) not in body
    
    # 曼哈顿距离计算
    def manhattan_dist(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    # 欧几里得距离计算
    def euclidean_dist(pos1, pos2):
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
    
    # ----------------------------------------------------------------------
    # � A*搜索算法：更智能的路径规划
    # ----------------------------------------------------------------------
    def a_star_path(start, goal):
        """优化版A*搜索算法：限制搜索范围，使用更高效的数据结构，支持障碍物检测"""
        # 快速检查目标是否已被占据
        if goal in body:
            return None, float('inf')
            
        # 如果起点就是终点
        if start == goal:
            return [], 0
        
        # 优化：限制搜索深度，避免在复杂情况下无限搜索
        max_search_steps = min(board * board // 2, 1000)
        search_steps = 0
        
        # 开放列表和关闭列表 - 使用集合加速检查
        open_set = []
        open_positions = set()  # 额外集合用于快速检查
        heapq.heappush(open_set, (0, start))
        open_positions.add(start)
        
        came_from = {}
        g_score = {start: 0}  # 从起点到当前点的实际代价
        f_score = {start: manhattan_dist(start, goal)}  # 使用优化的距离函数
        
        # 优化：预计算方向列表
        dir_list = list(dirs.items())
        
        while open_set and search_steps < max_search_steps:
            search_steps += 1
            _, current = heapq.heappop(open_set)
            open_positions.remove(current)
            
            if current == goal:
                # 重建路径
                path = []
                while current in came_from:
                    prev_pos, dir_taken = came_from[current]
                    path.append(dir_taken)
                    current = prev_pos
                path.reverse()
                return path, g_score[goal]
            
            # 优化：游戏后期减少搜索分支
            dirs_to_check = dir_list
            if game_progress > 0.6:
                # 只检查较少的方向，优先选择朝向食物的方向
                hx, hy = current
                fx, fy = goal
                preferred_dirs = []
                if hx > fx: preferred_dirs.append((0, (-1, 0)))
                if hx < fx: preferred_dirs.append((3, (1, 0)))
                if hy > fy: preferred_dirs.append((1, (0, -1)))
                if hy < fy: preferred_dirs.append((2, (0, 1)))
                
                # 最多检查3个方向
                dirs_to_check = preferred_dirs[:3] if preferred_dirs else dir_list[:3]
            
            for d, (dr, dc) in dirs_to_check:
                r, c = current
                neighbor = (r + dr, c + dc)
                
                if 0 <= neighbor[0] < board and 0 <= neighbor[1] < board and neighbor not in body:
                    tentative_g_score = g_score[current] + 1
                    
                    # 优化：动态启发式因子，基于游戏进度
                    heuristic_factor = 1.0 - min(0.5, game_progress * 0.5)
                    
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = (current, d)
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic_factor * manhattan_dist(neighbor, goal)
                        
                        # 优化：使用集合快速检查
                        if neighbor not in open_positions:
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))
                            open_positions.add(neighbor)
        
        return None, float('inf')
    
    # ----------------------------------------------------------------------
    # 🏃 智能空间评估：考虑蛇身体增长后的安全空间
    # ----------------------------------------------------------------------
    def advanced_flood_fill(start):
        """
        优化版洪水填充算法，评估移动方向的安全性，支持障碍物检测
        增加：搜索深度限制、提前剪枝、更高效的评分计算
        """
        # 快速检查起点是否有效
        if start in body or not (0 <= start[0] < board and 0 <= start[1] < board):
            return 1  # 返回最小值
            
        q = deque([start])
        seen = {start}
        
        # 记录每个位置到起点的距离
        distance_map = {start: 0}
        
        # 优化：限制搜索深度，避免在大棋盘上过度计算
        max_search_nodes = min(board * board // 2, 500)
        nodes_count = 0
        
        # 优化：预计算方向列表
        dir_values = list(dirs.values())
        
        # 计算空间的连通性指标
        while q and nodes_count < max_search_nodes:
            nodes_count += 1
            r, c = q.popleft()
            
            # 优化：游戏后期优先探索远离边界的方向
            if game_progress > 0.5:
                # 按距离边界远近排序方向
                dir_with_priority = []
                for dr, dc in dir_values:
                    nr, nc = r + dr, c + dc
                    new_pos = (nr, nc)
                    if (0 <= nr < board and 0 <= nc < board and 
                        new_pos not in body and new_pos not in seen):
                        # 计算到边界的距离作为优先级
                        border_dist = min(nr, board - 1 - nr, nc, board - 1 - nc)
                        dir_with_priority.append((-border_dist, dr, dc))  # 负号使距离大的排在前面
                
                # 按优先级排序
                dir_with_priority.sort()
                directions_to_check = [(dr, dc) for _, dr, dc in dir_with_priority]
            else:
                directions_to_check = dir_values
            
            for dr, dc in directions_to_check:
                nr, nc = r + dr, c + dc
                new_pos = (nr, nc)
                if (0 <= nr < board and 0 <= nc < board and 
                    new_pos not in body and new_pos not in seen):
                    seen.add(new_pos)
                    distance_map[new_pos] = distance_map[(r, c)] + 1
                    q.append(new_pos)
        
        # 优化：提前计算分数所需的关键指标
        seen_size = len(seen)
        if seen_size == 0:
            return 1
        
        # 计算平均距离（优化：避免重复计算）
        avg_distance = sum(distance_map.values()) / seen_size
        
        # 优化边界检测：只计算必要的边界位置
        boundary_count = 0
        border_threshold = 1
        
        # 游戏后期调整边界阈值
        if game_progress > 0.7:
            border_threshold = 2
        
        # 快速边界检测
        for pos in seen:
            if (pos[0] <= border_threshold or pos[0] >= board - border_threshold - 1 or 
                pos[1] <= border_threshold or pos[1] >= board - border_threshold - 1):
                boundary_count += 1
        
        boundary_ratio = boundary_count / seen_size
        
        # 优化评分计算
        if game_progress > 0.6:
            # 游戏后期更看重空间大小和安全性
            safety_factor = 1.0 - boundary_ratio
            return max(1, int(seen_size * 2 * safety_factor))
        else:
            # 综合评分：空间大小 * 平均距离 * (1 - 边界接近度)
            score = seen_size * avg_distance * (1 - boundary_ratio)
            return max(1, score)
    
    # ----------------------------------------------------------------------
    # 🔄 循环检测：避免蛇在小区域内原地绕圈
    # ----------------------------------------------------------------------
    def detect_cycle(pos):
        """优化版循环检测算法，更高效地识别绕圈行为"""
        # 如果蛇很短，不可能形成循环
        if snake_length < 8:  # 降低阈值以便更早检测
            return False
        
        # 获取位置历史记录
        recent_positions = getattr(game, 'recent_positions', None)
        if not recent_positions or len(recent_positions) < 12:  # 降低历史长度要求
            return False
        
        # 优化1：使用集合快速统计唯一位置数量
        recent_10_pos = list(recent_positions)[-10:]
        unique_pos_count = len(set(recent_10_pos))
        
        # 如果唯一位置太少，可能在绕圈
        if unique_pos_count <= 4:  # 更宽松的阈值，提高检测敏感度
            return True
        
        # 优化2：计算最近位置的平均距离（优化计算方式）
        if len(recent_positions) > 15:
            # 只计算最近的8个位置与当前位置的距离
            recent_8_pos = list(recent_positions)[-8:]
            total_dist = 0
            for old_pos in recent_8_pos:
                total_dist += manhattan_dist(pos, old_pos)
            avg_dist = total_dist / 8
            
            # 游戏后期更严格地检测
            threshold = 3.0
            if game_progress > 0.6:
                threshold = 2.5
            
            if avg_dist < threshold:
                return True
        
        # 优化3：检测方向变化模式
        if len(recent_positions) >= 15:
            # 检查是否在进行频繁的U形转弯
            direction_changes = 0
            positions = list(recent_positions)[-15:]
            
            for i in range(2, len(positions)):
                # 计算连续两步的方向
                prev_dir = (positions[i-1][0] - positions[i-2][0], 
                           positions[i-1][1] - positions[i-2][1])
                curr_dir = (positions[i][0] - positions[i-1][0], 
                           positions[i][1] - positions[i-1][1])
                
                # 检查是否反向
                if (prev_dir[0] == -curr_dir[0] and prev_dir[1] == -curr_dir[1]):
                    direction_changes += 1
                    # 如果短时间内多次反向，立即判定为循环
                    if direction_changes >= 2:
                        return True
        
        return False
    
    # 初始化或更新蛇的位置历史记录
    if not hasattr(game, 'recent_positions'):
        game.recent_positions = deque(maxlen=30)  # 减少历史记录长度，节省内存
    game.recent_positions.append(head)
    
    # ----------------------------------------------------------------------
    # 🔍 评估所有可能的移动方向
    # ----------------------------------------------------------------------
    def evaluate_directions():
        direction_scores = {}
        hx, hy = head
        
        for d, (dr, dc) in dirs.items():
            nr, nc = hx + dr, hy + dc
            new_pos = (nr, nc)
            
            # 跳过反向和无效方向
            if d == opposite_dir or not is_valid(new_pos):
                direction_scores[d] = -1
                continue
            
            # 循环惩罚
            if detect_cycle(new_pos):
                cycle_penalty = 0.3  # 降低可能导致循环的方向的评分
            else:
                cycle_penalty = 1.0
            
            # 计算方向评分
            score = 0
            
            # 基础策略评分
            
            # 1. 空间安全评分
            space_score = advanced_flood_fill(new_pos)
            score += space_score * 0.4  # 空间安全权重
            
            # 2. 食物接近度评分
            dist_to_food = manhattan_dist(new_pos, food)
            # 距离越近分数越高，但使用非线性关系
            food_score = 100 / (dist_to_food + 1)
            score += food_score * 0.3  # 食物接近度权重
            
            # 3. 边界远离度评分（越远离边界越安全）
            border_dist = min(nr, board - 1 - nr, nc, board - 1 - nc)
            border_score = border_dist * 10
            score += border_score * 0.2  # 边界远离度权重
            
            # 4. 移动多样性评分（避免一直朝一个方向移动）
            if hasattr(game, 'previous_directions') and len(game.previous_directions) > 3:
                if d == game.previous_directions[-1] == game.previous_directions[-2]:
                    direction_penalty = 0.7  # 连续多次同一方向会被惩罚
                else:
                    direction_penalty = 1.0
            else:
                direction_penalty = 1.0
            
            # 对抗模式特有策略（当is_opponent=True时）
            if is_opponent and player_head:
                
                # 5. 玩家攻击策略：尝试攻击玩家蛇头
                player_attack_bonus = 0
                dist_to_player = manhattan_dist(new_pos, player_head)
                
                # 如果距离玩家蛇头很近，给予攻击奖励
                if dist_to_player <= 2:
                    # 计算是否可以在下一步或两步内攻击到玩家
                    if dist_to_player == 1:
                        player_attack_bonus = 300  # 直接攻击奖励
                    elif dist_to_player == 2:
                        player_attack_bonus = 150  # 接近攻击奖励
                
                # 6. 包围策略：尝试切断玩家蛇的路径
                encircle_bonus = 0
                # 计算玩家蛇的可能移动方向
                if len(player_snake) > 1:
                    player_body_set = player_body
                    # 如果新位置可以切断玩家到食物的路径，给予奖励
                    player_to_food_path, _ = a_star_path(player_head, food)
                    if player_to_food_path and new_pos in [
                        (player_head[0] + dr, player_head[1] + dc) 
                        for dr, dc in dirs.values()
                    ]:
                        encircle_bonus = 100
                
                # 7. 防御策略：避免被玩家包围
                defense_bonus = 0
                # 计算玩家蛇头与对抗蛇头的位置关系
                if len(player_snake) > 5 and dist_to_player < 5:
                    # 检查是否处于被包围的风险
                    if space_score < 20:
                        defense_bonus = 50  # 在被包围风险下优先逃跑
                
                # 8. 食物竞争策略：当食物靠近时优先获取
                food_competition_bonus = 0
                if dist_to_food < manhattan_dist(player_head, food):
                    food_competition_bonus = 80  # 比玩家更接近食物时的奖励
                
                # 9. 避免撞玩家蛇：给予玩家蛇身体更大的避让权重
                avoid_player_penalty = 1.0
                if new_pos in player_body:
                    direction_scores[d] = -1
                    continue
                # 检查下一步是否靠近玩家蛇身体
                for p_pos in player_body:
                    if manhattan_dist(new_pos, p_pos) == 1:
                        avoid_player_penalty = 0.5
                        break
                
                # 根据游戏状态调整权重
                current_weight = 0.1  # 默认权重较低
                
                # 根据分数差距调整攻击性
                player_score = len(player_snake) - 3 if player_snake else 0
                score_diff = score - player_score
                
                if score_diff > 5:  # 对抗蛇领先时，更注重防御
                    current_weight = 0.1
                elif score_diff < -5:  # 对抗蛇落后时，更注重攻击
                    current_weight = 0.3
                else:  # 势均力敌时，平衡策略
                    current_weight = 0.2
                
                # 应用对抗模式策略评分
                score += (player_attack_bonus + encircle_bonus + 
                         defense_bonus + food_competition_bonus) * current_weight
                cycle_penalty *= avoid_player_penalty
            
            # 综合所有评分
            final_score = score * cycle_penalty * direction_penalty
            direction_scores[d] = final_score
        
        return direction_scores
    
    # ----------------------------------------------------------------------
    # � 主决策逻辑
    # ----------------------------------------------------------------------
    # 1. 首先尝试A*找食物路径
    path_to_food, path_length = a_star_path(head, food)
    
    # 如果有到食物的安全路径，且不会导致立即危险
    if path_to_food and path_to_food[0] != opposite_dir:
        # 检查路径第一步是否安全（空间足够）
        hx, hy = head
        dr, dc = dirs[path_to_food[0]]
        next_pos = (hx + dr, hy + dc)
        
        # 计算吃完食物后的预期空间
        # 模拟吃完食物后的身体状态（假设身体变长）
        if hasattr(game, 'simulate_growth'):
            future_space = game.simulate_growth(next_pos)
        else:
            # 简化版：当前空间评估
            future_space = advanced_flood_fill(next_pos)
        
        # 如果吃完食物后仍有足够空间，就去吃
        min_safe_space = max(10, snake_length // 2)  # 最小安全空间
        if future_space > min_safe_space:
            # 记录方向历史
            if not hasattr(game, 'previous_directions'):
                game.previous_directions = deque(maxlen=10)
            game.previous_directions.append(path_to_food[0])
            return path_to_food[0]
    
    # 2. 如果没有直接路径或路径不安全，评估所有方向
    direction_scores = evaluate_directions()
    
    # 找到评分最高的方向
    valid_directions = [(score, d) for d, score in direction_scores.items() if score > 0]
    
    if valid_directions:
        # 按评分排序
        valid_directions.sort(reverse=True, key=lambda x: x[0])
        
        # 选择最高分方向，但添加一些随机性以避免陷入局部最优
        best_score = valid_directions[0][0]
        # 找出所有接近最高分的方向（允许5%的误差）
        candidates = [d for score, d in valid_directions if score >= best_score * 0.95]
        
        # 从候选方向中随机选择（增加探索性）
        chosen_dir = random.choice(candidates)
        
        # 记录方向历史
        if not hasattr(game, 'previous_directions'):
            game.previous_directions = deque(maxlen=10)
        game.previous_directions.append(chosen_dir)
        
        return chosen_dir
    
    # 3. 实在无路：随机选一条不反向的安全路
    safe_moves = []
    for d, (dr, dc) in dirs.items():
        nr, nc = hx + dr, hy + dc
        if is_valid((nr, nc)) and d != opposite_dir:
            safe_moves.append(d)
    
    if safe_moves:
        return random.choice(safe_moves)
    
    # 4. 没路就随机（必死）
    return random.choice([0, 1, 2, 3])

# ---------------------------
# 普通模式主函数
# ---------------------------
def main_normal():
    """普通模式主函数：玩家可自行控制或AI接管"""
    seed = random.randint(0, int(1e9))
    # 使用全局游戏配置初始化游戏
    game = SnakeGame(
        seed=seed, 
        board_size=game_config["board_size"], 
        silent_mode=False
    )
    # 应用其他配置项
    game.cell_size = game_config["cell_size"]
    game.snake_speed = game_config["snake_speed"]
    game.enable_sound = game_config["enable_sound"]
    game.food_value = game_config["food_value"]
    game.enable_border = game_config["enable_border"]

    # 初始化
    clock = pygame.time.Clock()
    update_interval = 0.15  # 略微提高游戏更新频率，提升流畅度
    last_update = time.time()
    
    # 预加载按钮文本
    start_button_text = "开始游戏"
    retry_button_text = "再来一次"

    action = -1
    game_state = "welcome"  # 初始游戏状态：欢迎界面
    ai_connected = False    # AI 开关（由右侧按钮控制）
    ai_control = False      # 当前是否由 AI 控制
    countdown_snd = game.sound_count

    # 画面上用于鼠标点击检测的隐藏文本
    start_button_surf = game.font.render("START", True, (0, 0, 0))
    retry_button_surf = game.font.render("RETRY", True, (0, 0, 0))


    def draw_welcome():
        # 绘制深蓝色渐变背景
        for y in range(game.display_height):
            r = int(0)
            g = int(10)
            b = int(30 - 20 * y / game.display_height)
            pygame.draw.line(game.screen, (r, g, b), (0, y), (game.display_width, y))
            
        center_x = game.display_width // 2
        margin_top = 60  # 顶部边距
        spacing = 30     # 行间距
        btn_margin_top = 50  # 按钮与文字间距

        # 标题 - 使用大字体和绿色
        title = game.large_font.render("贪吃蛇游戏 - 普通模式", True, (0, 255, 0))
        title_rect = title.get_rect(center=(center_x, margin_top + title.get_height() // 2))
        
        # 标题阴影效果
        shadow_offset = 2
        shadow_surf = pygame.Surface(title.get_size())
        shadow_surf.fill((0, 0, 0, 0))
        shadow_surf.blit(game.large_font.render("贪吃蛇游戏 - 普通模式", True, (0, 100, 0)), (0, 0))
        game.screen.blit(shadow_surf, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
        game.screen.blit(title, title_rect)

        # 游戏介绍文本
        intro_texts = [
            "游戏目标: 控制蛇吃到尽可能多的食物，获得高分！",
            "操作说明: 使用方向键（↑↓←→）控制蛇的移动方向",
            "AI功能: 右侧面板可接通/断开AI，AI接通后会自动控制蛇的移动",
            "游戏规则: 撞到墙壁或自己的身体会导致游戏结束",
            "提示: 蛇吃到食物后会变长，移动速度会逐渐增加"
        ]
        
        # 计算位置一次并复用
        text_y = title_rect.bottom + spacing
        
        # 绘制所有介绍文本，使用不同颜色增强可读性
        for i, text_content in enumerate(intro_texts):
            if i == 0:  # 标题行使用高亮颜色
                text_color = (255, 255, 0)
            else:  # 其他行使用白色/浅灰色
                text_color = (200, 200, 200)
            
            info_text = game.font.render(text_content, True, text_color)
            game.screen.blit(info_text, (center_x - info_text.get_width() // 2, text_y))
            text_y += info_text.get_height() + 5

        # START 按钮 - 增强视觉效果
        btn_width, btn_height = 180, 50
        btn_rect = pygame.Rect(0, 0, btn_width, btn_height)
        btn_rect.centerx = center_x
        btn_rect.top = text_y + btn_margin_top
        
        # 按钮悬停效果检测
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = btn_rect.collidepoint(mouse_pos)
        
        # 绘制按钮背景 - 根据悬停状态改变颜色
        btn_color = (120, 200, 120) if is_hovered else (100, 180, 100)
        pygame.draw.rect(game.screen, btn_color, btn_rect, border_radius=8)
        pygame.draw.rect(game.screen, (50, 150, 50), btn_rect, 3, border_radius=8)
        
        # 如果悬停，添加轻微的阴影效果
        if is_hovered:
            shadow_offset = 2
            shadow_rect = btn_rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            # 使用半透明黑色
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=8)
            game.screen.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
        
        # 按钮文字
        text_s = game.font.render(start_button_text, True, (0, 0, 0))
        text_rect = text_s.get_rect(center=btn_rect.center)
        game.screen.blit(text_s, text_rect)
        
        # 提示文本
        tip_text = game.font.render("按任意键或点击按钮开始游戏", True, (150, 150, 150))
        tip_rect = tip_text.get_rect(center=(center_x, btn_rect.bottom + 25))
        game.screen.blit(tip_text, tip_rect)

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

        # 身体颜色渐变（绿→深绿）- 优化：不使用numpy，使用简单的线性计算
        body_count = max(len(display_snake) - 1, 1)
        for i, (r, c) in enumerate(display_snake[1:], start=0):
            # 简单的线性渐变计算，避免numpy依赖
            green_value = 255 - int((255 - 80) * (i / body_count))
            body_x = s_area_x + c * cell
            body_y = s_area_y + r * cell
            pygame.draw.rect(game.screen, (0, green_value, 0),
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
                            # 倒计时 1 秒 - 优化：减少重复计算
                            center_x, center_y = game.display_width // 2, game.display_height // 2
                            for i in range(1, 0, -1):
                                game.screen.fill((0, 0, 0))
                                cnt_surf = game.large_font.render(str(i), True, (255, 255, 255))
                                cnt_rect = cnt_surf.get_rect(center=(center_x, center_y))
                                game.screen.blit(cnt_surf, cnt_rect)
                                pygame.display.flip()
                                if countdown_snd:
                                    try:
                                        countdown_snd.play()
                                    except:
                                        pass  # 静默失败
                                pygame.time.wait(700)
                            action = -1
                            game_state = "running"
                            last_update = time.time()

                # 游戏结束界面按钮点击
                elif game_state == "game_over":
                    # 停止背景音乐
                    game.stop_bgm()
                    if hasattr(game, "retry_button_rect") and game.retry_button_rect.collidepoint(event.pos):
                        # 倒计时 1 秒 - 优化：使用rect的center方法
                        center_x, center_y = game.display_width // 2, game.display_height // 2
                        for i in range(1, 0, -1):
                            game.screen.fill((0, 0, 0))
                            cnt_surf = game.large_font.render(str(i), True, (255, 255, 255))
                            cnt_rect = cnt_surf.get_rect(center=(center_x, center_y))
                            game.screen.blit(cnt_surf, cnt_rect)
                            pygame.display.flip()
                            if countdown_snd:
                                try:
                                    countdown_snd.play()
                                except:
                                    pass  # 静默失败
                            pygame.time.wait(700)
                        game.reset()
                        action = -1
                        game_state = "running"
                        last_update = time.time()
                        # 开始播放背景音乐
                        game.play_bgm()
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
            pygame.display.flip()  # 确保欢迎界面正确显示
            clock.tick(20)
            continue
        if game_state == "game_over":
            draw_game_over()
            pygame.display.flip()  # 确保游戏结束界面正确显示
            clock.tick(20)
            continue
        
        # 如果是running状态，确保始终有渲染（即使不在更新间隔）
        if game_state == "running":
            game.render(ai_connected, draw_opponent=False, show_ai=True)
            pygame.display.flip()  # 确保所有渲染内容显示到屏幕

        # 游戏步骤更新
        now = time.time()
        if now - last_update >= update_interval:
            last_update = now  # 更新时间
            
            if game_state == "running":
                # 玩家控制绿色蛇
                # 即使没有新的键盘输入，蛇也会保持当前方向移动
                if ai_connected and ai_control:
                    # 只在AI控制时调用get_ai_action
                    chosen_action = get_ai_action(game, is_opponent=False)
                else:
                    # 对于玩家控制，action为-1时保持当前方向
                    chosen_action = action
                
                # 执行游戏步骤
                done, info = game.step(chosen_action)
                
                # 只有当游戏未结束时才渲染
                if not done:
                    game.render(ai_connected, draw_opponent=False, show_ai=True)
                
                # 重置玩家动作，这样蛇会继续按照当前方向移动
                # 只有当玩家按下方向键时，action才会改变
                action = -1

            # 检查游戏结束状态
            if done:
                game_state = "game_over"
                # 保存游戏结束时间，用于固定显示时长
                game.game_end_time = time.time()
                # 保存游戏结束时间，用于固定显示时长
                game.game_end_time = time.time()
                # 保存游戏结束时间，用于固定显示时长
                game.game_end_time = time.time()
                # 保存游戏结束时间，用于固定显示时长
                game.game_end_time = time.time()
                # 保存游戏结束时间，用于固定显示时长
                game.game_end_time = time.time()
                # 保存游戏结束时间，用于固定显示时长
                game.game_end_time = time.time()

        clock.tick(60)

    pygame.quit()
    sys.exit()

# ---------------------------
# 影子模式主函数
# ---------------------------
def main_three_snake():
    """影子模式主函数：玩家控制绿色蛇，AI1和AI2作为影子完全模仿玩家移动"""
    seed = random.randint(0, int(1e9))
    # 使用全局游戏配置初始化游戏
    game = SnakeGame(
        seed=seed, 
        board_size=game_config["board_size"], 
        silent_mode=False
    )
    # 应用其他配置项
    game.cell_size = game_config["cell_size"]
    game.snake_speed = game_config["snake_speed"]
    game.enable_sound = game_config["enable_sound"]
    game.food_value = game_config["food_value"]
    game.enable_border = game_config["enable_border"]

    # 初始化影子模式游戏状态
    game.reset_three_snake_mode()

    # 初始化
    clock = pygame.time.Clock()
    update_interval = 0.2  # 游戏更新间隔（秒）
    last_update = time.time()

    action = -1
    game_state = "welcome"  # 初始游戏状态：欢迎界面
    countdown_snd = game.sound_count
    
    # 绘制欢迎界面的函数
    def draw_welcome():
        # 绘制深蓝色渐变背景
        for y in range(game.display_height):
            r = int(0)
            g = int(10)
            b = int(30 - 20 * y / game.display_height)
            pygame.draw.line(game.screen, (r, g, b), (0, y), (game.display_width, y))
            
        center_x = game.display_width // 2
        margin_top = 60  # 顶部边距
        spacing = 30     # 行间距
        btn_margin_top = 50  # 按钮与文字间距

        # 标题 - 使用大字体和紫色（影子模式主题色）
        title = game.large_font.render("贪吃蛇游戏 - 影子模式", True, (220, 70, 220))
        title_rect = title.get_rect(center=(center_x, margin_top + title.get_height() // 2))
        
        # 标题阴影效果
        shadow_offset = 2
        shadow_surf = pygame.Surface(title.get_size())
        shadow_surf.fill((0, 0, 0, 0))
        shadow_surf.blit(game.large_font.render("贪吃蛇游戏 - 影子模式", True, (180, 50, 180)), (0, 0))
        game.screen.blit(shadow_surf, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
        game.screen.blit(title, title_rect)

        # 游戏介绍文本
        intro_texts = [
            "游戏目标: 控制绿色蛇，AI蛇作为影子完全模仿你的移动！",
            "操作说明: 使用方向键（↑↓←→）或WASD控制蛇的移动方向",
            "注意: AI蛇死亡玩家也会死亡，所有蛇同步增长蛇身！"
        ]
        
        # 绘制介绍文本
        for i, text in enumerate(intro_texts):
            text_surf = game.font.render(text, True, (200, 200, 200))
            text_rect = text_surf.get_rect(center=(center_x, title_rect.bottom + spacing + i * (text_surf.get_height() + 10)))
            game.screen.blit(text_surf, text_rect)
        
        # START 按钮
        btn_width, btn_height = 200, 60
        btn_rect = pygame.Rect(0, 0, btn_width, btn_height)
        btn_rect.centerx = game.display_width // 2
        btn_rect.top = title_rect.bottom + spacing + len(intro_texts) * (game.font.render("", True, (0,0,0)).get_height() + 10) + btn_margin_top
        
        # 绘制按钮
        pygame.draw.rect(game.screen, (220, 70, 220), btn_rect, border_radius=10)
        pygame.draw.rect(game.screen, (180, 50, 180), btn_rect, 3, border_radius=10)
        
        # 按钮文字
        btn_text = game.font.render("开始游戏", True, (255, 255, 255))
        btn_text_rect = btn_text.get_rect(center=btn_rect.center)
        game.screen.blit(btn_text, btn_text_rect)
        
        # 保存按钮位置用于点击检测
        game.start_button_rect = btn_rect
    
    # 主游戏循环 - 统一处理所有游戏状态
    while True:
        current_time = time.time()
        
        # 事件处理 - 对所有状态通用
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 欢迎界面事件处理
            if game_state == "welcome":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        game_state = "running"
                        if countdown_snd:
                            try:
                                countdown_snd.play()
                            except Exception:
                                pass
                        last_update = time.time()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 检测开始按钮点击
                    if hasattr(game, 'start_button_rect') and game.start_button_rect.collidepoint(event.pos):
                        game_state = "running"
                        if countdown_snd:
                            try:
                                countdown_snd.play()
                            except Exception:
                                pass
                        last_update = time.time()
            
            # 游戏运行状态事件处理
            elif game_state == "running":
                if event.type == pygame.KEYDOWN:
                    # 方向控制
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        action = 0  # UP
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        action = 1  # LEFT
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        action = 2  # RIGHT
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        action = 3  # DOWN
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        main_gui()
                        return
            
            # 游戏结束界面事件处理
            elif game_state == "game_over":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r or event.key == pygame.K_KP_ENTER:
                        # 重新开始
                        game.reset_three_snake_mode()
                        game_state = "running"
                        action = -1  # 重置动作
                        last_update = time.time()
                    elif event.key == pygame.K_m:
                        # 返回菜单
                        pygame.quit()
                        main_gui()
                        return
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 检测重试按钮点击 - 使用与draw_game_over_screen方法中完全相同的位置计算
                    button_width = 200
                    button_height = 60
                    button_y = game.display_height // 2
                    btn_spacing = 10  # 与draw_game_over_screen方法中使用的值一致
                    
                    retry_button_rect = pygame.Rect(
                        (game.display_width - button_width) // 2,
                        button_y,
                        button_width,
                        button_height
                    )
                    # 检测菜单按钮点击
                    menu_button_rect = pygame.Rect(
                        (game.display_width - button_width) // 2,
                        button_y + button_height + btn_spacing,
                        button_width,
                        button_height
                    )
                    # 检测退出按钮点击
                    exit_button_rect = pygame.Rect(
                        (game.display_width - button_width) // 2,
                        button_y + 2 * (button_height + btn_spacing),
                        button_width,
                        button_height
                    )
                    if retry_button_rect.collidepoint(event.pos):
                        game.reset_three_snake_mode()
                        game_state = "running"
                        action = -1  # 重置动作
                        last_update = time.time()
                    elif menu_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        main_gui()
                        return
                    elif exit_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
        
        # 根据当前游戏状态执行相应逻辑
        if game_state == "welcome":
            # 绘制欢迎界面
            draw_welcome()
            pygame.display.flip()
        
        elif game_state == "running":
            # 游戏逻辑更新
            if current_time - last_update >= update_interval:
                done, info = game.step_three_snake_mode(action)
                action = -1  # 重置动作
                last_update = current_time
                
                if done:
                    game_state = "game_over"
            
            # 绘制游戏界面
            game.draw_board()
            pygame.display.flip()
        
        elif game_state == "game_over":
            # 绘制游戏结束界面
            game.draw_game_over_screen()
            pygame.display.flip()
        
        # 控制帧率
        clock.tick(60)

# ---------------------------
# 对抗模式主函数
# ---------------------------
def main_opponent():
    """对抗模式主函数：玩家控制绿色蛇，AI控制红色蛇"""
    seed = random.randint(0, int(1e9))
    # 使用全局游戏配置初始化游戏
    game = SnakeGame(
        seed=seed, 
        board_size=game_config["board_size"], 
        silent_mode=False
    )
    # 应用其他配置项
    game.cell_size = game_config["cell_size"]
    game.snake_speed = game_config["snake_speed"]
    game.enable_sound = game_config["enable_sound"]
    game.food_value = game_config["food_value"]
    game.enable_border = game_config["enable_border"]

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
        # 绘制深蓝色渐变背景
        for y in range(game.display_height):
            r = int(0)
            g = int(10)
            b = int(30 - 20 * y / game.display_height)
            pygame.draw.line(game.screen, (r, g, b), (0, y), (game.display_width, y))
            
        margin_top = 60
        spacing = 35
        btn_margin_top = 25

        # 标题 - 根据分数显示不同内容和颜色
        if game.score >= 1000:
            title_text = "恭喜胜利！"
            title_color = (255, 255, 100)  # 金黄色标题
            shadow_color = (180, 180, 0)   # 深黄色阴影
        else:
            title_text = "游戏结束"
            title_color = (255, 255, 255)  # 白色标题
            shadow_color = (150, 150, 150) # 灰色阴影
            
        # 标题阴影效果
        title_shadow = game.large_font.render(title_text, True, shadow_color)
        title = game.large_font.render(title_text, True, title_color)
        title_rect = title.get_rect(center=(game.display_width // 2, margin_top))
        
        # 绘制阴影和标题
        shadow_offset = 2
        game.screen.blit(title_shadow, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
        game.screen.blit(title, title_rect)

        # 分数显示 - 使用更醒目的颜色和更大的字体
        score_text = game.font.render(f"最终分数: {game.score}", True, (255, 255, 150))
        score_rect = score_text.get_rect(center=(game.display_width // 2, title_rect.bottom + spacing))
        
        # 分数阴影效果
        score_shadow = game.font.render(f"最终分数: {game.score}", True, (150, 150, 50))
        game.screen.blit(score_shadow, (score_rect.x + 1, score_rect.y + 1))
        game.screen.blit(score_text, score_rect)

        # 蛇身长度 - 使用绿色系
        length = len(game.snake)
        length_text = game.font.render(f"蛇身长度: {length} 格", True, (150, 255, 150))
        length_rect = length_text.get_rect(center=(game.display_width // 2, score_rect.bottom + spacing // 2))
        game.screen.blit(length_text, length_rect)
        
        # 计算游戏时长统计
        stats_text = ""
        stats_rect = None
        if hasattr(game, 'game_start_time'):
            # 使用固定的结束时间计算时长，避免游戏结束后时长继续增加
            if hasattr(game, 'game_end_time'):
                game_duration = game.game_end_time - game.game_start_time
            else:
                game_duration = time.time() - game.game_start_time
            minutes = int(game_duration // 60)
            seconds = int(game_duration % 60)
            stats_text = f"游戏时长: {minutes}分{seconds}秒"
            stats_surf = game.font.render(stats_text, True, (200, 200, 255))
            stats_rect = stats_surf.get_rect(center=(game.display_width // 2, length_rect.bottom + spacing // 2))
            game.screen.blit(stats_surf, stats_rect)

        # 死亡原因 - 使用红色系突出显示
        reason_rect = None
        if hasattr(game, 'death_reason') and game.death_reason:
            reason_text = game.font.render(f"死亡原因: {game.death_reason}", True, (255, 150, 150))
            # 根据前面是否有统计信息调整位置
            if stats_rect:
                reason_rect = reason_text.get_rect(center=(game.display_width // 2, stats_rect.bottom + spacing // 2))
            else:
                reason_rect = reason_text.get_rect(center=(game.display_width // 2, length_rect.bottom + spacing // 2))
            game.screen.blit(reason_text, reason_rect)

        # 绘制蛇形展示区域 - 添加边框和背景美化
        s_area_width, s_area_height = 400, 300
        s_area_x = (game.display_width - s_area_width) // 2
        
        # 根据前面元素的位置确定起始Y坐标
        if reason_rect:
            s_area_y = reason_rect.bottom + 40
        elif stats_rect:
            s_area_y = stats_rect.bottom + 40
        else:
            s_area_y = length_rect.bottom + 40
            
        # 绘制带边框的展示区域
        pygame.draw.rect(game.screen, (60, 60, 60), (s_area_x, s_area_y, s_area_width, s_area_height), border_radius=12)
        pygame.draw.rect(game.screen, (40, 40, 40), (s_area_x + 1, s_area_y + 1, s_area_width - 2, s_area_height - 2), border_radius=11)
        pygame.draw.rect(game.screen, (70, 70, 70), (s_area_x, s_area_y, s_area_width, s_area_height), 1, border_radius=12)

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

        for i in range(length):
            col = (i % (cols - 2)) + 1 if direction == 1 else (cols - 2 - (i % (cols - 2)))
            display_snake.append((row + 1, col))
            if (i + 1) % (cols - 2) == 0:
                row += 2
                direction *= -1
                if row + 1 >= rows:
                    break  # 超出展示区则停止

        # 绘制蛇头（使用更醒目的蓝色）
        if display_snake:
            head_r, head_c = display_snake[0]
            head_x = s_area_x + head_c * cell
            head_y = s_area_y + head_r * cell
            pygame.draw.polygon(game.screen, (120, 120, 255), [
                (head_x + cell // 2, head_y),
                (head_x + cell, head_y + cell // 2),
                (head_x + cell // 2, head_y + cell),
                (head_x, head_y + cell // 2)
            ])
            # 眼睛 - 使用更亮的颜色
            eye_size = 2
            pygame.draw.circle(game.screen, (255, 255, 255), (head_x + 3, head_y + 3), eye_size)
            pygame.draw.circle(game.screen, (255, 255, 255), (head_x + cell - 3, head_y + 3), eye_size)

        # 身体颜色渐变（更平滑的绿色到深绿色）
        color_list = np.linspace(255, 50, max(len(display_snake) - 1, 1), dtype=np.uint8)
        for i, (r, c) in enumerate(display_snake[1:], start=0):
            body_x = s_area_x + c * cell
            body_y = s_area_y + r * cell
            # 使用更平滑的圆角矩形
            pygame.draw.rect(game.screen, (0, int(color_list[i]), 0),
                            (body_x, body_y, cell, cell), border_radius=4)

        # 按钮设置
        btn_width, btn_height = 200, 50
        btn_spacing = 15
        mouse_pos = pygame.mouse.get_pos()
        
        # 再来一次按钮 - 放置在蛇形展示区域下方，添加悬停效果
        retry_btn = pygame.Rect(0, 0, btn_width, btn_height)
        retry_btn.centerx = game.display_width // 2
        retry_btn.top = s_area_y + s_area_height + btn_margin_top
        
        # 检查按钮悬停状态
        is_retry_hovered = retry_btn.collidepoint(mouse_pos)
        retry_color = (150, 150, 150) if is_retry_hovered else (120, 120, 120)
        retry_border_color = (180, 180, 180) if is_retry_hovered else (150, 150, 150)
        
        # 美化按钮
        pygame.draw.rect(game.screen, retry_color, retry_btn, border_radius=10)
        pygame.draw.rect(game.screen, retry_border_color, retry_btn, 2, border_radius=10)
        
        # 悬停时添加轻微阴影效果
        if is_retry_hovered:
            shadow_offset = 2
            shadow_rect = retry_btn.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            # 使用半透明黑色
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=10)
            game.screen.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))

        retry_text = game.font.render("再来一次", True, (255, 255, 255))
        retry_text_rect = retry_text.get_rect(center=retry_btn.center)
        game.screen.blit(retry_text, retry_text_rect)

        # 返回菜单按钮 - 添加悬停效果
        menu_btn = pygame.Rect(0, 0, btn_width, btn_height)
        menu_btn.centerx = game.display_width // 2
        menu_btn.top = retry_btn.bottom + btn_spacing
        
        is_menu_hovered = menu_btn.collidepoint(mouse_pos)
        menu_color = (180, 180, 210) if is_menu_hovered else (150, 150, 180)
        menu_border_color = (200, 200, 230) if is_menu_hovered else (180, 180, 210)
        
        pygame.draw.rect(game.screen, menu_color, menu_btn, border_radius=10)
        pygame.draw.rect(game.screen, menu_border_color, menu_btn, 2, border_radius=10)
        
        if is_menu_hovered:
            shadow_offset = 2
            shadow_rect = menu_btn.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            # 使用半透明黑色
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=10)
            game.screen.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))

        menu_text = game.font.render("返回菜单", True, (255, 255, 255))
        menu_text_rect = menu_text.get_rect(center=menu_btn.center)
        game.screen.blit(menu_text, menu_text_rect)

        # 退出游戏按钮 - 添加悬停效果
        exit_btn = pygame.Rect(0, 0, btn_width, btn_height)
        exit_btn.centerx = game.display_width // 2
        exit_btn.top = menu_btn.bottom + btn_spacing
        
        is_exit_hovered = exit_btn.collidepoint(mouse_pos)
        exit_color = (250, 100, 100) if is_exit_hovered else (220, 70, 70)
        exit_border_color = (230, 80, 80) if is_exit_hovered else (180, 50, 50)
        
        pygame.draw.rect(game.screen, exit_color, exit_btn, border_radius=10)
        pygame.draw.rect(game.screen, exit_border_color, exit_btn, 2, border_radius=10)
        
        if is_exit_hovered:
            shadow_rect = exit_btn.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            pygame.draw.rect(game.screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
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
                        # 倒计时 1 秒
                        for i in range(1, 0, -1):
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
                        # 倒计时 1 秒
                        for i in range(1, 0, -1):
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
                        # 开始播放背景音乐
                        game.play_bgm()
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
                # 修复重复的键位检查
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    action = 0
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    action = 1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    action = 2
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
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
            pygame.display.flip()  # 确保欢迎界面内容显示
            clock.tick(20)
            continue
        if game_state == "game_over":
            draw_game_over()
            pygame.display.flip()  # 确保游戏结束界面内容显示
            clock.tick(20)
            continue

        # 游戏步骤更新
        now = time.time()
        if now - last_update >= update_interval:
            last_update = now  # 更新时间
            
            if game_state == "running":
                # 玩家控制绿色蛇 - 优化：直接使用action变量，减少中间变量
                done, info = game.step_opponent_mode(action)

                # 对抗模式下AI控制红色蛇
                if not game.opponent_dead:
                    opponent_action = get_ai_action(game, is_opponent=True)
                    done_opponent, _ = game.opponent_step(opponent_action)
                    
                    # 如果对抗蛇死亡，重新部署
                    if done_opponent:
                        # 延迟一小段时间再重新部署，让玩家能看到死亡效果
                        pygame.time.wait(500)
                        game.respawn_opponent()

                # 只有当游戏未结束时才渲染
                if not done:
                    game.render(ai_connected=False, draw_opponent=True, show_ai=False)
                
                # 重置玩家动作
                action = -1

                # 检查胜利条件（1000积分）
                if game.score >= 1000:
                    game_state = "game_over"
                    # 保存游戏结束时间，用于固定显示时长
                    game.game_end_time = time.time()

            # 检查游戏是否结束
            if done:
                game_state = "game_over"
                # 保存游戏结束时间，用于固定显示时长
                game.game_end_time = time.time()

        clock.tick(60)

    pygame.quit()
    sys.exit()

# ---------------------------
# 限时模式主函数
# ---------------------------
def main_timed():
    """限时模式主函数：在规定时间内尽可能获得高分"""
    seed = random.randint(0, int(1e9))
    # 使用全局游戏配置初始化游戏
    game = SnakeGame(
        seed=seed, 
        board_size=game_config["board_size"], 
        silent_mode=False
    )
    # 应用其他配置项
    game.cell_size = game_config["cell_size"]
    game.snake_speed = game_config["snake_speed"]
    game.enable_sound = game_config["enable_sound"]
    game.food_value = game_config["food_value"]
    game.enable_border = game_config["enable_border"]

    # 初始化
    clock = pygame.time.Clock()
    update_interval = 0.15  # 略微提高游戏更新频率，提升流畅度
    last_update = time.time()
    
    # 限时模式特有设置
    time_limit = 60  # 60秒时间限制
    start_time = time.time()
    
    # 预加载按钮文本
    start_button_text = "开始游戏"
    retry_button_text = "再来一次"

    action = -1
    game_state = "welcome"  # 初始游戏状态：欢迎界面
    ai_connected = False    # AI 开关（由右侧按钮控制）
    ai_control = False      # 当前是否由 AI 控制
    countdown_snd = game.sound_count

    # 画面上用于鼠标点击检测的隐藏文本
    start_button_surf = game.font.render("START", True, (0, 0, 0))
    retry_button_surf = game.font.render("RETRY", True, (0, 0, 0))

    def draw_welcome():
        # 绘制深蓝色渐变背景
        for y in range(game.display_height):
            r = int(0)
            g = int(10)
            b = int(30 - 20 * y / game.display_height)
            pygame.draw.line(game.screen, (r, g, b), (0, y), (game.display_width, y))
            
        center_x = game.display_width // 2
        margin_top = 60  # 顶部边距
        spacing = 30     # 行间距
        btn_margin_top = 50  # 按钮与文字间距

        # 标题 - 使用大字体和黄色（限时模式主题色）
        title = game.large_font.render("贪吃蛇游戏 - 限时模式", True, (255, 215, 0))
        title_rect = title.get_rect(center=(center_x, margin_top + title.get_height() // 2))
        
        # 标题阴影效果
        shadow_offset = 2
        shadow_surf = pygame.Surface(title.get_size())
        shadow_surf.fill((0, 0, 0, 0))
        shadow_surf.blit(game.large_font.render("贪吃蛇游戏 - 限时模式", True, (200, 180, 0)), (0, 0))
        game.screen.blit(shadow_surf, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
        game.screen.blit(title, title_rect)

        # 游戏介绍文本
        intro_texts = [
            "游戏目标: 在60秒内吃到尽可能多的食物，获得高分！",
            "操作说明: 使用方向键（↑↓←→）或WASD控制蛇的移动方向",
            "AI功能: 右侧面板可接通/断开AI，AI接通后会自动控制蛇的移动",
            "游戏规则: 撞到墙壁或自己的身体会导致游戏结束",
            "提示: 蛇吃到食物后会变长，移动速度会逐渐增加"
        ]
        
        # 计算位置一次并复用
        text_y = title_rect.bottom + spacing
        
        # 绘制所有介绍文本，使用不同颜色增强可读性
        for i, text_content in enumerate(intro_texts):
            if i == 0:  # 标题行使用高亮颜色
                text_color = (255, 255, 0)
            else:  # 其他行使用白色/浅灰色
                text_color = (200, 200, 200)
            
            info_text = game.font.render(text_content, True, text_color)
            game.screen.blit(info_text, (center_x - info_text.get_width() // 2, text_y))
            text_y += info_text.get_height() + 5

        # START 按钮 - 增强视觉效果
        btn_width, btn_height = 180, 50
        btn_rect = pygame.Rect(0, 0, btn_width, btn_height)
        btn_rect.centerx = center_x
        btn_rect.top = text_y + btn_margin_top
        
        # 按钮悬停效果检测
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = btn_rect.collidepoint(mouse_pos)
        
        # 绘制按钮背景 - 根据悬停状态改变颜色
        btn_color = (220, 180, 70) if is_hovered else (200, 160, 50)  # 黄色系按钮
        pygame.draw.rect(game.screen, btn_color, btn_rect, border_radius=8)
        pygame.draw.rect(game.screen, (180, 140, 30), btn_rect, 3, border_radius=8)
        
        # 如果悬停，添加轻微的阴影效果
        if is_hovered:
            shadow_offset = 2
            shadow_rect = btn_rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            # 使用半透明黑色
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=8)
            game.screen.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
        
        # 按钮文字
        text_s = game.font.render(start_button_text, True, (0, 0, 0))
        text_rect = text_s.get_rect(center=btn_rect.center)
        game.screen.blit(text_s, text_rect)
        
        # 保存按钮位置以供后续检测
        game.start_button_rect = btn_rect
        
        # 刷新屏幕显示
        pygame.display.flip()

    def draw_game_over():
        # 绘制渐变背景（红黑渐变）
        for y in range(game.display_height):
            # 从黑色到深红色的渐变
            r = int(50 + 150 * y / game.display_height)
            g = int(0)
            b = int(0)
            pygame.draw.line(game.screen, (r, g, b), (0, y), (game.display_width, y))
        
        center_x = game.display_width // 2
        margin_top = 80
        spacing = 30
        
        # 游戏结束标题
        title = game.large_font.render("时间到！", True, (255, 215, 0))  # 金色标题
        title_rect = title.get_rect(center=(center_x, margin_top))
        
        # 添加标题阴影
        shadow_surf = pygame.Surface(title.get_size())
        shadow_surf.fill((0, 0, 0, 0))
        shadow_surf.blit(game.large_font.render("时间到！", True, (200, 180, 0)), (0, 0))
        game.screen.blit(shadow_surf, (title_rect.x + 2, title_rect.y + 2))
        game.screen.blit(title, title_rect)
        
        # 显示分数信息
        score_text = game.font.render(f"最终得分: {game.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(center_x, title_rect.bottom + spacing))
        game.screen.blit(score_text, score_rect)
        
        # 显示蛇身长度
        length_text = game.font.render(f"蛇身长度: {len(game.snake)}", True, (255, 255, 255))
        length_rect = length_text.get_rect(center=(center_x, score_rect.bottom + spacing // 2))
        game.screen.blit(length_text, length_rect)
        
        # 显示游戏时长
        elapsed_time = min(time_limit, time.time() - start_time)
        time_text = game.font.render(f"游戏时长: {int(elapsed_time)}秒", True, (255, 255, 255))
        time_rect = time_text.get_rect(center=(center_x, length_rect.bottom + spacing // 2))
        game.screen.blit(time_text, time_rect)
        
        # 显示死亡原因
        if hasattr(game, 'death_reason') and game.death_reason:
            reason_text = game.font.render(f"{game.death_reason}", True, (255, 100, 100))
            reason_rect = reason_text.get_rect(center=(center_x, time_rect.bottom + spacing))
            game.screen.blit(reason_text, reason_rect)
        
        # 绘制分数统计面板
        stats_panel_y = time_rect.bottom + spacing * 2
        panel_width, panel_height = 400, 150
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.centerx = center_x
        panel_rect.y = stats_panel_y
        
        # 面板背景（半透明）
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        game.screen.blit(s, panel_rect)
        pygame.draw.rect(game.screen, (255, 215, 0), panel_rect, 2, border_radius=10)
        
        # 绘制按钮
        btn_width, btn_height = 150, 45
        btn_spacing = 20
        
        retry_button_rect = pygame.Rect(0, 0, btn_width, btn_height)
        retry_button_rect.centerx = center_x - (btn_width + btn_spacing) // 2
        retry_button_rect.bottom = panel_rect.bottom - 20
        
        menu_button_rect = pygame.Rect(0, 0, btn_width, btn_height)
        menu_button_rect.centerx = center_x + (btn_width + btn_spacing) // 2
        menu_button_rect.bottom = panel_rect.bottom - 20
        
        # 检测按钮悬停
        mouse_pos = pygame.mouse.get_pos()
        retry_hover = retry_button_rect.collidepoint(mouse_pos)
        menu_hover = menu_button_rect.collidepoint(mouse_pos)
        
        # 绘制重试按钮
        retry_color = (220, 180, 70) if retry_hover else (200, 160, 50)
        pygame.draw.rect(game.screen, retry_color, retry_button_rect, border_radius=8)
        pygame.draw.rect(game.screen, (180, 140, 30), retry_button_rect, 2, border_radius=8)
        
        # 绘制返回菜单按钮
        menu_color = (120, 120, 220) if menu_hover else (100, 100, 200)
        pygame.draw.rect(game.screen, menu_color, menu_button_rect, border_radius=8)
        pygame.draw.rect(game.screen, (80, 80, 200), menu_button_rect, 2, border_radius=8)
        
        # 按钮文字
        retry_text = game.font.render(retry_button_text, True, (0, 0, 0))
        retry_text_rect = retry_text.get_rect(center=retry_button_rect.center)
        game.screen.blit(retry_text, retry_text_rect)
        
        menu_text = game.font.render("返回菜单", True, (0, 0, 0))
        menu_text_rect = menu_text.get_rect(center=menu_button_rect.center)
        game.screen.blit(menu_text, menu_text_rect)
        
        # 保存按钮位置
        game.retry_button_rect = retry_button_rect
        game.menu_button_rect = menu_button_rect
        game.exit_button_rect = pygame.Rect(0, 0, 1, 1)  # 占位，实际不使用
        
        # 刷新屏幕显示
        pygame.display.flip()

    # 主循环
    while True:
        # 检查是否超时
        if game_state == "running":
            elapsed_time = time.time() - start_time
            if elapsed_time >= time_limit:
                game_state = "game_over"
                # 设置超时死亡原因
                game.death_reason = "时间到！游戏结束。"
                # 保存游戏结束时间，用于固定显示时长
                game.game_end_time = time.time()
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 欢迎界面 - 检查开始按钮点击
            if game_state == "welcome" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(game, 'start_button_rect') and game.start_button_rect.collidepoint(event.pos):
                    game_state = "running"
                    start_time = time.time()  # 重置开始时间
                    game.reset()
                    # 立即渲染初始画面，防止黑屏
                    game.render(ai_connected, draw_opponent=False, show_ai=True)
                    remaining_time = max(0, time_limit - (time.time() - start_time))
                    time_text = game.font.render(f"时间: {int(remaining_time)}秒", True, (255, 215, 0))
                    time_rect = time_text.get_rect(topright=(game.display_width - 20, 20))
                    bg_rect = pygame.Rect(0, 0, time_rect.width + 10, time_rect.height + 5)
                    bg_rect.topleft = (time_rect.left - 5, time_rect.top - 2)
                    pygame.draw.rect(game.screen, (0, 0, 0, 180), bg_rect)
                    pygame.draw.rect(game.screen, (255, 215, 0), bg_rect, 1)
                    game.screen.blit(time_text, time_rect)
                    pygame.display.flip()
            
            # 游戏结束界面 - 检查按钮点击
            elif game_state == "game_over" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(game, 'retry_button_rect') and game.retry_button_rect.collidepoint(event.pos):
                    # 重新开始游戏
                    game.reset()
                    start_time = time.time()
                    game_state = "running"
                elif hasattr(game, 'menu_button_rect') and game.menu_button_rect.collidepoint(event.pos):
                    # 返回主菜单
                    pygame.quit()
                    main_gui()
            
            # 键盘事件（游戏运行状态）
            elif event.type == pygame.KEYDOWN and game_state == "running":
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    action = 0
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    action = 1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    action = 2
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    action = 3
                elif event.key == pygame.K_x:
                    # 切换 AI 控制
                    ai_control = not ai_control
                    if ai_control:
                        ai_connected = True

        # 游戏运行状态
        if game_state == "welcome":
            draw_welcome()
            pygame.display.flip()  # 确保欢迎界面内容显示
            clock.tick(20)
            continue
        if game_state == "game_over":
            draw_game_over()
            pygame.display.flip()  # 确保游戏结束界面内容显示
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
                    # 只在AI控制时调用get_ai_action
                    chosen_action = get_ai_action(game, is_opponent=False)
                else:
                    # 对于玩家控制，action为-1时保持当前方向
                    chosen_action = action
                
                # 执行游戏步骤
                done, info = game.step(chosen_action)
                
                # 只有当游戏未结束时才渲染
                if not done:
                    # 绘制游戏画面，包括剩余时间
                    game.render(ai_connected, draw_opponent=False, show_ai=True)
                    
                    # 在右上角显示剩余时间
                    remaining_time = max(0, time_limit - (time.time() - start_time))
                    time_text = game.font.render(f"时间: {int(remaining_time)}秒", True, (255, 215, 0))
                    time_rect = time_text.get_rect(topright=(game.display_width - 20, 20))
                    
                    # 添加文字背景
                    bg_rect = pygame.Rect(0, 0, time_rect.width + 10, time_rect.height + 5)
                    bg_rect.topleft = (time_rect.left - 5, time_rect.top - 2)
                    pygame.draw.rect(game.screen, (0, 0, 0, 180), bg_rect)
                    pygame.draw.rect(game.screen, (255, 215, 0), bg_rect, 1)
                    
                    game.screen.blit(time_text, time_rect)
                    pygame.display.flip()
                    
                    # 重置动作，避免连续移动
                    action = -1
                else:
                    game_state = "game_over"
                    # 保存游戏结束时间，用于固定显示时长
                    game.game_end_time = time.time()
        else:
            # 即使不在更新间隔，也要绘制界面（特别是剩余时间）
            if game_state == "running":
                # 只更新时间显示，不更新游戏状态
                remaining_time = max(0, time_limit - (time.time() - start_time))
                game.render(ai_connected, draw_opponent=False, show_ai=True)
                time_text = game.font.render(f"时间: {int(remaining_time)}秒", True, (255, 215, 0))
                time_rect = time_text.get_rect(topright=(game.display_width - 20, 20))
                bg_rect = pygame.Rect(0, 0, time_rect.width + 10, time_rect.height + 5)
                bg_rect.topleft = (time_rect.left - 5, time_rect.top - 2)
                pygame.draw.rect(game.screen, (0, 0, 0, 180), bg_rect)
                pygame.draw.rect(game.screen, (255, 215, 0), bg_rect, 1)
                game.screen.blit(time_text, time_rect)
                pygame.display.flip()
                
                time_text = game.font.render(f"时间: {int(remaining_time)}秒", True, (255, 215, 0))
                time_rect = time_text.get_rect(topright=(game.display_width - 20, 20))
                
                bg_rect = pygame.Rect(0, 0, time_rect.width + 10, time_rect.height + 5)
                bg_rect.topleft = (time_rect.left - 5, time_rect.top - 2)
                pygame.draw.rect(game.screen, (0, 0, 0, 180), bg_rect)
                pygame.draw.rect(game.screen, (255, 215, 0), bg_rect, 1)
                
                game.screen.blit(time_text, time_rect)
                pygame.display.flip()

        # 限制帧率
        clock.tick(60)


# ---------------------------
# 主入口
# ---------------------------
def main_gui():
    """图形界面模式选择 - 优化版"""
    pygame.init()
    # 增加窗口高度以容纳所有按钮
    screen = pygame.display.set_mode((600, 560))
    pygame.display.set_caption("贪吃蛇游戏 - 选择模式")
    
    # 尝试加载中文字体，提供多种备选字体
    try:
        font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 30)
        large_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 48)
    except:
        # 如果无法加载中文字体，使用默认字体
        font = pygame.font.Font(None, 36)
        large_font = pygame.font.Font(None, 54)
    
    clock = pygame.time.Clock()
    running = True
    
    # 添加动画变量
    title_alpha = 0
    fade_in_speed = 5
    
    # 创建按钮类以简化代码和添加悬停效果
    class Button:
        def __init__(self, x, y, width, height, text, normal_color, hover_color, text_color, border_color):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.normal_color = normal_color
            self.hover_color = hover_color
            self.text_color = text_color
            self.border_color = border_color
            self.is_hovered = False
        
        def update(self, mouse_pos):
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        def draw(self, surface, font):
            # 先绘制阴影（如果悬停）
            if self.is_hovered:
                shadow_offset = 3
                shadow_rect = self.rect.copy()
                shadow_rect.x += shadow_offset
                shadow_rect.y += shadow_offset
                # 使用半透明黑色，需要确保surface支持alpha
                shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=12)
                surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
            
            # 绘制按钮背景
            color = self.hover_color if self.is_hovered else self.normal_color
            pygame.draw.rect(surface, color, self.rect, border_radius=12)
            pygame.draw.rect(surface, self.border_color, self.rect, 3, border_radius=12)
            
            # 绘制按钮文本
            text_surf = font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
    
    # 初始化按钮
    btn_width, btn_height = 200, 50
    btn_spacing = 20
    bottom_margin = 50
    
    # 调整布局为两行
    row_spacing = 30
    
    # 计算起始位置使按钮居中
    first_row_y = 140
    second_row_y = first_row_y + btn_height + row_spacing
    third_row_y = second_row_y + btn_height + row_spacing
    center_x = 300
    
    fourth_row_y = third_row_y + btn_height + btn_spacing
    
    buttons = [
        # 第一行按钮
        Button(center_x - btn_width - btn_spacing//2, first_row_y, btn_width, btn_height, 
               "普通模式", (120, 220, 120), (140, 240, 140), (0, 0, 0), (80, 200, 80)),
        Button(center_x + btn_spacing//2, first_row_y, btn_width, btn_height, 
               "对抗模式", (120, 120, 220), (140, 140, 240), (0, 0, 0), (80, 80, 200)),
        # 第二行按钮
        Button(center_x - btn_width - btn_spacing//2, second_row_y, btn_width, btn_height, 
               "限时模式", (220, 180, 70), (240, 200, 90), (0, 0, 0), (180, 160, 50)),
        Button(center_x + btn_spacing//2, second_row_y, btn_width, btn_height, 
               "影子模式", (220, 70, 220), (240, 90, 240), (255, 255, 255), (180, 50, 180)),
        # 第三行按钮 - 设置
        Button(center_x - btn_width//2, third_row_y, btn_width, btn_height, 
               "游戏设置", (220, 220, 120), (240, 240, 140), (0, 0, 0), (180, 180, 100)),
        # 第四行按钮 - 帮助与教程
        Button(center_x - btn_width//2, fourth_row_y, btn_width, btn_height, 
               "帮助与教程", (220, 120, 220), (240, 140, 240), (0, 0, 0), (180, 100, 180)),
        # 底部退出按钮
        Button(center_x - btn_width//2, fourth_row_y + btn_height + btn_spacing, btn_width, btn_height, 
               "退出游戏", (220, 70, 70), (240, 90, 90), (255, 255, 255), (180, 50, 50))
    ]
    
    # 绘制模式选择界面
    def draw_mode_selection():
        # 绘制渐变背景
        for y in range(560):
            # 创建从深蓝色到黑色的垂直渐变
            r = int(0)
            g = int(0)
            b = int(50 - 50 * y / 560)
            pygame.draw.line(screen, (r, g, b), (0, y), (600, y))
        
        # 绘制标题（带淡入效果）
        title = large_font.render("贪吃蛇游戏", True, (255, 255, 255))
        
        # 创建一个带透明度的surface
        title_surf = pygame.Surface(title.get_size(), pygame.SRCALPHA)
        title_surf.fill((255, 255, 255, title_alpha))
        title_surf.blit(title, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        title_rect = title.get_rect(center=(center_x, 80))
        screen.blit(title_surf, title_rect)
        
        # 绘制副标题
        subtitle = font.render("选择游戏模式", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(center_x, 120))
        screen.blit(subtitle, subtitle_rect)
        
        # 绘制所有按钮
        for button in buttons:
            button.draw(screen, font)
        
        # 添加版本信息
        version_text = font.render("v1.0", True, (100, 100, 100))
        screen.blit(version_text, (5, 530))
        
        pygame.display.flip()
    
    # 主循环
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新按钮状态
        for button in buttons:
            button.update(mouse_pos)
        
        # 处理淡入动画
        if title_alpha < 255:
            title_alpha = min(255, title_alpha + fade_in_speed)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 检查按钮点击
                if buttons[0].rect.collidepoint(mouse_pos):
                    pygame.quit()
                    main_normal()
                    return
                elif buttons[1].rect.collidepoint(mouse_pos):
                    pygame.quit()
                    main_opponent()
                    return
                elif buttons[2].rect.collidepoint(mouse_pos):
                    pygame.quit()
                    main_timed()
                    return
                elif buttons[3].rect.collidepoint(mouse_pos):
                    pygame.quit()
                    main_three_snake()
                    return

                elif buttons[4].rect.collidepoint(mouse_pos):
                    pygame.quit()
                    main_settings()
                    return
                elif buttons[5].rect.collidepoint(mouse_pos):
                    pygame.quit()
                    main_help()
                    return
                elif buttons[6].rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
            # 添加键盘支持
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    pygame.quit()
                    main_normal()
                    return
                elif event.key == pygame.K_2:
                    pygame.quit()
                    main_opponent()
                    return
                elif event.key == pygame.K_3:
                    pygame.quit()
                    main_timed()
                    return
                elif event.key == pygame.K_4:
                    pygame.quit()
                    main_three_snake()
                    return

                elif event.key == pygame.K_5:
                    pygame.quit()
                    main_settings()
                    return
                elif event.key == pygame.K_6:
                    pygame.quit()
                    main_help()
                    return
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        
        draw_mode_selection()
        clock.tick(60)  # 提高帧率使动画更流畅

def main_settings():
    """游戏设置界面 - 允许玩家自定义游戏参数"""
    pygame.init()
    screen = pygame.display.set_mode((700, 600))
    pygame.display.set_caption("贪吃蛇游戏 - 设置")
    
    # 尝试加载中文字体
    try:
        font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 24)
        large_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 40)
        small_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 20)
    except:
        font = pygame.font.Font(None, 30)
        large_font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 24)
    
    # 创建游戏配置对象（使用默认值）
    config = {
        "board_size": 40,          # 棋盘大小
        "cell_size": 20,           # 格子大小
        "snake_speed": 0.10,       # 蛇移动速度
        "enable_sound": True,      # 声音开关
        "food_value": 1,           # 食物分值
        "enable_border": True,     # 边界碰撞
        #"ai_difficulty": "medium"  # AI难度
    }
    
    # 可配置选项列表
    options = [
        {"name": "棋盘大小", "type": "slider", "min": 10, "max": 40, "step": 5, "value": config["board_size"]},
        {"name": "游戏速度", "type": "slider", "min": 0.05, "max": 0.3, "step": 0.01, "value": config["snake_speed"]},
        {"name": "食物分值", "type": "slider", "min": 1, "max": 5, "step": 1, "value": config["food_value"]},
        {"name": "声音效果", "type": "toggle", "value": config["enable_sound"]},
        {"name": "边界碰撞", "type": "toggle", "value": config["enable_border"]},
        #{"name": "AI难度", "type": "dropdown", "options": ["简单", "中等", "困难"], "value": config["ai_difficulty"]}
    ]
    
    # 滑动条和开关类
    class Slider:
        def __init__(self, x, y, width, height, min_val, max_val, step, initial_val):
            self.rect = pygame.Rect(x, y, width, height)
            self.min_val = min_val
            self.max_val = max_val
            self.step = step
            self.value = initial_val
            self.is_dragging = False
            self.handle_width = 20
            self.handle_rect = pygame.Rect(
                x + (width - self.handle_width) * ((initial_val - min_val) / (max_val - min_val)),
                y - 3,
                self.handle_width,
                height + 6
            )
        
        def update(self, mouse_pos, mouse_down):
            if mouse_down:
                if self.handle_rect.collidepoint(mouse_pos):
                    self.is_dragging = True
                elif self.rect.collidepoint(mouse_pos):
                    # 点击滑动条上的位置
                    ratio = (mouse_pos[0] - self.rect.x) / self.rect.width
                    self.value = min(self.max_val, max(self.min_val, self.min_val + (self.max_val - self.min_val) * ratio))
                    # 四舍五入到最近的步长
                    self.value = round(self.value / self.step) * self.step
                    # 更新滑块位置
                    self.handle_rect.x = self.rect.x + (self.rect.width - self.handle_width) * ((self.value - self.min_val) / (self.max_val - self.min_val))
            else:
                self.is_dragging = False
            
            if self.is_dragging:
                # 拖动滑块
                new_x = max(self.rect.x, min(mouse_pos[0] - self.handle_width // 2, self.rect.right - self.handle_width))
                self.handle_rect.x = new_x
                ratio = (new_x - self.rect.x) / (self.rect.width - self.handle_width)
                self.value = min(self.max_val, max(self.min_val, self.min_val + (self.max_val - self.min_val) * ratio))
                # 四舍五入到最近的步长
                self.value = round(self.value / self.step) * self.step
            
            return self.value
        
        def draw(self, surface, font):
            # 绘制滑动条背景
            pygame.draw.rect(surface, (80, 80, 80), self.rect, border_radius=5)
            # 绘制滑动条填充部分
            fill_width = (self.handle_rect.centerx - self.rect.x)
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(surface, (180, 180, 180), fill_rect, border_radius=5)
            # 绘制滑块
            pygame.draw.rect(surface, (220, 220, 220), self.handle_rect, border_radius=4)
            pygame.draw.rect(surface, (200, 200, 200), self.handle_rect, 2, border_radius=4)
            # 显示当前值
            value_text = small_font.render(str(round(self.value, 2)), True, (255, 255, 255))
            value_rect = value_text.get_rect(center=(self.rect.right + 40, self.rect.centery))
            surface.blit(value_text, value_rect)
    
    class ToggleSwitch:
        def __init__(self, x, y, width, height, initial_value):
            self.rect = pygame.Rect(x, y, width, height)
            self.value = initial_value
            self.is_on = initial_value
            self.circle_rect = pygame.Rect(
                x + 3 if not initial_value else x + width - height + 3,
                y + 3,
                height - 6,
                height - 6
            )
        
        def update(self, mouse_pos, mouse_down):
            if mouse_down and self.rect.collidepoint(mouse_pos):
                self.is_on = not self.is_on
                self.value = self.is_on
                # 更新圆形位置
                if self.is_on:
                    self.circle_rect.x = self.rect.x + self.rect.width - self.rect.height + 3
                else:
                    self.circle_rect.x = self.rect.x + 3
                return True
            return False
        
        def draw(self, surface, font=None):
            # 绘制开关背景
            bg_color = (80, 200, 80) if self.is_on else (100, 100, 100)
            pygame.draw.rect(surface, bg_color, self.rect, border_radius=15)
            # 绘制开关圆圈
            pygame.draw.circle(surface, (255, 255, 255), self.circle_rect.center, self.circle_rect.width // 2)
    
    class DropdownMenu:
        def __init__(self, x, y, width, height, options, initial_value):
            self.rect = pygame.Rect(x, y, width, height)
            self.options = options
            self.value = initial_value
            self.is_open = False
            self.option_rects = []
            for i, option in enumerate(options):
                self.option_rects.append(pygame.Rect(x, y + (i + 1) * height, width, height))
        
        def update(self, mouse_pos, mouse_down):
            if mouse_down:
                if self.rect.collidepoint(mouse_pos):
                    self.is_open = not self.is_open
                    return True
                elif self.is_open:
                    for i, rect in enumerate(self.option_rects):
                        if rect.collidepoint(mouse_pos):
                            self.value = self.options[i]
                            self.is_open = False
                            return True
                    # 点击外部关闭下拉菜单
                    self.is_open = False
            return False
        
        def draw(self, surface, font):
            # 绘制下拉菜单按钮
            pygame.draw.rect(surface, (80, 80, 80), self.rect, border_radius=5)
            pygame.draw.rect(surface, (120, 120, 120), self.rect, 1, border_radius=5)
            # 绘制当前选中的值
            text = font.render(self.value, True, (255, 255, 255))
            surface.blit(text, (self.rect.x + 10, self.rect.centery - text.get_height() // 2))
            # 绘制下拉箭头
            arrow_points = [(self.rect.right - 15, self.rect.centery - 5),
                            (self.rect.right - 5, self.rect.centery - 5),
                            (self.rect.right - 10, self.rect.centery + 5)]
            pygame.draw.polygon(surface, (255, 255, 255), arrow_points)
            
            # 绘制选项列表
            if self.is_open:
                for i, rect in enumerate(self.option_rects):
                    # 鼠标悬停检测 - 使用更亮的悬停颜色
                    hover_color = (150, 150, 180) if rect.collidepoint(pygame.mouse.get_pos()) else (80, 80, 80)
                    # 先绘制背景，确保完全覆盖
                    pygame.draw.rect(surface, hover_color, rect, border_radius=5)
                    # 绘制边框，确保没有漏边
                    pygame.draw.rect(surface, (120, 120, 120), rect, 1, border_radius=5)
                    option_text = font.render(self.options[i], True, (255, 255, 255))
                    surface.blit(option_text, (rect.x + 10, rect.centery - option_text.get_height() // 2))
    
    # 创建UI元素
    ui_elements = []
    y_pos = 120
    element_spacing = 60
    
    for i, option in enumerate(options):
        if option["type"] == "slider":
            ui_elements.append(Slider(200, y_pos, 300, 20, 
                                     option["min"], option["max"], option["step"], option["value"]))
        elif option["type"] == "toggle":
            ui_elements.append(ToggleSwitch(200, y_pos - 5, 80, 30, option["value"]))
        elif option["type"] == "dropdown":
            ui_elements.append(DropdownMenu(200, y_pos - 5, 150, 35, option["options"], option["value"]))
        y_pos += element_spacing
    
    # 创建按钮类
    class Button:
        def __init__(self, x, y, width, height, text, normal_color, hover_color, text_color, border_color):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.normal_color = normal_color
            self.hover_color = hover_color
            self.text_color = text_color
            self.border_color = border_color
            self.is_hovered = False
        
        def update(self, mouse_pos):
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        def draw(self, surface, font):
            # 先绘制阴影（如果悬停）
            if self.is_hovered:
                shadow_offset = 2
                shadow_rect = self.rect.copy()
                shadow_rect.x += shadow_offset
                shadow_rect.y += shadow_offset
                # 使用半透明黑色
                shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surf, (0, 0, 0, 80), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=8)
                surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
            
            # 绘制按钮背景
            color = self.hover_color if self.is_hovered else self.normal_color
            pygame.draw.rect(surface, color, self.rect, border_radius=8)
            pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=8)
            
            # 绘制按钮文本
            text_surf = font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
    
    # 创建保存和返回按钮
    save_button = Button(200, 520, 120, 40, "保存设置", (120, 200, 120), (140, 220, 140), (0, 0, 0), (80, 180, 80))
    back_button = Button(380, 520, 120, 40, "返回", (220, 120, 120), (240, 140, 140), (0, 0, 0), (180, 80, 80))
    
    # 保存配置到全局
    def save_config():
        # 更新配置字典
        for i, option in enumerate(options):
            if option["type"] == "slider":
                option["value"] = ui_elements[i].value
                if option["name"] == "棋盘大小":
                    config["board_size"] = int(ui_elements[i].value)
                elif option["name"] == "游戏速度":
                    config["snake_speed"] = ui_elements[i].value
                elif option["name"] == "食物分值":
                    config["food_value"] = int(ui_elements[i].value)
            elif option["type"] == "toggle":
                option["value"] = ui_elements[i].value
                if option["name"] == "声音效果":
                    config["enable_sound"] = ui_elements[i].value
                elif option["name"] == "边界碰撞":
                    config["enable_border"] = ui_elements[i].value
            # elif option["type"] == "dropdown":
            #     option["value"] = ui_elements[i].value
            #     if option["name"] == "AI难度":
            #         difficulty_map = {"简单": "easy", "中等": "medium", "困难": "hard", "easy": "easy", "medium": "medium", "hard": "hard"}
            #         config["ai_difficulty"] = difficulty_map[ui_elements[i].value]
        
        # 将配置保存为全局变量，让其他模式可以访问
        global game_config
        game_config = config
        
        # 显示保存成功提示
        show_success = True
        success_timer = 1.0  # 显示1秒
        return show_success, success_timer
    
    # 主循环
    running = True
    clock = pygame.time.Clock()
    show_success = False
    success_timer = 0
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        
        # 更新按钮状态
        save_button.update(mouse_pos)
        back_button.update(mouse_pos)
        
        # 更新UI元素
        for element in ui_elements:
            element.update(mouse_pos, mouse_down)
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 检查按钮点击
                if save_button.rect.collidepoint(mouse_pos):
                    show_success, success_timer = save_config()
                elif back_button.rect.collidepoint(mouse_pos):
                    pygame.quit()
                    main_gui()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    main_gui()
        
        # 更新成功提示计时器
        if show_success:
            success_timer -= 1/60  # 假设60FPS
            if success_timer <= 0:
                show_success = False
        
        # 绘制界面
        # 绘制渐变背景
        for y in range(600):
            r = int(20)
            g = int(20)
            b = int(40 - 30 * y / 600)
            pygame.draw.line(screen, (r, g, b), (0, y), (700, y))
        
        # 绘制标题
        title = large_font.render("游戏设置", True, (255, 255, 255))
        title_rect = title.get_rect(center=(350, 60))
        screen.blit(title, title_rect)
        
        # 绘制设置选项文本
        y_pos = 120
        for i, option in enumerate(options):
            option_text = font.render(option["name"], True, (220, 220, 220))
            screen.blit(option_text, (50, y_pos))
            y_pos += element_spacing
        
        # 绘制UI元素
        for element in ui_elements:
            if hasattr(element, 'draw'):
                element.draw(screen, font)
        
        # 绘制按钮
        save_button.draw(screen, font)
        back_button.draw(screen, font)
        
        # 绘制保存成功提示
        if show_success:
            # 创建半透明背景
            success_surf = pygame.Surface((300, 60), pygame.SRCALPHA)
            success_surf.fill((0, 120, 0, 180))
            pygame.draw.rect(success_surf, (0, 200, 0), (0, 0, 300, 60), 2, border_radius=10)
            screen.blit(success_surf, (200, 450))
            
            success_text = font.render("设置保存成功！", True, (255, 255, 255))
            text_rect = success_text.get_rect(center=(350, 480))
            screen.blit(success_text, text_rect)
        
        # 绘制说明文本
        help_text = small_font.render("提示: 部分设置需要重新开始游戏才能生效", True, (150, 150, 150))
        screen.blit(help_text, (180, 480))
        
        pygame.display.flip()
        clock.tick(60)

# 游戏配置全局变量
game_config = {
    "board_size": 40,
    "cell_size": 20,
    "snake_speed": 0.10,
    "enable_sound": True,
    "food_value": 1,
    "enable_border": True,
    "ai_difficulty": "medium"
}


def main_help():
    """游戏帮助和教程界面"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("贪吃蛇游戏 - 帮助与教程")
    
    # 尝试加载中文字体
    try:
        font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 24)
        large_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 40)
        small_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 20)
        tiny_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 18)
    except:
        font = pygame.font.Font(None, 30)
        large_font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 24)
        tiny_font = pygame.font.Font(None, 20)
    
    clock = pygame.time.Clock()
    
    # 创建按钮类
    class Button:
        def __init__(self, x, y, width, height, text, color, hover_color, text_color, border_color):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.color = color
            self.hover_color = hover_color
            self.text_color = text_color
            self.border_color = border_color
            self.is_hovered = False
        
        def draw(self, surface):
            # 先绘制阴影（如果悬停）
            if self.is_hovered:
                shadow_offset = 2
                shadow_rect = self.rect.copy()
                shadow_rect.x += shadow_offset
                shadow_rect.y += shadow_offset
                # 使用半透明黑色
                shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surf, (0, 0, 0, 80), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=10)
                surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
            
            # 绘制按钮背景
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, color, self.rect, border_radius=10)
            pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=10)  # 边框
            
            # 绘制按钮文本
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
        
        def update(self, mouse_pos):
            self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    # 创建按钮
    btn_width, btn_height = 180, 50
    center_x = 400
    
    buttons = [
        Button(center_x - btn_width//2, 520, btn_width, btn_height, "返回主菜单", 
               (120, 120, 120), (140, 140, 140), (255, 255, 255), (80, 80, 80)),
    ]
    
    # 绘制渐变背景
    def draw_background():
        for y in range(600):
            # 创建从深蓝色到黑色的垂直渐变
            r = int(0)
            g = int(0)
            b = int(50 - 50 * y / 600)
            pygame.draw.line(screen, (r, g, b), (0, y), (800, y))
    
    # 绘制帮助内容
    def draw_help_content():
        # 标题
        title = large_font.render("游戏帮助与教程", True, (255, 215, 0))
        screen.blit(title, (400 - title.get_width()//2, 40))
        
        # 基本操作
        operation_title = font.render("基本操作:", True, (255, 255, 255))
        screen.blit(operation_title, (100, 100))
        
        operation_texts = [
            "方向键: 控制蛇的移动方向",
            "WASD: 也可以用来控制蛇的移动",
            "空格键: 暂停/继续游戏",
            "ESC键: 返回主菜单"
        ]
        
        for i, text in enumerate(operation_texts):
            text_surface = small_font.render(text, True, (200, 200, 255))
            screen.blit(text_surface, (120, 130 + i * 30))
        
        # 游戏规则
        rules_title = font.render("游戏规则:", True, (255, 255, 255))
        screen.blit(rules_title, (100, 280))
        
        rules_texts = [
            "1. 控制贪吃蛇吃掉食物，使蛇变得更长",
            "2. 不要撞到墙壁或自己的身体",
            "3. 每吃掉一个食物，分数会增加",
            "4. 游戏难度会随着分数增加而提高"
        ]
        
        for i, text in enumerate(rules_texts):
            text_surface = small_font.render(text, True, (200, 200, 255))
            screen.blit(text_surface, (120, 310 + i * 30))
        
        # 游戏模式说明
        modes_title = font.render("游戏模式:", True, (255, 255, 255))
        screen.blit(modes_title, (450, 100))
        
        modes_texts = [
            "普通模式: 经典贪吃蛇玩法",
            "对抗模式: 与AI蛇进行对战",
            "限时模式: 在60秒内获得最高分数",
            "影子模式: AI蛇作为影子完全模仿玩家移动，AI死亡玩家也死亡"
            "提示: 使用游戏设置调整难度和参数"
        ]
        
        for i, text in enumerate(modes_texts):
            text_surface = tiny_font.render(text, True, (200, 200, 255))
            screen.blit(text_surface, (470, 130 + i * 30))
        
        # 快捷键提示
        shortcut_title = font.render("主菜单快捷键:", True, (255, 255, 255))
        screen.blit(shortcut_title, (450, 280))
        
        shortcut_texts = [
            "1-4: 选择游戏模式",
            "5: 打开游戏设置",
            "6: 打开帮助与教程",
            "ESC/q: 退出游戏"
        ]
        
        for i, text in enumerate(shortcut_texts):
            text_surface = tiny_font.render(text, True, (200, 200, 255))
            screen.blit(text_surface, (470, 310 + i * 25))
    
    # 主循环
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新按钮状态
        for button in buttons:
            button.update(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 处理按钮点击
                if buttons[0].rect.collidepoint(mouse_pos):
                    pygame.quit()
                    main_gui()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    main_gui()
        
        # 绘制界面
        draw_background()
        for button in buttons:
            button.draw(screen)
        draw_help_content()
        
        pygame.display.flip()
        clock.tick(60)


    pass  # 在实际使用时，会通过函数调用的方式进行保存和加载

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