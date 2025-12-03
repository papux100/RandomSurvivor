from enemigo import Enemigo
import texturas
import random
import math
import time

class EnemigoMejorado(Enemigo):
    def __init__(self, experiencia, vida, velocidad, tipo="zombie", pos=(500, 100)):
        # Obtener texturas para este tipo de enemigo
        animaciones_dict = texturas.obtener_textura_enemigo(tipo) 
        
        super().__init__(experiencia, vida, velocidad, animaciones_dict, pos=pos)
        self.tipo = tipo
        self.daño = 5
        self.velocidad_ataque = 1.0
        self.tiempo_ultimo_ataque = 0
        self.vida_max = vida
        self.experiencia_base = experiencia
        
        # Configurar follow después de inicializar
        self.follow = None
    
    def atacar(self, jugador, tiempo_actual):
        """Intenta atacar al jugador, devuelve True si atacó"""
        if tiempo_actual - self.tiempo_ultimo_ataque > self.velocidad_ataque:
            distancia = math.hypot(self.x - jugador.x, self.y - jugador.y)
            if distancia < 40:  # Rango de ataque
                self.tiempo_ultimo_ataque = tiempo_actual
                if hasattr(jugador, 'recibir_daño'):
                    return jugador.recibir_daño(self.daño)
        return False
    
    def recibir_daño(self, cantidad):
        """Recibe daño, devuelve True si murió"""
        self.vida -= cantidad
        return self.vida <= 0

# Tipos específicos de enemigos
class Zombie(EnemigoMejorado):
    def __init__(self, experiencia=10, vida=50, velocidad=1.5, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "zombie", pos)
        self.daño = 8
        self.experiencia = int(experiencia * 1.0)

class Esqueleto(EnemigoMejorado):
    def __init__(self, experiencia=15, vida=35, velocidad=2.0, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "esqueleto", pos)
        self.daño = 12
        self.velocidad_ataque = 1.5
        self.experiencia = int(experiencia * 1.2)

class Brujo(EnemigoMejorado):
    def __init__(self, experiencia=25, vida=40, velocidad=1.2, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "brujo", pos)
        self.daño = 15
        self.rango_ataque = 150
        self.cooldown_hechizo = 3.0
        self.tiempo_ultimo_hechizo = 0
        self.experiencia = int(experiencia * 1.5)
    
    def atacar(self, jugador, tiempo_actual):
        distancia = math.hypot(self.x - jugador.x, self.y - jugador.y)
        
        # Ataque cuerpo a cuerpo
        if distancia < 40:
            if super().atacar(jugador, tiempo_actual):
                return True
        
        # Hechizo a distancia
        if distancia < self.rango_ataque and tiempo_actual - self.tiempo_ultimo_hechizo > self.cooldown_hechizo:
            self.tiempo_ultimo_hechizo = tiempo_actual
            self.daño = 20  # Daño aumentado para el hechizo
            resultado = super().atacar(jugador, tiempo_actual)
            self.daño = 15  # Restaurar daño normal
            return resultado
        
        return False

class Momia(EnemigoMejorado):
    def __init__(self, experiencia=20, vida=80, velocidad=1.0, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "momia", pos)
        self.daño = 20
        self.regeneracion = 0.5  # Vida por segundo
        self.tiempo_ultima_regeneracion = 0
        self.experiencia = int(experiencia * 1.3)
    
    def update(self, dt):
        super().update(dt)
        # Regeneración pasiva
        self.tiempo_ultima_regeneracion += dt
        if self.tiempo_ultima_regeneracion >= 1.0:
            self.vida = min(self.vida + self.regeneracion, self.vida_max)
            self.tiempo_ultima_regeneracion = 0

class Escorpion(EnemigoMejorado):
    def __init__(self, experiencia=12, vida=25, velocidad=2.5, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "escorpion", pos)
        self.daño = 10
        self.veneno_daño = 2  # Daño extra por veneno
        self.veneno_duracion = 3
        self.experiencia = int(experiencia * 0.8)

class Gusano(EnemigoMejorado):
    def __init__(self, experiencia=8, vida=20, velocidad=3.0, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "gusano", pos)
        self.daño = 6
        self.velocidad_ataque = 0.5  # Ataca rápido
        self.experiencia = int(experiencia * 0.6)

