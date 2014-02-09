def edificios(request):
    from gaviota.apps.aulas.models import Edificio, Facultad, Carrera
    from datetime import datetime
    return {
            'edificios': Edificio.objects.all(),
            'facultades': Facultad.objects.all().order_by('nombre'),
            'carreras' : filter( lambda c: c.asignatura_set.count(), Carrera.objects.all().order_by('facultad__nombre')), 
            'hoy': datetime.now().date()
            }