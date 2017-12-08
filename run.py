from mechanize import Browser
from time import sleep
from BeautifulSoup import BeautifulSoup
from pygame import mixer

USERNAME = 'martin.bataille'
PASSWORD = 'mipass'
CONTROL = 'EX' # EX = examen, C1 = control 1, etc...
PREGUNTAS = 3
R1 = [50,40]
R2 = [56, 46]
RAMOS = ["Calculo", "Algebra"]

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
			notas[n_pregunta] = int(n[nota:nota+2])
		return notas

def mean(notas):
	return round(1.0*sum(notas)/len(notas))

mixer.init()
browser = Browser()
# Para que no cache que soy un robot
browser.set_handle_robots(False)

# Entra a la pagina
print "Ingresando a reclamos..."
browser.open('https://www.u-cursos.cl/upasaporte/login?servicio=dim_reclamos&')

# Obtiene el formulario
browser.form = list(browser.forms())[0]

# Lleno el formulario y lo envio
browser['username'] = USERNAME
browser['password'] = PASSWORD
browser.submit()

assert browser.geturl()[7:14] == "reclamo", "\nLOGIN INCORRECTO\n"
print "Login exitoso"
links_notas = []

# Busco los links que lleven a las notas que quiero, EX, C1, etc
for link in browser.links():
	if link.text == CONTROL:
		links_notas.append(link)
# Si no se encuentran, aborta
assert len(links_notas) != 0, '\nNO SE ENCONTRARON LINKS DEL CONTROL: {}\n'.format(CONTROL)
print "Buscando notas..."


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
				print "Sere wn"
				j = 0
			elif nota < R2[k]:
				print "Aun se puede"
				j = 1
			else:
				print "BIEN CTMMMM"
				j = 2
			mixer.music.load(MUSICA[k][j])
			mixer.music.play(-1, START[k][j])
			r = raw_input('presiona cualquier tecla para parar ')
			mixer.music.stop()
		browser.back()
	sleep(10)
