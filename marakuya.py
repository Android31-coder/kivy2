from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen

from kivy import platform
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp, sp

FPS = 60
SHIP_SPEED = dp(5)

class MainScreen(MDScreen):
    pass

class GameScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_interval(self.update, 1/FPS)
        self.eventkeys = {}
    def update(self, dt):
        for key in self.eventkeys:
            if self.eventkeys[key] == True:
                if key == "left":
                    self.moveLeft()
                if key == "right":
                    self.moveRight()

    def pressKey(self, key):
        self.eventkeys[key] = True

    def releaseKey(self, key):
        self.eventkeys[key] = False

    def moveLeft(self):
        self.ids.ship.pos[0] -= SHIP_SPEED

    def moveRight(self):
        self.ids.ship.pos[0] += SHIP_SPEED

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