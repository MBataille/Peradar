# -*- coding: utf-8 -*-

from mechanize import Browser
from kivy.logger import Logger as log
import re
from BeautifulSoup import BeautifulSoup

class Ramo:
	"""
	Permite guardar mas amigablemente los datos de un ramo
	Attrs: name (str), controles (lista de str)
	"""
	def __init__(self, name):
		self.name = name
		self.controles = []

	def __str__(self):
		return self.name + ': ' + '/'.join(str(c) for c in self.controles)

	def addControl(self, control):
		"""Agrega un control a los controles del ramo"""
		self.controles.append(control)

	def getControles(self):
		"""Retorna la lista de controles del ramo"""
		return [c for c in self.controles]

class ReclamoScraper:
	"""
	Interfaz para obtener la informacion de reclamos dim

	TODO: Agregar funcion para recibir notas que funcione con
	multiprocessing
	"""
	def __init__(self):
		self.browser = Browser()
		self.browser.set_handle_robots(False)
		self.soup = None
	def logIn(self, username, password, queue = None):
		"""
		Args: username (str), password (str), queue (mp.queue)

		Realiza el login en reclamos dim, retorna True en caso
		de ingresar exitosamente a reclamos, False en caso contrario.

		Si se le entrega una queue, el resultado lo escribe en la queue
		y ademas, escribe el browser y codigo html en la queue para que no se pierda
		la informacion del browser cuando se muera el proceso
		"""
		log.info('Lib: Checkeo de login')

		self.browser.open('https://www.u-cursos.cl/upasaporte/login?servicio=dim_reclamos&')

		self.browser.select_form(nr=0)

		self.browser['username'] = username
		self.browser['password'] = password
		resp = self.browser.submit()

		if self.browser.geturl()[7:14] == "reclamo": # LogIn exitoso
			log.info('Lib: Login exitoso')
			if queue is None:
				return True
			#log.debug('Lib: browser? %s response? %s', self.browser, resp.read())
			queue.put((True, self.browser, resp.read()))
			log.debug('Lib: Agregada la tupla')
			return
		log.warning('Lib: Login incorrecto')
		if queue is None: return False
		queue.put((False,))

	def setBrowser(self,browser,html):
		""" Recupera la informacion del proceso que realizo el Login"""
		self.browser = browser
		self.soup = BeautifulSoup(html)

	def getRamos(self):
		"""Retorna una lista con los ramos (cada ramo es un tag de beautifulsoup)"""
		ramos = []
		for el in self.soup.findAll(href = re.compile('cursos')):
			ramos.append(el) 
		if len(ramos) == 0: log.error('Lib: No hay ramos')
		return ramos 

	def getInfo(self):
		"""
		Retorna una lista de ramos (de la clase Ramo) que se encontraron en reclamos dim.
		Cada ramo contiene el nombre del ramo y sus controles.
		"""
		info = []
		i = 0
		# if self.soup is None: self.setSoup()
		L = self.soup.findAll(href = re.compile('view'))
		for r in self.getRamos():
			i += 1
			ramo = Ramo(r.string)
			while i<len(L) and len(L[i].string) == 2: # asumiendo que los controles son de largo 2
				log.debug('Lib: controles, %s', L[i].string)
				ramo.addControl(L[i].string) 
				i += 1
			log.debug('Lib: Ramo creado es: %s', ramo)
			info.append(ramo)
		return info