#main
from menu import *
import pygame
import sys
import random
import math
import os

# Importar los módulos del juego
from personajes import Personaje
from enemigo import Enemigo
import texturas
from colisiones import manejar_colisiones
from enemigos_tipos import EnemigoFactory
from poder import PoderFactory, ProyectilFuego, EspadaOrbitante, RayoElectro, CampoMag, AuraSag, LanzaHieloProyectil

# Inicializar Pygame PRIMERO
pygame.init()
inicializacion_menu()

# Inicializar texturas DESPUÉS de Pygame
texturas_personaje = texturas.inicializar_texturas()

# Variables del juego
running = True
en_juego = False
protagonista = None
enemigos = []
efectos_activos = []
tiempo_ultimo_enemigo = 0
intervalo_enemigos = 3.0
actual_animacion = "quieto_derecha"
clock = pygame.time.Clock()
mensaje_poder = ""
tiempo_mensaje = 0
duracion_mensaje = 3.0
nivel_juego = 1
tiempo_juego = 0
enemigos_derrotados = 0
experiencia_total = 0
font_pequena = pygame.font.SysFont(None, 24)
font_mediana = pygame.font.SysFont(None, 36)
font_grande = pygame.font.SysFont(None, 48)

MAX_EFECTOS_ACTIVOS = 50  # Límite máximo de efectos

# Colores para los enemigos según tipo (para círculos identificadores)
COLORES_ENEMIGOS = {
    "zombie": (50, 150, 50),
    "esqueleto": (200, 200, 200),
    "brujo": (150, 50, 200),
    "momia": (150, 100, 50),
    "escorpion": (200, 100, 50),
    "gusano": (100, 50, 100),
    "templario": (100, 150, 200),
    "angel_oscuro": (50, 50, 100),
    "sacerdote": (200, 200, 100)
}

def inicializar_juego():
    """Inicializa el juego"""
    global protagonista, enemigos, tiempo_ultimo_enemigo, actual_animacion
    global efectos_activos, nivel_juego, tiempo_juego, enemigos_derrotados, experiencia_total
    
    # Crear el personaje principal
    protagonista = Personaje(0, 100, 4, texturas_personaje)
    actual_animacion = "quieto_derecha"
    
    # Configurar hitbox del protagonista
    protagonista.set_hitbox((30, 40), (0, 5))
    
    # Limpiar listas
    enemigos = []
    efectos_activos = []
    
    # Reiniciar estadísticas
    nivel_juego = 1
    tiempo_juego = 0
    enemigos_derrotados = 0
    experiencia_total = 0
    
    # Generar enemigos iniciales
    for _ in range(5):
        enemigos.append(generar_enemigo_alrededor())
    
    tiempo_ultimo_enemigo = 0
    
    # Dar un poder inicial al jugador
    poder_inicial = PoderFactory.crear_poder("bola_fuego")
    resultado = protagonista.agregar_poder(poder_inicial)
    mostrar_mensaje(resultado)

def generar_enemigo_alrededor():
    """Genera un enemigo alrededor del protagonista"""
    if not protagonista:
        return None
    
    # Radio de aparición
    radio = random.randint(200, 400)
    
    # Ángulo aleatorio
    angulo = random.uniform(0, 2 * math.pi)
    
    # Calcular posición
    x = protagonista.x + radio * math.cos(angulo)
    y = protagonista.y + radio * math.sin(angulo)
    
    # Asegurar límites
    x = max(50, min(WIDTH - 50, x))
    y = max(50, min(HEIGHT - 50, y))
    
    # Crear enemigo aleatorio basado en el nivel
    tipos_nivel_bajo = ["zombie", "esqueleto", "gusano", "escorpion"]
    tipos_nivel_medio = ["brujo", "momia", "esqueleto"]
    tipos_nivel_alto = ["templario", "angel_oscuro", "sacerdote"]
    
    if nivel_juego < 3:
        tipo = random.choice(tipos_nivel_bajo)
    elif nivel_juego < 6:
        tipo = random.choice(tipos_nivel_medio)
    else:
        tipo = random.choice(tipos_nivel_alto)
    
    # Crear el enemigo con el Factory
    nuevo_enemigo = EnemigoFactory.crear_enemigo(tipo, nivel_juego, (x, y))
    
    # Configurar follow y hitbox
    nuevo_enemigo.setFollow(protagonista)
    nuevo_enemigo.set_hitbox((30, 40), (0, 5))
    
    return nuevo_enemigo

