# -*- coding: utf-8 -*-
import multiprocessing as mp
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger as log
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, SlideTransition


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
            is_logged = self.output.get()
            if not is_logged:
                log.info('Peradar: Login incorrecto')
                self.go_back()
                return
            else:
                self.manager.transition = SlideTransition(direction='left',
                                                          duration=0.2)
                self.manager.current = 'info'
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
