from kivymd.uix.bottomsheet.bottomsheet import MDWidget
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen

from kivy import platform
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.image import Image

from random import randint


FPS = 60
SHIP_SPEED = dp(5)
BULLET_SPEED = dp(10)
ENEMY_SPEED = dp(3)
ENEMY_SPAWN_INTERVAL = 1

class MainScreen(MDScreen):
    pass

class GameScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_interval(self.update, 1/FPS)
        self.eventkeys = {}
        self.bullets = []
        self.paused = False
        self.enemies = []
        self.spawn_timer = 0

    def make_pause(self):
        self.paused = not self.paused   

    def update(self, dt):
        if self.paused:
            return
        for key in self.eventkeys:
            if self.eventkeys[key] == True:
                if key == "left":
                    self.moveLeft()
                if key == "right":
                    self.moveRight()
                if key == "shot":
                    self.shot()
                    self.eventkeys[key] = False
        for bullet in self.bullets:
            bullet.pos[1] += BULLET_SPEED

        self.spawn_timer += dt
        if self.spawn_timer >= ENEMY_SPAWN_INTERVAL:
            self.spawn_enemy()
            self.spawn_timer = 0

        for enemy in self.enemies:
            enemy.pos[1] -= ENEMY_SPEED

            for bullet in self.bullets[:]:
                if enemy.collide_widget(bullet):
                    self.enemies.remove(enemy)
                    self.ids.front.remove_widget(enemy)
                    self.bullets.remove(bullet)
                    self.ids.front.remove_widget(bullet)
                    break

            if enemy.pos[1] < 0:
                self.enemies.remove(enemy)
                self.ids.front.remove_widget(enemy)

    def pressKey(self, key):
        self.eventkeys[key] = True

    def releaseKey(self, key):
        self.eventkeys[key] = False

    def moveLeft(self):
        self.ids.ship.pos[0] -= SHIP_SPEED

    def moveRight(self):
        self.ids.ship.pos[0] += SHIP_SPEED
    
    def shot(self):
        shot = Shot(pos = (self.ids.ship.center_x, self.ids.ship.top))
        self.bullets.append(shot)
        self.ids.front.add_widget(shot)

class Shot(MDWidget):
    pass

class Enemy(Image):
    pass

class ShooterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"

        self.sm = MDScreenManager()

        self.sm.add_widget(MainScreen(name = "main"))
        self.sm.add_widget(GameScreen(name = "game"))

        return self.sm
    
if platform != "android" or platform != "ios":
    Window.size = (500, 600)

    Window.top = 100
    Window.left = 600

app = ShooterApp()
app.run()