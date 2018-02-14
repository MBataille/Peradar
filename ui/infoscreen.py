# -*- coding: utf-8 -*-
from lib import Control
from kivy.app import App
from kivy.logger import Logger as log
from kivy.properties import StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, SlideTransition
from unidecode import unidecode

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
        self.ramo_name = self.unparsed_ramo_name.split(' ')[0]
        # n = unidecode(name).split(' ')  # quito el codigo del ramo y le saco tildes
        # self.ramo_name = ' '.join(n[i] for i in range(1, len(n)))  # para evitar errores

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
