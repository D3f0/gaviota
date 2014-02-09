#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from django.template import Library

from gaviota.apps.aulas.sort import DictadoSorter
from datetime import datetime, time, date, timedelta
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
import simplejson
from time import time as get_time
from gaviota.apps.aulas.models import DIAS_SEMANA as dias
from gaviota.local_settings import DIAS_SEMANA
from gaviota.apps.aulas.models import Aula, UtilizacionAula, Asignatura
from itertools import cycle

register = Library()

@register.simple_tag
def generar_listado_aulas(aulas, fecha1, fecha2, horario, dias, dictados):
    '''
    Este template tag genera el listado de aulas en una tabla. En el template
    se agrega una función JavaScript para mostrar un tooltip
    '''
    
    if type(dictados) == QuerySet:
        if dictados.model == Dictado:
            dictados = DictadoSorter(dictados)
        else:
            raise ValueError('Se paso un QuerySet que no es de Dictado al templatetag')
    elif type(dictados) != DictadoSorter:
        raise ValueError('No se paso ni un DictadoSorter ni un QuerySet de Dictados')
    
    t1 = get_time()
    
    tmpl = u'<table class="listado_aulas"><tr><th colspan="2">Aula</th>%s</table>'
    
    contenido = u'' 
    for aula in aulas:
        contenido = u'%s<th>%d<span class="tip-message">Aula número %d</span></th>' % (contenido, aula.numero, aula.numero) 
    contenido = u'%s</tr>' % contenido # Cerramos la primera fila
    
    # TODO: Revisar la fecha
    for numero_dia, dia in dias:
        long_horas = 0
        tmp = '<tr>'
        
        for hora_str, hora_dt in horario.by_str_dt():
            long_horas += 1
            tmp = u'%s<th>%s</th>\n' % (tmp, hora_str)
            hora_inicio, hora_fin = hora_dt, hora_dt + horario.salto 
            
            for aula in aulas:
                fecha_dia = fecha1 + timedelta(days = numero_dia)
                curso = dictados.get_dictado(aula, fecha_dia, hora_inicio, hora_fin)
                #import ipdb; ipdb.set_trace()
                if curso:
                    #import pdb
                    #pdb.set_trace()
                    color = curso.asignatura.carrera.all()[0].facultad.color
                else:
                    color = u'#fff'
                
                #TODO: Modificar el dia
                dia_str = ''
                    
                tmp = u'''%s<td class="aula_hora" style='color: %s';>
                    <div class="data" style="display:none">%s</div>
                    </td>''' % (tmp,
                                color,
                                simplejson.dumps({'dia': numero_dia,
                                                  'hora': hora_str,
                                                  'aula': aula.numero,
                                                  'fecha': dia_str
                                                      })
                                )
                    
            tmp = '%s</tr>' % tmp
        contenido = u'%s<tr><th rowspan="%d">%s</th>%s</tr>\n' % \
            (contenido,
             #tmp,
             long_horas + 1,
             dia,
             tmp)
    
    retval = tmpl %contenido
    return retval

