import pygame
import sys
import os
import random
import math

# Inicializar Pygame PRIMERO
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego Pygame")
clock = pygame.time.Clock()

# Ahora importamos nuestros módulos después de inicializar Pygame
from personajes import Personaje
from enemigo import Enemigo
import texturas
from colisiones import manejar_colisiones  # Importar el sistema de colisiones

# Crear el personaje y enemigos principal DESPUÉS de inicializar Pygame
protagonista = Personaje(0, 1, 4, texturas.texturas_personaje)
actual = "quieto_derecha"

# Configurar hitbox del protagonista (más pequeña que la imagen)
protagonista.set_hitbox((30, 40), (0, 5))

# Lista para almacenar enemigos
enemigos = []

# Función para generar enemigos alrededor del protagonista
def generar_enemigo_alrededor():
    # Radio de aparición (aleatorio entre 150 y 300 píxeles)
    radio = random.randint(150, 300)
    
    # Ángulo aleatorio en radianes
    angulo = random.uniform(0, 2 * math.pi)
    
    # Calcular posición basada en el ángulo y radio
    x = protagonista.x + radio * math.cos(angulo)
    y = protagonista.y + radio * math.sin(angulo)
    
    # Asegurar que el enemigo no salga de los límites de la pantalla
    x = max(50, min(WIDTH - 50, x))
    y = max(50, min(HEIGHT - 50, y))
    
    # Crear el enemigo
    nuevo_enemigo = Enemigo(
        experiencia=0,
        vida=1,
        velocidad=random.uniform(1.5, 2.5),  # Velocidad aleatoria
        animaciones_dict=texturas.texturas_personaje,
        follow=protagonista,
        pos=(x, y)
    )
    
    # Configurar hitbox del enemigo
    nuevo_enemigo.set_hitbox((30, 40), (0, 5))
    
    return nuevo_enemigo

# Generar algunos enemigos iniciales
for _ in range(3):
    enemigos.append(generar_enemigo_alrededor())

# Variables para controlar la generación de enemigos
tiempo_ultimo_enemigo = 0
intervalo_enemigos = 3.0  # Segundos entre generación de enemigos

# Bucle principal del juego
running = True
while running:
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Tecla E para generar un enemigo manualmente
            if event.key == pygame.K_e:
                enemigos.append(generar_enemigo_alrededor())

    # Obtener teclas presionadas
    keys = pygame.key.get_pressed()

    # Actualizar lógica del juego
    dt = clock.tick(60) / 1000.0  # Delta time en segundos

    # Movimiento del personaje
    if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]:
        if keys[pygame.K_w]:
            protagonista.y -= protagonista.velocidad
            if actual == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_a]:
            protagonista.x -= protagonista.velocidad
            actual = "quieto_izquierda"
            if actual == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_s]:
            protagonista.y += protagonista.velocidad
            if actual == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_d]:
            protagonista.x += protagonista.velocidad
            actual = "quieto_derecha"
            if actual == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
    else:
        protagonista.cambiar_animacion(actual)

    # Actualizar animaciones
    protagonista.update(dt)
    
    # Actualizar enemigos
    for enemigo in enemigos:
        enemigo.update(dt)

    # Manejar colisiones
    manejar_colisiones(protagonista, enemigos)

    # Generar nuevos enemigos periódicamente
    tiempo_actual = pygame.time.get_ticks() / 1000.0  # Convertir a segundos
    if tiempo_actual - tiempo_ultimo_enemigo > intervalo_enemigos:
        enemigos.append(generar_enemigo_alrededor())
        tiempo_ultimo_enemigo = tiempo_actual

    # Dibujar
    screen.fill((50, 100, 50))  # Fondo verde
    protagonista.draw(screen)
    
    # Dibujar enemigos
    for enemigo in enemigos:
        enemigo.draw(screen)
        
    # Dibujar hitboxes para debugging (opcional - descomenta para ver)
    # protagonista.draw_hitbox(screen, (255, 0, 0))  # Rojo para protagonista
    # for enemigo in enemigos:
    #     enemigo.draw_hitbox(screen, (0, 0, 255))  # Azul para enemigos

    # Actualizar pantalla
    pygame.display.flip()

# Salir del juego
pygame.quit()
sys.exit()