# -*- coding: utf-8 -*-
"""
Módulo: utils.py
Descripción: Encapsula la arquitectura Orientada a Objetos (Tablero, Jugador, 
Maquina y Juego) y las funciones de interfaz gráfica en terminal (limpieza de
pantalla y renderizado simultáneo de tableros con colores).
"""

import os
import time
import numpy as np
import variables as var
import funciones as fn


# ==============================================================================
# UTILIDADES DE CONSOLA Y VISUALIZACIÓN
# ==============================================================================

def limpiar_pantalla() -> None:
    """
    Limpia la terminal de forma multiplataforma (Windows, macOS y Linux).
    
    ¿Por qué es necesario?
    Cumple el requisito 15: evita que la terminal se sature de texto histórico,
    manteniendo en pantalla únicamente el estado actual y los dos tableros.
    """
    comando = "cls" if os.name == "nt" else "clear"
    os.system(comando)


def formatear_celda(simbolo: str) -> str:
    """Traduce un carácter de la matriz NumPy a su representación ANSI con color."""
    return var.MAPA_VISUAL_COLORES.get(simbolo, simbolo)


def mostrar_dos_tableros(
    tablero_izquierdo: np.ndarray,
    tablero_derecho: np.ndarray,
    titulo_izq: str = "MI FLOTA (Mis Barcos)",
    titulo_der: str = "MI RADAR (Mis Disparos)"
) -> None:
    """
    Imprime dos tableros de NumPy uno al lado del otro con sus respectivos índices
    de fila y columna en los bordes y colores diferenciados.
    
    ¿Por qué renderizar en paralelo (Side-by-Side)?
    Permite al jugador visualizar simultáneamente el estado de su propia flota y
    el registro de sus ataques sin necesidad de hacer scroll vertical en la terminal.
    """
    tamaño = tablero_izquierdo.shape[0]
    separador_central = "      ║      "
    
    # Cabeceras de ambos tableros
    print(f"\n{var.COLOR_CABECERA}{titulo_izq.center(31)}{separador_central}{titulo_der.center(31)}{var.COLOR_RESET}")
    
    # Índices superiores de columna (0 a 9)
    indices_col = "    " + " ".join(f"{col:2d}" for col in range(tamaño))
    print(f"{var.COLOR_CABECERA}{indices_col}{separador_central}{indices_col}{var.COLOR_RESET}")
    
    # Borde superior del marco
    borde_sup = "   ╔" + "═══" * tamaño + "╗"
    print(f"{var.COLOR_CABECERA}{borde_sup}{separador_central}{borde_sup}{var.COLOR_RESET}")
    
    # Filas de ambos tableros con números de fila en los bordes izquierdo y derecho
    for fila in range(tamaño):
        celdas_izq = "  ".join(formatear_celda(tablero_izquierdo[fila, col]) for col in range(tamaño))
        celdas_der = "  ".join(formatear_celda(tablero_derecho[fila, col]) for col in range(tamaño))
        
        linea_izq = (
            f"{var.COLOR_CABECERA}{fila:2d} ║{var.COLOR_RESET} "
            f"{celdas_izq} "
            f"{var.COLOR_CABECERA}║ {fila:2d}{var.COLOR_RESET}"
        )
        linea_der = (
            f"{var.COLOR_CABECERA}{fila:2d} ║{var.COLOR_RESET} "
            f"{celdas_der} "
            f"{var.COLOR_CABECERA}║ {fila:2d}{var.COLOR_RESET}"
        )
        print(f"{linea_izq}{var.COLOR_CABECERA}{separador_central}{var.COLOR_RESET}{linea_der}")
        
    # Borde inferior del marco
    borde_inf = "   ╚" + "═══" * tamaño + "╝"
    print(f"{var.COLOR_CABECERA}{borde_inf}{separador_central}{borde_inf}{var.COLOR_RESET}")
    print(f"{var.COLOR_CABECERA}{indices_col}{separador_central}{indices_col}{var.COLOR_RESET}")
    
    # Leyenda cromática compacta
    leyenda = (
        f"\n   Leyenda: "
        f"[{formatear_celda(var.SIMBOLO_BARCO)}] Barco (Blanco)   "
        f"[{formatear_celda(var.SIMBOLO_AGUA)}] Agua (Azul)   "
        f"[{formatear_celda(var.SIMBOLO_AGUA_DISPARADA)}] Agua disparada (Azul)   "
        f"[{formatear_celda(var.SIMBOLO_TOCADO)}] Tocado (Rojo)\n"
    )
    print(leyenda)


