# -*- coding: utf-8 -*-
import multiprocessing as mp
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger as log
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty,\
    BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen  # , SlideTransition
from loadball import LoadBall


class NotasWidget(Widget):
    notas = ListProperty([])
    control = ObjectProperty(None)
    # control_name = StringProperty("")
    resultado = StringProperty("")


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
    schedules = ObjectProperty(dict())
    layouts = ObjectProperty(dict())
    queue = ObjectProperty(mp.Queue())
    cota = NumericProperty(55)

    def on_leave(self):
        for schedule in self.schedules:  # mata todo
            schedule.cancel()

    def _resultado(self, notas):
        mean = sum(notas) * 1.0 / len(notas)
        return True if mean >= self.cota else False

    def gotNotas(self, control, notas):
        layout = self.layouts[control.id]  # LoadFloatLayout donde va el buscando
        self.schedules[control.id].cancel()
        layout.clear_widgets()
        layout.add_widget(NotasWidget(notas=notas, control=control, 
                                      resultado=str(self._resultado(notas))))

    def waitNotas(self, dt):
        if not self.queue.empty():
            out = self.queue.get()
            log.info('Lib: Got notas del ramo %s, %s', out[0], out[1])
            self.gotNotas(out[0], out[1])

    def setPeradar(self, p):
        """ Args: p (lista de controles de la clase Control)"""
        self.peradar = p

        for i in range(len(self.peradar)):
            c = self.peradar[i]
            float_layout = LoadFloatLayout(size_hint=(1.0 / len(self.peradar), 1))
            float_layout.label_text += c.name + '\n' + c.ramo
            c.setId(i)
            log.debug('Offlib: Got control: %s, %s', c.name, c.ramo)
            self.box_layout.add_widget(float_layout)
            self.layouts[c.id] = float_layout

            ev = Clock.schedule_interval(float_layout.findBall().move,
                                         1.0 / 60)
            self.schedules[c.id] = ev
            log.debug('OffLib: Creating schedule of %s\'s ball: %s',\
                      c, float_layout.findBall())

        app = App.get_running_app()
        get_nota = mp.Process(target=app.scrape.searchNotas,
                              args=(p, self.queue, app.username, app.password))
        get_nota.daemon = True

        get_nota.start()

        ev = Clock.schedule_interval(self.waitNotas, 1)

        self.schedules['waitNotas'] = ev
