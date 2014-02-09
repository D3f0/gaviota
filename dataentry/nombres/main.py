#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
Script para rippear nombres desde un sitio
'''

import sys
import os
import atexit
import string
import urllib2
import pdb
from utils import timeit
import shelve
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from soupselect import select
import codecs

if os.environ.get('FROM') == 'kate':
    def parar():
        raw_input("Presione una tecla para continuar")
    atexit.register(parar)
 
# ----------------------------------------------------------------------------
CACHE = shelve.open('url_cache')
# Estructura de la chache
# url -> (date, content)
def cerrar_cache():
    global CACHE
    CACHE.close()
atexit.register(cerrar_cache)


# Mejora de esta función usando shelve
@timeit
def read_url(url, ret = True):
    '''
    Descarga una URL. Utiliza cache.
    Ret inidica que se debe retornar el contenido. El uso sin iter devuelve None
    pero si realiza la petición (para medir el tiempo).
    '''
    if ret and CACHE.has_key(url):
        return CACHE[url]
    cont = None         # Auxiliar para recupuerar el contenido
    f = urllib2.urlopen(url)
    if ret:
        cont = f.read()
        CACHE[url] = cont
        
    f.close()
    return cont
# ----------------------------------------------------------------------------

def lista_nombres(url, **kwargs):
    parcial = []
    url = url % kwargs
    cont = read_url(url)
    # Con el HTML hacemos la sopa
    sopa = BeautifulSoup(cont)
    # y en la sopa buscamos
    for fila_nombre in select(sopa, 'table table table[border=0] tr'):
        try:
            nombre = fila_nombre.td.contents[0]
        except Exception, e:
            # Filas vacias
            pass
        else:
            parcial.append(nombre)
    return parcial

PATH = './data/'

@timeit
def main(argv = sys.argv):
    
    nombres = [
        'ambos_sexos', 'masculinos', 'femeninos'
    ]
    
    URL = "http://www.sitiosargentina.com.ar/Nombres/%(sexo)s/%(letra)s.htm"
    
    for sexo in nombres:
        f = codecs.open(PATH + sexo + '.txt', 'wb', 'utf-8')
        
        for letra in string.uppercase:
            # Agregamos un |n
            lista = lista_nombres(URL, sexo = sexo, letra = letra)
            if not lista:
                lista = lista_nombres(URL, sexo = sexo, letra = letra.lower())
            try:
                for nombre in lista:
                    try:
                        f.write(u'%s\n' % nombre)
                    except Exception, e:
                        # Problemas de encoding
                        print e
                        
                print "Escritos %s de sexo %s letra %s" % (len(lista), sexo, letra)
            except Exception, e:
                
                print e
                
        f.close()

if __name__ == "__main__":
    sys.exit(main())
