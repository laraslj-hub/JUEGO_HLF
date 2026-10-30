# -*- coding: utf-8 -*-
"""
Módulo: funciones.py
Descripción: Contiene las funciones centrales de creación de tableros, 
generación aleatoria de embarcaciones, validación de márgenes espaciales 
con NumPy y ejecución de disparos.
"""

import random
import numpy as np
import variables as var


def crear_tablero(tamaño: int = var.TAMANO_TABLERO) -> np.ndarray:
    """
    Crea y devuelve una matriz cuadrada de NumPy rellena con el carácter '_'.
    
    ¿Por qué usar np.full con dtype='<U1'?
    Reservar memoria contigua para caracteres Unicode de longitud 1 optimiza
    el uso de RAM y permite aplicar operaciones vectorizadas de comparación
    mucho más rápido que usando listas anidadas de Python.
    """
    return np.full((tamaño, tamaño), var.SIMBOLO_AGUA, dtype="<U1")


def crear_barco(eslora: int, tamaño: int = var.TAMANO_TABLERO) -> list[tuple[int, int]]:
    """
    Genera de forma aleatoria las coordenadas de un barco según su eslora.
    
    ¿Por qué se diseña así?
    Se elige un punto de origen (fila, columna) al azar y un vector de dirección.
    A partir del origen se proyectan las casillas sumando el vector unitario.
    Esto garantiza que todas las casillas del barco sean contiguas y rectilíneas.
    """
    while True:
        # Selección aleatoria de la coordenada inicial
        fila_inicial = random.randint(0, tamaño - 1)
        col_inicial = random.randint(0, tamaño - 1)
        
        # Selección aleatoria de una de las 4 direcciones cardinales
        delta_fila, delta_col = random.choice(list(var.ORIENTACIONES.values()))
        
        barco: list[tuple[int, int]] = []
        for i in range(eslora):
            nueva_fila = fila_inicial + (delta_fila * i)
            nueva_col = col_inicial + (delta_col * i)
            barco.append((nueva_fila, nueva_col))
            
        # Verificamos preliminarmente que el barco no se salga de los límites del tablero
        dentro_limites = all(0 <= f < tamaño and 0 <= c < tamaño for f, c in barco)
        if dentro_limites:
            return barco


def validar_posicion_barco(barco: list[tuple[int, int]], tablero: np.ndarray) -> bool:
    """
    Comprueba que el barco esté dentro del tablero, no se superponga con otro
    y mantenga al menos 1 casilla de separación horizontal y vertical (halo de seguridad).
    
    ¿Por qué usar Slicing de NumPy en lugar de bucles?
    En lugar de recorrer casilla por casilla, calculamos la caja delimitadora
    (bounding box) que rodea al barco ampliada en 1 unidad en todas direcciones.
    Mediante una única operación vectorial `np.any()`, comprobamos si existe
    alguna 'O' en esa submatriz en tiempo constante O(1).
    """
    tamaño = tablero.shape[0]
    filas = [coordenada[0] for coordenada in barco]
    columnas = [coordenada[1] for coordenada in barco]
    
    # 1. Comprobación de límites del tablero
    if min(filas) < 0 or max(filas) >= tamaño or min(columnas) < 0 or max(columnas) >= tamaño:
        return False
        
    # 2. Definición del perímetro de seguridad (1 casilla de margen alrededor del barco)
    # Se usa max(0, ...) y min(tamaño, ...) para no indexar fuera de los bordes de la matriz.
    fila_min = max(0, min(filas) - 1)
    fila_max = min(tamaño, max(filas) + 2)  # +2 porque el límite superior en slicing es exclusivo
    col_min = max(0, min(columnas) - 1)
    col_max = min(tamaño, max(columnas) + 2)
    
    # Extraemos la submatriz que comprende al barco y su halo circundante
    submatriz_entorno = tablero[fila_min:fila_max, col_min:col_max]
    
    # Si hay algún barco ('O') en la submatriz, la posición es inválida
    if np.any(submatriz_entorno == var.SIMBOLO_BARCO):
        return False
        
    return True


