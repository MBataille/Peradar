import os, sys

file_name = 'config.ini'
params = dict()
keys = ['USERNAME', 'PASSWORD', 'RAMOS', 'CONTROL', 'PREGUNTAS', \
'R1', 'R2', 'MUSICA', 'START', 'MENSAJES_CADA']
doc  = {
	'USERNAME' : 'Ingresa tu usuario de u pasaporte. Tus datos se utilizaran UNICAMENTE para ingresar a reclamos.dim',
	'PASSWORD' : 'Ingresa tu pass de u pasaporte. Tus datos se utilizaran UNICAMENTE para ingresar a reclamos.dim',
	'CONTROL' : 'Ingresa el codigo del control o examen que quieres ver, \'C1\' si quieres ver el primer control, \'EX\' si quieres ver el examen.',
	'PREGUNTAS' : 'Ingresa la cantidad de preguntas que tiene el control o examen que quieres ver.',
	'RAMOS' : 'Ingresa tus ramos, ingresa 0 para terminar',
	'R2' : 'OPCIONAL: Ingresa la nota por ramo que necesitas en el examen para ir a examen de segunda.\
	Si no aplica, dejalo en cero.',
	'R1' : 'Ingresa la nota por ramo que necesitas para pasar el ramo (sin tener que dar el examen de segunda).',
	'MUSICA' : 'Ingresa las canciones que se reproduciran',
	'START' : 'Ingresa el segundo en el que quieres que empiece cada cancion (asi te saltas la intro).',
	'MENSAJES_CADA' : 'Ingresa cada cuanto tiempo quieres que el programa imprima \'Aun no hay notas\'.	Lo recomendado es 300 (es decir, 5 mins)'	
}
for k in keys:
	params[k] = -1
class ConfigFileError(Exception):
	pass

def checkValido(q, opts = ["s", "n"], w = "Ingresa una opcion valida!",\
                imprimirOpciones = True):
    if imprimirOpciones:
        q+= " ("
        inicial = True
        for o in opts:
            if inicial:
                q+=str(o)
                inicial = False
            else: q+= "/" + str(o)
        q+=") "
    r = raw_input(q)
    while not r in opts:
        print w
        r = raw_input(q)
    return r

def printError(msg):
	print "##########################################"
	print msg
	print "##########################################"

def readConfig(params):
	for key in keys:
		if key == 'PREGUNTAS':
			try:
				params[key] = int(params[key])
			except ValueError:
				raise ConfigFileError("Numero de preguntas no entero. Se sugiere borrar el archivo")
		elif key == 'RAMOS':
			params[key] = params[key].split(',')
		elif key == 'R1' or key == 'R2':
			if len(params[key].split(',')) != len(params['RAMOS']):
				raise ConfigFileError("Cantidad de ramos incosistente. Se sugiere borrar el archivo")
			params[key] = params[key].split(',')
			for i in range(len(params[key])):
				try:
					params[key][i] = int(params[key][i])
				except ValueError:
					raise ConfigFileError("R1 o R2 no es entero. Se suguiere borrar el archivo")
		elif key == 'MUSICA':
			l = params[key].split(':')
			if len(l) != len(params['RAMOS']):
				raise ConfigFileError("Dimensiones de MUSICA inconsistente. Se sugiere borrar el archivo")
			songs = [s.split(',') for s in l]
			params[key] = songs
		elif key == 'START':
			l = params[key].split(':')
			if len(l) != len(params['RAMOS']):
				raise ConfigFileError("Dimensiones de START inconsistente. Se sugiere borrar el archivo")
			start = [s.split(',') for s in l]

			for i in range(len(start)):
				for j in range(len(start[i])):
					try:
						start[i][j] = float(start[i][j])
					except ValueError:
						raise ConfigFileError("Tiempos de START no son numeros. Se sugiere borrar el archivo")
			params[key] = start
		elif key == 'MENSAJES_CADA':
			try:
				params[key] = int(params[key])
			except ValueError:
				raise ConfigFileError("MENSAJES_CADA no es entero. Se sugiere borrar el archivo")
	return params
print 'Bienvenido al sistema de configuracion!'

def toConfig(sth):
	c = ''
	if type(sth) == list:
		if type(sth[0]) == list:
			for i in range(len(sth)):
				if i > 0:
					c += ':'
				for j in range(len(sth[i])):
					if j > 0:
						c += ',' + str(sth[i][j])
					else:
						c += str(sth[i][j])
		else:
			for i in range(len(sth)):
				if i > 0:
					c += ',' + str(sth[i])
				else:
					c += str(sth[i])
	else:
		c = str(sth)
	return c
assert toConfig('abc') == 'abc'
assert toConfig(123) == '123'
assert toConfig([1,2,3]) == '1,2,3', toConfig([1,2,3])
assert toConfig(['1', '2', '3']) == '1,2,3'
assert toConfig([[1,2,3],[4,5,6]]) == '1,2,3:4,5,6'
assert toConfig([['1','2','3'],['4','5','6']]) == '1,2,3:4,5,6'

