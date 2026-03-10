import ollama
import serial
import json
import time
import re  # <--- Necesario para extraer el JSON del texto libre

# 1. Configuración del puerto serie
try:
    pico_serial = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
except Exception as e:
    print(f"Advertencia: No se pudo abrir el puerto serie: {e}")
    pico_serial = None

def enviar_comando_motor(direccion: str, velocidad: int) -> str:
    comando = {"dir": direccion, "vel": velocidad}
    trama_json = json.dumps(comando) + '\n'
    
    if pico_serial:
        pico_serial.write(trama_json.encode('utf-8'))
        return f"Éxito: Comando {trama_json.strip()} enviado al hardware."
    return f"Simulación: Se habría enviado {trama_json.strip()}"

herramienta_motor = {
    'type': 'function',
    'function': {
        'name': 'enviar_comando_motor',
        'description': 'Controla los motores. Úsalo para mover el vehículo.',
        'parameters': {
            'type': 'object',
            'properties': {
                'direccion': {
                    'type': 'string',
                    'enum': ['adelante', 'atras', 'izquierda', 'derecha', 'frenar']
                },
                'velocidad': {
                    'type': 'integer'
                }
            },
            'required': ['direccion', 'velocidad']
        }
    }
}

def procesar_instruccion(prompt_usuario):
    print(f"\n[{time.strftime('%H:%M:%S')}] Usuario: {prompt_usuario}")
    tiempo_inicio_total = time.time()
    
    # --- FASE 1: Decisión Lógica (Inferencia) ---
    t0_inferencia = time.time()
    respuesta = ollama.chat(
        model= 'qwen2.5-coder:3b',
        messages=[{'role': 'user', 'content': prompt_usuario}],
        tools=[herramienta_motor]
    )
    t1_inferencia = time.time()
    print(f"  [Log] Tiempo de decisión IA: {t1_inferencia - t0_inferencia:.2f} s")
    
    # Evaluar si la IA usó la API nativa de herramientas
    if respuesta['message'].get('tool_calls'):
        for tool in respuesta['message']['tool_calls']:
            if tool['function']['name'] == 'enviar_comando_motor':
                args = tool['function']['arguments']
                
                # --- FASE 2: Ejecución Física (Hardware vía API) ---
                t0_hardware = time.time()
                resultado_hardware = enviar_comando_motor(args.get('direccion'), args.get('velocidad'))
                t1_hardware = time.time()
                print(f"  [Log] Tiempo de ejecución Hardware: {(t1_hardware - t0_hardware) * 1000:.2f} ms")
                print(f"  [Acción Oficial] Ejecutando: {args}")
                
    else:
        # --- EL BYPASS: La IA respondió con texto libre ---
        texto_crudo = respuesta['message'].get('content', '')
        print(f"  [Aviso] La IA hizo bypass de la API. Intentando rescatar el JSON...")
        
        # Buscar cualquier bloque entre llaves {} usando Regex (ignora los ```json y texto extra)
        match = re.search(r'\{[\s\S]*\}', texto_crudo)
        
        if match:
            json_limpio = match.group(0)
            try:
                # Intentar parsear el string limpio a un diccionario Python
                datos = json.loads(json_limpio)
                
                if datos.get('name') == 'enviar_comando_motor' and 'arguments' in datos:
                    args = datos['arguments']
                    
                    # Limpieza y seguridad para el Rover:
                    direccion = args.get('direccion', 'frenar')
                    # Asegurar que la velocidad sea un entero positivo absoluto
                    try:
                        velocidad = abs(int(args.get('velocidad', 0)))
                    except ValueError:
                        velocidad = 0 
                    
                    # --- FASE 2: Ejecución Física (Hardware Rescatado) ---
                    t0_hardware = time.time()
                    resultado_hardware = enviar_comando_motor(direccion, velocidad)
                    t1_hardware = time.time()
                    
                    print(f"  [Log] Tiempo de ejecución Hardware: {(t1_hardware - t0_hardware) * 1000:.2f} ms")
                    print(f"  [Acción Rescatada] Ejecutando Dir: '{direccion}' | Vel: {velocidad}")
                else:
                    print(f"  [Fallo] El JSON existe pero no coincide con la herramienta esperada.")
                    
            except json.JSONDecodeError:
                print(f"  [Error Crítico] El texto parecía JSON pero la sintaxis está rota: \n{json_limpio}")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] IA respondió solo texto conversacional: {texto_crudo}")

    tiempo_fin_total = time.time()
    print(f"=== Tiempo Total del Ciclo: {tiempo_fin_total - tiempo_inicio_total:.2f} s ===")

# Bucle de pruebas
while True:
    procesar_instruccion(input("msj: "))