def mostrar_tablero_individual(tablero: np.ndarray, titulo: str) -> None:
    """
    Muestra un único tablero centrado con numeración en sus cuatro bordes.
    Se utiliza en las pruebas unitarias y en la pantalla de revelación final.
    """
    tamaño = tablero.shape[0]
    print(f"\n{var.COLOR_CABECERA}{titulo.center(38)}{var.COLOR_RESET}")
    indices_col = "    " + " ".join(f"{col:2d}" for col in range(tamaño))
    print(f"{var.COLOR_CABECERA}{indices_col}{var.COLOR_RESET}")
    print(f"{var.COLOR_CABECERA}   ╔{'═══' * tamaño}╗{var.COLOR_RESET}")
    
    for fila in range(tamaño):
        celdas = "  ".join(formatear_celda(tablero[fila, col]) for col in range(tamaño))
        print(
            f"{var.COLOR_CABECERA}{fila:2d} ║{var.COLOR_RESET} "
            f"{celdas} "
            f"{var.COLOR_CABECERA}║ {fila:2d}{var.COLOR_RESET}"
        )
        
    print(f"{var.COLOR_CABECERA}   ╚{'═══' * tamaño}╝{var.COLOR_RESET}")
    print(f"{var.COLOR_CABECERA}{indices_col}{var.COLOR_RESET}\n")


# ==============================================================================
# CLASES DE PROGRAMACIÓN ORIENTADA A OBJETOS (POO)
# ==============================================================================

class Tablero:
    """
    Clase que modela los tableros de un participante.
    
    ¿Por qué encapsular ambos arrays de NumPy en una clase `Tablero`?
    Cada jugador necesita gestionar dos matrices: su tablero propio (con sus barcos)
    y su tablero de seguimiento o radar (donde anota sus disparos al rival).
    Agruparlos en un objeto asegura la integridad de los datos y ofrece métodos
    de alto nivel como `tiene_barcos_activos()`.
    """
    
    def __init__(self, tamaño: int = var.TAMANO_TABLERO) -> None:
        self.tamaño: int = tamaño
        self.matriz_flota: np.ndarray = fn.crear_tablero(tamaño)
        self.matriz_disparos: np.ndarray = fn.crear_tablero(tamaño)
        
    def inicializar_flota_aleatoria(self) -> None:
        """Coloca automáticamente los 6 barcos reglamentarios en la matriz de flota."""
        fn.colocar_barcos(self.matriz_flota)
        
    def tiene_barcos_activos(self) -> bool:
        """
        Verifica si aún queda alguna casilla con el símbolo 'O' sin descubrir.
        Usa `np.any` para evaluar toda la matriz de forma vectorizada.
        """
        return bool(np.any(self.matriz_flota == var.SIMBOLO_BARCO))
        
    def contar_casillas_barco_restantes(self) -> int:
        """Devuelve el número exacto de casillas 'O' pendientes de ser impactadas."""
        return int(np.sum(self.matriz_flota == var.SIMBOLO_BARCO))


