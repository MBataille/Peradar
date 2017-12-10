from mechanize import Browser
import time
from BeautifulSoup import BeautifulSoup
from pygame import mixer

USERNAME = 'miusuario'
PASSWORD = 'mipass'
CONTROL = 'EX' # EX = examen, C1 = control 1, etc...
PREGUNTAS = 3
R1 = [50,40]
R2 = [56, 46]
RAMOS = ["Calculo", "Algebra"]
MENSAJES_CADA = 5*60 # La cantidad de segundos entre mensaje y mensaje

# MUSICA: lista de una lista por ramo, cada lista contiene la musica que 
# se va a reproducir dependiendo de si cagaste, vas a ex de 2da, pasaste, respectivamente
# en el ramo correspondiente. Sientete libre de cambiar los nombres de las canciones.
MUSICA = [['calculo_cagaste.mp3','calculo_segunda.mp3','calculo_pasaste.mp3'],
['algebra_cagaste.mp3','algebra_segunda.mp3','algebra_pasaste.mp3']]

# START: segundo en el que quieres que parta cada cancion, sigue la misma estructura que MUSICA
# esto sirve pa saltarte la parte fome y llegar al tiro al coro o lo que quieras
START = [[45.5, 46.5, 46.5], [45.5, 46.5, 46.5]]

def parse(html):
	parsed_html = BeautifulSoup(html) # lo categoriza en body, div, etc para acceder mas rapido
	table = parsed_html.find(lambda tag: tag.name=='table') # busca la tabla
	rows = table.findAll(lambda tag: tag.name=='tr') # la ordena en filas
	if len(rows) == PREGUNTAS+1: # estan todas las preguntas 
		notas = [0 for i in range(PREGUNTAS)]
		for i in range(1, len(rows)):
			el = rows[i].findAll(lambda tag: tag.name=='td')
			p = str(el[0])
			n = str(el[1])
			n_pregunta = p.find('P') + 1
			n_pregunta = int(p[n_pregunta]) - 1
			nota = n.find('>') + 1
			if n[nota] == '-': return None 
			if n[nota+1] == '<': notas[n_pregunta] = int(n[nota])
			else: notas[n_pregunta] = int(n[nota:nota+2])
		return notas

def mean(notas):
	return round(1.0*sum(notas)/len(notas))

def log(s):
	t = time.localtime()
	print "{}:{}:{}".format(t.tm_hour, t.tm_min, t.tm_sec) + " " + s


mixer.init()
browser = Browser()
# Para que no cache que soy un robot
browser.set_handle_robots(False)

# Entra a la pagina
log("Ingresando a reclamos...")
browser.open('https://www.u-cursos.cl/upasaporte/login?servicio=dim_reclamos&')

# Obtiene el formulario
browser.form = list(browser.forms())[0]

# Lleno el formulario y lo envio
browser['username'] = USERNAME
browser['password'] = PASSWORD
browser.submit()

assert browser.geturl()[7:14] == "reclamo", "\nLOGIN INCORRECTO\n"
log("Login exitoso")
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
			except:
				print "############################"
				print "No encuentro el archivo de musica que me diste. \
				Escribiste bien el nombre? Verificaste que estamos en el mismo directorio?"
				print "############################"
				assert False, ""
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