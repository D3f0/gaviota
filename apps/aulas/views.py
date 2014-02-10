#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from gaviota.apps.aulas.models import Aula, Asignatura, DIAS_SEMANA, UtilizacionAula, Horario
from gaviota.apps.aulas.models import Edificio
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from gaviota.apps.aulas.fechas import timeiter
from datetime import datetime, timedelta, date
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models.query_utils import Q
from gaviota.apps.aulas.forms import AsignaturaSearchForm
from gaviota.apps.aulas.fechas import semana_de

from datetime import datetime, timedelta
#from descom.middleware import threadlocals
from gaviota.log import debug
from apps.aulas.forms import UtilizacionPorCantidadForm, BusquedaSimple
from apps.aulas.models import Facultad, Carrera
from django.utils.datastructures import SortedDict
from django.utils.html import escape
from django.conf import settings

# Para la salida en Excel
from cStringIO import StringIO
from apps.aulas.fechas import dateiter
from apps.aulas.sort import HorarioSorter
import xlwt

def index(request):
    return render_to_response('aulas/index.html',
                              {
                               'edificios': Edificio.objects.all(),
                               },
                               context_instance=RequestContext(request))

def mostrar_dia(request, y, m, d, aulas = None):
    y, m, d = map(int, (y, m, d))
    fecha = date(y,m,d)
#    if not aulas:
#        aulas = Aula._default_manager.all()
#
#    dictados = Dictado._default_manager.all()
#    # Generamos el rango de una semana
#    fecha1, fecha2 = semana_de( datetime(int(y), int(m), int(d)) )
#
    horario = timeiter('7:00', '23:30', '0:30')
#    #dias = [ DIAS_SEMANA[i] for i in (1, 3, 4)]
#    dias = DIAS_SEMANA
#    conj_dictados = None
    # Basicamete le delegamso todo al template tag
    return render_to_response('aulas/semana.html', {
                'fecha': fecha,
                'horario': horario,
            },
            context_instance=RequestContext(request))

def buscar_index(request):
    '''
        Punto de entrada a las buquedas
    '''
    if request.method == "GET":
        form = AsignaturaSearchForm()
    else:
        form = AsignaturaSearchForm(request.POST)
        if form.is_valid():
            # Vamos a construir la query en función de los valores
            # del formulario.
            query_horario = []
            get = lambda name: form.cleaned_data.get(name)

            hora_inicio =  get('hora_inicio')
            hora_fin = get('hora_fin')
            aulas = get('aulas')
            dias = get('dias')

            persona = get('persona')
            carrera = get('carrera')
            facultad = get('facultad')

            if hora_inicio:
                query_horario.append(Q(hora_inicio__gte = hora_inicio))

            if hora_fin:
                query_horario.append(Q(hora_fin__lte = hora_fin))

            if aulas:
                query_horario.append(Q(aula__in = aulas))

            if dias:
                print dias
                query_horario.append(Q(dia__in = dias))

            if persona:
                query_horario.append(Q(asignatura__persona = persona))

            if carrera:
                query_horario.append(Q(asignatura__carrera = carrera))

            if facultad:
                query_horario.append(Q(asignatura__carrera__facultad = facultad))
            #import ipdb; ipdb.set_trace()
            resultado = Horario.objects.filter(*query_horario)


#            import ipdb; pdb.set_trace()

            resultado = [ h.asignatura for h in resultado ]
            resultado = set(resultado)

            return render_to_response('aulas/resultado_busqueda.html',
                               {
                                'resultado' : resultado,

                                },
                               context_instance=RequestContext(request))

    return render_to_response('aulas/busqueda/buscar-simple.html', {'form':form}, context_instance=RequestContext(request))

def busqueda_simple(request):

    form = BusquedaSimple()
    return render_to_response('aulas/busqueda/buscar-simple.html',
                              {'form':form},
                              context_instance=RequestContext(request))