def mostrar_mensaje(texto):
    """Muestra un mensaje temporal en pantalla"""
    global mensaje_poder, tiempo_mensaje  # ¡IMPORTANTE!
    mensaje_poder = texto
    tiempo_mensaje = duracion_mensaje

def actualizar_juego():
    """Actualiza la lógica del juego"""
    global tiempo_ultimo_enemigo, actual_animacion, nivel_juego, tiempo_juego
    global enemigos_derrotados, experiencia_total, tiempo_mensaje, efectos_activos
    
    dt = clock.tick(60) / 1000.0
    tiempo_juego += dt
    
    # Limitar el número de efectos activos (optimización)
    if len(efectos_activos) > MAX_EFECTOS_ACTIVOS:
        # Eliminar los efectos más antiguos primero
        efectos_activos = efectos_activos[-MAX_EFECTOS_ACTIVOS:]
    
    # Actualizar tiempo del mensaje
    if tiempo_mensaje > 0:
        tiempo_mensaje -= dt
    
    # Manejar entrada del teclado
    keys = pygame.key.get_pressed()
    
    # Movimiento del personaje
    movimiento = False
    if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]:
        movimiento = True
        if keys[pygame.K_w]:
            protagonista.y -= protagonista.velocidad
            if actual_animacion == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_a]:
            protagonista.x -= protagonista.velocidad
            actual_animacion = "quieto_izquierda"
            if actual_animacion == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_s]:
            protagonista.y += protagonista.velocidad
            if actual_animacion == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
        if keys[pygame.K_d]:
            protagonista.x += protagonista.velocidad
            actual_animacion = "quieto_derecha"
            if actual_animacion == "quieto_derecha":
                protagonista.cambiar_animacion("caminar_derecha")
            else:
                protagonista.cambiar_animacion("caminar_izquierda")
    
    if not movimiento:
        protagonista.cambiar_animacion(actual_animacion)
    
    # Actualizar animaciones
    protagonista.update(dt)
    
    # Actualizar enemigos y verificar colisiones
    tiempo_actual = pygame.time.get_ticks() / 1000.0
    enemigos_a_eliminar = []
    
    for enemigo in enemigos:
        enemigo.update(dt)
        
        # Verificar colisión con efectos
        for efecto in efectos_activos[:]:
            if hasattr(efecto, 'x') and hasattr(efecto, 'y') and hasattr(efecto, 'radio'):
                distancia = math.hypot(efecto.x - enemigo.x, efecto.y - enemigo.y)
                if distancia < efecto.radio + 20:
                    if hasattr(efecto, 'aplicar_daño'):
                        if efecto.aplicar_daño(enemigo):
                            enemigos_a_eliminar.append(enemigo)
                            experiencia_total += getattr(enemigo, 'experiencia', 10)
                            break
        
        # Verificar ataque del enemigo al jugador
        if hasattr(enemigo, 'atacar'):
            if enemigo.atacar(protagonista, tiempo_actual):
                if protagonista.recibir_daño(enemigo.daño):
                    game_over()
                    return
    
    # Eliminar enemigos muertos
    for enemigo in enemigos_a_eliminar:
        if enemigo in enemigos:
            enemigos.remove(enemigo)
            enemigos_derrotados += 1
    
    # Manejar colisiones físicas
    manejar_colisiones(protagonista, enemigos)
    
    # Actualizar y usar poderes
    if hasattr(protagonista, 'poderes'):
        for poder in protagonista.poderes:
            efectos = poder.usar(protagonista, enemigos, tiempo_actual)
            
            if any(isinstance(ef, AuraSag) for ef in efectos):
                # Eliminar auras antiguas si las hay
                efectos_activos = [ef for ef in efectos_activos if not isinstance(ef, AuraSag)]
            
            efectos_activos.extend(efectos)
    
    # Actualizar efectos activos
    efectos_a_eliminar = []
    for efecto in efectos_activos:
        # Pasar el jugador como referencia para efectos que lo necesiten
        if isinstance(efecto, AuraSag):
            if not efecto.update(dt, protagonista, enemigos):
                efectos_a_eliminar.append(efecto)
        else:
            if not efecto.update(dt, protagonista, enemigos):
                efectos_a_eliminar.append(efecto)

    # Eliminar efectos muertos
    for efecto in efectos_a_eliminar:
        if efecto in efectos_activos:
            efectos_activos.remove(efecto)
    
    # Generar nuevos enemigos
   # if tiempo_actual - tiempo_ultimo_enemigo > intervalo_enemigos:
   #     cantidad_enemigos = min(3 + nivel_juego // 2, 10)
   #     for _ in range(cantidad_enemigos):
   #         enemigos.append(generar_enemigo_alrededor())
   #     tiempo_ultimo_enemigo = tiempo_actual
    
    # Aumentar dificultad con el tiempo
    if tiempo_juego > nivel_juego * 30:
        nivel_juego += 1
        mostrar_mensaje(f"¡Nivel {nivel_juego}!")
    
    # Ganar experiencia automáticamente con el tiempo
    experiencia_ganada = int(dt * 5)  # 5 exp por segundo
    experiencia_total += experiencia_ganada
    if protagonista.ganar_experiencia(experiencia_ganada):
        mostrar_mensaje(f"¡Nivel {protagonista.nivel}!")

