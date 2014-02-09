#! /usr/bin/env python
# -*- encoding: utf-8 -*-

def crear_titulos():
    titulos = { 
        'ingeniería': 
                '''
                Analista Programador Universitario
                Ingeniería Civil Orientación Construcciones
                Ingeniería Civil Orientación Hidráulica 
                Ingeniería Electrónica
                Ingeniería en Petróleo
                Ingeniería Forestal
                Ingeniería Industrial
                Ingeniería Mecánica
                Ingeniería Química
                Licenciatura en Higiene y Seguridad en el Trabajo
                Licenciatura en Informática
                Licenciatura en Matemática
                Profesorado de Tercer Ciclo de la Educación General Básica y de la Educación Polimodal en Matemática
                Profesorado en Matemática
                ''',
        'económicas': 
                '''
                Contador Público Nacional
                Licenciatura en Administración
                Licenciatura en Economía
                Licenciatura en Administración de Empresas Turísticas
                Técnico Universitario Contable
                Técnico Universitario en  Administración Pública
                Técnico Universitario en  Administración Bancaria
                Técnico Universitario en Administración Ambiental
                Técnico Universitario en Administración de Cooperativas
                ''',
        'derecho': 
                '''
                Abogacía
                Abogacía Especialista para la Magistratura
                ''',
        'humanidades':
                '''
                Licenciatura en Ciencia Política
                Licenciatura en Comunicación Social
                Licenciatura en Geografía
                Licenciatura en Gestión Ambiental
                Licenciatura en Historia
                Licenciatura en Letras
                Licenciatura en Trabajo Social
                Licenciatura en Turismo
                Profesorado en Letras EGB y Polimodal
                Profesorado en Geografía EGB y Polimodal
                Profesorado en Historia EGB
                Profesorado en Geografía
                Profesorado en Historia
                Profesorado en Letras
                Profesorado y Licenciatura en Ciencias de la Educación
                Tecnicatura en Turismo
                Tecnicatura SIG
                ''',
        'naturales':
                '''
                Bioquímica
                Enfermería
                Farmacia
                Geología
                Licenciatura en Ciencias Biológicas
                Profesorado en Ciencias Biológicas
                Licenciatura en Enfermería
                Técnico Universitario en Química
                Profesorado en Química
                Licenciatura en Química
                Profesorado en Ciencias Naturales para 3º Ciclo de EGB y Polimodal
                Licenciatura en Protección y Saneamiento Ambiental
                Técnico Universitario en Protección Ambiental
                Técnico en Producción Agropecuaria
                ''',
    }
    # Cadena a lista
    for carrera, lista_titulos in titulos.iteritems():
        lista_titulos = [ t.strip() for t in lista_titulos.split('\n') ]
        lista_titulos = filter(lambda t: len(t) > 1, lista_titulos)
        titulos[carrera] = lista_titulos
    # Y ahora,
    return titulos

import sys
import os
from pprint import pprint
def main(argv = sys.argv):
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        sys.path += '..', '../..', '../../..'
        sets = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../settings.py'))
        sets = '../../settings'
        os.environ['DJANGO_SETTINGS_MODULE'] = sets
    from django.db.models import get_app, get_apps
    return
    pprint(crear_titulos())
    return 0
if __name__ == "__main__":
    sys.exit(main())