#===============================================================================
# pedidos
#===============================================================================
def pedidos(request):
    '''
    Pedidos de aulas
    '''
    form = AulaRequestForm()
    data = {
            'form': form,
            }
    return render_to_response('aulas/pedidos.html', data, context_instance=RequestContext(request))

def horario_aula(request, id):
    aulas = Aula.objects.all()
    aula = get_object_or_404(Aula, id=id)
    #aula = aulas.get( id = id)
    return render_to_response('aulas/tabla_aula.html', locals(), context_instance=RequestContext(request))

def mostrar_edificio(request, edificio_id):
    '''
    Motrar las aulas de un edificio.
    '''
    edificio = get_object_or_404(Edificio, id=edificio_id)
    aulas_edificio = edificio.aula_set.all().order_by('capacidad') # TODO: Hacer funcionar

    return render_to_response('aulas/listado_aulas_edificio.html', locals(), context_instance=RequestContext(request))

def horario_aula_excel(request, id):
    aula = get_object_or_404(Aula, id=id)
    data = {
            'aula': aula,
            'excel': True,
            }
    response = render_to_response('aulas/listado_horario_aula.html', data,
                                  context_instance=RequestContext(request))
    filename = "horario-%s.xls" % (aula.nombre_corto())
    filename = filename.replace(' ', '-')
    response['Content-Disposition'] = 'attachment; filename='+filename
    response['Content-Type'] = 'application/vnd.ms-excel;charset=utf-8;'
    response['Content-Encoding'] = 'utf-8'

    return response

def horario_aula_excel_xlwt(request, id, encoding = 'utf8'):
    aula = get_object_or_404(Aula, id=id)

    output = StringIO()
    excel = xlwt.Workbook(encoding = encoding)
    hoja = excel.add_sheet('Horarios %s' % aula.nombre_corto())

    # Definicion de estilo
    borders = xlwt.Borders()
    borders.left = 3
    borders.right = 3
    borders.top = 3
    borders.bottom = 3
    estilo_bordes = xlwt.XFStyle()
    estilo_bordes.borders = borders

    # Definición de estilo
    estilo_celda_horario = xlwt.Style.easyxf(strg_to_parse = "font: bold on; align: wrap on, vert centre, horiz center" )
    estilo_celda_horario.borders = xlwt.Borders()
    estilo_celda_horario.borders.left = 1
    estilo_celda_horario.borders.right = 1
    estilo_celda_horario.borders.top = 1
    estilo_celda_horario.borders.bottom = 1

    # FEO FEO FEO
    hoja._Worksheet__portrait = 0
    # Título
    hoja.write_merge(0, 0, 0, 6, 'Horarios del aula %s' % aula.nombre_corto(), estilo_celda_horario)

    hoja.col(0).width = 1600

    hoja.papersize_code = 8

    for n, dia in enumerate(settings.DIAS_SEMANA_DICT.values()):
        hoja.write(1, n+1, dia, estilo_bordes)
        hoja.col(n+1).width = 1600 + 5* 500

    for n, hora in enumerate(settings.HORAS):
        #hoja.write()
        hoja.write( n +2, 0, hora, estilo_bordes)

    for horario in aula.horario_set.all():
        col = horario.dia + 1
        fila_inicio = (horario.hora_inicio.hour - 7) * 2 + ((horario.hora_inicio.minute == 30) and 1 or 0)
        fila_fin = (horario.hora_fin.hour - 7)* 2 + ((horario.hora_fin.minute == 30) and 1 or 0) - 1
        hoja.write_merge(fila_inicio + 2,fila_fin + 2,col,col, unicode(horario.asignatura.nombre), estilo_celda_horario)


    excel.save(output)
    output.seek(0)
    filename = "horario-aula-%s.xls" % aula.nombre_corto().encode('utf-8').decode('string_escape')
    filename = filename.replace(' ', '-')
    response = HttpResponse(output.getvalue())
    response['Content-Disposition'] = 'attachment; filename='+filename
    response['Content-Type'] = 'application/vnd.ms-excel;charset=utf-8;'
    response['Content-Encoding'] = 'utf-8'
    return response


