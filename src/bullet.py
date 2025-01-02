#
# bullet.py
#


# Импортируем:
from gdf.graphics import *
from gdf.math import *


# Класс пули:
class Bullet:
    def __init__(self, position: vec2, direction: float, sprite: Sprite2D, boom: Sprite2D, by_player) -> None:
        self.position = position
        self.direction = direction
        self.size = vec2(24, 24)
        self.speed = 8
        self.damage = 25
        self.sprite = sprite
        self.by_player = by_player

        self.particles = ParticleEffect2D(
            texture       = [boom],
            position      = position,
            direction     = vec2(0, 0),
            start_size    = vec2(4, 4),
            end_size      = vec2(0, 0),
            speed         = vec2(100, 200),
            damping       = 0.01,
            duration      = vec2(0.1, 1),
            count         = 16,
            gravity       = vec2(0, 0),
            start_angle   = 0.0,
            end_angle     = 0.0,
            is_infinite   = True,
            is_local_pos  = False,
            is_dir_angle  = False,
            custom_update = None
        ).create()

    # Обновление пули:
    def update(self, delta_time: float) -> None:
        self.position.y += self.direction * self.speed * 100 * delta_time
        self.particles.update(delta_time)

    # Отрисовка пули:
    def render(self, batch: SpriteBatch2D) -> None:
        self.particles.render()
        batch.draw(
            self.sprite,
            self.position.x - self.size.x / 2,
            self.position.y - self.size.y / 2,
            self.size.x, self.size.y, 0.0 if self.by_player else 180.0
        )
