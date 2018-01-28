# -*- coding: utf-8 -*-

import kivy
kivy.require('1.10.1')

from kivy.animation import Animation
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.logger import Logger as log
from kivy.clock import Clock
from kivy.vector import Vector
from lib import ReclamoScraper
from math import radians, cos, sin, exp
from pathos.helpers import mp
from unidecode import unidecode
"""
Estructura:
LoginScreen -> LoadScreen -> InfoScreen -> SearchScreen

LoginScreen:
    Formulario para ingresar a reclamos.
    Luego de completar el formulario, pasa inmediatamente a loadscreen

LoadScreen:
    Trata de ingresar a reclamos con los datos del usuario.
    Si ingresa a reclamos, pasa a infoscreen, de lo contrario
    vuelve a loginscreen

InfoScreen:
    Muestra los ramos y controles que encuentra en reclamos
    Selecciona controles y pasa a searchscreen
    Puede volver a loginscreen para cambiar de usuario

Searchscreen:
    Busca las notas del o los controles seleccionados.
    A penas esta disponible la nota de un control la muestra
"""

class InfoScreen(Screen):
    def setInfo(self):
        """"
        setInfo: None -> None
        Busca los ramos y controles en reclamos y luego los carga en InfoScreen
        """
        log.info('Peradar: Setting info')
        app = App.get_running_app()
        ramos = app.scrape.getInfo() # ramos es un Ramo (clase Ramo en lib)
        self.ids.listaRamos_layout.createRamos(ramos)

class ListaRamosLayout(BoxLayout):
    """Layout donde van varios RamoLayout"""
    def createRamos(self, ramos):
        """Dada una lista de ramos (de la clase Ramo) crea los RamoLayout y ControlesLayout"""
        for ramo in ramos:
            log.debug('Peradar: Creando %s', ramo.name)
            ramo_layout = RamoLayout()
            ramo_layout.setName(ramo.name) 
            ramo_layout.createControles(ramo.getControles())
            log.debug('Peradar: Adding widget (almost done)')
            self.add_widget(ramo_layout)
class RamoLayout(BoxLayout):
    """Layout donde va un Label y un ControlesLayout"""
    ramo_name = StringProperty('')

    def setName(self, name):
        """Settea el nombre del ramo que luego se muestra en pantalla"""
        n = unidecode(name).split(' ') # quito el codigo del ramo y le saco tildes para evitar
        self.ramo_name = ' '.join(n[i] for i in range(1, len(n))) # errores
    def createControles(self, controles):
        """Crea los controles de este ramo dado una lista de controles"""
        self.ids.controles_layout.createControles(controles)

class ControlesLayout(BoxLayout):
    """Layout donde va un Label y un boton por control"""
    active_btn = ObjectProperty(None)
    normal_color = ListProperty([1, 1, 1, .3])
    pressed_color = ListProperty([1, 1, 1, .7])

    def btn_pressed(self, instance, value):
        if not self.active_btn is None:
            self.active_btn.background_color = self.normal_color
        instance.background_color = self.pressed_color
        self.active_btn = instance

    def createControles(self, controles):
        """Crea un boton por control"""
        for control in controles:
            control_btn = Button(text = control, background_normal = '', background_down = '',
                background_color = self.normal_color)
            control_btn.bind(state = self.btn_pressed)
            self.add_widget(control_btn)

class LoadBall(Widget):
    """Pelota de la animacion de cargando"""
    angle = NumericProperty(0)
    radius = NumericProperty(0)
    def move(self):
        """Descripcion del movimiento de la pelota"""  
        if self.angle >= 450: self.angle = 90
        self.angle += 10*exp(-(self.angle/100-2.7)**2) + 1
        self.pos = Vector(self.radius*cos(radians(self.angle)), 
            self.radius*sin(radians(self.angle))) + self.parent.center


class LoadScreen(Screen):
    ball = ObjectProperty(None)
    username = StringProperty(None)
    password = StringProperty(None)
    output = ObjectProperty(None)
    wait_login_schedule = ObjectProperty(None)
    update_schedule = ObjectProperty(None)

    def on_enter(self):
        log.info('Peradar: Procesando login')
        app = App.get_running_app()

        self.output = mp.Queue() # sirve de intermediario entre procesos

        # creo el proceso
        getLogin = mp.Process(target = app.scrape.logIn,
            args = (self.username,self.password), kwargs = {'queue' : self.output})
        getLogin.daemon = True
        getLogin.start() # lo lanzo
        log.info('Peradar: Proceso login creado!')
        self.wait_login_schedule = Clock.schedule_interval(self.wait_login, 1.0/30)

    def on_pre_enter(self): # para la animacion de la pelota
        self.update_schedule = Clock.schedule_interval(self.update, 1.0/60)
      

    def on_leave(self): # al cambiar de ventana, cancela la animacion y la espera de info
        self.wait_login_schedule.cancel()
        self.update_schedule.cancel()

    def wait_login(self, dt): # espera respuesta del proceso
        if not self.output.empty():
            out = self.output.get()
            if not out[0]:
                log.info('Peradar: Login incorrecto')
                self.go_back()
                return
            else:
                self.manager.transition = SlideTransition(direction = 'left', duration = 0.2)
                self.manager.current = 'info'
                App.get_running_app().scrape.setBrowser(out[1],out[2])
                self.manager.get_screen('info').setInfo()            

    def go_back(self):
        log.info('Peradar: Going back...')
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

        load.save_login(loginText, passwordText) # guarda la informacion


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
        sm.add_widget(InfoScreen(name = 'info'))
        return sm

if __name__ == '__main__':
    LoginApp().run()