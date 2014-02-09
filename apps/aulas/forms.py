#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Formularios de administración

from django import forms
from datetime import time,date, timedelta, datetime
from time import strptime
from gaviota.apps.aulas.models import Asignatura, Facultad, Persona
from django.forms.util import ValidationError
from gaviota.apps.aulas.widgets import ColorSelect, CuatrimestreDateWidget
from apps.aulas.models import Horario, HorarioFijo, Aula, Medio, DIAS_SEMANA, Carrera,\
    HORARIO, HORARIO_NULL, ANIOS, CUATRIMESTRES
from django.conf import settings
from gaviota.log import debug
from django.utils.safestring import mark_safe
from gaviota.apps.aulas.fechas import dateiter
from django.utils.encoding import smart_unicode
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from copy import copy

#===============================================================================
# Colores
#===============================================================================
COLORES = [ (k, k) for k in settings.COL_TABLE.split()]

class FacultadForm(forms.ModelForm):
    color = forms.ChoiceField(choices = COLORES, widget = ColorSelect)


class CarreraModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, carrera):
        return smart_unicode(u"%s %s" % (carrera.facultad.nombre.upper(), carrera))

class DependeDeChoiceField(forms.ModelChoiceField):
    # Cuando hay dictado simultaneo
    def label_from_instance(self, asignatura):
        return smart_unicode(u"%s %s" % (asignatura ,', '.join(map(lambda c: "(%s %s)" % (c.nombre, c.facultad.nombre.upper())
                                                                   , asignatura.carrera.all()) )))
    
class AsignaturaForm(forms.ModelForm):
    nombre = forms.CharField(help_text="Nombre de la asignatura, Ej: Contabilidad 1 (Comisión 1)")
    anio = forms.ChoiceField(ANIOS, label = "Año en la carrera")
    carrera = CarreraModelMultipleChoiceField(Carrera.objects.all().order_by('facultad__nombre', 'nombre'), 
                                             help_text = """Para agregar una nueva carrera, vuelva al menu
                                                principal, agregue la carrera y refreseque este formulario""")
    
    inicio = forms.DateField(label = u"Fecha de inicio", initial = date(2009, 2, 16),
                             widget = forms.widgets.TextInput(attrs = {'class': 'vDateField'}),
                             )
    fin = forms.DateField(label = u"Fecha de finalización", initial = date(2009, 6, 30),
                          widget = forms.widgets.TextInput(attrs = {'class': 'vDateField'}),
                          )
    
    depende_de = DependeDeChoiceField(Asignatura.objects.filter().order_by('nombre')  ,
                                        label = 'Depende de',
                                        help_text = u"""
                                        Si la asignatura depde de otra signatura utilizando la MISMA aula y el MISMO
                                        docente, indicar en este campo a que materia corresponde.
                                        """, required = False
                                        )
    def clean_depende_de(self):
        ''' Evitar que una asignatura sea dependiente de si misma '''
        value = self.data.get('depende_de', None)
        if value:
            try:
                asignatura = Asignatura.objects.get(id = value)
            except:
                return
            else:
                if hasattr(self, 'instance') and self.instance and self.instance == asignatura:
                    raise ValidationError('No se puede hacer dependiente a una materia de si misma')
                return asignatura
    
    class Meta:
        model = Asignatura

# Generar un time desde una cadena '12:30'
def time_from_str(cad, fmt = '%H:%M'):
    try:
        timetuple = strptime(cad, fmt)
        return time(timetuple.tm_hour, timetuple.tm_min)
    except:
        return None

class HorarioValidacionMixin(object):
    
    def fechas(self):
        return 
    
    def clean_hora_fin(self):
        '''
        La hora de finalización no puede ser menor que la hora de inicio
        '''
        # Obtenemos el prefijo
        prefix = self.prefix and self.prefix + '-' or ''
        campo = lambda c: self.data.get(prefix + c)
        s_ini, s_fin = campo('hora_inicio'), campo('hora_fin')
        h_ini, h_fin = map(time_from_str, (s_ini, s_fin))

        if h_fin and h_ini and h_fin <= h_ini:
            raise ValidationError(u"La hora de finalización debe se mayor a la de comienzo")
        return s_fin
    
    def clean_aula(self):
        ''' Verificación de la no superposición de Horarios '''
        
        # Lambdas
        prefix = self.prefix and self.prefix + '-' or ''
        campo = lambda c: self.data.get(prefix + c, self.data.get(c))
        id_aula = campo('aula')
        if not id_aula:
            return
        aula = Aula.objects.get(id = id_aula)
        
        return aula
    
        # FIXME: No permitir superposiciones en el futuro.
        hora_inicio, hora_fin = map(lambda h: datetime.strptime(h, '%H:%M').time(),
                                    map(campo, ('hora_inicio', 'hora_fin')))
        
        fecha_inicio, fecha_fin = map(lambda f: datetime.strptime(f, '%Y-%m-%d').date(),
                                      map(campo, ('inicio', 'fin')))
        
        
