import pygame
import random
import math
from enemigos_tipos import EnemigoFactory
from poder import PoderFactory

class GameManager:
    def __init__(self, ancho_pantalla, alto_pantalla):
        self.ancho = ancho_pantalla
        self.alto = alto_pantalla
        self.nivel_actual = 1
        self.oleada_actual = 1
        self.enemigos_restantes = 0
        self.tiempo_entre_oleadas = 30.0  # segundos
        self.tiempo_ultima_oleada = 0
        self.enemigos_por_oleada = 10
        self.crecimiento_oleadas = 1.5  # Multiplicador por oleada
        
        # Sistema de recompensas
        self.opciones_poder = 3  # Cantidad de opciones al subir de nivel
        self.poderes_disponibles = []
        
        # Estadísticas
        self.enemigos_derrotados = 0
        self.tiempo_juego = 0
        self.oro_total = 0
        
    def generar_oleada(self, jugador):
        """Genera una nueva oleada de enemigos"""
        self.oleada_actual += 1
        cantidad = int(self.enemigos_por_oleada * (self.crecimiento_oleadas ** (self.oleada_actual - 1)))
        self.enemigos_restantes = cantidad
        
        enemigos = []
        for _ in range(cantidad):
            # Variar el tipo de enemigo según la oleada
            nivel_enemigo = min(10, self.oleada_actual // 3 + 1)
            
            # Posición aleatoria alrededor del jugador
            angulo = random.uniform(0, 2 * math.pi)
            distancia = random.randint(300, 500)
            x = jugador.x + distancia * math.cos(angulo)
            y = jugador.y + distancia * math.sin(angulo)
            
            # Mantener dentro de límites razonables
            x = max(100, min(self.ancho - 100, x))
            y = max(100, min(self.alto - 100, y))
            
            enemigo = EnemigoFactory.crear_enemigo_aleatorio(nivel_enemigo, (x, y))
            enemigo.setFollow(jugador)
            enemigos.append(enemigo)
        
        return enemigos
    
    def verificar_fin_oleada(self, enemigos):
        """Verifica si la oleada actual ha terminado"""
        return len(enemigos) == 0
    
    def generar_opciones_poder(self, jugador):
        """Genera opciones de poderes para que el jugador elija"""
        self.poderes_disponibles = []
        
        # Evitar repetir poderes que ya tiene al máximo nivel
        poderes_existentes = {type(p).__name__: p for p in jugador.poderes}
        
        for _ in range(self.opciones_poder):
            # Generar poder aleatorio
            poder = PoderFactory.crear_poder_aleatorio()
            
            # Si el jugador ya tiene este poder, subirle el nivel
            if type(poder).__name__ in poderes_existentes:
                poder_existente = poderes_existentes[type(poder).__name__]
                if poder_existente.nivel < poder_existente.max_nivel:
                    poder.nivel = poder_existente.nivel + 1
                else:
                    # Si está al máximo, buscar otro poder
                    continue
            
            self.poderes_disponibles.append(poder)
    
    def seleccionar_poder(self, indice, jugador):
        """El jugador selecciona un poder"""
        if 0 <= indice < len(self.poderes_disponibles):
            poder = self.poderes_disponibles[indice]
            jugador.agregar_poder(poder)
            self.poderes_disponibles = []
            return True
        return False
    
    def actualizar(self, dt, jugador, enemigos):
        """Actualiza la lógica del juego"""
        self.tiempo_juego += dt
        
        # Verificar si hay que generar nueva oleada
        if self.verificar_fin_oleada(enemigos):
            self.tiempo_ultima_oleada += dt
            if self.tiempo_ultima_oleada >= self.tiempo_entre_oleadas:
                nuevos_enemigos = self.generar_oleada(jugador)
                enemigos.extend(nuevos_enemigos)
                self.tiempo_ultima_oleada = 0
    
    def dibujar_hud(self, screen, jugador, font):
        """Dibuja el HUD del juego"""
        # Barra de vida
        vida_ancho = 200
        vida_altura = 20
        vida_x = 10
        vida_y = 10
        
        # Fondo de la barra
        pygame.draw.rect(screen, (100, 100, 100), 
                        (vida_x, vida_y, vida_ancho, vida_altura))
        
        # Vida actual
        vida_actual_ancho = (jugador.vida / jugador.vida_max) * vida_ancho
        pygame.draw.rect(screen, (255, 0, 0), 
                        (vida_x, vida_y, vida_actual_ancho, vida_altura))
        
        # Texto de vida
        vida_texto = font.render(f"Vida: {int(jugador.vida)}/{jugador.vida_max}", 
                                True, (255, 255, 255))
        screen.blit(vida_texto, (vida_x + 5, vida_y))
        
        # Experiencia y nivel
        exp_texto = font.render(f"Nivel: {jugador.nivel} | Exp: {jugador.experiencia}", 
                               True, (255, 255, 255))
        screen.blit(exp_texto, (10, 40))
        
        # Oro
        oro_texto = font.render(f"Oro: {jugador.oro}", True, (255, 255, 255))
        screen.blit(oro_texto, (10, 70))
        
        # Oleada
        oleada_texto = font.render(f"Oleada: {self.oleada_actual}", True, (255, 255, 255))
        screen.blit(oleada_texto, (10, 100))
        
        # Tiempo de juego
        minutos = int(self.tiempo_juego // 60)
        segundos = int(self.tiempo_juego % 60)
        tiempo_texto = font.render(f"Tiempo: {minutos:02d}:{segundos:02d}", 
                                  True, (255, 255, 255))
        screen.blit(tiempo_texto, (10, 130))
        
        # Enemigos derrotados
        derrotados_texto = font.render(f"Derrotados: {self.enemigos_derrotados}", 
                                      True, (255, 255, 255))
        screen.blit(derrotados_texto, (10, 160))
        
        # Mostrar poderes activos
        y_poder = 200
        for i, poder in enumerate(jugador.poderes):
            poder_texto = font.render(f"{poder.nombre} Nv.{poder.nivel}", 
                                     True, (255, 255, 255))
            screen.blit(poder_texto, (10, y_poder))
            y_poder += 25