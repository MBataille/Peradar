# -*- coding: utf-8 -*-
from lib import ReclamoScraper, Control
from math import radians, cos, sin, exp
import multiprocessing as mp
import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.logger import Logger as log
from kivy.vector import Vector
from kivy.properties import StringProperty, ObjectProperty, NumericProperty,\
    ListProperty, BooleanProperty
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.widget import Widget
from unidecode import unidecode

kivy.require('1.10.1')
Config.set('kivy', 'log_level', 'debug')
Config.write()

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


class LoadBall(Widget):
    """Pelota de la animacion de cargando"""
    angle = NumericProperty(0)
    radius = NumericProperty(0)

    def move(self, *args):
        """Descripcion del movimiento de la pelota"""
        # log.info('Peradar: I am %s', self)
        if self.angle >= 450:
            self.angle = 90
        self.angle += 10 * exp(-(self.angle / 100 - 2.7)**2) + 1
        self.pos = Vector(self.radius * cos(radians(self.angle)),
                          self.radius * sin(radians(self.angle)))\
            + self.parent.center

    def reset(self):
        self.angle = 90


class LoadFloatLayout(FloatLayout):
    def findBall(self):
        t = type(LoadBall())
        for child in self.children:
            if t == type(child):
                return child
        log.error('Peradar: No se encontro LoadBall. Children: %s',
                  self.children)
        raise Exception('LoadBall not found')


class SearchScreen(Screen):
    peradar = ListProperty([])
    box_layout = ObjectProperty(None)
    schedules = ListProperty([])
    # layouts = ListProperty([])
    queue = ObjectProperty(mp.Queue())

    def on_pre_enter(self):
        for load_float_layout in self.box_layout.children:
            load_ball = load_float_layout.findBall()
            log.info('Peradar: Updating LoadBall: %s ', load_ball)
            ev = Clock.schedule_interval(load_float_layout.findBall().move,
                                         1.0 / 60)
            self.schedules.append(ev)

    def on_leave(self):
        for schedule in self.schedules:
            schedule.cancel()

    def waitNotas(self, dt):
        if not self.queue.empty():
            out = self.queue.get()
            log.info('Lib: Got notas del ramo %s, %s', out[0], out[1])

    def setPeradar(self, p):
        """ Args: p (lista de controles de la clase Control)"""
        self.peradar = p
        app = App.get_running_app()
        get_nota = mp.Process(target=app.scrape.searchNotas,
                              args=(p, self.queue, app.username, app.password))
        get_nota.daemon = True
        get_nota.start()

        for c in self.peradar:
            float_layout = LoadFloatLayout(size_hint=(1.0 / len(self.peradar), 1))
            float_layout.label_text += c.name + '\n' + c.ramo
            self.box_layout.add_widget(float_layout)
        ev = Clock.schedule_interval(self.waitNotas, 1)
        self.schedules.append(ev)


class InfoScreen(Screen):
    info = ObjectProperty(None)
    infoText = StringProperty("Selecciona el o los controles que quieras poner en el peradar")

    def setInfo(self):
        """"
        setInfo: None -> None
        Busca los ramos y controles en reclamos y luego los carga en InfoScreen
        """
        log.info('Peradar: Setting info')
        app = App.get_running_app()
        self.info = app.scrape.getInfo()  # info es una lista de Ramos
        self.ids.listaRamos_layout.createRamos(self.info)

    def resetInfo(self):
        """ borra la info """
        self.ids.listaRamos_layout.clear_widgets()

    def go_back(self):
        log.info('Peradar: Going back to login from info...')
        self.manager.transition = SlideTransition(direction='right',
                                                  duration=0.2)
        self.manager.current = 'login'
        self.resetInfo()
        login_scr = self.manager.get_screen('login')
        login_scr.resetForm()

    def go_forward(self):
        """Avanza a la siguiente pantalla, verifica que hayan controles seleccionados
        y los envia a la pantalla siguiente"""
        controles = self.ids.listaRamos_layout.getSelectedControles()
        if len(controles) == 0:
            log.warning('No se han seleccionado controles')
            self.infoText = 'No se han seleccionado controles! Selecciona al\
             menos un control para continuar'
            # seba, eventualmente pon lo de arriba en rojo, gracias :D
        self.manager.get_screen('search').setPeradar(controles)
        self.manager.transition = SlideTransition(direction='left',
                                                  duration=0.2)
        self.manager.current = 'search'

    def findRamo(self, name):
        """Busca un ramo dado su nombre, retorna none si no encuentra"""
        for ramo in self.info:
            if ramo.name == name:
                return ramo
        return None


class ListaRamosLayout(BoxLayout):
    """Layout para mostrar info de varios ramos (cada uno en un RamoLayout)"""
    def createRamos(self, ramos):
        """Dada una lista de ramos de la clase Ramos
        crea los RamoLayout y ControlesLayout"""
        for ramo in ramos:
            log.debug('Peradar: Creando %s', ramo.name)
            ramo_layout = RamoLayout()
            ramo_layout.setName(ramo.name)
            ramo_layout.createControles(ramo.getControles())
            self.add_widget(ramo_layout)

    def getSelectedControles(self):
        """Devuelve una lista de controles de la clase Control
        que fueron seleccionados por el usuario"""
        selected_controles = []
        for child in self.children:  # child = RamoLayout
            c_name = child.getActiveBtnName()
            if c_name is not None:
                r_name = child.unparsed_ramo_name
                r = self.parent.parent.findRamo(child.unparsed_ramo_name)
                if r is None:
                    log.error('Peradar: Ramo en RamoLayout no esta en Info')
                    raise Exception('Inconsistencia: RamoLayout no coincide con Info')
                c_url = r.findControlUrl(c_name)
                if c_url is None:
                    log.error('Peradar: Control %s, Nombre Ramo %s, Ramo %s',
                              c_name, r_name, r)
                    raise Exception('Selected control not found')
                selected_controles.append(Control(c_name, c_url, child.ramo_name))
        return selected_controles