#        import ipdb; ipdb.set_trace()
        dia = campo('dia')
        if dia:
            # Si es un horario, obtenemos todas las fechas
            fechas = list(dateiter(fecha_inicio, fecha_fin, int(dia) + 1))
        else:
            # Esto por si es una validación de HorarioFijo
            fechas = [ campo('fecha'), ]

        qs_superpos = aula.utilizacionaula_set.filter(
                                                   hora_inicio__gte = hora_inicio,
                                                   # Esto está feo, todavía 
                                                   # no se por que
                                                   hora_fin__lt = hora_fin,
                                                   fecha__in = fechas
                                                   )
        # Si es uno existente, nos excluimos
        if self.instance:
            qs_superpos = qs_superpos.exclude(horario = self.instance)
        
        # Separamos las que tienen horario asociado y las que no
        qs_con_horario = qs_superpos.exclude( horario__isnull = True )
        qs_con_horario.query.group_by = ['horario_id', ]
        
        qs_sin_horario = qs_superpos.exclude( horario__isnull = False )
        
        #superpos = set( map( lambda d: d.horario, qs_superpos) )
        # Hay superposición de horarios?
        
#        if qs_con_horario or qs_sin_horario:
#            from ipdb import set_trace; set_trace()

        texto = u''
        for utilizacion in qs_con_horario:
            
            texto = '''%sAula en uso por el horario de %s a %s de %s
            
            <br />''' % (texto, 
                         utilizacion.horario.hora_inicio,
                         utilizacion.horario.hora_fin,
                         utilizacion.horario.asignatura.nombre)
            
        for utilizacion in qs_sin_horario:
            texto = '''%sAula en uso por el %s<br />''' % (texto, 
                         utilizacion,
                         )
            
        # Si el texto es vacío, tiramos error de validación
        if texto:
            raise ValidationError(mark_safe(texto))

        return aula

class HorarioChoiceField(forms.ChoiceField):
    def __getattribute__(self, name):
        print "HorarioChoiceField", name
        return object.__getattribute__(self, name)


class HorarioChoiceWidget(forms.widgets.Select):
    
    def render(self, name, value, attrs=None):
        if value and type(value) not in (unicode, str):
            value = value.strftime('%H:%M')
        return super(HorarioChoiceWidget, self).render(name, value, attrs)


class AulaModelChoiceField(forms.ModelChoiceField):
    ''' Para facilitar la entrada de aulas '''
    def label_from_instance(self, aula):
        if aula.numero:
            tmp = u'%d' % (aula.numero)
        else:
            tmp = u'%s' % (aula.nombre)
        return u'%s (Capacidad: %s)' % (tmp, aula.capacidad ) 
        
        
class HorarioForm(forms.ModelForm, HorarioValidacionMixin):
    
    hora_inicio = forms.ChoiceField(label = "Hora comienzo",
                                        choices = HORARIO_NULL,
                                        
                                        widget = HorarioChoiceWidget)
                                        #required = False)
    
    hora_fin = forms.ChoiceField(label = u"Hora finalización", 
                                          choices = HORARIO_NULL,
                                          widget = HorarioChoiceWidget)
                                        #required = False)
    aula = AulaModelChoiceField(Aula.objects.all(), required = False, label="Aula", help_text="Puede quedar sin asignar.")
    
    
    def clean(self):
        # Retornar self.cleaned_data
        return super(forms.ModelForm, self).clean()
    
    class Meta:
        model = Horario
    

class HorarioFijoForm(forms.ModelForm, HorarioValidacionMixin):
    hora_inicio = forms.ChoiceField(label = "Hora comienzo",
                                        choices = HORARIO_NULL,
                                        
                                        widget = HorarioChoiceWidget)
                                        #required = False)
    
    hora_fin = forms.ChoiceField(label = u"Hora finalización", 
                                          choices = HORARIO_NULL,
                                          widget = HorarioChoiceWidget)
    class Meta:
        model = HorarioFijo
        exclude = ('horario', 'cancelada', )
        
class HorarioFijoAdminForm(forms.ModelForm):
    
    def __init___(self, *args, **kwargs):
        super(HorarioFijoAdminForm, self).__init__(*args, **kwargs)
        # order now: a b c
        order = ('b', 'c', 'a')
        tmp = copy(self.fields)
        self.fields = SortedDict()
        for item in order:
            self.fields[item] = tmp[item]

    
    descripcion = forms.CharField('Título')
    class Meta:
        model = HorarioFijo
        exclude = ('asignatura', 'cancelada', 'horario',)

