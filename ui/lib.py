# -*- coding: utf-8 -*-

from mechanize import Browser
from kivy.logger import Logger as log
import re
from BeautifulSoup import BeautifulSoup

class Ramo:
	def __init__(self, name):
		self.name = name
		self.controles = []

	def __str__(self):
		return self.name + ': ' + '/'.join(str(c) for c in self.controles)

	def addControl(self, control):
		self.controles.append(control)

	def getControles(self):
		return [c for c in self.controles]

class ReclamoScraper:
	def __init__(self):
		self.browser = Browser()
		self.browser.set_handle_robots(False)
		self.searchFor = []
		self.soup = None
	def logIn(self, username, password, queue = None):
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
		self.browser = browser
		#log.debug('Lib: response: %s', self.browser.response())
		self.soup = BeautifulSoup(html)
	def setSoup(self, resp):
		self.soup = BeautifulSoup(resp.read())

	def getRamos(self):
		ramos = []
		for el in self.soup.findAll(href = re.compile('cursos')):
			ramos.append(el) 
		if len(ramos) == 0: log.error('Lib: No hay ramos')
		return ramos

	def getControles(self, ramo):
		cont = []
		self.browser.follow_link(url_regex = ramo['href'])
		soup = BeautifulSoup(browser.response().read())
		for el in soup.findAll(lambda tag: tag.name == 'td' and not tag.has_key('class')):
			cont.append(el)
		browser.back()
		if len(cont) == 0: log.warning('Lib: No hay controles para el ramo ' + str(ramo.string))
		return cont	
	#Still have to test this 
	def getInfo(self):
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

def mean(notas):
	return round(1.0*sum(notas)/len(notas))

def t_str(t):
	if t < 10:
		return '0' + str(t)
	return str(t)

"""
# Entra a la pagina
log("Ingresando a reclamos...")


soup = BeautifulSoup(browser.response().read())

ramos = getRamos(soup)
#print 'ramos ', ramos
RAMOS = []
for ramo in ramos:
	print "Se ha detectado el ramo", ramo.string
	r = checkValido('Quieres buscar nota de ese ramo?')
	if r == 'n': continue
	getControles(ramo)


parse(browser.response().read())

links_notas = []

# Busco los links que lleven a las notas que quiero, EX, C1, etc
for link in browser.links():
	if link.text == CONTROL:
		links_notas.append(link)
# Si no se encuentran, aborta
assert len(links_notas) != 0, '\nNO SE ENCONTRARON LINKS DEL CONTROL: {}\n'.format(CONTROL)
log("Buscando notas...")

t0 = None
noHayNotas = True
hayNota = [False for i in range(len(links_notas))]
while False in hayNota:
	for k in range(len(links_notas)):
		if hayNota[k]: continue
		link = links_notas[k]
		browser.follow_link(link) # me meto a la pagina con las notas
		html = browser.response().read() # obtengo TODO el codigo fuente de la pagina
		notas = parse(html) # lo paso a notas
		if notas != None:
			hayNota[k] = True # habemus nota
			nota = mean(notas)
			j = -1
			if nota < R1[k]:
				log("No pasaste :(")
				j = 0
			elif nota < R2[k]:
				log("Se puede con examen de segunda")
				j = 1
			else:
				log("Pasaste!!!!")
				j = 2
			try:
				mixer.music.load(MUSICA[k][j])
			except PygameError:
				raise MusicFileError("No se encontro el archivo de musica ingresado, {}. Verifica que lo escribiste bien y que esta en este mismo directorio".format(MUSICA[k][j]))
			mixer.music.play(-1, START[k][j])
			r = raw_input('presiona cualquier tecla para parar ')
			mixer.music.stop()
		browser.back()
	if t0 == None:
		log( "Aun no hay notas")
		t0 = time.time()
	else:
		if time.time()-t0 >= MENSAJES_CADA:
			log("Aun no hay notas")
			t0 = time.time()
	time.sleep(10)
"""