class Jugador:
    """
    Clase base que representa a un participante en el juego.
    Aplica el principio de Responsabilidad Única (SRP) delegando la gestión
    matricial en su atributo `tablero` (composición).
    """
    
    def __init__(self, nombre: str, es_humano: bool = True) -> None:
        self.nombre: str = nombre
        self.es_humano: bool = es_humano
        self.tablero: Tablero = Tablero(var.TAMANO_TABLERO)
        self.tablero.inicializar_flota_aleatoria()
        
    def elegir_coordenada_disparo(self) -> tuple[int, int]:
        """
        Solicita o calcula la coordenada de disparo según el tipo de jugador.
        Si es humano, valida la entrada por teclado; si es máquina, selecciona
        aleatoriamente entre las coordenadas aún no exploradas usando NumPy.
        """
        if self.es_humano:
            return self._solicitar_coordenada_teclado()
        return self._calcular_disparo_ia()
        
    def _solicitar_coordenada_teclado(self) -> tuple[int, int]:
        """Valida de forma robusta las entradas del usuario para evitar cierres por ValueError."""
        tamaño = self.tablero.tamaño
        while True:
            try:
                entrada = input(
                    f"{var.COLOR_CABECERA}Introduzca coordenada de disparo "
                    f"como 'fila,columna' (ej. 3,5) [0-{tamaño - 1}]: {var.COLOR_RESET}"
                ).strip()
                
                # Permitimos separar por coma o por espacio para mayor ergonomía
                partes = entrada.replace(",", " ").split()
                if len(partes) != 2:
                    print(f"{var.COLOR_TOCADO}Formato incorrecto. Debe introducir dos números separados por coma.{var.COLOR_RESET}")
                    continue
                    
                fila, col = int(partes[0]), int(partes[1])
                
                if not (0 <= fila < tamaño and 0 <= col < tamaño):
                    print(f"{var.COLOR_TOCADO}Fuera de rango. Los valores deben estar entre 0 y {tamaño - 1}.{var.COLOR_RESET}")
                    continue
                    
                if self.tablero.matriz_disparos[fila, col] != var.SIMBOLO_AGUA:
                    print(f"{var.COLOR_ALERTA}Ya ha disparado a la casilla ({fila}, {col}). Elija otra para no perder eficacia.{var.COLOR_RESET}")
                    continue
                    
                return (fila, col)
            except ValueError:
                print(f"{var.COLOR_TOCADO}Entrada no válida. Introduzca únicamente números enteros.{var.COLOR_RESET}")

    def _calcular_disparo_ia(self) -> tuple[int, int]:
        """
        Calcula el disparo aleatorio de la máquina de forma eficiente con NumPy.
        
        ¿Por qué usar `np.argwhere`?
        En lugar de generar coordenadas al azar en un bucle `while` (lo cual se
        volvería lento cuando quedan pocas casillas libres), `np.argwhere` extrae
        instantáneamente todos los índices `(fila, col)` donde aún hay `'_'`.
        """
        casillas_disponibles = np.argwhere(self.tablero.matriz_disparos == var.SIMBOLO_AGUA)
        indice_elegido = np.random.choice(len(casillas_disponibles))
        fila, col = casillas_disponibles[indice_elegido]
        return (int(fila), int(col))


