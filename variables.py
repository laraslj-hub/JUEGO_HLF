# -*- coding: utf-8 -*-
"""
Módulo: variables.py
Descripción: Almacena las constantes globales de configuración del juego, 
las especificaciones de la flota y los códigos de color ANSI para la terminal.
"""

from colorama import Fore, Style, init

# Inicializamos colorama con autoreset=False para controlar manualmente
# cuándo aplicar y restablecer los estilos en el renderizado matricial.
init(autoreset=False)

# ==============================================================================
# PARÁMETROS DEL TABLERO Y LA FLOTA
# ==============================================================================

# Tamaño por defecto de la matriz cuadrada (10 filas x 10 columnas).
TAMANO_TABLERO: int = 10

# Composición de la flota según especificación:
# 1 barco de eslora 4, 2 barcos de eslora 3 y 3 barcos de eslora 2 (Total: 6 barcos).
# Se ordenan de mayor a menor eslora porque algorítmicamente es más eficiente
# ubicar primero los objetos de mayor tamaño cuando el tablero está despejado,
# reduciendo la probabilidad de colisiones y reintentos aleatorios.
FLOTA_ESLORAS: list[int] = [4, 3, 3, 2, 2, 2]

# Puntos de impacto totales necesarios para ganar la partida (4 + 3*2 + 2*3 = 16).
TOTAL_IMPACTOS_VICTORIA: int = sum(FLOTA_ESLORAS)

# Orientaciones posibles expresadas como vectores unitarios de dirección (fila, columna).
ORIENTACIONES: dict[str, tuple[int, int]] = {
    "NORTE": (-1, 0),
    "SUR": (1, 0),
    "ESTE": (0, 1),
    "OESTE": (0, -1)
}

# ==============================================================================
# SÍMBOLOS LÓGICOS INTERNOS (MATRIZ NUMPY)
# ==============================================================================

SIMBOLO_AGUA: str = "_"
SIMBOLO_BARCO: str = "O"
SIMBOLO_TOCADO: str = "X"
SIMBOLO_AGUA_DISPARADA: str = "A"

# ==============================================================================
# PALETA DE COLORES PARA LA INTERFAZ DE TERMINAL
# ==============================================================================
# Se emplean secuencias de escape ANSI mediante colorama para cumplir el requisito
# visual: agua en tonos azules, barcos en blanco brillante e impactos resaltados.

COLOR_RESET: str = Style.RESET_ALL
COLOR_AGUA: str = Fore.BLUE + Style.BRIGHT          # Azul para el mar ('_' y 'A')
COLOR_BARCO: str = Fore.WHITE + Style.BRIGHT        # Blanco brillante para los barcos ('O')
COLOR_TOCADO: str = Fore.RED + Style.BRIGHT         # Rojo intenso para impactos ('X')
COLOR_CABECERA: str = Fore.CYAN + Style.BRIGHT      # Cian para marcos y títulos
COLOR_EXITO: str = Fore.GREEN + Style.BRIGHT        # Verde para mensajes de victoria/acierto
COLOR_ALERTA: str = Fore.YELLOW + Style.BRIGHT      # Amarillo para avisos de turno

# Diccionario de mapeo visual para traducir el símbolo de NumPy a su versión coloreada.
MAPA_VISUAL_COLORES: dict[str, str] = {
    SIMBOLO_AGUA: f"{COLOR_AGUA}{SIMBOLO_AGUA}{COLOR_RESET}",
    SIMBOLO_BARCO: f"{COLOR_BARCO}{SIMBOLO_BARCO}{COLOR_RESET}",
    SIMBOLO_TOCADO: f"{COLOR_TOCADO}{SIMBOLO_TOCADO}{COLOR_RESET}",
    SIMBOLO_AGUA_DISPARADA: f"{COLOR_AGUA}{SIMBOLO_AGUA_DISPARADA}{COLOR_RESET}"
}