import ollama
import serial
import json
import time

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
        model= 'qwen2.5-coder:1.5b',
        messages=[{'role': 'user', 'content': prompt_usuario}],
        tools=[herramienta_motor]
    )
    t1_inferencia = time.time()
    print(f"  [Log] Tiempo de decisión IA: {t1_inferencia - t0_inferencia:.2f} s")
    
    if respuesta['message'].get('tool_calls'):
        for tool in respuesta['message']['tool_calls']:
            if tool['function']['name'] == 'enviar_comando_motor':
                args = tool['function']['arguments']
                
                # --- FASE 2: Ejecución Física (Hardware) ---
                t0_hardware = time.time()
                resultado_hardware = enviar_comando_motor(args.get('direccion'), args.get('velocidad'))
                t1_hardware = time.time()
                print(f"  [Log] Tiempo de ejecución Hardware: {(t1_hardware - t0_hardware) * 1000:.2f} ms")
                print(f"  [Acción] Ejecutando: {args}")
                
                # --- FASE 3: Síntesis de Respuesta (Inferencia final) ---
                t0_sintesis = time.time()
                respuesta_final = ollama.chat(
                    model='llama3.2:3b',
                    messages=[
                        {'role': 'user', 'content': prompt_usuario},
                        respuesta['message'],
                        {'role': 'tool', 'content': resultado_hardware}
                    ]
                )
                t1_sintesis = time.time()
                print(f"  [Log] Tiempo de síntesis IA: {t1_sintesis - t0_sintesis:.2f} s")
                print(f"[{time.strftime('%H:%M:%S')}] IA: {respuesta_final['message']['content']}")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] IA: {respuesta['message']['content']}")

    tiempo_fin_total = time.time()
    print(f"=== Tiempo Total del Ciclo: {tiempo_fin_total - tiempo_inicio_total:.2f} s ===")

# Pruebas
# procesar_instruccion("Avanzá a media máquina hacia el objetivo")
# procesar_instruccion("Detené los motores de inmediato")
# procesar_instruccion("Anda en reversa a toda velocidad")
while True:
    procesar_instruccion(input("msj:"))
