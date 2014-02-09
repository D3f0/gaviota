#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from django.db import models
from django.conf import settings #@UnusedImport

from settings import CHARFIELD_MAX_LEN , DIAS_SEMANA, DIAS_SEMANA_DICT, HORARIO, BASE_URL  

from datetime import datetime, date, timedelta, time
from gaviota.apps.aulas.fechas import dateiter #@UnresolvedImport
from django.db.models import signals
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from itertools import imap
from gaviota.log import debug
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


class Recurso(models.Model):
    '''
    Clase abstracata para representar los recursos
    '''
    class Meta:
        abstract = True


class Telefono(models.Model):
    nombre = models.CharField(max_length = 40, blank = True)
    numero = models.CharField(max_length = 20)
    
    def __unicode__(self):
        return '%s%s' % (
                         self.nombre and ('%s ' % self.nombre) or '',
                         self.numero
        )

class Edificio(models.Model):
    nombre = models.CharField(max_length = 70)
    direccion = models.CharField(max_length = 120, blank = True)
    codigo_postal = models.CharField(max_length = 120, blank = True)
    telefonos = models.ManyToManyField(Telefono, blank = True)
    
    
    def aulas_en_orden(self, **kwargs):
        qs = self.aula_set.filter(**kwargs)
        qs.query.order_by = ['nombre', 'id',]
        return qs
        
    def __unicode__(self):
        return u'%s' % (self.nombre, )

class Aula(Recurso):
    #
    # Las aulas del edificio de la facultad son
    # filter( lambda x: x not in ([11, 12, 56, 58, 60, 62] + range(26, 55)), range (1, 64))
    #
    
    numero = models.IntegerField(u'Número de aula', null = True, blank = True)
    nombre = models.CharField(u'Nombre', max_length = CHARFIELD_MAX_LEN, default='Aula')
    capacidad = models.PositiveSmallIntegerField(u'Capacidad de peronas', null = True, blank = True)
    edificio = models.ForeignKey('Edificio', blank = False)
    
    def __unicode__(self):
        return u'%s %s %s' % (self.nombre, self.numero or '',
                              self.capacidad and '(Capacidad: %d)' % self.capacidad or '')
    
    def nombre_corto(self):
        return u'%s %s' % (self.nombre, self.numero or '')
    
    def get_absolute_url(self):
        return u'%s/aulas/horario_aula/%s/' % (BASE_URL, self.id)
    
    def __eq__(self, other):
        if type(self) == type(other):
            if self.numero == other.numero and \
               self.nombre == other.nombre:
                return True
        return False
    
    # @classmethod
    def get_cursoevento_fecha(self, fecha):
        assert type(fecha) == datetime.datetime
    
    class Meta:
        unique_together = ('nombre', 'numero')
    
class Medio(Recurso):
    '''
        Representa un medio como un Proyector, etc.
    '''
    nombre = models.CharField(max_length = CHARFIELD_MAX_LEN)
    
    def __unicode__(self):
        return unicode(self.nombre)

class Facultad(models.Model):
    '''
        Facultad
        Cada facultad tiene un color que la diferencia de las otras a la hora
        de dibujar las tablas.
    '''
    nombre = models.CharField(max_length = CHARFIELD_MAX_LEN)
    color = models.CharField(max_length = 6)
    
    def __unicode__(self):
        return u'Facultad de %s' % self.nombre
    
    def html_color(self):
        estilo = 'width: 20px; height: 20px; background-color: #%s;' % self.color
        estilo += 'border: 1px solid #222'
        return '<div style="%s">&nbsp;</div>' % estilo
    
    html_color.allow_tags = True
    html_color.short_description = 'Color'
    
    class Meta:
        verbose_name_plural = 'Facultades'

class Carrera(models.Model):
    '''
        Carrera
    '''
    facultad = models.ForeignKey('Facultad')
    nombre = models.CharField(max_length = CHARFIELD_MAX_LEN)
    
    def __unicode__(self):
        return u'%s' % self.nombre
    
