#!/usr/bin/python3

"""
Practica 1 - Web acortadora de URLs

Pablo Castillo Lopez
ITT
p.castillol @ alumnos.urjc.es
SAT (Universidad Rey Juan Carlos)
"""

import webapp
import urllib.parse
import os.path

contents = {}    #{urlReal: numero_urlAcortada}
contentsInv = {} #{numero_urlAcortada: urlReal}

FILE_NAME = "urls.csv"

formulario = """
    <form action="" method="POST">
        URL que quieres acortar:<br>
        <input type="text" name="url" value="gsyc.urjc.es"/>
        <br><br>
        <input type="submit" value="Acortar URL">
    </form>
"""

class AppShort(webapp.webApp):

    def writeCSV(self, num, url):
        fd = open(FILE_NAME, 'a') #Abrimos fichero en modo escritura poniendo puntero al final de el. Si no existe, se crea.
        fd.write(str(num) + "," + url + "\n")
        fd.close()

    def readCSV(self):
        if os.path.isfile(FILE_NAME):
            fd = open(FILE_NAME, 'r') #Abrimos fichero en modo lectura.

            for linea in fd.readlines():
                num = int(linea.split(",")[0])
                url = linea.split(",")[1]
                url = url.replace("\n", "")

                #Rellenamos los diccionarios con el contenido que teniamos en el fichero csv.
                contents[url] = num
                contentsInv[num] = url

            fd.close()


    def parse(self, request):
        self.method = request.split()[0]
        self.resource = request.split()[1]
        self.body = request.split("=")[-1] #Obtenemos el valor del campo url del body (url=http://pag.com).
        self.request = request
        return(self.method, self.resource, self.body, self.request)

    def process(self, parsedRequest): #Ha de devolver 2 valores (httpCode, htmlAnswer).
        if len(contents) == 0:
            self.readCSV()

        # Metodo GET
        if self.method == "GET":
            #si el recurso es / : 200 OK
            if self.resource == "/":
                httpCode = "200 OK"
                htmlAnswer = formulario

                for i in contentsInv:
                    htmlAnswer = htmlAnswer + str(i) + ": " + contentsInv[i] + "<br>"

            #si el recurso es distinto de / : 302 Found o 404 Not Found
            else:
                try:
                    resourceName = self.resource.replace("/", "") #quitamos la barra al recurso.
                    num = int(resourceName)

                    if num in contentsInv:
                        httpCode = "302 Found"
                        htmlAnswer = ("<html><head><meta http-equiv='refresh' content='0; " +
                                      "url=" + contentsInv[num] +"'></head>")
                    else:
                        httpCode = "404 Not Found"
                        htmlAnswer = "ERROR. Recurso no disponible."

                except ValueError:
                    httpCode = "404 Not Found"
                    htmlAnswer = "Introduce un numero en el recurso."

        # Metodo POST
        elif self.method == "POST":
            #POST sin qs. Devolvemos error.
            if "url" not in self.request:
                httpCode = "404 Not Found"
                htmlAnswer = "ERROR. Metodo POST sin body (qs)."

            #POST con qs
            else:
                body = urllib.parse.unquote(self.body) #decodificamos url (caracteres %xx).

                #Si enviamos formulario vacio.
                if body == "":
                    httpCode = "404 Not Found"
                    htmlAnswer = "No se ha introducido una url."

                #Si metemos url en formulario.
                else:
                    if not (body[0:7] == "http://" or body[0:8] == "https://"):
                        body = "http://" + body

                    #Si la url a acortar no esta incluida en el diccionario, la añadimos y lo guardamos en el fichero csv.
                    if not body in contents:
                        num = len(contentsInv)

                        contentsInv[num] = body
                        contents[body] = num
                        self.writeCSV(num, body)

                        httpCode = "200 OK"
                        htmlAnswer = ("<html><body><a href='" + contentsInv[num] + "'>" + str(num) + "</a>" +
                                      " --> " +
                                      "<a href='" + contentsInv[num] + "'>" + contentsInv[num] + "</a>" +
                                      "</body></html>")
                                      #Muestra como enlaces pinchables la url acortada y la url original.

                    #si la url a acortar ya estuviera en el diccionario.
                    else:
                        httpCode = "200 OK"
                        htmlAnswer = "La url ya esta asignada."

        # Si el metodo no es ni GET ni POST.
        else:
            httpCode = "404"
            htmlAnswer = "Not Found"

        return(httpCode, htmlAnswer)

if __name__ == "__main__":
    testWebApp = AppShort("localhost", 1234)
