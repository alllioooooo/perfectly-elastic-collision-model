import sys
import pygame
import sympy as sp

m1, m2, v1i, v2i, v1f, v2f = sp.symbols('m_1, m_2, v_1i, v_2i, v_1f, v_2f')
half = sp.numer(1) / 2

# Уравнение сохранения импульса
momentum_eq = sp.Eq(
    m1 * v1i + m2 * v2i,
    m1 * v1f + m2 * v2f
)
# Уравнение сохранения кинетической энергии
energy_eq = sp.Eq(
    half * m1 * v1i ** 2 + half * m2 * v2i ** 2,
    half * m1 * v1f ** 2 + half * m2 * v2f ** 2
)
# Решение системы уравнений относительно v1f и v2f
solutions = sp.solve([momentum_eq, energy_eq], [v1f, v2f])

# Отбор решений, которые соответствуют физическим условиям (скорости должны измениться после столкновения)
solutions = [s for s in solutions if s != (v1i, v2i)][0]
v1f_solved, v2f_solved = [sp.simplify(s) for s in solutions]

# Лямбда-функции для вычисления скоростей после столкновения на основе полученных решений
v1f_f = sp.lambdify([m1, m2, v1i, v2i], v1f_solved)
v2f_f = sp.lambdify([m1, m2, v1i, v2i], v2f_solved)

# Инициализация pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Блоки")

# Цвета
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# Класс блока
class Block:
    def __init__(self, x, y, mass, velocity, color):
        self.mass = mass
        self.velocity = velocity
        self.color = color
        self.size = int(40 * (mass / 10) ** (1 / 3))
        self.rect = pygame.Rect(x, y - self.size, self.size, self.size)

    def move(self):
        self.rect.x += self.velocity

    def collide_with_wall(self):
        if self.rect.x <= 0:
            self.rect.x = 0  # Коррекция положения, чтобы блок не уходил за пределы экрана
            self.velocity = -self.velocity  # Изменение направления движения
            return True
        return False

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.SysFont(None, 25)
        mass_text = font.render(str(self.mass), True, BLACK)
        screen.blit(mass_text, (self.rect.x + self.size // 2 - mass_text.get_width() // 2,
                                self.rect.y + self.size // 2 - mass_text.get_height() // 2))


def calculate_collision_velocity(b1, b2):
    m1, m2, v1i, v2i = b1.mass, b2.mass, b1.velocity, b2.velocity
    v1f = v1f_f(m1, m2, v1i, v2i)
    v2f = v2f_f(m1, m2, v1i, v2i)
    return v1f, v2f


# Создание блоков
block1 = Block(200, HEIGHT, 1, 0, YELLOW)
block2 = Block(500, HEIGHT, 100, -2, RED)

collision_count = 0

# Главный цикл
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    block1.move()
    block2.move()

    if block1.rect.colliderect(block2.rect):
        v1_final, v2_final = calculate_collision_velocity(block1, block2)
        block1.velocity = v1_final
        block2.velocity = v2_final

        # Минимальное смещение, чтобы избежать зацикливания столкновений
        while block1.rect.colliderect(block2.rect):
            block1.rect.x += block1.velocity
            block2.rect.x += block2.velocity

        collision_count += 1

    if block1.collide_with_wall():
        block1.velocity = abs(block1.velocity)
        collision_count += 1

    block1.draw()
    block2.draw()

    # Отображаем количество столкновений
    font = pygame.font.SysFont(None, 35)
    collision_text = font.render(f"Collisions: {collision_count}", True, WHITE)
    screen.blit(collision_text, (WIDTH // 2 - collision_text.get_width() // 2, 10))

    pygame.display.flip()
    pygame.time.Clock().tick(100)

pygame.quit()
sys.exit()