CUATRIMESTRES = (
    (1, 'Primer Cuatrimestre', ),
    (2, 'Segundo Cuatrimestre', ),
    (3, 'Anual',)
)

ANIOS = map( lambda n: (n, unicode(n)), range(1,6))

class Asignatura(models.Model):
    '''
    Una materia o un curso.
    Si es una materia, el campo regular es verdadero.
    El horario se debería setear en una grilla semanal.
    '''
    
    # Una cátedra puede tener más de un profesor
    persona = models.ManyToManyField('Persona', blank = True)
    
    # Un curso puede estar en más de una carrera
    anio = models.PositiveSmallIntegerField(u'Año', choices = ANIOS)
    
    cuatrimestre = models.PositiveSmallIntegerField(u'Dictado en', 
                                                    choices=CUATRIMESTRES)
    carrera = models.ManyToManyField('Carrera', blank = True)
    
    nombre = models.CharField(max_length = CHARFIELD_MAX_LEN)
    
    descripcion = models.TextField(null=True, default = None, blank = True)
    
    inicio = models.DateField('Fecha de inicio', 
                              null = True, 
                              default = None)
    
    fin = models.DateField('Fecha de finlaización',
                           null = True, 
                           default = None)
    
    cant_alumnos = models.PositiveIntegerField('Cantidad de alumnos', 
                                               blank = True, 
                                               null = True)
    
    #dictado_simultaneo = models.ManyToManyField('Asignatura')
    depende_de = models.ForeignKey('self', blank = True, null = True )
    
    
    def personas_que_la_dictan(self):
        return ', '.join(map(unicode, self.persona.all()))
    
    def carreras(self):
        return '; '.join(map(unicode, self.carrera.all()))
    
    def save(self, force_insert=False, force_update=False):
        '''
        En cada save debemos verificar si se condicen los horarios
        con las instancias de dictado
        '''
        m = models.Model.save(self, force_insert, force_update)
        
        return m

    def nombre_cuatrimestre(self):
        try:
            return dict(CUATRIMESTRES)[self.cuatrimestre]
        except (KeyError, ValueError):
            return u''
        
    def cuatri_corto(self):
        if self.cuatrimestre == 1:
            return u'1°'
        elif self.cuatrimestre == 2:
            return u'2°'
        else:
            return u'Anual'
    
    def dependencia(self):
        if self.depende_de:
            return u'%s (%s)' % (self.depende_de, ','.join(map(unicode, self.depende_de.carrera.all())))
        return u''
    #dependencia.makr_as_safe = True
    
    def __unicode__(self):
        #if self.dictado_simultaneo.count():
        #tmp = u''
        #if self.depende_de:
        #    facultades = ','.join(map( lambda c: unicode(c.facultad), self.depende_de.carrera.all()))
        #    if self.depende_de.nombre == self.nombre:
        #        tail = 'depende de %s' % self.depende_de.nombre.carrera
        #    else:
        #        tail = u' depende de %s (%s)' % (self.depende_de.nombre, facultades)
        #else:
        #    tail = u''
        return u'%s' % (self.nombre, )
    
    class Meta:
        #unique_together = ('nombre','carrera', )
        verbose_name_plural = 'Asignaturas'
        verbose_name = 'Asignatura'
    
    
