import pygame

def manejar_colisiones(protagonista, enemigos):
    """
    Maneja todas las colisiones del juego
    - Colisión entre protagonista y enemigos
    - Colisión entre enemigos
    - Colisión con bordes de pantalla
    """
    # Colisión con bordes de pantalla
    manejar_colisiones_pantalla(protagonista)
    
    for enemigo in enemigos:
        manejar_colisiones_pantalla(enemigo)
    
    # Colisión entre protagonista y enemigos
    for enemigo in enemigos:
        if protagonista.actor_animado.actor.collides_with_actor(enemigo.actor_animado.actor):
            resolver_colision(protagonista, enemigo)
    
    # Colisión entre enemigos
    for i, enemigo1 in enumerate(enemigos):
        for j, enemigo2 in enumerate(enemigos):
            if i != j and enemigo1.actor_animado.actor.collides_with_actor(enemigo2.actor_animado.actor):
                resolver_colision(enemigo1, enemigo2)

def manejar_colisiones_pantalla(entidad):
    """Maneja colisiones con los bordes de la pantalla"""
    ancho_pantalla, alto_pantalla = 800, 600  # Ajusta según tu tamaño de pantalla
    
    # Margen para evitar que se salga completamente
    margen = 5
    
    # Limitar movimiento horizontal
    if entidad.x < margen:
        entidad.x = margen
    elif entidad.x > ancho_pantalla - margen:
        entidad.x = ancho_pantalla - margen
    
    # Limitar movimiento vertical
    if entidad.y < margen:
        entidad.y = margen
    elif entidad.y > alto_pantalla - margen:
        entidad.y = alto_pantalla - margen

def resolver_colision(entidad1, entidad2):
    """
    Resuelve la colisión entre dos entidades separándolas
    """
    # Calcular vector de separación
    dx = entidad1.x - entidad2.x
    dy = entidad1.y - entidad2.y
    
    # Calcular distancia (evitar división por cero)
    distancia = max(0.1, (dx**2 + dy**2)**0.5)
    
    # Normalizar y aplicar separación
    separacion_x = dx / distancia
    separacion_y = dy / distancia
    
    # Cantidad de separación (ajustable)
    fuerza_separacion = 2
    
    # Aplicar separación
    entidad1.x += separacion_x * fuerza_separacion
    entidad1.y += separacion_y * fuerza_separacion
    
    entidad2.x -= separacion_x * fuerza_separacion
    entidad2.y -= separacion_y * fuerza_separacion

def verificar_colision_proyectil(proyectil, objetivos):
    """
    Verifica colisión entre un proyectil y una lista de objetivos
    Devuelve el objetivo impactado o None
    """
    for objetivo in objetivos:
        if proyectil.actor_animado.actor.collides_with_actor(objetivo.actor_animado.actor):
            return objetivo
    return None