# -*- coding: utf-8 -*-
from lib import ReclamoScraper
import kivy
from kivy.app import App
from kivy.config import Config
from kivy.logger import Logger as log
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from loginscreen import LoginScreen
from loadscreen import LoadScreen
from infoscreen import InfoScreen
from searchscreen import SearchScreen

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

class LoginApp(App):

    scrape = ObjectProperty(None)
    username = StringProperty(None)
    password = StringProperty(None)

    def build(self):
        log.info('Peradar: Launching Peradar!')
        self.scrape = ReclamoScraper()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(LoadScreen(name='load'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(SearchScreen(name='search'))
        return sm


if __name__ == '__main__':
    LoginApp().run()
