# RED-SHADOW: Advanced FiveM Dump Analysis Engine

**RED-SHADOW** es una herramienta profesional de análisis forense para volcados de servidores **FiveM (redENGINE)**. Diseñada para identificar triggers explotables, detectar anticheats y generar reportes técnicos detallados.

## Características

### Core Analysis
- **Detección de Anticheats**: Identifica WaveShield, Phoenix AC, Nexus, FireAC y otros sistemas de protección
- **Extracción de Triggers**: Localiza todos los eventos del servidor
- **Análisis de Flujo de Datos**: Rastrea dependencias cruzadas entre triggers
- **Detección de Honeypots**: Identifica trampas diseñadas para banear ejecutores
- **Análisis de Validaciones**: Detecta protecciones de servidor

### Reporting
- **Reportes Forenses**: Análisis técnico profundo de cada trigger
- **Trazabilidad Completa**: Dónde se define, dónde se llama
- **Código Extraído**: Muestra el código Lua exacto del servidor
- **Puntuación de Riesgo**: Calcula el riesgo individual y general
- **Exportación JSON**: Reportes estructurados

## Instalación

```bash
git clone https://github.com/FardosESP/red-shadow.git
cd red-shadow
pip install colorama
```

## Uso

```bash
python red_shadow_destroyer_v3.py /ruta/al/dump
```

## Versiones

- **v2.0**: Advanced Analysis Engine
- **v3.0**: Terminal Hacker Edition (Interfaz profesional)

## Disclaimer

Uso autorizado solamente. El uso no autorizado es ilegal.