@register.simple_tag
def generar_html_tabla_aulas(fecha, horario):
    '''
    Genera el listado de aulas para una semana.
    '''
    if fecha.weekday() == 6: # Domingo?
        fecha += timedelta(days=1) #Lunes siguiente
    fecha1 = fecha - timedelta( days = fecha.weekday() ) # Buscamos el lunes
    fecha2 = fecha + timedelta( days = 5 - fecha.weekday() ) # Buscamos el sábado
    u_aulas_qs = UtilizacionAula.objects.filter(fecha__lte = fecha2, fecha__gte = fecha1)
    utilizaciones = TablaUtilizacion(u_aulas_qs)
    aulas = Aula.objects.all()
    
    tmpl = u'<table class="listado_aulas"><tr><th colspan="2">Aula</th>%s</table>'
     
    contenido = u'' 
    for aula in aulas:
        contenido = u'%s<th>%d<span class="tip-message">Aula número %d</span></th>' % (contenido, aula.numero, aula.numero) 
    contenido = u'%s</tr>' % contenido # Cerramos la primera fila
     
    for numero_dia, dia in dias:
        long_horas = 0
        tmp = '<tr>'
        
        for hora_str, hora_dt in horario.by_str_dt():
            long_horas += 1
            tmp = u'%s<th>%s</th>\n' % (tmp, hora_str)
            hora_inicio, hora_fin = hora_dt, hora_dt + horario.salto 
            
            for aula in aulas:
                fecha_dia = fecha1 + timedelta(days = numero_dia)
                curso = utilizaciones.get_dictado(aula, fecha_dia, hora_inicio, hora_fin)
                #import ipdb; ipdb.set_trace()
                curso = None
                if curso:
                    #import pdb
                    #pdb.set_trace()
                    color = curso.asignatura.carrera.all()[0].facultad.color
                else:
                    color = u'#fff'
                
                #TODO: Modificar el dia
                dia_str = ''
                    
                tmp = u'''%s<td class="aula_hora" style='color: %s';>
                    <div class="data" style="display:none">%s</div>
                    </td>''' % (tmp,
                                color,
                                simplejson.dumps({'dia': numero_dia,
                                                  'hora': hora_str,
                                                  'aula': aula.numero,
                                                  'fecha': dia_str
                                                      })
                                )
                    
            tmp = '%s</tr>' % tmp
        contenido = u'%s<tr><th rowspan="%d">%s</th>%s</tr>\n' % \
            (contenido,
             #tmp,
             long_horas + 1,
             dia,
             tmp)
    
    retval = tmpl % contenido
    return retval

class TablaUtilizacion(object):
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


        self.tabla = {}
        for utiliza in qs:
            fecha = utiliza.fecha
            if not self.tabla.has_key(fecha):
                self.tabla[fecha] = {}
            self.tabla[fecha][utiliza.aula] = qs.filter(fecha = fecha, aula = utiliza.aula)
        
    def __len__(self):
        return self.qs.count()
        
    def get_dictado(self, aula, dia, hora_inicio, hora_fin):
        '''
        El acceso es por aula, hora, dia
        '''
        
        hora_inicio = type(hora_inicio) == datetime and hora_inicio.time() or hora_inicio
        hora_fin = type(hora_fin) == datetime and hora_fin.time() or hora_fin
        assert type(aula) is Aula
        #assert type(dia) is datetime, "Tipo de dia: %s" % type(dia)
        
        try:
            cursos_aula_dia = self.tabla[dia][aula]
            #if cursos_aula_dia:
                #import ipdb; ipdb.set_trace()
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
        
#    def __str__(self):
#        return pformat(self.tabla, 2)


@register.simple_tag
def color_de(aula, numero_dia, hora):
    hora = datetime.strptime(hora, '%H:%M').time()
    horario = aula.horario_set.filter(dia = numero_dia, hora_inicio__lte = hora, hora_fin__gt = hora)
    if horario and horario.count() == 1:
        horario = horario.get()
        return 
    
    return u'FFFFFF'