def dibujar_enemigo_con_color(enemigo, screen, offset_x, offset_y):
    """Dibuja un enemigo con su textura y color identificador"""
    # Dibujar el enemigo con su textura
    enemigo.draw_con_offset(screen, offset_x, offset_y)
    
    # Dibujar un círculo de color según el tipo (debajo del enemigo)
    if hasattr(enemigo, 'tipo') and enemigo.tipo in COLORES_ENEMIGOS:
        color = COLORES_ENEMIGOS[enemigo.tipo]
        
        # Círculo identificador
        pygame.draw.circle(screen, color, 
                          (int(enemigo.x + offset_x), int(enemigo.y + offset_y + 50)), 
                          12)
        
        # Borde blanco
        pygame.draw.circle(screen, (255, 255, 255), 
                          (int(enemigo.x + offset_x), int(enemigo.y + offset_y + 50)), 
                          12, 2)
        
        # Barra de vida (opcional)
        if hasattr(enemigo, 'vida_max') and hasattr(enemigo, 'vida'):
            vida_porcentaje = enemigo.vida / enemigo.vida_max
            vida_ancho = 40
            vida_x = enemigo.x + offset_x - vida_ancho // 2
            vida_y = enemigo.y + offset_y - 60
            
            # Fondo de la barra
            pygame.draw.rect(screen, (50, 50, 50), 
                            (vida_x, vida_y, vida_ancho, 5))
            
            # Vida actual
            pygame.draw.rect(screen, color, 
                            (vida_x, vida_y, int(vida_ancho * vida_porcentaje), 5))