class Templario(EnemigoMejorado):
    def __init__(self, experiencia=40, vida=100, velocidad=1.8, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "templario", pos)
        self.daño = 25
        self.armadura = 0.3  # Reduce 30% del daño
        self.experiencia = int(experiencia * 2.0)
    
    def recibir_daño(self, cantidad):
        cantidad_reducida = cantidad * (1 - self.armadura)
        return super().recibir_daño(cantidad_reducida)

class AngelOscuro(EnemigoMejorado):
    def __init__(self, experiencia=60, vida=70, velocidad=2.2, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "angel_oscuro", pos)
        self.daño = 30
        self.vuela = True  # Ignora algunos obstáculos
        self.experiencia = int(experiencia * 2.5)

class Sacerdote(EnemigoMejorado):
    def __init__(self, experiencia=35, vida=60, velocidad=1.3, pos=(500, 100)):
        super().__init__(experiencia, vida, velocidad, "sacerdote", pos)
        self.daño = 18
        self.curacion_aliados = 2  # Cura a aliados cercanos
        self.rango_curacion = 100
        self.experiencia = int(experiencia * 1.8)

# Factory para crear enemigos
class EnemigoFactory:
    @staticmethod
    def crear_enemigo(tipo, nivel=1, pos=None):
        if pos is None:
            pos = (random.randint(100, 700), random.randint(100, 500))
        
        # Multiplicador según nivel
        multiplicador = 1 + (nivel - 1) * 0.5
        
        enemigos = {
            "zombie": lambda: Zombie(
                experiencia=int(10 * multiplicador),
                vida=int(50 * multiplicador),
                velocidad=1.5,
                pos=pos
            ),
            "esqueleto": lambda: Esqueleto(
                experiencia=int(15 * multiplicador),
                vida=int(35 * multiplicador),
                velocidad=2.0,
                pos=pos
            ),
            "brujo": lambda: Brujo(
                experiencia=int(25 * multiplicador),
                vida=int(40 * multiplicador),
                velocidad=1.2,
                pos=pos
            ),
            "momia": lambda: Momia(
                experiencia=int(20 * multiplicador),
                vida=int(80 * multiplicador),
                velocidad=1.0,
                pos=pos
            ),
            "escorpion": lambda: Escorpion(
                experiencia=int(12 * multiplicador),
                vida=int(25 * multiplicador),
                velocidad=2.5,
                pos=pos
            ),
            "gusano": lambda: Gusano(
                experiencia=int(8 * multiplicador),
                vida=int(20 * multiplicador),
                velocidad=3.0,
                pos=pos
            ),
            "templario": lambda: Templario(
                experiencia=int(40 * multiplicador),
                vida=int(100 * multiplicador),
                velocidad=1.8,
                pos=pos
            ),
            "angel_oscuro": lambda: AngelOscuro(
                experiencia=int(60 * multiplicador),
                vida=int(70 * multiplicador),
                velocidad=2.2,
                pos=pos
            ),
            "sacerdote": lambda: Sacerdote(
                experiencia=int(35 * multiplicador),
                vida=int(60 * multiplicador),
                velocidad=1.3,
                pos=pos
            )
        }
        
        if tipo in enemigos:
            return enemigos[tipo]()
        
        return Zombie(pos=pos)
    
    @staticmethod
    def crear_enemigo_aleatorio(nivel=1, pos=None):
        tipos = ["zombie", "esqueleto", "brujo", "momia", "escorpion", 
                "gusano", "templario", "angel_oscuro", "sacerdote"]
        
        # Probabilidades según nivel
        if nivel < 3:
            tipos = ["zombie", "esqueleto", "gusano", "escorpion"]
        elif nivel < 6:
            tipos = ["zombie", "esqueleto", "brujo", "momia", "escorpion"]
        elif nivel < 10:
            tipos = ["brujo", "momia", "templario", "sacerdote"]
        else:
            tipos = ["templario", "angel_oscuro", "sacerdote", "brujo"]
        
        tipo = random.choice(tipos)
        return EnemigoFactory.crear_enemigo(tipo, nivel, pos)