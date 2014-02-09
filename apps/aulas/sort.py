#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from django.conf import settings
from pprint import pformat
from datetime import datetime
from gaviota.apps.aulas.models import Aula

class DictadoSorter(object):
    ''' Debido a la cantidad de consultas que se generan en una tabla
    de 3600 entradas, usar filter se hace muy lento. Mediante esta
    clase relizamos una buqueda más rápida sobre un queryset preexistente.
    '''
    def __init__(self, qs):
        '''
            Queryset con el conjunto de aulas.
        '''
        self.qs = qs
#        import ipdb; ipdb.set_trace()
        print "Inicializado con", qs.count(), "elementos"
#        dias = set(sorted(map(lambda dic: dic.dia, qs)))
#        aulas_listas = map(lambda d: [ a.numero for a in d.aulas.all()], qs)
#        aulas = set()
#        for numeros in aulas_listas:
#            for n in numeros:
#                aulas.add(n)
#        aulas = set([ d.aulas.all for d in qs ])
#        self.tabla = {}
#        for dia in dias:
#            self.tabla[dia] = {}
#            for aula in aulas:
#                self.tabla[dia][aula] = qs.filter(dia = dia, aulas = aula)
        self.tabla = {}
        for dictado in qs:
            dia = dictado.dia
            if not self.tabla.has_key(dia):
                self.tabla[dia] = {}
            for aula in dictado.aulas.all():
                self.tabla[dia][aula] = qs.filter(dia = dia, aulas = aula)
        
    def __len__(self):
        return self.qs.count()
        
    def get_dictado(self, aula, dia, hora_inicio, hora_fin):
        '''
        El acceso es por aula, hora, dia
        '''
        
        hora_inicio = type(hora_inicio) == datetime and hora_inicio.time() or hora_inicio
        hora_fin = type(hora_fin) == datetime and hora_fin.time() or hora_fin
        assert type(aula) is Aula
        assert type(dia) is datetime, "Tipo de dia: %s" % type(dia)
        
        try:
            cursos_aula_dia = self.tabla[dia][aula]
            if cursos_aula_dia:
                import ipdb; ipdb.set_trace()
            result = []
            
            for curso in cursos_aula_dia:
                # Ojo con el mayor o igual y el menor estricto
                # responde a la misma semántica de los slices
                if hora_inicio >= curso.hora_inicio and hora_fin < curso.hora_fin:
                    result.append(curso)
            # Medio trucho pero nos aseugramos de que no exitan cursos superpuestos
            if not result:
                return
            assert len(result) < 2, "Dos cursos se estan dando en la misma aula al mismo tiempo %s" % result
            return result[0]
        except KeyError:
            return None
        
    def __str__(self):
        return pformat(self.tabla, 2)
    

class HorarioSorter(object):
    def __init__(self, queryset):
        self.queryset = queryset
        self.sort()
        
    def sort(self):
        self.tabla = {}
        for e in self.queryset:
            dia = e.dia
            if not self.tabla.has_key(dia):
                self.tabla[dia] = {}
                for aula in Aula.objects.all():
                    self.tabla[dia][aula] = self.queryset.filter(dia = dia, 
                                                                 aula = aula)
    
    def __len__(self):
        return self.queryset.count()
    
    def get_horario(self, aula, dia, hora_desde, hora_hasta):
        hora_inicio = type(hora_desde) == datetime and hora_desde.time() or hora_desde
        hora_fin = type(hora_hasta) == datetime and hora_hasta.time() or hora_hasta
        assert type(aula) is Aula
        assert type(dia) is datetime, "Tipo de dia: %s" % type(dia)
        raise NotImplementedError('')
        
    
    
def test():
    ''' Prueba sobre este día '''
    from gaviota.apps.aulas.models import Dictado
    from datetime import timedelta, datetime
    from pprint import pprint
    ahora = datetime.now()
    ini = ahora + timedelta(days = -7 )
    fin = ahora + timedelta(days = 7 )
    qs = Dictado.objects.filter( dia__gte = ini, dia__lte = fin)
    print qs
    print qs.count()
    ds = DictadoSorter(qs)
    pprint(ds.tabla)