if os.path.isfile(file_name):
	print 'Hemos detectado un archivo de configuracion existente'
	r = checkValido( 'Deseas eliminarlo y configurarlo desde cero (s)\
	 o sobreescribir (n)?')
	if r == 'n':
		with open(file_name, 'r') as f:
			for line in f:
				key, val = line.split('=')
				val = val.split('\n')[0]
				if params[key] != -1:
					raise ConfigFileError("Parametro desconocido. Se sugiere borrar archivo")
				params[key] = val
			params = readConfig(params)
			print "Los parametros son los siguientes:"
			for key in keys:
				if key == 'RAMOS':
					for i in range(len(params[key])):
						print 'El ramo numero {} es {}'.format(i+1, params[key][i])
						rc = raw_input('Si quieres cambiarlo, ingresa el nuevo valor, de lo contrario, ingresa \'n\'')
						if rc != 'n': params[key][i] = rc
				elif key == 'R1' or key == 'R2':
					for i in range(len(params['RAMOS'])):
						msg = '' if key == 'R1' else 'teniendo sobre un 4 en el examen de segunda '
						print params['RAMOS'], params[key]
						print 'Para {} la nota para pasar el ramo es {}'.format(params['RAMOS'][i], params[key][i])
						opts = [str(j) for j in range(71)] + ['n']
						r12 = checkValido('Si quieres cambiar la nota, ingresa la nueva nota,\
						 de lo contrario ingresa \'n\'', opts = opts, imprimirOpciones = False)
						if r12 != 'n': params[key][i] = int(r12)
				elif key == 'MUSICA':
					for i in range(len(params['RAMOS'])):
						msg = ['bajo un {}'.format(params['R2'][i]),
						'entre un {} y un {}'.format(params['R2'][i], params['R1'][i]),
						'sobre un {}'.format(params['R1'][i])]
						for j in range(3):
							print 'Se reproducira {} si tienes '.format(params[key][i][j]) + msg[j] + ' en {}'.format(params['RAMOS'][i])
							rm1 = raw_input('Si quieres cambiar la cancion, ingresa el nombre (ejemplo.mp3),\
								de lo contrario, ingresa \'n\'')
							if rm1 != 'n': params[key][i][j] = rm1
				elif key == 'START':
					for i in range(len(params['MUSICA'])):
						for j in range(len(params['MUSICA'][i])):
							print 'Se reproducira {} desde el segundo {}'.format(params['MUSICA'][i][j],
								params['START'][i][j])
							rs = raw_input('Si quieres cambiarlo, ingresa el segundo desde el cual quieres comience,\
								de lo contrario ingresa \'n\'')
							if rs != 'n':
								notFloat = True
								while notFloat:
									try:
										params[key][i][j] = float(rm1)
										notFloat = False
									except ValueError: 	
										rs = raw_input('Ingresa un numero!')
				elif key == 'MENSAJES_CADA':
					print key + ' = ' + toConfig(params[key])
					rc = raw_input('Si quieres cambiarlo, ingresa el nuevo valor, de lo contrario, ingresa \'n\'')
					if rc != 'n':
						notInt = True
						while notInt:
							try:
								params[key] = int(rc)
								notInt = False
							except ValueError:
								rc = raw_input('Ingresa un entero!')

				else:
					print key + ' = ' + toConfig(params[key])
					rg = raw_input('Si quieres cambiarlo, ingresa el nuevo valor, de lo contrario, ingresa \'n\'')
					if rg != 'n':
						params[key] = rg
		print "La configuracion ha terminado! Ya puedes correr run.py, gracias por tu paciencia!"
		sys.exit()

with open(file_name, 'w') as f:
	for key in keys:
		print doc[key]
		if key == 'R1' or key == 'R2':
			params[key] = []
			for i in range(len(params['RAMOS'])):
				q = 'Para {}: '.format(params['RAMOS'][i])
				r12 = checkValido(q, opts = [str(i) for i in range(71)], imprimirOpciones = False)
				if r12 != 'n': params[key].append(int(r12))
		elif key == 'RAMOS':
			i = 1
			ramo = raw_input('Ramo numero ' + str(i) + ': ')
			while ramo == 0:
				ramo = raw_input('Debes ingresar al menos un ramo!')
			params[key] = []
 			while ramo != '0':
 				params[key].append(ramo)
				i += 1
				ramo = raw_input('Ramo numero ' + str(i) + ': ')
		elif key == 'MUSICA':
			params[key] = [[None for k in range(3)] for lst in range(len(params['RAMOS']))]
			for i in range(len(params['RAMOS'])):
				msg = ['bajo un {}'.format(params['R2'][i]),
				'entre un {} y un {}'.format(params['R2'][i], params['R1'][i]),
				'sobre un {}'.format(params['R1'][i])]
				for j in range(3):
					q = 'Ingresa la cancion que se reproducira si tienes ' + msg[j] + ' en {} '.format(params['RAMOS'][i])
					rm1 = raw_input(q)
					params[key][i][j] = rm1

		elif key == 'START':
			params[key] = [[None for k in range(3)] for lst in range(len(params['RAMOS']))]
			for i in range(len(params['MUSICA'])):
				for j in range(len(params['MUSICA'][i])):
					q = 'Desde que segundo quieres que comience {} '.format(params['MUSICA'][i][j])
					rs = raw_input(q)
					notFloat = True
					while notFloat:
						try:
							params[key][i][j] = float(rs)
							notFloat = False
						except ValueError:
							rs = raw_input('Ingresa un numero!')
		else:
			re = raw_input()
			if key == 'PREGUNTAS' or key == 'MENSAJES_CADA':
				notInt = True
				while notInt:
					try:
						params[key] = int(re)
						notInt = False
					except ValueError:
						re = raw_input('Ingresa un entero!')
			else:
				params[key] = re
		f.write(key + '=' + toConfig(params[key]) + '\n')
print "La configuracion ha terminado! Ya puedes correr run.py, gracias por tu paciencia!"