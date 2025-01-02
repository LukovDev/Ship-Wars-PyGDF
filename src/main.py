#
# main.py - Основной запускаемый файл программы.
#


# Импортируем:
import gdf
from gdf.graphics import *
from gdf.audio import *
from gdf.input import *
from gdf.math import *
from gdf import files

from player import Player
from bullet import Bullet
from enemy import Enemy


# Класс игры:
class GameClass(Window):
    def __init__(self) -> None:
        self.input   = None  # Обработчик ввода.
        self.camera  = None  # Игровая камера.
        self.player  = None  # Наш игрок.
        self.sprites = None  # Спрайты.
        self.sounds  = None  # Звуки.
        self.font    = None  # Шрифт.
        self.fontgen = None  # Генератор текстур текста.
        self.enemies = []    # Список врагов.
        self.bullets = []    # Список выпущенных патронов.
        self.batch   = None  # Пакетная отрисовка.

        self.restart_timecount = 3.0  # 3 секунды до перезагрузки.
        self.restart_timeout   = 0.0  # Отсчёт времени для перезагрузки.

        self.enemy_per_sec = 0.5    # 8 врагов в секунду.
        self.enemy_timeout = 0.0  # Время ожидания для создания нового врага.

        self.enemy_spawn = lambda p, n: self.enemies.append(Enemy(p, self.sprites[n], self.sprites["boom"]))
        self.bullet_spawn = lambda p, d, n, b: self.bullets.append(
            Bullet(p, d, self.sprites[n], self.sprites["boom"], b)
        )

        self.shoot_sound = lambda: self.sounds[random.choice(["shoot-1", "shoot-2"])].play()
        self.boom_sound  = lambda: self.sounds["boom"].play()

        # Создаём окно и переходим в игровой цикл:
        self.init()

    # Создать окно:
    def init(self) -> None:
        super().__init__(
            title      = "Ship Wars",
            icon       = files.load_image("./data/icons/runapp-icon.png"),
            size       = vec2(600, 800),
            vsync      = False,
            fps        = 60,
            visible    = True,
            titlebar   = True,
            resizable  = True,
            fullscreen = False,
            min_size   = vec2(0, 0),
            max_size   = vec2(float("inf"), float("inf")),
            samples    = 16
        )

    # Перезапуск игры:
    def restart(self) -> None:
        self.enemies.clear()
        self.bullets.clear()
        self.player = Player(vec2(0, -225), self.sprites["ship-1"], self.sprites["boom"])

    # Вызывается при создании окна:
    def start(self) -> None:
        # Наш обработчик ввода данных:
        self.input = InputHandler(self.window)

        # 2D камера:
        self.camera = Camera2D(
            width    = self.window.get_width(),
            height   = self.window.get_height(),
            position = vec2(0, 0),
            angle    = 0.0,
            zoom     = 1.0
        )

        # Шрифт:
        self.font = FontFile("./data/fonts/pixel-font.ttf").load()

        # Генератор шрифта:
        self.ui_font = {
            "hp": FontGenerator(self.font),
            "kills": FontGenerator(self.font),
            "miss": FontGenerator(self.font),
            "resp": FontGenerator(self.font),
        }

        # Пакетная отрисовка:
        self.batch = SpriteBatch2D()

        # Загрузка игровых данных:

        # Спрайты:
        self.sprites = {
            # Спрайты кораблей:
            "ship-1": Sprite2D(files.load_texture("./data/sprites/ship-1.png").set_pixelized()),
            "ship-2": Sprite2D(files.load_texture("./data/sprites/ship-2.png", True).set_pixelized()),
            "ship-3": Sprite2D(files.load_texture("./data/sprites/ship-3.png").set_pixelized()),
            "ship-4": Sprite2D(files.load_texture("./data/sprites/ship-4.png", True).set_pixelized()),

            # Спрайты пулей:
            "bullet-1": Sprite2D(files.load_texture("./data/sprites/bullet-1.png").set_pixelized()),
            "bullet-2": Sprite2D(files.load_texture("./data/sprites/bullet-2.png").set_pixelized()),

            # Спрайт взрыва:
            "boom": Sprite2D(files.load_texture("./data/sprites/boom.png").set_pixelized()),
        }

        # Звуки:
        self.sounds = {
            "laser-shoot": Sound("./data/sounds/laser-shoot.wav").load(),
            "shoot-1":     Sound("./data/sounds/shoot-1.wav").load(),
            "shoot-2":     Sound("./data/sounds/shoot-2.wav").load(),
            "boom":        Sound("./data/sounds/boom.wav").load(),
        }

        # Наш игрок:
        self.player = Player(vec2(0, -225), self.sprites["ship-1"], self.sprites["boom"])

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:

        # Обрабатываем перезапуск игры в случае смерти игрока:
        if self.player.death: self.restart_timeout += delta_time
        if self.restart_timeout >= self.restart_timecount:
            self.restart_timeout = 0.0
            self.restart()

        # Создание врага:
        if self.enemy_timeout <= 0:
            self.enemy_spawn(vec2(random.uniform(-250, +250), self.window.get_height()+64), "ship-2")
            self.enemy_timeout = 1/self.enemy_per_sec
        self.enemy_timeout -= delta_time

        # Обновление пуль:
        for b in list(self.bullets):
            b.update(delta_time)

            # Удалить пулю если та вылетела за пределы окна:
            sz = self.window.get_size().xy
            if not (-sz.x/2 <= b.position.x <= sz.x and -sz.y/2-64 <= b.position.y <= sz.y):
                if b in self.bullets: self.bullets.remove(b)

            # Проверка на попадание пули во врага:
            for enemy in list(self.enemies):
                r = max(abs(enemy.size.x), abs(enemy.size.y))/2
                if length(b.position.xy - enemy.position.xy) <= r and enemy.rendering and b.by_player:
                    if b.by_player: enemy.hp -= b.damage
                    if b in self.bullets: self.bullets.remove(b)

            # Проверка на попадание пули в игрока:
            r = max(abs(self.player.size.x), abs(self.player.size.y))/2
            if length(b.position.xy - self.player.position.xy) <= r and not b.by_player:
                self.player.hp -= b.damage
                if b in self.bullets: self.bullets.remove(b)

        # Обновление игрока:
        self.player.update(delta_time, self.input, self.bullet_spawn, self.shoot_sound, self.boom_sound)

        # Обновление врагов:
        for enemy in list(self.enemies):
            enemy.update(delta_time, self.bullet_spawn, self.shoot_sound, self.boom_sound, self.player.new_kill)

            sz = self.window.get_size().xy
            if not (-sz.x/2 <= enemy.position.x <= sz.x and -sz.y/2-64 <= enemy.position.y <= sz.y+64) or enemy.death:
                if not enemy.death: self.player.miss += 1
                if enemy in self.enemies: self.enemies.remove(enemy)

        # Обновляем камеру:
        self.camera.update()

    # Вызывается каждый кадр (игровая отрисовка):
    def render(self, delta_time: float) -> None:
        # Очищаем окно (значения цвета от 0 до 1):
        self.window.clear(6/255, 12/255, 24/255)

        self.batch.begin()
        # Отрисовка пули:
        for b in self.bullets:
            b.render(self.batch)

        # Отрисовка врагов:
        for enemy in self.enemies:
            enemy.render(self.batch)

        # Отрисовка игрока:
        self.player.render(self.batch)
        self.batch.end()

        # Отрисовываем пакет спрайтов:
        self.batch.render()

        # Запекаем шрифты:
        self.ui_font["hp"].bake_texture(f"HP: {self.player.hp}", 32, (1, 0, 0, 1), smooth = False)
        self.ui_font["kills"].bake_texture(f"Kills: {self.player.kills}", 24, (1, 0, 0, 1), smooth = False)
        self.ui_font["miss"].bake_texture(f"Misses: {self.player.miss}", 24, (1, 0, 0, 1), smooth = False)
        self.ui_font["resp"].bake_texture(
            f"Respawning  in  {int(self.restart_timecount-self.restart_timeout+1)}",
            24, (1, 1, 1, 1), smooth = False
        )

        # Рисуем интерфейс:
        self.camera.ui_begin()
        size = self.window.get_size()
        Sprite2D(self.ui_font["kills"].get_texture()).render(32, 110)
        Sprite2D(self.ui_font["miss"].get_texture()).render(32, 75)
        Sprite2D(self.ui_font["hp"].get_texture()).render(32, 32)

        if self.player.death:
            Sprite2D().render(0, 0, size.x, size.y, color=(0.0, 0.0, 0.0, 0.4))
            death_text_sz = vec2(self.ui_font["resp"].get_width(), self.ui_font["resp"].get_height())
            Sprite2D(self.ui_font["resp"].get_texture()).render(size.x/2-death_text_sz.x/2, size.y/2-death_text_sz.y/2)
        self.camera.ui_end()

        # Отрисовываем всё в окно:
        self.window.display()

    # Вызывается при изменении размера окна:
    def resize(self, width: int, height: int) -> None:
        self.camera.resize(width, height)  # Обновляем размер камеры.

    # Вызывается при разворачивании окна:
    def show(self) -> None:
        pass

    # Вызывается при сворачивании окна:
    def hide(self) -> None:
        pass

    # Вызывается при закрытии окна:
    def destroy(self) -> None:
        pass


# Если этот скрипт запускают:
if __name__ == "__main__":
    print(gdf.get_version())

    # Создаём игровой класс:
    game = GameClass()