def dibujar_juego():
    """Dibuja el juego en la pantalla"""
    screen = declaraciones["screen"]
    
    # Fondo del juego
    screen.fill((20, 20, 40))
    
    # Calcular offset de cámara para centrar al protagonista
    camera_x = protagonista.x - WIDTH // 2
    camera_y = protagonista.y - HEIGHT // 2
    
    # Dibujar efectos activos primero (detrás de todo)
    for efecto in efectos_activos:
        if hasattr(efecto, 'draw'):
            efecto.draw(screen, -camera_x, -camera_y)
    
    # Dibujar enemigos con colores
    for enemigo in enemigos:
        dibujar_enemigo_con_color(enemigo, screen, -camera_x, -camera_y)
    
    # Dibujar protagonista (centrado)
    protagonista.draw_con_offset(screen, -camera_x, -camera_y, centrado=True)
    
    # Dibujar HUD
    dibujar_hud()
    
    # Dibujar mensaje de poder si existe
    if tiempo_mensaje > 0 and mensaje_poder:
        alpha = min(255, int(tiempo_mensaje * 300))
        texto = font_mediana.render(mensaje_poder, True, (255, 255, 100))
        texto_rect = texto.get_rect(center=(WIDTH // 2, 100))
        
        # Fondo semitransparente
        surf = pygame.Surface((texto_rect.width + 20, texto_rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0, alpha//2), surf.get_rect(), border_radius=10)
        pygame.draw.rect(surf, (255, 255, 100, alpha), surf.get_rect(), 2, border_radius=10)
        
        screen.blit(surf, (texto_rect.x - 10, texto_rect.y - 5))
        screen.blit(texto, texto_rect)

def dibujar_hud():
    """Dibuja el HUD del juego"""
    screen = declaraciones["screen"]
    
    # Barra de vida
    vida_ancho = 300
    vida_altura = 25
    vida_x = 20
    vida_y = 20
    
    # Fondo de la barra
    pygame.draw.rect(screen, (50, 50, 50), 
                    (vida_x, vida_y, vida_ancho, vida_altura), border_radius=5)
    
    # Vida actual
    vida_porcentaje = protagonista.vida / protagonista.vida_max
    vida_actual_ancho = vida_porcentaje * vida_ancho
    color_vida = (int(255 * (1 - vida_porcentaje)), int(255 * vida_porcentaje), 0)
    pygame.draw.rect(screen, color_vida, 
                    (vida_x, vida_y, vida_actual_ancho, vida_altura), border_radius=5)
    
    # Texto de vida
    vida_texto = font_pequena.render(f"Vida: {int(protagonista.vida)}/{protagonista.vida_max}", 
                                    True, (255, 255, 255))
    screen.blit(vida_texto, (vida_x + 10, vida_y + 5))
    
    # Nivel y experiencia del jugador
    nivel_texto = font_pequena.render(f"Nivel Jugador: {protagonista.nivel} | Exp: {protagonista.experiencia}", 
                                     True, (255, 255, 255))
    screen.blit(nivel_texto, (20, 55))
    
    # Tiempo y nivel del juego
    minutos = int(tiempo_juego // 60)
    segundos = int(tiempo_juego % 60)
    tiempo_texto = font_pequena.render(f"Tiempo: {minutos:02d}:{segundos:02d} | Nivel Juego: {nivel_juego}", 
                                      True, (255, 255, 255))
    screen.blit(tiempo_texto, (20, 80))
    
    # Estadísticas
    derrotados_texto = font_pequena.render(f"Derrotados: {enemigos_derrotados} | Exp Total: {experiencia_total}", 
                                          True, (255, 255, 255))
    screen.blit(derrotados_texto, (20, 105))
    
    # Poderes activos
    y_poder = 140
    if hasattr(protagonista, 'poderes'):
        for poder in protagonista.poderes:
            stack_text = f" x{poder.stacks}" if poder.stacks > 1 else ""
            poder_texto = font_pequena.render(f"• {poder.nombre} Nv.{poder.nivel}{stack_text}", 
                                             True, (200, 200, 255))
            screen.blit(poder_texto, (20, y_poder))
            y_poder += 25
    
    # Controles
    controles_y = HEIGHT - 60
    controles = [
        "Controles:",
        "WASD - Moverse",
        "M - Poder aleatorio",
        "E - Spawn enemigo (debug)",
        "ESC - Volver al menú"
    ]
    
    for i, control in enumerate(controles):
        color = (255, 255, 255) if i == 0 else (200, 200, 200)
        control_texto = font_pequena.render(control, True, color)
        screen.blit(control_texto, (WIDTH - 250, controles_y + i * 25))
    
    # Contador de enemigos
    contador = font_pequena.render(f"Enemigos en pantalla: {len(enemigos)}", True, (255, 255, 255))
    screen.blit(contador, (WIDTH - 250, 20))

def game_over():
    """Maneja el fin del juego"""
    global en_juego
    
    en_juego = False
    mostrar_mensaje(f"¡GAME OVER! Tiempo: {int(tiempo_juego//60)}:{int(tiempo_juego%60):02d}")
    
    # Restaurar elementos del menú
    estado_bloques["rect1"] = True
    estado_bloques["rect2"] = True
    estado_bloques["rect3"] = True
    estado_bloques["rect4"] = False
    estado_bloques["rect5"] = False
    estado_bloques["rect6"] = False
    Variables_Globales["STARTGAME"] = False

# Bucle principal
while running:
    if en_juego:
        # Modo juego activo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Volver al menú
                    en_juego = False
                    estado_bloques["rect1"] = True
                    estado_bloques["rect2"] = True
                    estado_bloques["rect3"] = True
                    estado_bloques["rect4"] = False
                    estado_bloques["rect5"] = False
                    estado_bloques["rect6"] = False
                    Variables_Globales["STARTGAME"] = False
                elif event.key == pygame.K_e:
                    # Tecla E para generar enemigo (debug)
                    enemigos.append(generar_enemigo_alrededor())
                    mostrar_mensaje("Enemigo generado (debug)")
                elif event.key == pygame.K_m:
                    # Tecla M para obtener poder aleatorio
                    if hasattr(protagonista, 'ganar_poder_aleatorio'):
                        resultado = protagonista.ganar_poder_aleatorio()
                        mostrar_mensaje(resultado)
        
        # Actualizar juego
        actualizar_juego()
        
        # Dibujar juego
        dibujar_juego()
        
    else:
        # Modo menú
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                running = menu_eventos(event, running)
                
                # Si se hizo clic en START GAME
                if Variables_Globales["STARTGAME"] and not en_juego:
                    en_juego = True
                    inicializar_juego()
        
        # Dibujar menú
        menu()
        
        # Mostrar estadísticas finales si hubo game over
        if tiempo_mensaje > 0 and mensaje_poder and "GAME OVER" in mensaje_poder:
            # Fondo semitransparente
            surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(surf, (0, 0, 0, 200), surf.get_rect())
            declaraciones["screen"].blit(surf, (0, 0))
            
            # Título
            titulo = font_grande.render("GAME OVER", True, (255, 50, 50))
            titulo_rect = titulo.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            declaraciones["screen"].blit(titulo, titulo_rect)
            
            # Estadísticas
            stats = [
                f"Tiempo de supervivencia: {int(tiempo_juego//60)}:{int(tiempo_juego%60):02d}",
                f"Enemigos derrotados: {enemigos_derrotados}",
                f"Nivel alcanzado: {nivel_juego}",
                f"Experiencia total: {experiencia_total}",
                f"Poderes obtenidos: {len(protagonista.poderes) if protagonista else 0}"
            ]
            
            for i, stat in enumerate(stats):
                stat_texto = font_mediana.render(stat, True, (255, 255, 255))
                stat_rect = stat_texto.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
                declaraciones["screen"].blit(stat_texto, stat_rect)
            
            # Mensaje para continuar
            continuar = font_pequena.render("Haz clic en START para jugar de nuevo", True, (200, 200, 200))
            continuar_rect = continuar.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            declaraciones["screen"].blit(continuar, continuar_rect)
    
    pygame.display.flip()

pygame.quit()
sys.exit()