class JuegoHundirLaFlota:
    """
    Clase controladora que orquesta el flujo completo de la partida,
    la alternancia de turnos, la repetición de tiro por acierto y las condiciones de fin.
    """
    
    def __init__(self, nombre_humano: str = " Comandante (Jugador)") -> None:
        self.humano: Jugador = Jugador(nombre=nombre_humano.strip(), es_humano=True)
        self.maquina: Jugador = Jugador(nombre="Flota IA (Máquina)", es_humano=False)
        self.ultimo_evento: str = "Inicio del combate naval. ¡Buena suerte!"
        
    def renderizar_interfaz_jugador(self, turno_actual: str) -> None:
        """
        Limpia la terminal y dibuja únicamente la cabecera de estado y los dos
        tableros del jugador humano (requisito 3 y 15).
        """
        limpiar_pantalla()
        print(f"{var.COLOR_CABECERA}╔═════════════════════════════════════════════════════════════════════════════╗")
        print(f"║                     HUNDIR LA FLOTA - TERMINAL EDITION                      ║")
        print(f"╚═════════════════════════════════════════════════════════════════════════════╝{var.COLOR_RESET}")
        
        # Indicador explícito de a qué jugador corresponde el turno (requisito 10)
        print(f"\n  {var.COLOR_ALERTA}► TURNO ACTUAL: {turno_actual.upper()}{var.COLOR_RESET}")
        print(f"  ► Último registro: {self.ultimo_evento}")
        print(
            f"  ► Casillas de barcos pendientes por descubrir -> "
            f"Enemigas: {self.maquina.tablero.contar_casillas_barco_restantes()} | "
            f"Propias: {self.humano.tablero.contar_casillas_barco_restantes()}"
        )
        
        # Mostramos siempre únicamente los dos tableros del jugador humano
        mostrar_dos_tableros(
            self.humano.tablero.matriz_flota,
            self.humano.tablero.matriz_disparos,
            titulo_izq="MI TABLERO DE BARCOS",
            titulo_der="MI TABLERO DE DISPAROS"
        )

    def iniciar_partida(self, modo_automatico: bool = False, max_turnos_demo: int = None) -> None:
        """
        Ejecuta el bucle principal del juego hasta que todos los barcos de uno
        de los contendientes sean descubiertos.
        
        Si `modo_automatico=True`, los disparos del jugador humano también se
        eligen de forma asistida para poder visualizar una demostración fluida.
        """
        jugador_activo = self.humano
        oponente = self.maquina
        contador_turnos = 0
        
        while self.humano.tablero.tiene_barcos_activos() and self.maquina.tablero.tiene_barcos_activos():
            if max_turnos_demo is not None and contador_turnos >= max_turnos_demo:
                break
                
            self.renderizar_interfaz_jugador(jugador_activo.nombre)
            
            if jugador_activo.es_humano:
                if modo_automatico:
                    casilla = jugador_activo._calcular_disparo_ia()
                    print(f"{var.COLOR_CABECERA}[DEMO] Disparando automáticamente a la coordenada {casilla}...{var.COLOR_RESET}")
                    time.sleep(0.8)
                else:
                    casilla = jugador_activo.elegir_coordenada_disparo()
            else:
                print(f"{var.COLOR_ALERTA}La máquina ({jugador_activo.nombre}) está calculando su disparo...{var.COLOR_RESET}")
                time.sleep(1.0 if not modo_automatico else 0.6)
                casilla = jugador_activo.elegir_coordenada_disparo()
                
            # Ejecución del disparo
            acierto, detalle = fn.disparar(
                casilla=casilla,
                tablero_objetivo=oponente.tablero.matriz_flota,
                tablero_disparos=jugador_activo.tablero.matriz_disparos,
                mostrar_mensaje=True
            )
            
            self.ultimo_evento = f"{jugador_activo.nombre} disparó a {casilla} -> {detalle}"
            contador_turnos += 1
            
            # Comprobamos si el disparo acaba de hundir el último barco rival
            if not oponente.tablero.tiene_barcos_activos():
                break
                
            # Regla de repetición de turno (Requisito 9):
            # Si acierta una coordenada del barco rival, repite turno y vuelve a disparar.
            if acierto:
                self.ultimo_evento += " ¡Repite turno por haber acertado!"
                time.sleep(1.1 if not modo_automatico else 0.5)
                continue
            else:
                # Si es agua, cambia el turno al otro jugador
                jugador_activo, oponente = oponente, jugador_activo
                time.sleep(1.1 if not modo_automatico else 0.5)
                
        # Al concluir el bucle, mostramos la resolución final de la partida
        self._mostrar_pantalla_final()

    def _mostrar_pantalla_final(self) -> None:
        """
        Gestiona el desenlace del juego cumpliendo estrictamente el requisito 11:
        - Si gana el humano: muestra el tablero de la máquina con todos sus barcos
          y un mensaje de felicitación.
        - Si gana la máquina: muestra el tablero del humano con todos sus barcos
          y un mensaje indicando la derrota.
        """
        limpiar_pantalla()
        print(f"{var.COLOR_CABECERA}╔═════════════════════════════════════════════════════════════════════════════╗")
        print(f"║                           FIN DE LA PARTIDA                                 ║")
        print(f"╚═════════════════════════════════════════════════════════════════════════════╝{var.COLOR_RESET}")
        
        if not self.maquina.tablero.tiene_barcos_activos():
            print(
                f"\n{var.COLOR_EXITO}¡FELICIDADES! Ha ganado la partida.{var.COLOR_RESET}\n"
                f"Ha descubierto y hundido todos los barcos de su rival ({self.maquina.nombre}).\n"
                f"A continuación se muestra el tablero de la máquina con la ubicación de toda su flota:"
            )
            mostrar_tablero_individual(
                self.maquina.tablero.matriz_flota,
                titulo="TABLERO DE LA MÁQUINA (FLOTA DESCUBIERTA)"
            )
        elif not self.humano.tablero.tiene_barcos_activos():
            print(
                f"\n{var.COLOR_TOCADO}Ha perdido la partida.{var.COLOR_RESET}\n"
                f"La máquina ha descubierto todos sus barcos antes de que usted pudiera hundir la flota rival.\n"
                f"A continuación se muestra su propio tablero con el estado final de todos sus barcos:"
            )
            mostrar_tablero_individual(
                self.humano.tablero.matriz_flota,
                titulo="MI TABLERO DE FLOTA (TODOS LOS BARCOS DESCUBIERTOS)"
            )
        else:
            print(f"\n{var.COLOR_ALERTA}Demostración finalizada tras alcanzar el límite de turnos de prueba.{var.COLOR_RESET}")
            mostrar_dos_tableros(
                self.humano.tablero.matriz_flota,
                self.humano.tablero.matriz_disparos
            )


