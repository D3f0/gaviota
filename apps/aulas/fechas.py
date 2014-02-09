#! /usr/bin/env python
# -*- encoding: utf-8 -*-

__all__ = ('dateiter', 'timeiter', 'semana_de', )

from datetime import timedelta, time, datetime
from functools import partial


def dateiter(begin, end, weekday = 1, step = timedelta(7)):
    '''
    Itera sobre fechas
        :param begin: fecha de inicio (inico del rango)
        :parm end: fecha de finalización (fin del rango)
        :param weekday: Fecha correspondiente con date.isoweekday
        :param step: Espacio entre fechas
    '''
    
    begin_wd = begin.isoweekday()
    
    if begin_wd > weekday:
        # TODO: Ver si el 7 no es en realidad el step.days
        begin += timedelta(days = 7 - begin_wd + weekday)
    elif begin_wd < weekday:
        begin += timedelta(days = weekday - begin_wd )
        
    #ini_wd = begin.isoweekday() # Día de comienzo
    while begin <= end:
        yield begin
        begin += step

class timeiter(object):
    '''
    Iterador de horario.
    '''
    STRFMT = '%H:%M'
    STROMT = STRFMT
    def __init__(self, inicio, fin, salto = '0:30'):
        self.__inicio = None
        self.__fin = None
        self.__salto = None
        
        # Llamamos a los seters
        self.inicio = inicio
        self.actual = self.inicio
        self.fin = fin
        self.salto = salto
        
    def set_inicio(self, ini):
        if type(ini) == time:
            self.__inicio = datetime(1900, 1, 1, ini.hour, ini.minute)
        elif type(ini) == str:
            self.__inicio = datetime.strptime(ini, self.STRFMT)
        else:
            raise ValueError('Inicio no puede ser %s' % ini)
    inicio = property(lambda s: s.__inicio, set_inicio, doc=u"Inicio de iteración")
    
    def set_fin(self, fin):
        if type(fin) == time:
            self.__fin = datetime(1900, 1, 1, fin.hour, fin.minute)
        elif type(fin) == str:
            self.__fin = datetime.strptime(fin, self.STRFMT)
        else:
            raise ValueError('Fin no puede ser %s' % fin)
    fin = property(lambda s: s.__fin, set_fin, doc=u"Inicio de iteración")
    
    
    def set_salto(self, salto):
        if type(salto) == timedelta:
            self.__salto = salto
        elif type(salto) == str:
            t = datetime.strptime(salto, self.STRFMT)
            self.__salto = timedelta( seconds = t.minute * 60 + t.hour * 3600)
        else:
            raise ValueError('Salto no puede ser %s' % salto)
        
    salto = property(lambda self: self.__salto, set_salto, doc="Salto en la iteración")
    
    def __iter__(self):
        return self
    
    def next(self):
        ''' Iterador que itera sobre datetimes, la más flexible,
        existen dos métodos generadores de conveniencia: by_time que
        retorna datetime.time y by_str(fmt = STRFMT) que genera cadenas
        '''
        while self.actual <= self.fin:
            retval = self.actual
            self.actual += self.salto
            return retval
        raise StopIteration()
           
    
    def __str__(self):
        return "<Iterador desde %(inicio)s hasta %(fin)s de a %(paso)s>" % {
                'inicio': self.inicio.strftime(self.STRFMT),                                                           
                'fin': self.fin.strftime(self.STRFMT),
                'paso': self.salto
                }

    def by_time(self):
        ''' Generador para iterar de a times '''
        localini = self.inicio
        while localini <= self.fin:
            yield localini.time()
            localini += self.salto
    
    def by_str(self, fmt = None):
        ''' Generador para iterar de a strs'''
        fmt = fmt and fmt or self.STRFMT
        localini = self.inicio
        while localini <= self.fin:
            yield localini.strftime(fmt)
            localini += self.salto
    
    def by_str_dt(self, fmt = None):
        ''' Generador para tuplas (cadena, datetime)'''
        fmt = fmt and fmt or self.STRFMT
        localini = self.inicio
        while localini <= self.fin:
            yield (localini.strftime(fmt), localini)
            localini += self.salto


def semana_de(fecha):
    ''' Dada una fecha, genera el lunes'''
    
    d = fecha.isoweekday()
    if d == 0:
        raise ValueError("No se puede generar la semana para un domingo")
    lunes = fecha - timedelta(days = d - 1) # Empezamos el lunes, que es 1
    sabado = lunes + timedelta(days = 5)
    return lunes, sabado
        
def range_iter(range):
    range = None
            
import sys

def main(argv = sys.argv):
    ''' Funcion main '''
    print "Probando iterador de fecha"
    ti = timeiter('7:30', '12:30', '0:15')
    print ti
    for x in ti.by_time():
        print x
    print "-" * 30
    for x in ti.by_str():
        print x
    
if __name__ == "__main__":
    sys.exit(main())
