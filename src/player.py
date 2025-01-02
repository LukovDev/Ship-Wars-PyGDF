#
# player.py
#


# Импортируем:
from gdf.graphics import *
from gdf.input import *
from gdf.math import *


# Игрок:
class Player:
    def __init__(self, position: vec2, sprite: Sprite2D, boom: Sprite2D) -> None:
        self.position = position
        self.sprite = sprite
        self.rendering = True
        self.size = vec2(48, 48)
        self.speed = 4

        self.bullet_per_sec = 8    # 8 патронов в секунду.
        self.bullet_timeout = 0.0  # Время ожидания для создания новой пули.

        self.heal         = 1    # Насколько очков лечить игрока.
        self.heal_per_sec = 0.1  # Сколько раз лечить в секунду.
        self.heal_timeout = 0.0  # Время ожидания нового лечения.

        self.max_hp = 100
        self.hp = 100
        self.kills = 0
        self.miss = 0
        self.death = False

        self.explode = ParticleEffect2D(
            texture       = [boom],
            position      = self.position,
            direction     = vec2(0, 0),
            start_size    = vec2(32, 32),
            end_size      = vec2(0, 0),
            speed         = vec2(100, 500),
            damping       = 0.05,
            duration      = vec2(0.1, 1),
            count         = 24,
            gravity       = vec2(0, 0),
            start_angle   = random.uniform(-360.0, +360.0),
            end_angle     = random.uniform(-360.0, +360.0),
            is_infinite   = False,
            is_local_pos  = False,
            is_dir_angle  = False,
            custom_update = None
        )

    # Добавить новое убийство в счётчик:
    def new_kill(self) -> None:
        self.kills += 1

    # Обновление игрока:
    def update(self, delta_time: float, input_hander: InputHandler, bullet_spawn, shoot_sound, boom_sound) -> None:
        if self.hp <= 0:
            self.hp = 0
            self.explode.position.xy = self.position.xy
            if self.rendering:
                boom_sound()
                self.explode.create()
                self.death = True
            self.explode.update(delta_time)
            self.rendering = False
            return

        # Лечим игрока:
        if self.heal_timeout <= 0:
            self.hp += self.heal
            self.heal_timeout = self.heal_per_sec
        self.heal_timeout -= 1/60 * (delta_time*60)

        # Ограничиваем хп:
        self.hp = clamp(self.hp, 0, self.max_hp)

        # Передвигаем игрока влево:
        if input_hander.get_key_pressed()[Key.K_a]:
            self.position.x -= self.speed * 100 * delta_time

        # Передвигаем игрока вправо:
        if input_hander.get_key_pressed()[Key.K_d]:
            self.position.x += self.speed * 100 * delta_time

        # Передвигаем игрока вперёд:
        if input_hander.get_key_pressed()[Key.K_w]:
            self.position.y += self.speed * 100 * delta_time

        # Передвигаем игрока назад:
        if input_hander.get_key_pressed()[Key.K_s]:
            self.position.y -= self.speed * 100 * delta_time

        # Выпускаем пулю нажатием на пробел:
        if input_hander.get_key_pressed()[Key.K_SPACE] or input_hander.get_mouse_pressed()[0]:
            if self.bullet_timeout <= 0:
                bullet_spawn(self.position.xy+vec2(0, 24), +1, "bullet-1", True)
                shoot_sound()
                self.bullet_timeout = 1/self.bullet_per_sec
        self.bullet_timeout -= delta_time

        # Ограничиваем координаты игрока по горизонтали:
        self.position.x = clamp(self.position.x, -250, +250)

        # Ограничиваем координаты игрока по вертикали:
        self.position.y = clamp(self.position.y, -350, +350)

    # Отрисовка игрока:
    def render(self, batch: SpriteBatch2D) -> None:
        if not self.rendering:
            self.explode.render()
        else:
            batch.draw(
                self.sprite,
                self.position.x - self.size.x / 2,
                self.position.y - self.size.y / 2,
                self.size.x, self.size.y
            )
