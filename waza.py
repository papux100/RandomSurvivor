import pygame
import sys
import os

# Inicializar Pygame PRIMERO
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego Pygame")
clock = pygame.time.Clock()

# Ahora importamos nuestros módulos después de inicializar Pygame
from personajes import Personaje
import texturas

# Crear el personaje principal DESPUÉS de inicializar Pygame
protagonista = Personaje(0, 1, 4, texturas.texturas_personaje)
actual="quieto_derecha"

# Bucle principal del juego
running = True
while running:
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Obtener teclas presionadas
    keys = pygame.key.get_pressed()
    
    # Actualizar lógica del juego
    dt = clock.tick(60) / 1000.0  # Delta time en segundos
    

    # Movimiento del personaje
    if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]:
        if keys[pygame.K_w]:
            protagonista.y -= protagonista.velocidad
            if actual=="quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_a]:
            protagonista.x -= protagonista.velocidad
            actual="quieto_izquierda"
            if actual=="quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_s]:
            protagonista.y += protagonista.velocidad
            if actual=="quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_d]:
            protagonista.x += protagonista.velocidad
            actual="quieto_derecha"
            if actual=="quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
    else:
        protagonista.cambiar_animacion(actual)
    
    # Actualizar animaciones
    protagonista.update(dt)
    
    # Dibujar
    screen.fill((50, 100, 50))  # Fondo verde
    protagonista.draw(screen)
    
    # Actualizar pantalla
    pygame.display.flip()

# Salir del juego
pygame.quit()
sys.exit()