class RamoLayout(BoxLayout):
    """Layout para mostar info de un ramo: descripcion (Label)
     y controles (ControlesLayout)"""
    ramo_name = StringProperty('')
    unparsed_ramo_name = StringProperty('')

    def setName(self, name):
        """Settea el nombre del ramo que luego se muestra en pantalla"""
        self.unparsed_ramo_name = name
        n = unidecode(name).split(' ')  # quito el codigo del ramo y le saco tildes
        self.ramo_name = ' '.join(n[i] for i in range(1, len(n)))  # para evitar errores

    def createControles(self, controles):
        """Crea los controles de este ramo dado una lista de controles"""
        self.ids.controles_layout.createControles(controles)

    def getActiveBtnName(self):
        """Devuelve el nombre del boton activo o None si es que no hay boton activo"""
        active_btn = self.ids.controles_layout.active_btn
        is_active = self.ids.controles_layout.is_active
        if is_active:
            return active_btn.text
        return None


class ControlesLayout(BoxLayout):
    """Layout que muestra una lista de controles (cada uno como boton)"""
    active_btn = ObjectProperty(None)
    is_active = BooleanProperty(False)
    normal_color = ListProperty([1, 1, 1, .3])
    pressed_color = ListProperty([1, 1, 1, .7])

    def btn_pressed(self, instance):
        """Mantiene el rastro del boton presionado"""
        if self.is_active:
            self.active_btn.background_color = self.normal_color  # active_btn deja de estar activo
            self.is_active = False
            if self.active_btn == instance:
                return
        instance.background_color = self.pressed_color
        self.active_btn = instance
        self.is_active = True

    def createControles(self, controles):
        """Dado una lista de controles de la clase Control, hace un boton por control"""
        for control in controles:
            control_btn = Button(text=control.name, background_normal='',
                                 background_down='',
                                 background_color=self.normal_color)
            control_btn.bind(on_press=self.btn_pressed)
            self.add_widget(control_btn)


class LoadScreen(Screen):
    """Pantalla de carga, acá se procesa el login"""
    ball = ObjectProperty(None)
    output = ObjectProperty(None)
    wait_login_schedule = ObjectProperty(None)
    update_schedule = ObjectProperty(None)

    def on_enter(self):
        log.info('Peradar: Procesando login')
        app = App.get_running_app()

        self.output = mp.Queue()  # sirve de intermediario entre procesos

        # creo el proceso
        getLogin = mp.Process(target=app.scrape.logIn,
                              args=(app.username, app.password),
                              kwargs={'queue': self.output})
        getLogin.daemon = True
        getLogin.start()  # lo lanzo
        log.info('Peradar: Proceso login creado!')
        self.wait_login_schedule = Clock.schedule_interval(self.wait_login,
                                                           1.0 / 30)

    def on_pre_enter(self):  # para la animacion de la pelota
        self.update_schedule = Clock.schedule_interval(self.update, 1.0 / 60)

    def on_leave(self):  # al cambiar de ventana, cancela la animacion y espera la info
        self.wait_login_schedule.cancel()
        self.update_schedule.cancel()
        self.ball.reset()

    def wait_login(self, dt):  # espera respuesta del proceso
        if not self.output.empty():
            out = self.output.get()
            if not out[0]:
                log.info('Peradar: Login incorrecto')
                self.go_back()
                return
            else:
                self.manager.transition = SlideTransition(direction='left',
                                                          duration=0.2)
                self.manager.current = 'info'
                App.get_running_app().scrape.setBeautifulSoup(out[1])
                self.manager.get_screen('info').setInfo()

    def go_back(self):
        log.info('Peradar: Going back...')
        self.manager.transition = SlideTransition(direction='right', duration=0.2)
        self.manager.current = 'login'
        login_scr = self.manager.get_screen('login')
        login_scr.showWarning()
        login_scr.resetForm()

    def save_login(self, username, password):
        app = App.get_running_app()
        app.username = username
        app.password = password

    def update(self, dt):
        self.ball.move()


class LoginScreen(Screen):
    login_info_text = StringProperty('Ingresa tu usuario y pass de U-Pasaporte')

    def __init__(self, *args, **kwargs):
        super(LoginScreen, self).__init__(*args, **kwargs)
        self.login_info_text = 'Ingresa tu usuario y pass de U-Pasaporte'
        self.ids.password.bind(on_text_validate=self.changeScreen)

    def changeScreen(self, *args):
        log.info('Peradar: Cambiado a load')

        self.manager.transition = SlideTransition(direction="left", duration=0.2)
        self.manager.current = 'load'

        load = self.manager.get_screen('load')
        load.save_login(self.ids.login.text, self.ids.password.text)  # guarda la informacion

    def showWarning(self):
        log.info('Peradar: Mostrando warning')
        self.login_info_text = 'Usuario o pass incorrectos, por favor intenta nuevamente'

    def resetForm(self):
        log.info('Peradar: Reseteando Form')
        self.ids['login'].text = ""
        self.ids['password'].text = ""


class LoginApp(App):

    scrape = ObjectProperty(None)
    username = StringProperty(None)
    password = StringProperty(None)

    def build(self):
        self.scrape = ReclamoScraper()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(LoadScreen(name='load'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(SearchScreen(name='search'))
        return sm


if __name__ == '__main__':
    LoginApp().run()
