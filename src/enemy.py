#
# enemy.py
#


# Импортируем:
import time
from gdf.graphics import *
from gdf.math import *


# Класс врага:
class Enemy:
    def __init__(self, position: vec2, sprite: Sprite2D, boom: Sprite2D) -> None:
        self.position = position
        self.sprite = sprite
        self.rendering = True
        self.size = vec2(48, 48)
        self.speed = 2
        self.offset_strength = 2
        self.offset_speed = 2
        self.bullet_per_sec = 1    # 8 патронов в секунду.
        self.bullet_timeout = random.uniform(0, 1)  # Время ожидания для создания новой пули.
        self.hp = 100
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

    # Обновление игрока:
    def update(self, delta_time: float, bullet_spawn, shoot_sound, boom_sound, new_kill) -> None:
        self.hp = clamp(self.hp, 0, 100)
        if self.hp <= 0:
            self.explode.position.xy = self.position.xy
            if self.rendering:
                boom_sound()
                self.explode.create()
                new_kill()
            self.explode.update(delta_time)
            if len(self.explode.particles) <= 0: self.death = True
            self.rendering = False
            return

        self.position.x += sin(time.time()*self.offset_speed)*self.offset_strength

        self.position.y -= self.speed * 100 * delta_time

        if self.bullet_timeout <= 0:
            bullet_spawn(self.position.xy+vec2(0, -24), -1, "bullet-1", False)
            shoot_sound()
            self.bullet_timeout = 1/self.bullet_per_sec
        self.bullet_timeout -= delta_time

        # Ограничиваем координаты игрока по горизонтали:
        self.position.x = clamp(self.position.x, -250, +250)

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