# ==============================================================================
# DEMOSTRACIÓN GUIADA DE REQUISITOS TÉCNICOS (PUNTOS 6, 8 Y 14)
# ==============================================================================

def ejecutar_demo_terminal() -> None:
    """
    Prepara y ejecuta la demostración interactiva desde la terminal (requisito 14),
    incluyendo las pruebas específicas de los puntos 6 y 8 y una simulación de juego.
    """
    limpiar_pantalla()
    print(f"{var.COLOR_CABECERA}=== MODO DEMOSTRACIÓN: PASO 1 (PRUEBA DE COLOCACIÓN Y DISPARO MANUAL) ==={var.COLOR_RESET}\n")
    
    # 1. Crear tablero 10x10 con NumPy
    tablero_prueba = fn.crear_tablero(10)
    
    # 2. Posicionar los dos barcos de prueba solicitados en el requisito 6:
    # Barco de eslora 2 en [(0,1), (1,1)] y barco de eslora 4 en [(1,3), (1,4), (1,5), (1,6)]
    barco_eslora_2 = [(0, 1), (1, 1)]
    barco_eslora_4 = [(1, 3), (1, 4), (1, 5), (1, 6)]
    
    fn.colocar_barco(barco_eslora_2, tablero_prueba)
    fn.colocar_barco(barco_eslora_4, tablero_prueba)
    
    print("Se han posicionado los dos barcos de prueba:")
    print(f" - Barco 1 (eslora 2): {barco_eslora_2}")
    print(f" - Barco 2 (eslora 4): {barco_eslora_4}")
    mostrar_tablero_individual(tablero_prueba, "TABLERO DE PRUEBA (BARCOS COLOCADOS)")
    
    input(f"{var.COLOR_ALERTA}Presione ENTER para probar la función disparar() sobre el barco de 2 casillas...{var.COLOR_RESET}")
    limpiar_pantalla()
    
    print(f"{var.COLOR_CABECERA}=== MODO DEMOSTRACIÓN: PASO 2 (PRUEBA DE DISPARO AL BARCO DE ESLORA 2) ==={var.COLOR_RESET}\n")
    print("Disparando a la coordenada (0, 1) [Barco de 2 casillas]:")
    fn.disparar((0, 1), tablero_prueba)
    
    print("\nDisparando a la coordenada (1, 1) [Barco de 2 casillas]:")
    fn.disparar((1, 1), tablero_prueba)
    
    print("\nDisparando a la coordenada (5, 5) [Prueba de disparo al Agua]:")
    fn.disparar((5, 5), tablero_prueba)
    
    mostrar_tablero_individual(tablero_prueba, "TABLERO TRAS LOS DISPAROS DE PRUEBA")
    
    print("Opciones de continuación de la Demo:")
    print("  1. Ver simulación rápida de partida completa hasta el desenlace final.")
    print("  2. Ver demostración breve (10 turnos automáticos) y volver al menú.")
    eleccion = input(f"\n{var.COLOR_CABECERA}Seleccione una opción (1/2): {var.COLOR_RESET}").strip()
    
    partida_demo = JuegoHundirLaFlota(nombre_humano="Jugador Demo")
    if eleccion == "2":
        partida_demo.iniciar_partida(modo_automatico=True, max_turnos_demo=10)
    else:
        partida_demo.iniciar_partida(modo_automatico=True, max_turnos_demo=None)
        
    input(f"\n{var.COLOR_CABECERA}Presione ENTER para regresar al menú principal...{var.COLOR_RESET}")