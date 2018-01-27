import kivy
kivy.require('1.0.7')

from kivy.animation import Animation
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.logger import Logger as log
from kivy.clock import Clock
from kivy.vector import Vector
from lib import ReclamoScraper
from math import radians, cos, sin, exp
import multiprocessing as mp

class LoadBall(Widget):
    angle = NumericProperty(0)
    radius = NumericProperty(0)
    def move(self):  
        if self.angle >= 450: self.angle = 90
        self.angle += 10*exp(-(self.angle/100-2.7)**2) + 1
        self.pos = Vector(self.radius*cos(radians(self.angle)), 
            self.radius*sin(radians(self.angle))) + self.parent.center


class LoadScreen(Screen):
    ball = ObjectProperty(None)
    username = StringProperty(None)
    password = StringProperty(None)
    output = ObjectProperty(None)

    def on_enter(self):
        log.info('Peradar: Procesando login')
        app = App.get_running_app()
        self.output = mp.Queue()
        getLogin = mp.Process(target = app.scrape.logIn,
            args = (self.username,self.password), kwargs = {'queue' : self.output})
        getLogin.daemon = True
        getLogin.start()
        log.info('Peradar: Proceso login creado!')
        Clock.schedule_interval(self.wait_login, 1.0/30)

    def wait_login(self, dt):
        if not self.output.empty():
            if self.output.get():
                log.info('Peradar: Login correcto...')
                ##### hartas cosas #####
                return
            # login incorrecto
            log.info('Peradar: Login incorrecto')
            self.manager.transition = SlideTransition(direction= 'right', duration = 0.2)
            self.manager.current = 'login'
            login_scr = self.manager.get_screen('login')
            login_scr.showWarning()
            login_scr.resetForm()        
    def save_login(self, username, password):
        self.username = username
        self.password = password

    def update(self, dt):
        self.ball.move()

class LoginScreen(Screen):
    login_info_text = StringProperty('Ingresa tu usuario y pass de U-Pasaporte')

    def changeScreen(self, loginText, passwordText):
        log.info('Peradar: Cambiado a load')

        self.manager.transition = SlideTransition(direction="left", duration = 0.2)
        self.manager.current = 'load'

        load = self.manager.get_screen('load')
        Clock.schedule_interval(load.update, 1.0/60)

        load.save_login(loginText, passwordText)


    def showWarning(self):
        log.info('Peradar: Mostrando warning')
        self.login_info_text = 'Usuario o pass incorrectos, por favor intenta nuevamente'

    def resetForm(self):
        log.info('Peradar: Reseteando Form')
        self.ids['login'].text = ""
        self.ids['password'].text = ""


class LoginApp(App):

    scrape = ObjectProperty(None)

    def build(self):
        self.scrape = ReclamoScraper()
        sm = ScreenManager();
        sm.add_widget(LoginScreen(name = 'login'))
        sm.add_widget(LoadScreen(name = 'load'))
        return sm

if __name__ == '__main__':
    LoginApp().run()