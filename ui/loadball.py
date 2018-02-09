# -*- coding: utf-8 -*-
from math import radians, cos, sin, exp
from kivy.vector import Vector
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget


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
