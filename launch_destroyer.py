#!/usr/bin/env python3
"""
RED-SHADOW DESTROYER v4.0 - Launcher
Abre la interfaz web para análisis forense de dumps FiveM
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_gui import launch_web_gui

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🔥 RED-SHADOW DESTROYER v4.0")
    print("  Análisis Forense de Dumps FiveM - Interfaz Web")
    print("="*70 + "\n")
    
    print("🌐 Abriendo interfaz web...")
    print("📝 Ingresa la ruta del dump desde el navegador\n")
    
    # Lanzar interfaz web (landing page)
    launch_web_gui(engine=None, auto_open=True)
