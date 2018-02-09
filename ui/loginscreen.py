# -*- coding: utf-8 -*-
from kivy.logger import Logger as log
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, SlideTransition


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
