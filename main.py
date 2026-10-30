# -*- coding: utf-8 -*-
"""
Módulo: main.py
Descripción: Punto de entrada principal para ejecutar el juego "Hundir la Flota"
desde la terminal de Visual Studio Code.
"""

import sys
import variables as var
import utils


def mostrar_menu_principal() -> None:
    """Presenta el menú interactivo inicial en la consola."""
    utils.limpiar_pantalla()
    print(f"{var.COLOR_CABECERA}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                 BIENVENIDO A HUNDIR LA FLOTA                     ║")
    print(f"║           Programación Modular Orientada a Objetos               ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{var.COLOR_RESET}\n")
    print("Seleccione el modo de ejecución:")
    print(f"  {var.COLOR_EXITO}[1]{var.COLOR_RESET} Jugar partida completa contra la Máquina (Terminal)")
    print(f"  {var.COLOR_ALERTA}[2]{var.COLOR_RESET} Ejecutar Modo Demo (Pruebas guiadas + Simulación)")
    print(f"  {var.COLOR_TOCADO}[3]{var.COLOR_RESET} Salir de la aplicación\n")


def main() -> None:
    """Controla el bucle principal de la aplicación y gestiona las interrupciones."""
    while True:
        try:
            mostrar_menu_principal()
            opcion = input(f"{var.COLOR_CABECERA}Introduzca el número de su elección (1-3): {var.COLOR_RESET}").strip()
            
            if opcion == "1":
                nombre = input(f"\n{var.COLOR_CABECERA}Introduzca su nombre o alias (ENTER para 'Comandante'): {var.COLOR_RESET}").strip()
                if not nombre:
                    nombre = "Comandante"
                partida = utils.JuegoHundirLaFlota(nombre_humano=nombre)
                partida.iniciar_partida(modo_automatico=False)
                input(f"\n{var.COLOR_CABECERA}Presione ENTER para volver al menú principal...{var.COLOR_RESET}")
                
            elif opcion == "2":
                utils.ejecutar_demo_terminal()
                
            elif opcion == "3":
                utils.limpiar_pantalla()
                print(f"{var.COLOR_EXITO}Gracias por jugar a Hundir la Flota. ¡Hasta pronto!{var.COLOR_RESET}")
                sys.exit(0)
            else:
                print(f"{var.COLOR_TOCADO}Opción no válida. Por favor, seleccione 1, 2 o 3.{var.COLOR_RESET}")
                input("Presione ENTER para continuar...")
                
        except KeyboardInterrupt:
            print(f"\n\n{var.COLOR_ALERTA}Saliendo del programa de forma segura...{var.COLOR_RESET}")
            sys.exit(0)


if __name__ == "__main__":
    main()