# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from mechanize import Browser
from kivy.logger import Logger as log
import re
import time

_base_url = 'http://reclamo.dim.uchile.cl'

def _is_int(a):
	try:
		int(a)
		return True
	except ValueError:
		return False


class Control:
	"""
	Guarda los datos de un control,
	Attrs: name (str), partial_url (str), ramo (str), id (int)
	"""

	def __init__(self, name, partial_url, ramo=None):
		self.name = name
		self.partial_url = partial_url
		self.ramo = ramo if ramo is None else ramo.split(' ')[0]
		self.id = None

	def setId(self, an_id):
		self.id = an_id

	def __str__(self):
		return ('' if self.ramo is None else (self.ramo + ": ")) + self.name


class Ramo:
	"""
	Permite guardar mas amigablemente los datos de un ramo
	Attrs: name (str), controles (lista de Controles, de la clase Control)
	"""
	def __init__(self, name):
		self.name = name
		self.controles = []

	def __str__(self):
		return (self.name + ': ') + '/'.join(str(c) for c in self.controles)

	def addControl(self, control, url):
		"""Agrega un control a los controles del ramo"""
		self.controles.append(Control(control, url, ramo=self.name))

	def getControles(self):
		"""Retorna la lista de controles del ramo"""
		return [c for c in self.controles]

	def findControlUrl(self, name):
		"""Busca un control dado su nombre y retorna partial_url, si no lo encuentra, retorna None"""
		for c in self.controles:
			if c.name == name:
				return c.partial_url
		return None


class ReclamoScraper:
	"""
	Interfaz para obtener la informacion de reclamos dim

	ToDo: Agregar funcion para recibir notas que funcione con
	multiprocessing
	"""
	def __init__(self):
		self.browser = Browser()
		self.browser.set_handle_robots(False)
		self.soup = None
		self.username = None
		self.password = None
		self.resp = None

	def logIn(self, username, password, queue=None, selfUserPass=False):
		"""
		Args: username (str), password (str), queue (mp.queue), selfUserPass (bool)

		Realiza el login en reclamos dim, retorna True en caso
		de ingresar exitosamente a reclamos, False en caso contrario.

		En caso de usarlo con multiprocessing es necesario pasar una queue,
		a traves de la queue se entregara una tupla con el resultado (True o False)
		y el codigo html de reclamos (si es que el resultado es True)

		Si selfUserPass se settea a True, entonces usa el user y pass de la clase.
		Importante setear user y pass con setUserPass antes.
		"""
		log.info('Lib: Checkeo de login')

		if selfUserPass:
			if self.username is None or self.password is None:
				log.warning('Lib: Se espera self.username o self.password pero no han sido seteados!')
				if username is None or password is None:
					log.error('Lib: No se entrega username o pass, se aborta login')
					return
			else:
				username = self.username
				password = self.password

		self.browser.open('https://www.u-cursos.cl/upasaporte/login?servicio=dim_reclamos&')

		self.browser.select_form(nr=0)

		self.browser['username'] = username
		self.browser['password'] = password
		self.resp = self.browser.submit()
		if self.browser.geturl()[7:14] == "reclamo":  # LogIn exitoso
			log.info('Lib: Login exitoso')
			if queue is None:
				return True
			queue.put(True)
			return
		log.warning('Lib: Login incorrecto')
		if queue is None:
			return False
		queue.put(False)

	def setBeautifulSoup(self, html=None):
		""" Recupera la informacion del proceso que realizo el Login"""
		if html is None:
			self.soup = BeautifulSoup(self.resp)
		else:
			self.soup = BeautifulSoup(html)

	def setUserPass(self, user, passw):
		"""Settea usuario y pass para el login. Evitar el uso de esta funcion"""
		self.username = user
		self.password = passw

	def getRamos(self):
		"""Retorna una lista con los ramos (cada ramo es un tag de beautifulsoup)"""
		ramos = []
		for el in self.soup.findAll(href=re.compile('cursos')):
			ramos.append(el)
		if len(ramos) == 0:
			log.error('Lib: No hay ramos')
		return ramos

	def getInfo(self):
		"""
		Retorna una lista de ramos (de la clase Ramo) que se encontraron en reclamos dim.
		Cada ramo contiene el nombre del ramo y sus controles.
		"""
		if self.soup is None:
			if self.resp is None:
				log.error('Lib: No se encontro resp ni soup.')
				raise Exception('Mechanize response not found')
			self.setBeautifulSoup()
		info = []
		i = 0
		L = self.soup.findAll(href=re.compile('view'))
		for r in self.getRamos():
			i += 1
			ramo = Ramo(r.string)
			while i < len(L) and len(L[i].string) == 2:  # asumiendo que los controles son de largo 2
				ramo.addControl(L[i].string, L[i]['href'])
				i += 1
			log.debug('Lib: Ramo creado es: %s', ramo)
			info.append(ramo)
		return info

	def getNotas(self, control):
		"""
		Retorna una lista con las notas.
		Si no hay notas, retorna una lista vacia.
		"""
		log.debug('Lib: Opening, %s', (_base_url + control.partial_url))
		self.soup = BeautifulSoup(self.browser.open(_base_url + control.partial_url).read())
		self.browser.back()
		if self.soup.find('table') is None:
			log.debug('Lib: TABLE NOT FOUND\n %s', self.soup.prettify())
		notas = []
		for row in self.soup.find('table').findAll('tr'):
			for el in row.findAll('td'):
				nota = None
				if _is_int(el.text):
					nota = int(el.text)
				if nota is not None:
					notas.append(nota)
		log.debug('Lib: Notas: %s', notas)
		return notas

	def searchNotas(self, p, queue, user, passw):
		"""
		Busca notas por ramo en reclamos hasta que encuentra al menos 3
		"""
		if not self.logIn(user, passw):
			raise Exception('Usuario o Contraseña incorrectos')
		notas_ramos = [[] for _ in p]
		while [] in notas_ramos:
			for i in range(len(p)):
				if len(notas_ramos[i]) >= 3:
					continue
				notas_ramos[i] = self.getNotas(p[i])
				if len(notas_ramos[i]) >= 3:
					log.debug('Lib: Sent notas: %s, del ramo: %s', notas_ramos[i], p[i])
					queue.put((p[i], notas_ramos[i]))
			time.sleep(10)