def horario_facutlad(request, facultad_id):
    #facultad = get_object_or_404(Facultad, id = id_facultad)
    return

def estadisticas_utilizacion(request):
    '''
    Realiza la estadística:
        _________________________________
        |    | Cant 1 | Cant 2 | Cant 3 |
        | F1 |        |        |        |
        | F2 |        |        |        |
        | F3 |        |        |        |
        _________________________________
    '''
    if request.method == "POST":
        facultades = Facultad.objects.all().order_by('-nombre')
        form = UtilizacionPorCantidadForm(request.POST)

        if form.is_valid():
            intervalos = form.cleaned_data['cantidades']
            resultado = {}

            for facultad in facultades:
                #carreras =  filter ( lambda c: c.asignatura_set.count(), facultad.carrera_set.all())

                cantidades = []
                asignaturas = set()
                for carrera in facultad.carrera_set.all():
                    # A cada asignatura le pido la cantidad de alumnos que sean > 0
                    for a in carrera.asignatura_set.all():
                        asignaturas.add(a)
                cantidades += filter( lambda c: c, map( lambda x: x.cant_alumnos, asignaturas))
                cantidades.sort()
                fac_cant = {}
                for i, inter in enumerate(intervalos):
                    if i == 0:
                        fac_cant[inter] = len(filter( lambda n: n > 0 and n <= inter, cantidades ))
                    else:
                        fac_cant[inter] = len(filter( lambda n: n > intervalos[ i -1 ] and n <= inter , cantidades ))
                fac_cant[inter + 1] = len(filter( lambda n: n > inter, cantidades ))

                resultado[facultad] = fac_cant.values()
            titulos = []
            for i, v in enumerate(intervalos):
                if i == 0:
                    titulos.append('Entre 0 y %d' % v)
                else:
                    titulos.append('Entre %d y %d' % (intervalos[i-1] + 1, v))
            titulos.append('Mayor a %d' % (v + 1))

    else:
        form = UtilizacionPorCantidadForm()

    return render_to_response('aulas/estadistica_uso_aula.html', locals(), context_instance=RequestContext(request))


def superposiciones(request):
    '''
    Mostrar las superposiciones entre los horarios, ordenados por aula.
    '''
    aulas = Aula.objects.all()
    superpos_aula = SortedDict()
    # Por cada aula
    for aula in aulas:
        superposicion_parcial = set()
        for dia, _ in DIAS_SEMANA:
            # Horarios de ese día
            horarios = list(aula.horario_set.filter(dia = dia))
            for horario in horarios:
                otros_horarios = filter(lambda x: x is not horario, horarios)

                for otro in otros_horarios:
                    if horario.hora_inicio > otro.hora_inicio and \
                        otro.hora_fin <= horario.hora_inicio:
                        continue
                    elif horario.hora_inicio < otro.hora_inicio and \
                        horario.hora_fin <= otro.hora_inicio:
                        continue
                    superpos = [ horario, otro ]
                    superpos.sort( cmp = lambda h1, h2: cmp(h1.asignatura.nombre, h2.asignatura.nombre) )
                    superposicion_parcial.add( tuple(superpos) )

        if superposicion_parcial:
            superpos_aula[ aula ] = superposicion_parcial


    data = { 'superpos_aula': superpos_aula }
    return render_to_response('aulas/superposiciones.html', data, context_instance=RequestContext(request))


