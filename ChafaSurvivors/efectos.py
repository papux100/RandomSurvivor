import pygame
import time

class EfectoEstado:
    def __init__(self, nombre, duracion):
        self.nombre = nombre
        self.duracion = duracion
        self.tiempo_inicio = time.time()
        
    def esta_activo(self):
        return time.time() - self.tiempo_inicio < self.duracion
    
    def aplicar(self, objetivo, dt):
        pass

class Veneno(EfectoEstado):
    def __init__(self, daño_por_segundo, duracion):
        super().__init__("Veneno", duracion)
        self.daño_por_segundo = daño_por_segundo
        self.tiempo_ultimo_daño = 0
        
    def aplicar(self, objetivo, dt):
        if hasattr(objetivo, 'recibir_daño'):
            self.tiempo_ultimo_daño += dt
            if self.tiempo_ultimo_daño >= 1.0:  # Daño cada segundo
                objetivo.recibir_daño(self.daño_por_segundo)
                self.tiempo_ultimo_daño = 0

class Ralentizacion(EfectoEstado):
    def __init__(self, porcentaje, duracion):
        super().__init__("Ralentización", duracion)
        self.porcentaje = porcentaje
        self.velocidad_original = None
        
    def aplicar(self, objetivo, dt):
        if hasattr(objetivo, 'velocidad'):
            if self.velocidad_original is None:
                self.velocidad_original = objetivo.velocidad
            
            objetivo.velocidad = self.velocidad_original * (1 - self.porcentaje)
    
    def terminar(self, objetivo):
        if self.velocidad_original is not None:
            objetivo.velocidad = self.velocidad_original

class Congelacion(EfectoEstado):
    def __init__(self, duracion):
        super().__init__("Congelación", duracion)
        self.velocidad_original = None
        
    def aplicar(self, objetivo, dt):
        if hasattr(objetivo, 'velocidad'):
            if self.velocidad_original is None:
                self.velocidad_original = objetivo.velocidad
                objetivo.velocidad = 0.1  # Casi detenido
    
    def terminar(self, objetivo):
        if self.velocidad_original is not None:
            objetivo.velocidad = self.velocidad_original

class Maldicion(EfectoEstado):
    def __init__(self, reduccion_daño, duracion):
        super().__init__("Maldición", duracion)
        self.reduccion_daño = reduccion_daño
        self.daño_original = None
        
    def aplicar(self, objetivo, dt):
        if hasattr(objetivo, 'daño'):
            if self.daño_original is None:
                self.daño_original = objetivo.daño
                objetivo.daño *= (1 - self.reduccion_daño)
    
    def terminar(self, objetivo):
        if self.daño_original is not None:
            objetivo.daño = self.daño_original