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
import json

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
        #Clock.schedule_interval(self.update, 1/FPS)
        self.eventkeys = {}
        self.bullets = []
        self.paused = False
        self.enemies = []
        self.spawn_timer = 0
        self.lives = 3
        self.score = 0

    def on_pre_enter(self):
        app = MDApp.get_running_app()
        self.ids.ship.source = app.current_skin
        self.update_ui()
        if not hasattr(self, "clock_event"):
            self.clock_event = Clock.schedule_interval(self.update, 1/FPS)
        self.paused = False
        self.restart_game()

    def on_pre_leave(self):
        if hasattr(self, "clock_event"):
            self.clock_event.cencel()
            del self.clock_event
        self.paused = True

    def update_ui(self):
        self.ids.lives_label.text = " ❤ " * self.lives
        self.ids.score_label.text = f"Збито: {self.score}"

    def game_over(self):
        self.paused = True
        self.ids.overlay.opacity = 1
        app = MDApp.get_running_app()
        self.ids.final_score.text = f"Збито ворогів: {self.score}"
        if self.score > app.high_score:
            app.high_score = self.score
            app.save_data()
        self.ids.final_high_score.text = f"Рекорд: {app.high_score}"

    def restart_game(self):
        self.lives = 3
        self.score = 0
        self.paused = False
        self.ids.overlay.opacity = 0
        self.spawn_timer = 0
        
        for b in self.bullets[:]:
            self.ids.front.remove_widget(b)
        self.bullets.clear()
        for e in self.enemies[:]:
            self.ids.front.remove_widget(e)
        self.enemies.clear()
        self.ids.ship.center_x = self.center_x
        self.update_ui()
    
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

        for bullet in self.bullets[:]:
            if bullet.pos[1] > self.height:
                self.bullets.remove(bullet)
                self.ids.front.remove_widget(bullet)
        
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
                    self.score += 1
                    self.update_ui()
                    break
            
            if enemy.pos[1] < 0:
                self.enemies.remove(enemy)
                self.ids.front.remove_widget(enemy)
            
            if enemy.colide_widget(self.ids.ship):
                damage = getattr(enemy, "damage", 1)
                self.lives -= damage
                self.update_ui()
                self.enemies.remove(enemy)
                self.ids.front.remove_widget(enemy)
                if self.lives <= 0:
                    self.game_over()

class SettingsScreen(MDScreen):
    pass

    def pressKey(self, key):
        self.eventkeys[key] = True

    def releaseKey(self, key):
        self.eventkeys[key] = False
    
    def moveLeft(self):
        new_x = self.ids.ship.pos[0] - SHIP_SPEED
        if new_x <0:
            new_x = 0   
        self.ids.ship.pos[0] = new_x
    
    def moveRight(self):
        new_x = self.ids.ship.pos[0] + SHIP_SPEED
        if new_x + self.ids.ship.width > self.width:
            new_x = self.width - self.ids.ship.width
        self.ids.ship.pos[0] = new_x 
    
    def shot(self):
        shot = Shot(pos = (self.ids.ship.center_x, self.ids.ship.top))
        self.bullets.append(shot)
        self.ids.front.add_widget(shot)
    
    def spawn_enemy(self):
        x = randint(0, int(self.width - dp(50)))
        enemy = Enemy(pos = (x, self.height))

        r = randint(1, 100)
        if r <= 70:
            enemy.source = "assets/images/enemy.png"
            enemy.damage = 1
        elif r <= 90:
            enemy.source = "assets/images/enemy.png"
            enemy.damage = 2
        else:
            enemy.source = "assets/images/enemy.png"
            enemy.damage = -1

        self.enemies.append(enemy)
        self.ids.front.add_widget(enemy)
    
    

                

class Shot(MDWidget):
    pass

class Enemy(Image):
    pass


class ShooterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark" # Light, Automatic
        self.theme_cls.primary_palette = "Orange"

        self.high_score = 0
        self.current_skin = "assets/images/rocket.png"

        try:
            with open("sett.json", "r") as file:
                data = json.load(file)
                self.high_score = data.get("high_score", 0)
                self.current_skin = data.get("current_skin", "assets/images/rocket.png")
        except Exception:
            self.save_data()

        self.sm = MDScreenManager()
        
        self.sm.add_widget(MainScreen(name = "main"))
        self.sm.add_widget(GameScreen(name = "game"))
        self.sm.add_widget(SettingsScreen(name = "sett"))

        return self.sm
    def seve_data(self):
        data = {
            "high_score": self.high_score,
            "current_skin": self.current_skin
        }
        with open("sett.json", "w") as file:
            json.dump(data, file)

    def set_skin(self, skin):
        self.current_skin = skin
        self.seve_data()

if platform != "android" or platform != "ios":
    Window.size = (500, 600)

    Window.top = 100
    Window.left = 600

app = ShooterApp()
app.run()
