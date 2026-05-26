#!/usr/bin/env python3
"""
Консольная Змейка (Snake Game)
Управление: Стрелки или WASD
Только встроенные библиотеки: os, time, random, sys
"""

import os
import sys
import time
import random
import threading
from typing import List, Tuple

# Константы для символов
WALL = '#'
HEAD = 'O'
BODY = 'o'
FOOD = '*'
EMPTY = ' '

# Направления
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class SnakeGame:
    def __init__(self, width: int = 20, height: int = 15, speed: float = 0.15):
        self.width = width
        self.height = height
        self.speed = speed
        self.score = 0
        self.game_over = False
        self.running = True
        
        # Инициализация змейки (начинаем с центра)
        start_x = width // 2
        start_y = height // 2
        self.snake: List[Tuple[int, int]] = [
            (start_x, start_y),      # Голова
            (start_x - 1, start_y),  # Тело
            (start_x - 2, start_y),  # Хвост
        ]
        self.direction = RIGHT
        self.next_direction = RIGHT
        
        # Генерация первой еды
        self.food = self._generate_food()
        
        # Поток для ввода с клавиатуры
        self._setup_keyboard()
    
    def _setup_keyboard(self):
        """Настройка неблокирующего ввода с клавиатуры"""
        if os.name == 'nt':  # Windows
            import msvcrt
            self.msvcrt = msvcrt
            self.use_msvcrt = True
        else:  # Linux/Mac
            import tty
            import termios
            self.tty = tty
            self.termios = termios
            self.use_msvcrt = False
            self.old_settings = None
    
    def _get_key(self) -> str:
        """Получение нажатой клавиши (неблокирующее)"""
        if self.use_msvcrt:
            if self.msvcrt.kbhit():
                key = self.msvcrt.getch()
                if isinstance(key, bytes):
                    key = key.decode('utf-8', errors='ignore')
                return key
            return ''
        else:
            # Для Unix-систем используем select для неблокирующего чтения
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.read(1)
            return ''
    
    def _process_input(self):
        """Обработка ввода в отдельном потоке"""
        if os.name != 'nt':
            # Настройка терминала для Linux/Mac
            import tty
            import termios
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        
        try:
            while self.running:
                key = self._get_key()
                
                if key == '\x1b':  # ESC - последовательность стрелок
                    if os.name != 'nt':
                        import select
                        if select.select([sys.stdin], [], [], 0.05)[0]:
                            key += sys.stdin.read(1)
                        if select.select([sys.stdin], [], [], 0)[0]:
                            key += sys.stdin.read(1)
                    
                    if key == '\x1b[A':  # Вверх
                        if self.direction != DOWN:
                            self.next_direction = UP
                    elif key == '\x1b[B':  # Вниз
                        if self.direction != UP:
                            self.next_direction = DOWN
                    elif key == '\x1b[C':  # Вправо
                        if self.direction != LEFT:
                            self.next_direction = RIGHT
                    elif key == '\x1b[D':  # Влево
                        if self.direction != RIGHT:
                            self.next_direction = LEFT
                
                elif key.lower() in ('w', 'ц'):
                    if self.direction != DOWN:
                        self.next_direction = UP
                elif key.lower() in ('s', 'ы'):
                    if self.direction != UP:
                        self.next_direction = DOWN
                elif key.lower() in ('d', 'в'):
                    if self.direction != LEFT:
                        self.next_direction = RIGHT
                elif key.lower() in ('a', 'ф'):
                    if self.direction != RIGHT:
                        self.next_direction = LEFT
                elif key.lower() == 'q':
                    self.running = False
                
                time.sleep(0.05)  # Небольшая задержка для предотвращения высокой нагрузки CPU
        finally:
            # Восстановление настроек терминала
            if os.name != 'nt' and self.old_settings:
                import termios
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def _generate_food(self) -> Tuple[int, int]:
        """Генерация еды в случайном месте, не занятом змейкой"""
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if (x, y) not in self.snake:
                return (x, y)
    
    def _draw(self):
        """Отрисовка игрового поля"""
        # Создание пустого поля
        field = [[EMPTY for _ in range(self.width)] for _ in range(self.height)]
        
        # Рисуем стены
        for x in range(self.width):
            field[0][x] = WALL
            field[self.height - 1][x] = WALL
        for y in range(self.height):
            field[y][0] = WALL
            field[y][self.width - 1] = WALL
        
        # Рисуем еду
        fx, fy = self.food
        field[fy][fx] = FOOD
        
        # Рисуем змейку
        for i, (x, y) in enumerate(self.snake):
            if 0 <= x < self.width and 0 <= y < self.height:
                if i == 0:
                    field[y][x] = HEAD
                else:
                    field[y][x] = BODY
        
        # Очистка экрана и отрисовка
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print('=' * self.width)
        print(f'Счет: {self.score} | Управление: Стрелки/WASD | Q - выход')
        print('=' * self.width)
        
        for row in field:
            print(''.join(row))
        
        print('=' * self.width)
    
    def _update(self):
        """Обновление состояния игры"""
        if self.game_over:
            return
        
        # Обновление направления
        self.direction = self.next_direction
        
        # Вычисление новой позиции головы
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        
        # Проверка столкновения со стенами
        if (new_head[0] <= 0 or new_head[0] >= self.width - 1 or
            new_head[1] <= 0 or new_head[1] >= self.height - 1):
            self.game_over = True
            return
        
        # Проверка столкновения с самой собой
        if new_head in self.snake[:-1]:  # Не проверяем последний сегмент (он сдвинется)
            self.game_over = True
            return
        
        # Добавление новой головы
        self.snake.insert(0, new_head)
        
        # Проверка: съела ли змейка еду
        if new_head == self.food:
            self.score += 1
            self.food = self._generate_food()
            # Змейка удлиняется (не удаляем хвост)
        else:
            # Удаляем хвост (движение без роста)
            self.snake.pop()
    
    def run(self):
        """Основной игровой цикл"""
        print("Запуск игры 'Змейка'...")
        print("Управление: Стрелки или WASD, Q - выход")
        time.sleep(1)
        
        # Запуск потока для обработки ввода
        input_thread = threading.Thread(target=self._process_input, daemon=True)
        input_thread.start()
        
        try:
            while self.running and not self.game_over:
                self._update()
                self._draw()
                time.sleep(self.speed)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
        
        # Финальная отрисовка
        self._draw()
        
        if self.game_over:
            print("\n*** ИГРА ОКОНЧЕНА! ***")
            print(f"Ваш счет: {self.score}")
            print("Нажмите Enter для выхода...")
            input()


def main():
    # Создание и запуск игры
    game = SnakeGame(width=30, height=20, speed=0.15)
    game.run()


if __name__ == '__main__':
    main()
