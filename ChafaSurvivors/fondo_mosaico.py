import pygame
import os
from variable_global import Variables_Globales, RUTAS_FONDOS, COLORES_MUNDOS

class FondoMosaico:
    def __init__(self, mundo_actual):
        self.mundo = mundo_actual
        self.mosaico_original = None
        self.mosaico_escalado = None
        self.tamaño_mosaico = Variables_Globales["TAMAÑO_MOSAICO"]
        self.cargar_mosaico()
        
    def cargar_mosaico(self):
        """Carga y prepara el mosaico para el mundo actual"""
        ruta_fondo = RUTAS_FONDOS.get(self.mundo)
        
        if not ruta_fondo or not os.path.exists(ruta_fondo):
            print(f"Fondo no encontrado para {self.mundo}: {ruta_fondo}")
            print("Usando color de fondo por defecto")
            self.mosaico_original = None
            self.mosaico_escalado = None
            return
        
        try:
            # Cargar la imagen
            self.mosaico_original = pygame.image.load(ruta_fondo)
            
            # Escalar al tamaño deseado
            nuevo_tamaño = (self.tamaño_mosaico, self.tamaño_mosaico)
            self.mosaico_escalado = pygame.transform.scale(self.mosaico_original, nuevo_tamaño)
            
            # Optimizar
            if self.mosaico_escalado.get_alpha():
                self.mosaico_escalado = self.mosaico_escalado.convert_alpha()
            else:
                self.mosaico_escalado = self.mosaico_escalado.convert()
            
            print(f"Mosaico cargado para {self.mundo}: {ruta_fondo} -> {nuevo_tamaño}")
            
        except Exception as e:
            print(f"Error cargando mosaico {ruta_fondo}: {e}")
            self.mosaico_original = None
            self.mosaico_escalado = None
    
    def dibujar(self, screen, camera_offset_x, camera_offset_y):
        """Dibuja el mosaico infinito basado en la posición de la cámara"""
        if not self.mosaico_escalado:
            # Si no hay mosaico, usar color de fondo
            color_fondo = COLORES_MUNDOS.get(self.mundo, (0, 0, 0))
            screen.fill(color_fondo)
            return
        
        # Obtener dimensiones de pantalla
        screen_width, screen_height = screen.get_size()
        mosaico_size = self.tamaño_mosaico
        
        # Calcular cuántos mosaicos necesitamos para cubrir la pantalla
        # Teniendo en cuenta el offset de la cámara
        start_x = int(camera_offset_x) % mosaico_size - mosaico_size
        start_y = int(camera_offset_y) % mosaico_size - mosaico_size
        
        # Número de mosaicos necesarios para cubrir la pantalla
        num_x = (screen_width // mosaico_size) + 3
        num_y = (screen_height // mosaico_size) + 3
        
        # Dibujar mosaicos
        for y in range(num_y):
            for x in range(num_x):
                pos_x = start_x + (x * mosaico_size)
                pos_y = start_y + (y * mosaico_size)
                
                # Verificar si el mosaico está dentro de la pantalla
                if (pos_x + mosaico_size > 0 and pos_x < screen_width and
                    pos_y + mosaico_size > 0 and pos_y < screen_height):
                    
                    screen.blit(self.mosaico_escalado, (pos_x, pos_y))
    
    def cambiar_mundo(self, nuevo_mundo):
        """Cambia el mosaico cuando se cambia de mundo"""
        if nuevo_mundo != self.mundo:
            self.mundo = nuevo_mundo
            self.cargar_mosaico()
    
    def ajustar_tamaño(self, nuevo_tamaño):
        """Ajusta el tamaño del mosaico"""
        if nuevo_tamaño != self.tamaño_mosaico and self.mosaico_original:
            self.tamaño_mosaico = nuevo_tamaño
            Variables_Globales["TAMAÑO_MOSAICO"] = nuevo_tamaño
            
            # Re-escalar el mosaico
            nuevo_tamaño_tuple = (nuevo_tamaño, nuevo_tamaño)
            self.mosaico_escalado = pygame.transform.scale(self.mosaico_original, nuevo_tamaño_tuple)
            
            print(f"Mosaico reescalado a {nuevo_tamaño}x{nuevo_tamaño}")