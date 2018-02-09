# -*- coding: utf-8 -*-
import multiprocessing as mp
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger as log
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen  # , SlideTransition
from loadball import LoadBall


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