CURSO_EVENTO_SEARCH_FMT = (('t', 'Tabla'),
                           ('l', 'Listado'),)


INTERVALOS = (('0:30', '30 minutos'),
              ('1:00', '1 hora'),
              ('1:30', '1 hora 30 minutos'),
              ('2:00', '2 horas'),
              ('2:30', '2 horas 30 minutos'),
              ('3:00', '3 horas'),
              ('3:30', '3 horas 30 minutos'),
              ('4:00', '4 horas'),
              ('4:30', '4 horas 30 minutos'),
              ('5:00', '5 horas'),
              ('5:30', '5 horas 30 minutos'),
              ('6:00', '6 horas'),
               )
TIPOS = [
         ('a', 'Eventos y cursos'),
         ('c', 'Solo Cursos'),
         ('e', 'Solo eventos'),
         ]


class AsignaturaSearchForm(forms.Form):
    '''
    Selección detallada del curso sobre el que se quieren 
    generar los listados.
    '''
    # tipo = forms.ChoiceField(choices = CURSO_EVENTO_SEARCH_FMT)
    # intervalo_horario = forms.ChoiceField(choices = INTERVALOS)
    
    hora_inicio = forms.TimeField(help_text = "Ej: 12:30",
                                 #input_formats = '%H:%M',
                                 label = "Comenzando a partir de la hora", 
                                 required=False,
                                 widget=forms.TimeInput(
                                    attrs={'class':'borrable horario'}))
    
    hora_fin = forms.TimeField(help_text = "Ej: 20:30",
                                 #input_formats = '%H:%M',
                                 label = "Finalizando antes de la hora", 
                                 required=False,
                                 widget=forms.TimeInput(
                                    attrs={'class':'borrable horario'}))
     
    dias = forms.MultipleChoiceField(choices = DIAS_SEMANA, 
                                     widget=forms.CheckboxSelectMultiple(
                                        attrs={'class':'flat'}), 
                                     required = False)
    
    aulas = forms.ModelMultipleChoiceField(Aula._default_manager.all(),
                                    widget = forms.CheckboxSelectMultiple(
                                        attrs={'class':'flat'}),
                                    required=False)
    
    carrera = forms.ModelChoiceField(Carrera._default_manager.all(), 
                                     required = False)
    
    facultad = forms.ModelChoiceField(Facultad._default_manager.all(), 
                                      required = False)
    
    persona = forms.ModelChoiceField(Persona._default_manager.all(), 
                                     required = False)
    
#    tipo = forms.ChoiceField( choices= TIPOS,
#                            help_text = 'Marque esta casilla si se trata de un Evento',
#                            required = False)
    

class FechaHoraSearchForm(forms.Form):
    fecha_inicio = forms.DateField(label="Fecha desde")
    fecha_fin = forms.DateField(label = "Fecha hasta")
    
class UtilizacionPorCantidadForm(forms.Form):
    cantidades = forms.CharField(help_text="""Ingrese las cantidades oerdenadas separadas espacios. Ej: 10 20 40 50""")
    
    
    def clean_cantidades(self):
        value = self.data['cantidades']
        values = value.split(' ')
        int_vals = []
        try:
            for v in values:
                int_vals.append(int(v))
        except:
            raise ValidationError(u'%s no es una entero válido' % v)
        
        for v in int_vals:
            if v <= 0:
                raise ValidationError(u'%s es menor a cero' % v)
            if values.count(v) > 1:
                raise ValidationError(u'%s esta repetido' % v)
        int_vals_ord = copy(int_vals)
        int_vals_ord.sort()
        for i, j in zip(int_vals, int_vals_ord):
            if i != j:
                raise ValidationError(u'Valores sin ordenar: %d' % i)
        
        return int_vals
    
class BusquedaSimple(forms.Form):
    '''
    Fromulario para las búquedas simples
    '''
    TIPOS = (
             (0, 'Clases y eventos'),
             (1, 'Clases'),
             (2, 'Eventos'),
             )
    nombre = forms.CharField(max_length = 50)
    buscar_en = forms.ChoiceField( choices = TIPOS )
    
    
    
class BusquedaPorFechaForm(forms.Form):
    nombre = forms.CharField(max_length = 50)
    fecha_desde = forms.DateField()
    hora_desde = forms.TimeField()
    fecha_desde = forms.DateField()
    fecha_hasta = forms.TimeField()
    
    
    
    
