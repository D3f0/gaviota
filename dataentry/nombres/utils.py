#! /usr/bin/python
# -*- encoding: utf-8 -*-
from time import time, sleep

pretydict = lambda d: ','.join(['%s = %s' for k, v in d.iteritems()])

def timeit(f):
    '''Decorador para medir el tiempo'''
    def wrapped(*largs, **kwargs):
        t1 = time()
        retval = f(*largs, **kwargs)
        t = time() - t1
        print "%s tomó %f en ejecutarse con argumentos: %s %s" % (
                f.func_name, t, # Nombre de la función y tiempo
                ', '.join(map(str,largs)),  # Lista de argumentos
                pretydict(kwargs),          # Argumentos diccionario
            )
        return retval
    return wrapped
    
if __name__ == "__main__":
    '''
    Pequeñas pruebas
    '''
    print "Probando decorador de medicion de tiempo"
    @timeit
    def slow():
        sleep(1)
        return 1
    assert slow() == 1, "No se ha retornado nada"
    