def colocar_barco(barco: list[tuple[int, int]], tablero: np.ndarray) -> np.ndarray:
    """
    Posiciona un barco concreto sobre el tablero escribiendo 'O' en sus coordenadas.
    
    Nota técnica: Recibe la lista de tuplas [(f1, c1), (f2, c2)...] y modifica
    el array de NumPy asignando el carácter 'O'.
    """
    for fila, col in barco:
        tablero[fila, col] = var.SIMBOLO_BARCO
    return tablero


def colocar_barcos(tablero: np.ndarray, esloras: list[int] = None) -> np.ndarray:
    """
    Genera y posiciona de forma aleatoria la flota completa de 6 barcos
    (3 de eslora 2, 2 de eslora 3 y 1 de eslora 4) cumpliendo todas las restricciones
    de no superposición y separación mínima de 1 casilla.
    """
    if esloras is None:
        esloras = var.FLOTA_ESLORAS
        
    tamaño = tablero.shape[0]
    
    for eslora in esloras:
        colocado = False
        intentos = 0
        max_intentos = 1000  # Salvaguarda contra bloqueos por configuraciones imposibles
        
        while not colocado and intentos < max_intentos:
            intentos += 1
            barco_candidato = crear_barco(eslora, tamaño)
            if validar_posicion_barco(barco_candidato, tablero):
                colocar_barco(barco_candidato, tablero)
                colocado = True
                
        if not colocado:
            # Si por azar geométrico se produjera un bloqueo, se reinicia el tablero
            # y se vuelve a intentar recursivamente para garantizar siempre una solución válida.
            tablero.fill(var.SIMBOLO_AGUA)
            return colocar_barcos(tablero, esloras)
            
    return tablero


def disparar(
    casilla: tuple[int, int], 
    tablero_objetivo: np.ndarray, 
    tablero_disparos: np.ndarray = None,
    mostrar_mensaje: bool = True
) -> tuple[bool, str]:
    """
    Ejecuta un disparo sobre la coordenada `casilla` en `tablero_objetivo`.
    
    - Si impacta en un barco ('O'), lo sustituye por 'X' e imprime 'Tocado'.
    - Si impacta en agua ('_'), lo sustituye por 'A' e imprime 'Agua'.
    - Si se proporciona `tablero_disparos` (el radar del jugador), registra también
      allí el resultado para mantener sincronizados ambos tableros.
      
    Devuelve una tupla: (acierto: bool, mensaje: str)
    """
    fila, col = casilla
    contenido_actual = tablero_objetivo[fila, col]
    
    if contenido_actual == var.SIMBOLO_BARCO:
        tablero_objetivo[fila, col] = var.SIMBOLO_TOCADO
        if tablero_disparos is not None:
            tablero_disparos[fila, col] = var.SIMBOLO_TOCADO
        mensaje = "¡Tocado! Ha impactado en un barco enemigo."
        if mostrar_mensaje:
            print(f"{var.COLOR_EXITO}>>> {mensaje}{var.COLOR_RESET}")
        return True, mensaje
        
    elif contenido_actual == var.SIMBOLO_AGUA:
        tablero_objetivo[fila, col] = var.SIMBOLO_AGUA_DISPARADA
        if tablero_disparos is not None:
            tablero_disparos[fila, col] = var.SIMBOLO_AGUA_DISPARADA
        mensaje = "Agua. El disparo ha caído en el mar."
        if mostrar_mensaje:
            print(f"{var.COLOR_AGUA}>>> {mensaje}{var.COLOR_RESET}")
        return False, mensaje
        
    else:
        # Caso en que se dispare a una coordenada ya descubierta ('X' o 'A')
        mensaje = "Coordenada ya disparada anteriormente. Pierde el disparo."
        if mostrar_mensaje:
            print(f"{var.COLOR_ALERTA}>>> {mensaje}{var.COLOR_RESET}")
        return False, mensaje