import pygame
from herramientas import Actor

class ActorAnimado:
    def __init__(self, imagen_inicial, posicion, animaciones_dict, animacion_inicial=None, velocidad=0.1):
        """
        imagen_inicial: primera textura para el Actor
        posicion: tuple (x, y) o posición inicial
        animaciones_dict: {nombre_animacion: [lista_de_texturas]}
        """
        # Crear el Actor
        self.actor = Actor(imagen_inicial, posicion)
        
        self.animaciones = animaciones_dict
        self.velocidad_animacion = velocidad
        self.tiempo_acumulado = 0
        
        # Configurar animación inicial
        if animacion_inicial and animacion_inicial in self.animaciones:
            self.animacion_actual = animacion_inicial
        else:
            self.animacion_actual = list(self.animaciones.keys())[0]
        
        self.frame_actual = 0
        # Establecer la imagen inicial correcta
        self.actor.image = self.animaciones[self.animacion_actual][self.frame_actual]
    
    def update(self, dt):
        """Actualiza la animación del Actor"""
        self.tiempo_acumulado += dt
        if self.tiempo_acumulado >= self.velocidad_animacion:
            self.tiempo_acumulado = 0
            frames = self.animaciones[self.animacion_actual]
            self.frame_actual = (self.frame_actual + 1) % len(frames)
            # Actualizar la imagen del Actor
            self.actor.image = self.animaciones[self.animacion_actual][self.frame_actual]
    
    def cambiar_animacion(self, nombre_animacion, forzar_reinicio=False):
        """Cambia a una animación específica"""
        if nombre_animacion in self.animaciones:
            if forzar_reinicio or nombre_animacion != self.animacion_actual:
                self.animacion_actual = nombre_animacion
                self.frame_actual = 0
                self.tiempo_acumulado = 0
                self.actor.image = self.animaciones[self.animacion_actual][self.frame_actual]
                return True
        return False

    def draw(self, surface):
        """Dibuja el Actor en la superficie proporcionada"""
        self.actor.draw(surface)
    
    def draw_con_offset(self, surface, offset_x=0, offset_y=0, centrado=False):
        """Dibuja el Actor en la superficie proporcionada aplicando offset"""
        self.actor.draw_con_offset(surface, offset_x, offset_y, centrado)

    # Métodos específicos de animación
    def get_animacion_actual(self):
        return self.animacion_actual
    
    def get_frame_actual(self):
        return self.frame_actual
    
    def set_velocidad(self, nueva_velocidad):
        self.velocidad_animacion = nueva_velocidad