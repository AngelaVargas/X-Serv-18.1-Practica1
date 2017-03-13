
#Ángela Vargas Alba
#!/usr/bin/python3

import webApp
import csv
import os

class App (webApp.webApp):

	real_url={}		#Creo dos diccionarios, uno para las url reales y otro para las url acortadas
	short_url={}
	sequency = 0

	def write (self,urlLong,urlShort):
		with open("urls.csv", "a") as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow([int(urlShort)] + [urlLong])
		return None

	def read (self,file):

		with open('urls.csv', 'r') as csvfile:
			if os.stat('urls.csv').st_size == 0: #si es igual a 0 el fichero está vacío
				print("El fichero CSV aún no contiene urls")
			else:
				reader = csv.reader(csvfile)
				for row in reader: #siguiendo lo que hemos hecho, row[0] = urlshort y row[1] = urlLong
					self.short_url[row[1]] = int(row[0])
					self.real_url[int(row[0])] = row[1]
					self.sequency = self.sequency + 1
				return None 
	

	def parse(self, request):

		try:

			resource = request.split(' ', 2)[1]
			method = request.split(' ', 2)[0]

			if len(self.short_url) == 0:
				self.read('urls.csv')
		
			if method == "GET":
				print("He recibido un GET")
				body = ""
			elif method == "POST":
				print("He recibido un POST")
				body = request.split('\r\n\r\n', 1)[1]			#Me quedo con : valor=www.urjc.es
				body = body.split("=")[1].replace("+", " ")	#Me quedo con: www.urjc.es

		except IndexError:
			print("Vuelva a introducir una url")

		return (method, resource, body)

	def process(self, parsedRequest):

		(method, resource, body) = parsedRequest

		form = '<form action="" method="POST">'
		form += 'Introduce url para acortar: <input type="text" name="valor">'
		form += '<input type="submit" value="Enviar">'
		form += '</form>'

		if method == "GET":
			if resource == "/":					#Estoy en el caso del primer GET con una url real que quiero acortar, entonces debo enviar el form
				returnCode = "200 OK"
				htmlAnswer = "<html><body>" + form\
								+ "<p>" + "Url acortadas: "	+	str(self.short_url)\
								+ "\nUrl reales: "	+	str(self.real_url)	+	"</p></body></html>"
			else:
				try:
					resource = int(resource[1:])
					if resource in self.short_url:		#Si tengo la url acortada, redirijo a la que tenga guardada en mi dicc
						returnCode = "300 Redirect"
						htmlAnswer = "<html><body><meta http-equiv='refresh'"	+	"content='1 url="	+	self.short_url[resource] + "'>"\
										+ "</p>" + "</body></html>"
					else:
						returnCode = "404 Not Found"
						htmlAnswer = "<html><body>Error: Recurso no disponible</body></html>"

				except ValueError:
						returnCode = "404 Not Found"
						htmlAnswer = "<html><body>Error: Recurso no disponible</body></html>"

		elif method == "POST":
			if body == "":								#En el cuerpo del POST no hay url y debo devolver código de error
				returnCode = "404 Not Found"
				htmlAnswer = "<html><body>Error: Introduzca una url\n</body></html>"

				return (returnCode, htmlAnswer)
	
			elif body.find("http") == -1:			#Si en el cuerpo hay una url SIN http, devuelve -1 como error porque no lo encuentra
				print("Entro por el NO http")
				body = "http://" + body				#A la url le debo añadir la cabecera http://

			else:														#Si en el cuerpo hay url , y SI lleva http
				print("Entro por el SÍ http")
				body = body.split("%3A%2F%2F")[0]\
						+ "://" + body.split("%3A%2F%2F")[1]		# La url con http se queda como: http%3A%2F%2Furjc.es, así que lo sustituyo


			if body in self.real_url:						#Si la url ya estaba en el dicc, busco su short y la introduzco en sequency
				print("Esta url está repetida")				
				sequency = self.real_url[body]		#Averiguo cuál era su url acortada a través del dicc de url_short y con la url real (body)
			else:
				print("Entro por donde todavía no hay url real")
				print(self.sequency)
				self.sequency = self.sequency + 1		#Si no estaba, a sequency le sumo 1 para generar una nueva y lo introduzco a sequency
				sequency = self.sequency
				print(sequency)

			self.real_url[body] = sequency		#Introduzco la url acortada al dicc de url_short a través de la url real (body)
			self.short_url[sequency] = body		#Introduzco la url real al dicc de url_real a través de la url acortada (sequency)
			self.write(body,sequency)
			returnCode = "200 OK"
			htmlAnswer ="<html><body><a href=" + body + ">" + body + "</href><p><a href="	+	str(sequency)	+	">"	+	str(sequency)	+	"</href></body></html>"		#Devuelvo la url con http y la url acortada que será un número de secuencia


		else:

			returnCode = "404 Not Found"
			htmlAnswer = "<html><body>Error en el método</body></html>"


		return (returnCode, htmlAnswer)


if __name__ == "__main__":
    try:
        testWebApp = App("localhost", 1234)
    except KeyboardInterrupt:
        print ("\nInterrupted aplication")