def horario_carrera(request, carrera_id):
    carrera = get_object_or_404(Carrera, id = carrera_id)
    resultado  = {}
    # Anios
    asignaturas = carrera.asignatura_set.all()
    anios = list(set(map(lambda a: a.anio, asignaturas)))
    anios.sort()

    for anio in anios:
        asignaturas_anio = asignaturas.filter(anio = anio).order_by('nombre')
        resultado[ anio ] = asignaturas_anio

    data = {'carrera': carrera,
            'asignaturas': resultado
            }
    return render_to_response('aulas/horario_carrera.html', data, context_instance=RequestContext(request))

def horario_carrera_excel(request, carrera_id):
    carrera = get_object_or_404(Carrera, id = carrera_id)
    resultado  = {}
    # Anios
    asignaturas = carrera.asignatura_set.all()
    anios = list(set(map(lambda a: a.anio, asignaturas)))
    anios.sort()

    for anio in anios:
        asignaturas_anio = asignaturas.filter(anio = anio).order_by('nombre')
        resultado[ anio ] = asignaturas_anio

    data = {'carrera': carrera,
            'asignaturas': resultado,
            'excel': True,
            }
    response = render_to_response('aulas/tabla_horario_carrera.html', data, context_instance=RequestContext(request))

    filename = "horario-carrera-%s.xls" % carrera.nombre.encode('utf-8').decode('string_escape')

    filename = filename.replace(' ', '-')
    response['Content-Disposition'] = 'attachment; filename='+filename
    response['Content-Type'] = 'application/vnd.ms-excel;charset=utf-8;'
    response['Content-Encoding'] = 'utf-8'

    return response

def horario_carrera_excel_xlwt(request, carrera_id):
    ''' Generar el horario mediante XLWT '''
    carrera = get_object_or_404(Carrera, id = carrera_id)
    resultado  = {}


def horarios_dia(request):
    '''
    Generar la tabla de los horarios de un mismo día x todas las aulas:
    ___________________________________________
    |       | aula | aula | aula | ... | aula |
    | 7:30  | xxx  | xxx  | xxx  |     |      |
    ___________________________________________
    '''
    pass


def sin_asignar(request):
    facultad_asig = SortedDict()
    for f in Facultad.objects.all():
        horarios_no_asignados = Horario.objects.filter( aula__isnull = True, asignatura__carrera__facultad = f)
        if horarios_no_asignados:
            facultad_asig[f] = horarios_no_asignados
    data = {
            'horarios': facultad_asig,
            }
    return render_to_response('aulas/sin_asignar.html', data, context_instance=RequestContext(request))

def horario_dia(request, n_dia):
    aulas = Aula.objects.all().order_by('-capacidad')
    dia = dict(settings.DIAS_SEMANA)[int(n_dia)]

    data = {
            'aulas': aulas,
            'dia': dia,
            'n_dia': n_dia,
            }
    return render_to_response('aulas/por_dia.html', data, context_instance=RequestContext(request))


def tabla(request,
          fecha_base = datetime.today(),
          dias = None,
          aulas = None,
          hora_inicio = settings.HORAS[0],
          hora_fin = settings.HORAS[-1],
          ):
    '''
    Tabla de horarios, iteración, día de la semana, horario, aula.
    '''
    q_dict = {}

    if dias:
        q_dict['dia__in'] = dias

    if aulas:
        q_dict['aula__in'] = aulas

    if hora_inicio:
        q_dict['hora_inicio__gte'] = hora_inicio

    if hora_fin:
        q_dict['hora_fin__lt'] = hora_fin

    horarios = Horario.objects.filter(**q_dict)
    tabla_horario = HorarioSorter(horarios)
    #return HttpResponse('hola %s %s %s %s' % (hora_inicio, hora_fin, dias, horarios.count()))
    datos = {
             'aulas': aulas or Aula.objects.all(),
             'fecha_base': fecha_base,
             'dias': dias or settings.DIAS_SEMANA,
             'rango_horario': timeiter('13:00', '23:00', '0:30'),
             'tabla_horario': tabla_horario,
             }
    return render_to_response("aulas/tablas/tabla.html", datos,
                              context_instance=RequestContext(request))