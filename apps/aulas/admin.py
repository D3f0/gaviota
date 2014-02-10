#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from django.contrib import admin
from gaviota.apps.aulas.models import *
from django.conf import settings
from copy import copy
from django import forms
from gaviota.apps.aulas.forms import FacultadForm, HorarioForm, HorarioFijoForm
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from apps.aulas.forms import AsignaturaForm, HorarioFijoAdminForm
from gaviota.log import debug

site = admin.AdminSite()

class AulaAdmin(admin.ModelAdmin):
    search_fields = ('nombre', )
    list_display = ('nombre_corto',  'capacidad', 'edificio', )
    list_display_links = ('nombre_corto',)

    def queryset(self, request):
        """
        Filter based on the current user.
        """
        #raise ValueError('nO!')
        qs = Aula.objects.order_by('-nombre', '-numero')
        #qs.query.order_by = ['nombre', 'numero',]
        return qs

    model = Aula

site.register(Aula, AulaAdmin)

class CarreraAdmin(admin.ModelAdmin):
    model = Carrera
    list_display = ('nombre', 'facultad')
    list_filter = ('facultad', )
    search_fields = ('nombre', )
    def queryset(self, request):
        qs = Carrera.objects.all()
        qs.order_by = ('facultad')
        return qs

site.register(Carrera, CarreraAdmin)


class HorarioInline(admin.TabularInline):
    def formfield_for_dbfield(self, db_field, **kwargs):
        '''
        Ajuste de tamaño de select
        '''

        if db_field.name in ['aulas', 'medios']:
            #kwargs['attrs'] = {'size': 2}
            #dict_args = copy(kwargs)
            #dict_args.has_key('request') and dict_args.pop('kwargs')
            #dict_args = dict_args.pop('request')
            #formfield = db_field.formfield(**dict_args)
            formfield = db_field.formfield()
            formfield.widget.attrs = {'size':5}
            #return formfield
            formfield.widget = RelatedFieldWidgetWrapper(formfield.widget, db_field.rel, self.admin_site)

            return formfield
        return BaseModelAdmin.formfield_for_dbfield(self, db_field, **kwargs)

    model = Horario
    extra = 6
    form = HorarioForm

    #class GalleryItemAdmin(admin.ModelAdmin):
#    def save_model(self, request, obj, form, change):
#        raise Exception('hoigan')
#        super(HorarioInline, self).save_model(request, obj, form, change)
#        debug('Salvando M2M')
#        form.save_m2m()
#        obj.save()


class HorarioFijoInline(admin.TabularInline):

#    def formfield_for_dbfield(self, db_field, **kwargs):
#        '''
#        Ajuste de tamaño de select
#        '''
#
#        if db_field.name in ['aula', 'medio']:
#            #kwargs['attrs'] = {'size': 2}
#            formfield = db_field.formfield()#**kwargs)
#            formfield.widget.attrs = {'size':5}
#            #return formfield
#            formfield.widget = RelatedFieldWidgetWrapper(formfield.widget, db_field.rel, self.admin_site)
#
#            return formfield
#        return BaseModelAdmin.formfield_for_dbfield(self, db_field, **kwargs)
#
    model = HorarioFijo
    extra = 3
    form = HorarioFijoForm
    exclude = (
               #'horario',
               'excepcional',
               )

class HorarioFijoAdmin(admin.ModelAdmin):
    #model = HorarioFijo
    # Oden de los fields
    fields = ('descripcion', 'responsable', 'hora_inicio', 'hora_fin', 'fecha', 'aula', 'medios')
    exclude = (
               #'asignatura',
               'excepcional',
               #'horario',
               )
    form = HorarioFijoAdminForm

site.register(HorarioFijo, HorarioFijoAdmin)

class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dependencia',  'cuatrimestre', 'anio', 'carreras', 'personas_que_la_dictan',
                    'inicio', 'fin', 'cant_alumnos', 'descripcion', )
    search_fields = ('nombre', 'descripcion', )
    #filter_vertical = ('persona',)
    filter_horizontal = ('persona',)

    form = AsignaturaForm
    inlines = [
               HorarioInline,
               # TODO: Fixme
               HorarioFijoInline,
    ]
    class Meta:
        model = Asignatura

    class Media:
        js = (
              settings.MEDIA_URL + 'js/cuatrimestre.js',
        )
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        dirty = False
        try:
            formset.save_m2m()
        except ValueError:
            dirty = True
        for instance in instances:
            instance.user = request.user
            instance.save()
        if dirty:
            formset.save_m2m()

    # TODO: Restringir el depnde de
    def _formfield_for_dbfield(self, db_field, **kwargs):
        '''
        Ajuste de tamaño de select
        '''

        if db_field.name in ['depende_de']:
            print kwargs.keys()
            #formfield = db_field.formfield()
            #formfield.widget.attrs = {'size':5}
            #return formfield
            #formfield.widget = RelatedFieldWidgetWrapper(formfield.widget, db_field.rel, self.admin_site)

            #return formfield
        return BaseModelAdmin.formfield_for_dbfield(self, db_field, **kwargs)


site.register(Asignatura, AsignaturaAdmin)

class UtilizacionAulaAdmin(admin.ModelAdmin):
    list_display = ('nombre_asignatura',
                    'fecha',
                    'dia_nombre',
                    'hora_inicio',
                    'hora_fin',
                    'aula',
                    'lista_medios',
                    )
    search_fields = ('asignatura__nombre', 'aula__nombre',  )
#    list_filter = ('aulas', )
    model = UtilizacionAula

#site.register(UtilizacionAula, UtilizacionAulaAdmin)

class FacultadAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'html_color', )
    model = Facultad
    form = FacultadForm

    class Media:
        js = (
              settings.MEDIA_URL + 'js/colores.js',
        )

class HorarioAdmin(admin.ModelAdmin):

    list_display = ('asignatura', 'dia', 'hora_inicio', 'hora_fin', 'aula',)
    #search_fields = ('curso_evento__nombre',  )
    form = HorarioForm
    model = Horario

#site.register(Horario , HorarioAdmin)

site.register(Facultad, FacultadAdmin)
site.register(Medio)


#site.register(Telefono)
#site.register(Carrera)

class PersonaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'correo_electronico', )#'telefono_1', 'telefono_2',)
    list_display_links = ('nombre', 'apellido', )
    search_fields = ('nombre', 'apellido', 'correo_electronico')

site.register(Persona, PersonaAdmin)

#site.register( HorarioFijo )

class AulaInline(admin.TabularInline):
    model = Aula

class EdificioAdmin(admin.ModelAdmin):
    inlines = (
               AulaInline,
               )

# site.register(Edificio, EdificioAdmin)