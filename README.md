# RED-SHADOW: Advanced FiveM Dump Analysis Engine

**RED-SHADOW** es una herramienta profesional de analisis forense para volcados de servidores **FiveM (redENGINE)**. Diseñada para identificar triggers explotables, detectar anticheats y generar reportes tecnicos detallados.

## Versiones

| Version | Descripcion |
|---------|-------------|
| **v4.0** | Advanced Forensic Engine - GUI interactivo en CMD, tecnicas avanzadas |
| **v3.0** | Terminal Hacker Edition - Interfaz profesional |
| **v2.0** | Advanced Analysis Engine |

## Caracteristicas v4.0

### GUI Interactivo en CMD
- Menu de navegacion completo con 14 secciones
- Busqueda de triggers por nombre
- Visualizacion categorizada de resultados
- Exportacion a JSON y HTML

### Analisis de Triggers (Avanzado)
- Deteccion de `RegisterNetEvent`, `AddEventHandler`, `TriggerServerEvent`, `TriggerClientEvent`, `RegisterServerEvent`, `RegisterCommand`
- Contexto extendido (20 lineas antes/despues)
- Clasificacion de riesgo con puntuacion 0-100%
- Deteccion de honeypots y trampas
- Cadenas de triggers cross-file (DFS graph)
- Referencias cruzadas entre archivos

### Deteccion de Ofuscacion
- `LOADSTRING` / `EVAL` patterns
- Codificacion Base64 y hexadecimal
- `string.char()` code points
- Concatenacion masiva de strings
- Cifrado XOR / `bit.bxor`
- Arrays de bytes ofuscados
- `getfenv` / `setfenv` manipulation
- Analisis de entropia de Shannon para ajustar confianza

### Analisis de Natives
- Deteccion de natives por hash (`Citizen.InvokeNative(0x...)`)
- Categorizacion: PLAYER, VEHICLE, WEAPON, WORLD, NETWORK, MONEY
- Deteccion de natives peligrosas (god mode, teleport, weapon spawn)

### Server Callbacks
- ESX: `ESX.RegisterServerCallback`
- QBCore: `QBCore.Functions.CreateCallback`
- ox_lib: `lib.callback.register`
- Deteccion de callbacks sin validacion

### Fingerprinting de Anticheats (21+ firmas)
- WaveShield, Phoenix AC, Nexus AC, FireAC
- Anticheese, EasyAdmin, txAdmin
- Badger AC, Spectate Guard, NoPixel AC
- FiveGuard, QBCore AC, ESX AC, vRP Guard
- Clean AC, FairPlay, Shield AC, Lynx AC
- Cerberus, Overwatch AC
- Custom Webhook Ban systems

### Vulnerabilidades de Seguridad
- **SQL Injection**: Queries con concatenacion de strings
- **Token Leak**: Webhooks de Discord, API keys, tokens expuestos
- **Credential Leak**: Passwords hardcodeados, connection strings
- **Insecure HTTP**: Comunicacion sin cifrar
- **Dangerous Exports**: Exports peligrosos accesibles desde client

### Resource Manifests
- Parsing de `fxmanifest.lua` y `__resource.lua`
- Extraccion de server/client scripts
- Mapeo de dependencias
- Deteccion de NUI pages

### Deteccion de Codigo Duplicado
- Hash MD5 de bloques de 5 lineas
- Identificacion de clones entre archivos

### Reportes
- **JSON**: Reporte estructurado completo
- **HTML**: Reporte visual con tema dark hacker
- Estadisticas generales, graficos de riesgo, tablas de triggers

## Instalacion

```bash
git clone https://github.com/FardosESP/red-shadow.git
cd red-shadow
pip install colorama
```

## Uso

Solo ejecuta:
```bash
python main.py
```

Se abrira el menu interactivo en la terminal donde puedes:
1. Seleccionar la ruta del dump
2. Ejecutar el analisis (con o sin GUI)
3. Buscar actualizaciones
4. Reinstalar/reparar la herramienta

El launcher se encarga de todo: instala el proyecto si no existe, verifica updates, y lanza el motor de analisis.

### Modo legacy (argumentos)
```bash
python main.py /ruta/al/dump           # Analisis con GUI
python main.py /ruta/al/dump --no-gui  # Analisis sin GUI
```

## Estructura del Proyecto

```
red-shadow/
  main.py                      # Launcher con auto-updater
  red_shadow_destroyer_v4.py   # v4.0 Advanced Forensic Engine
  red_shadow_destroyer_v3.py   # v3.0 Terminal Hacker Edition
  red_shadow_destroyer_v2.py   # v2.0 Advanced Analysis Engine
  .version                     # Version tracking
  README.md
```

## Disclaimer

Uso autorizado solamente. El uso no autorizado es ilegal.