@register.simple_tag
def dibujar_celda_horario_de(aula, numero_dia, hora_str):
    
    hora = datetime.strptime(hora_str, '%H:%M').time()
    horario = aula.horario_set.filter(dia = numero_dia, 
                                      hora_inicio__lte = hora, 
                                      hora_fin__gt = hora)
    # Un solo horario, esto es lo más normal
    if horario.count() == 1:
        horario = horario.get()
        colores = map( lambda c: c.facultad.color, horario.asignatura.carrera.all())
        colores = list(set(colores)) # Eliminamos duplicados
        #import ipdb; ipdb.set_trace()
        
        #horario.asignatura.carrera.all()
        return mark_safe(""" 
        <td style="background-color: #%(color)s; text-align: center; padding: 2px;" class="simple horario_%(horario_id)d"> 
        <b>%(nombre)s<br/></b> 
        <small>%(personas)s</small>
        
        </td>
        """ % { 
                          'color' : colores[0], 
                          'nombre': horario.asignatura.nombre,
                          'personas': '; '.join(map(unicode, horario.asignatura.persona.all())),
                          'horario_id': horario.id, 
            }
        )
    
    # Celda sin horarios
    elif horario.count() == 0:
        return mark_safe(u"""<td style='width: 18%; position: relative;' class="horario"><p style="font-size: 8px; top: 2px; left: 2px; "></p></td>""")
    # Varias materias superpuestas
    else:
        texto_materias = u''
        colores = set()
        for h in horario:
            map( lambda c: colores.add( c.facultad.color), h.asignatura.carrera.all() )
            texto_materias = '''%(texto_materias)s<b>%(nombre)s<br/></b> 
                                <small>%(personas)s</small><br />''' % {
                                                      'texto_materias': texto_materias, 
                                                      'nombre': h.asignatura.nombre,
                                                      'personas': '; '.join(map(unicode, h.asignatura.persona.all())),
                                                  }
        # Recorrimos todos los horarios de la celda
        if len(colores) == 1:
            color = colores.pop() # No se indexan los conjuntos
            frente = ''
        else:
            color = '#000'
            frente = 'red'
        
        clase_css_horarios = "superposicion_%s" % '_'.join([ str(h.id) for id in horario])
        
        return mark_safe(u'''
            <td style="background-color: #%(color)s; color: #(frente)s text-align: center; padding: 0px;
                border: 2px solid red; font-style: oblique;" class="superpuesto %(horario_id)s"
            >
                %(texto_materias)s
            </td>
        ''' % { 'texto_materias': texto_materias,
                'color': color,
                'frente': frente,
                'horario_id': clase_css_horarios,
               })
        
@register.simple_tag                                                                  
def horario_del_dia(asignatura, dia):
    horarios = list(asignatura.horario_set.filter(dia = dia))
    if asignatura.depende_de:
        horarios += list(asignatura.depende_de.horario_set.filter(dia = dia))
    
    salida = []
    for horario in horarios:
        salida.append(
                u'%s - %s <br /><b>%s</b>' % (
                                             horario.hora_inicio.strftime('%H:%M'),
                                             horario.hora_fin.strftime('%H:%M'),
                                             horario.aula and horario.aula.nombre_corto() or "Sin aula asignada",
                                             )
            )
    return mark_safe(u'<br />'.join(salida))

def vertical(cadena):
    if cadena:
        return '%s<br />' % '<br />'.join(cadena)
    return u''

@register.simple_tag
def tabla_ocupacion(aulas, 
                    fecha_base, 
                    dias, 
                    rango_horario, 
                    tabla_horario, 
                    opts = None):
    '''
    Genera el contenido de la tabla de horarios
    '''
    # Fila de encabezado
    tmp = u'<tr><th colspan="2"></th>'
    #import ipdb; ipdb.set_trace()
    for aula in aulas:
        tmp = u'%s<th>' % tmp
        if aula.numero:
            tmp = u'%s %d' % (tmp, aula.numero)
        else:
            tmp = u'%s %s' % (tmp, vertical(aula.nombre))
        if aula.capacidad:
            tmp = u'%s<br /> %s' % (tmp, u'(%d)' % aula.capacidad)
        tmp = '%s</th>' % tmp
    tmp = '%s</tr>\n' % (tmp)
    # Los horarios son fijos y se van a iterar varias veces, necesito
    # por eso los convierto en una lista.
    horarios = list(rango_horario)
    
    for num, dia in dias:
        tmp = u'%s <tr><th rowspan="%d">%s</th></tr>' % (tmp, 
                                                        len(horarios) + 1,
                                                        vertical(dia))
        for hora in horarios:
            tmp = u'%s<tr><td>%s</td>' % (tmp, hora.strftime('%H:%M'))
            for aula in aulas:
                tmp = u'%s <td>&nbsp;</td>' % tmp
            tmp = u'%s</tr>\n' % (tmp, )
        tmp = '%s\n' % (tmp, )
    
    return tmp