# -*- coding: utf-8 -*-
from lib import Ramo
from kivy.logger import Logger as log
import time

filename = 'offlib.ini'
separators = [';', ':', ',']

def _parse_ini(val, i=0):
	if i >= len(separators):
		return val
	r = [_parse_ini(va, i + 1) for va in val.split(separators[i])]
	if len(r) == 1:
		return r[0]
	return r


class ReclamoScraper:
	def __init__(self):
		f = open(filename, 'r')
		self.username = None
		self.password = None
		self.d = dict()

		# Parse offlib.ini

		for line in f:
			key, val = line.split('=')
			val = val.split('\n')[0]
			if key == 'ramos':
				ramos = []
				for va in val.split(';'):
					v = va.split(':')
					ramo = Ramo(v[0])
					for el in v[1].split(','):
						ramo.addControl(el, '')
					ramos.append(ramo)
				self.d[key] = ramos
			else:
				self.d[key] = _parse_ini(val)

	def logIn(self, username, password, queue=None, selfUserPass=False):
		"""
		Args: username (str), password (str), queue (mp.queue), selfUserPass (bool)

		Realiza el login en reclamos dim, retorna True en caso
		de ingresar exitosamente a reclamos, False en caso contrario.

		En caso de usarlo con multiprocessing es necesario pasar una queue,
		a traves de la queue se entregara una tupla con el resultado (True o False)
		y el codigo html de reclamos (si es que el resultado es True)

		Si selfUserPass se settea a True, entonces usa el user y pass de la clase.
		En cuyo caso es importante setear user y pass con setUserPass antes.
		"""
		log.info('OffLib: Checkeo de login')

		if selfUserPass:
			if self.username is None or self.password is None:
				log.warning('OffLib: Se espera self.username o self.password pero no han sido seteados!')
				if username is None or password is None:
					log.error('OffLib: No se entrega username o pass, se aborta login')
					return
			else:
				username = self.username
				password = self.password
		if self.d['delay_logIn'] is not None:
			time.sleep(float(self.d['delay_logIn']))
		log.debug('OffLib: %s, %s', self.d['username'], self.d['password'])
		if username == self.d['username'] and password == self.d['password']:  # LogIn exitoso
			log.info('OffLib: Login exitoso')
			if queue is None:
				return True
			queue.put(True)
			return
		log.warning('OffLib: Login incorrecto')
		if queue is None:
			return False
		queue.put(False)

	def setUserPass(self, user, passw):
		"""Settea usuario y pass para el login. Evitar el uso de esta funcion"""
		self.username = user
		self.password = passw

	def getInfo(self):
		"""
		Retorna una lista de ramos (de la clase Ramo) que se encontraron en reclamos dim.
		Cada ramo contiene el nombre del ramo y sus controles.
		"""
		return self.d['ramos']

	def searchNotas(self, p, queue, user, passw):
		"""
		Busca notas por ramo en reclamos hasta que encuentra al menos 3
		"""
		if not self.logIn(user, passw):
			raise Exception('Usuario o Contraseña incorrectos')
		
		for i in range(len(p)):
			if self.d['delay_searchNotas'] is not None\
				and i < len(self.d['delay_searchNotas']):
				time.sleep(float(self.d['delay_searchNotas'][i]))
			queue.put((p[i], [float(nota) for nota in self.d['notas'][i]]))