class UtilizacionAula(models.Model):
    '''
    Existen muchas instancias de UtilizacionAula.
    Se generan con el save() de Asignatura.
    '''
    asignatura = models.ForeignKey('Asignatura', blank = True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha = models.DateField()
    #aulas = models.ManyToManyField('Aula', blank = True, null = True)
    aula = models.ForeignKey('Aula', null = True)
    medios = models.ManyToManyField('Medio', blank = True)
    excepcional = models.BooleanField('Cancelada?')
    horario = models.ForeignKey('Horario', null = True, blank = True)
    
    
    def __unicode__(self):
        #TODO: Verrificar esto
        return u'%s de %s a %s, el %s' % (
                  self.asignatura, self.hora_inicio,
                  self.hora_fin, self.fecha  
                )
        
    def dia_nombre(self):
        return _(self.fecha.strftime('%A'))
        
        
    def nombre_asignatura(self):
        return unicode(self.asignatura)
    
    def lista_medios(self):
        return ', '.join(map(unicode, self.medios.all()))
    
    
    # Campos que no se comparan...
    NO_COMPARE = ['id', 'excepcional', ]
    
    def __eq__(self, other):
        ''' Comparación. Al final no la usamos. '''
        if type(self) == type(other):
            return self.pk == other.pk
        return False
    
    @classmethod
    def get_curso(cls, fecha, hora_inicio, hora_fin, aulas):
        
        if not hasattr(aulas, "__iter__"):
            aulas = [aulas.id, ]
        if type(fecha) == datetime:
            fecha = datetime.date()
        cursos = \
        UtilizacionAula._default_manager.filter(dia = fecha,
                                        hora_inicio__gte = hora_inicio,
                                        #TODO: Ver esto con MySQL, debería ser LTE, FECHAS!!!
                                        hora_fin__gte    = hora_fin,
                                        aulas__id__in = aulas
                                        )
        cant = cursos.count()
        if cant:
            if cant == 1:
                return cursos[0]
            return cursos
    
    
    @classmethod
    def get_range(cls, ini = None, fin = None):
        '''
        Si los parametros inicio y fin son None, entonces se obtie
        la semana
        '''
        query_dict = {}
        if not ini and not fin:
            hoy = datetime.datetime.now()
            isoweekday = hoy.isoweekday()
            ini = hoy - datetime.timedelta(days = isoweekday)
            fin = hoy + datetime.timedelta(days =  6-isoweekday)
        if ini:
            query_dict['dia__gte'] = ini
        if fin:
            query_dict['dia__lte'] = fin 
        return UtilizacionAula.objects.filter(**query_dict)
    
    @classmethod
    def get_dia(cls, dia):
        return UtilizacionAula.objects.filter(dia = dia)
    @classmethod
    def get_hoy(cls):
        hoy = datetime.datetime.now()
        return cls.get_dia(hoy)
    
    class Meta:
        verbose_name_plural = u'Utilización de Aulas (autogenerados a partir de Horario)'
        verbose_name = u'Utilización de Aula'
        
def to_time(string, fmt='%H:%M'):
    if type(string) == time:
        return string
    return datetime.strptime(string, fmt).time()



HORARIO_NULL = [('', '----')] + HORARIO
 
def concatenar_related(model_or_qs, sep = ', ', ret = unicode):
    '''
    Une con coma los elementos relacionados
    '''
    
    if isinstance(model_or_qs, models.Model):
        objs = model_or_qs._default_manager.all()
    else:
        objs = model_or_qs.all()
    
    if not objs:
        return ''
    else:
        return sep.join(map(ret, objs)) 
    

#===============================================================================
# Horario
#===============================================================================

class Horario(models.Model):
    '''
    Horario "Canónico".
    Cada vez que se guarda uno de estos horarios se generan las instancias
    de Dictado.
    '''

    asignatura = models.ForeignKey('Asignatura', blank = True, null = True)
    # Corresponde con el isoweekday de dateitme.date
    dia = models.IntegerField( choices = DIAS_SEMANA)
    hora_inicio = models.TimeField( )
    hora_fin = models.TimeField( )
    aula = models.ForeignKey(Aula, blank = True, null = True)
    # Puede no utilizar medios
    medios = models.ManyToManyField(Medio, blank = True, null = True)
    # Un campo para indiciar si es repetible
    
    def weekday_name(self):
        '''
        Retorna el día de la semana
        '''
        return DIAS_SEMANA_DICT[ self.dia ]
    
    # isoweekday()
    @staticmethod
    def time_from_str(hora, fmt='%H:%M:%S'):
        try:
            tm = time.strptime(hora, fmt)
        except ValueError:
            tm = time.strptime(hora, fmt[:-3])
        return datetime.time(tm.tm_hour, tm.tm_min, tm.tm_sec)
    
    def __unicode__(self):
        # Una materia puede pertenecer a más de una carrer
        try:
            recursos = concatenar_related(self.medios, ret = lambda r: unicode(r.nombre))
        
            if recursos:
                recursos = 'y ' + recursos
            return u'%s el %s de %s a %s utilizando %s %s' % (
                self.asignatura,
                DIAS_SEMANA_DICT [self.dia],
                self.hora_inicio,
                self.hora_fin,
                self.aula,
                recursos
            )
        except ValueError:
            # Si no se pueden navergar las relaciones
            return "Horario"
    
    @staticmethod
    def crear_horarios(instance, sender, created, **kwargs):
        '''
        Atiende la llamada cuando se guarda un cursoevento
        '''
        asignatura = instance
        # Tomamos los horarios
        horarios = asignatura.horario_set.all()
        
        if not created:
            cont_dict = 0
            dictados_viejos = UtilizacionAula.objects.filter(asignatura = asignatura)
            for d in dictados_viejos:
                if not d.excepcional:
                    d.delete()
                    cont_dict += 1
        
        for horario in horarios:
            aulas, medios = horario.aula, horario.medios.all()
            
            inicio, fin = horario.asignatura.inicio, horario.asignatura.fin
            #dictados = horario.asignatura.dictado_set.all()
            for fecha in dateiter(inicio, fin, horario.dia):
                # Mostramos la fecha
            
                # Generamos la instancia de dictado, asociando el cursoevento
                # y convirtiendo las fechas en datetimes
                
                d = UtilizacionAula(dia = fecha,
                            curso_evento = horario.asignatura, 
                            hora_inicio = horario.hora_inicio,
                            hora_fin = horario.hora_fin
                            )
                
                d.save()
                d.aula = horario.aula
                d.medios.add(*medios)
                
                d.save()
                
    def delete(self):
        dictados = UtilizacionAula.objects.filter( horario = self)
        debug('Borrando UtilizacionAula %s' % dictados)
        map (lambda dictado: dictado.delete(), dictados)
        return models.Model.delete(self)
    
    def check_datos_horario(self, dictado):
        if self.dia != dictado.fecha.isoweekday():
            return 
        return False
    
    @staticmethod
    def crear_utilizacionaula_desde_horario(horario, fecha):
        d = UtilizacionAula()
        d.asignatura = horario.asignatura
        d.horario = horario
        d.aula = horario.aula
        d.fecha = fecha
        d.asignatura = horario.asignatura
        d.hora_inicio = horario.hora_inicio
        d.hora_fin = horario.hora_fin
        d.save()
        for m in horario.medios.all():
            d.medios.add(m)
        return d.save()
            
    @staticmethod
    def crear_utiliizacionaula_de_horario(instance, sender, created, **kwargs):
        horario = instance
        
        clean = []  # En caso de que hubiese reducción de Dictados

        # No modificamos lo que ya pasó, solo modificamos los dictados que
        # existen en el futuro.
        #import ipdb; ipdb.set_trace()
        dictados = UtilizacionAula.objects.filter( horario = horario, 
                                           fecha__gte = datetime.now() 
                                           ) # -> QerySet
        hoy = datetime.now().date()
        if not horario.aula:
            debug('Horario sin asignación de aula')
            map(lambda dictado: dictado.delete(), dictados)
            debug('Dicados borrados: %d.' % len(dictados))
            return
            
        for fecha in dateiter(horario.asignatura.inicio,
                              horario.asignatura.fin,
                              horario.dia + 1):
            # Iteración por fecha...
            if not created:
                if fecha < hoy:
                    debug('Saltando dictado transcurrido', fecha)
                    continue
            if not dictados:
                Horario.crear_utilizacionaula_desde_horario(horario, fecha)
                continue
            else:
                try:
                    # Existe un dictado en la fecha?
                    qs = dictados.filter(fecha = fecha)
                    d = qs.get() # Esto debería retronar solo uno...
                    # Esta bandera me permite ver si modifiqué algo
                    # y no acceder a la base si no hubo modificaciones
                    #debug('Actualizando')
                    edit = False
                    # Existe el listado, como único
                    if d.aula != horario.aula:
                        d.aula = horario.aula
                        edit = True
                    if d.hora_inicio != horario.hora_inicio:
                        d.hora_inicio = horario.hora_inicio
                        edit = True
                    if d.hora_fin != horario.hora_fin:
                        d.hora_fin = horario.hora_fin
                        edit = True
                    
                    
                    medios_horario = set(map(lambda h: h.pk, horario.medios.all()))
                    medios_dictado = set(map(lambda i: i.pk, d.medios.all()))
                    debug('Haciendo comparacion entre', medios_horario, 
                                                        medios_dictado)    
                    if medios_horario != medios_dictado:
                        debug('Cambio en medios', medios_horario, medios_dictado)
                        
                        d.medios.clear()
                        for m in horario.medios.all():
                            d.medios.add(m)
                        edit = True
                        
                    if edit:
                        d.save()
                    
                        
                    # Si no se editó, no se hace nada
                    clean.append(d)
                        
                except ObjectDoesNotExist:
                    debug('Creando')
                    # Si no existe un dictado en la fecha, lo creo
                    d = Horario.crear_utilizacionaula_desde_horario(horario, fecha)
                    clean.append(d)
                except MultipleObjectsReturned:
                    debug('Quitando varios...')
                    map( lambda dictado: dictado.delete(), qs.all())
                    d = Horario.crear_utilizacionaula_desde_horario(horario, fecha)
                    clean.append(d)
                
        for d in dictados:
            if not d in clean:
                debug('Borrando %s' % d)
                d.delete()
                
        #print "Debo crear horarios para %s creado %s" % (horario, created)

signals.post_save.connect(Horario.crear_utiliizacionaula_de_horario, Horario)

#signals.post_save.connect(Horario.crear_horarios, Asignatura)

class HorarioFijo(UtilizacionAula):
    '''
    Esta se da una sola vez. Utilizado por eventos.
    
    '''
    # Una descripción
    descripcion = models.CharField("Título", max_length = 400, blank = False, null = True)
    responsable = models.CharField(max_length = 400)
    
    def save(self):
        ''' Guardar '''
        dictado = UtilizacionAula.objects.filter( horario = self)
        super(HorarioFijo, self).save()
    
    def delete(self):
        ''' Borrar '''
        dictado = UtilizacionAula.objects.filter( ) 
        super(HorarioFijo, self).delete()
        
    def __unicode__(self):
        return "Horario Fijo %s" % (self.fecha)
    
    class Meta:
        verbose_name = "Horario transitorios"
        verbose_name_plural = "Horarios transitorios"
    
class Persona(models.Model):
    '''
    Personas, generalmente docentes.
    '''
    
    apellido = models.CharField("Apellido(s)", max_length = CHARFIELD_MAX_LEN)
    nombre = models.CharField("Nombres(s)", max_length = CHARFIELD_MAX_LEN, blank = True, null = True)
    correo_electronico = models.EmailField(u"Correo Electrónico", blank = True, null = True)
    telefono_1 = models.PositiveIntegerField(blank = True, null = True)
    telefono_2 = models.PositiveIntegerField(blank = True, null = True)
    telefono_3 = models.PositiveIntegerField(blank = True, null = True)
    
    def __unicode__(self):
        return u'%s %s' % (self.apellido.upper(), self.nombre )
    class Meta:
        verbose_name = 'Docente'
        

class Evento(models.Model):
    '''
    Un evento es una Jornada, Curso o culquier activdidad que utilize aulas
    pero no sea parte de la avtividad normal de la facultad (no corresponde
    a un cursado de una materia).
    Una vez 
    '''
    nombre = models.CharField(max_length = 100)
    descripcion = models.CharField(max_length = 1024)        
    

class ReservaAula(models.Model):
    '''
    Para las peticiones de aula.
    '''
    solicitante = models.ForeignKey(User)
    materia = models.CharField(max_length = 50)
    cantidad_estimada = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField()
    observaciones = models.CharField(max_length = 400)
    
class ReservaAulaHorario(models.Model):
    reserva = models.ForeignKey('ReservaAula')
    dia = models.CharField(max_length = 1)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
