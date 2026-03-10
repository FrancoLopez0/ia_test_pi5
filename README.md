# 🚀 PoC: Control de Tracción Diferencial Mediante IA Local (Edge AI)

Este repositorio contiene los resultados de la prueba de concepto (PoC) ejecutada en la computadora de a bordo (Raspberry Pi 5). El objetivo es validar la viabilidad de utilizar un modelo de lenguaje pequeño (SLM) de forma 100% local para traducir instrucciones en lenguaje natural a comandos cinemáticos estructurados (JSON) hacia los microcontroladores.

## ⚙️ Arquitectura del Código

El script de prueba actúa como el puente de software entre el razonamiento lógico de la IA y la ejecución física en el hardware. Se divide en tres bloques fundamentales:

1. **Capa de Comunicaciones (Serial):** Intenta establecer una conexión UART en `/dev/ttyACM0` a 115200 baudios para enviar las tramas al controlador de motores.
2. **Definición de Interfaz (Tool Schema):** Se define la `herramienta_motor`, un contrato estricto que instruye al modelo sobre las direcciones permitidas (`adelante`, `atras`, `izquierda`, `derecha`, `frenar`) y el parámetro numérico de `velocidad` (PWM).
3. **Bucle de Inferencia:** * La IA (en este caso, `qwen2.5-coder:1.5b` para maximizar velocidad) recibe el prompt.
* Analiza la semántica de la frase.
* Debe construir el objeto JSON y preparar los argumentos para la ejecución en el hardware físico.



---

## 📊 Análisis de Resultados de Rendimiento

Las pruebas de latencia se ejecutaron sobre la Raspberry Pi 5 procesando inferencia en CPU.

| Instrucción de Prueba | Resultado Modelo 1.5B (Acción / Latencia) | Resultado Modelo 3B (Acción / Latencia) | Evaluación de la Inferencia | 
| ----- | ----- | ----- | ----- | 
| *Dirección simple* ("avanza a la derecha" / "rápido a la derecha") | `derecha`, vel: 50 (3.49 s) | `derecha`, vel: 100 (**24.50 s**\*) | **3B es más asertivo**. *Nota: El pico de 24s se debe al "Cold Start" (carga inicial en RAM).* | 
| *Comando general* ("retrocede") | `atras`, vel: 50 (3.97 s) | `atras`, vel: 100 (7.13 s) | Ambos entienden la cinemática básica. | 
| *Urgencia* ("corre!") | N/A (No probado) | `adelante`, vel: 100 (6.36 s) | **3B abstrae perfectamente** el concepto de urgencia a velocidad máxima. | 
| *Modificador extremo* ("muuuy despacio hacia la izquierda") | `izquierda`, vel: 100 (4.99 s) ❌ | `izquierda`, vel: 1 (10.12 s) ✅ | **Victoria crítica del 3B**. El 1.5B falló la lógica matemática; el 3B aplicó precisión quirúrgica. | 
| *Abstracción/Emergencia* ("quedate quieto" / "escondete") | `frenar`, vel: 0 (3.69 s) | `frenar`, vel: 0 (6.36 s) | Ambos asocian quedarse quieto con frenar, pero **el 3B logra entender "esconderse" como una orden de frenado**. |

---

## 🔍 Hallazgos Técnicos 

Al revisar los logs de salida, hay tres comportamientos críticos que debemos tener en cuenta para la siguiente iteración de la arquitectura:

1. **Latencia Operativa:** El modelo promedia **~3.9 segundos** para deducir un comando. Esto confirma que el control por voz o texto es viable para planificación de rutas o comandos de alto nivel (Waypoints), pero no debemos usar la IA para la evasión de obstáculos de bajo nivel, que debe seguir delegada a los sensores del microcontrolador.
2. **Bypass de la API de Tools:** En los resultados, la IA imprimió el JSON directamente como texto libre (cayendo en el bloque `else` del código) en lugar de usar la estructura nativa de `tool_calls`. Este es un comportamiento típico en modelos de menos de 2B parámetros. El modelo es lo suficientemente inteligente para crear el JSON, pero su formato de salida no activó la ejecución automática del puerto serie.
3. **Desviación de Parámetros:** En la instrucción de girar "muy despacio", la IA alucinó un valor de velocidad de 100. Necesitamos implementar límites duros en el lado del microcontrolador y mejorar el `system prompt` de la herramienta.

4. **La Penalización del "Cold Start" (Arranque en frío)**:
El primer comando al modelo 3B tardó 24.50 segundos. Esto ocurre porque la Raspberry Pi 5 tuvo que leer un archivo de más de 2 GB desde la memoria SD (o eMMC) y cargarlo en la RAM/ZRAM antes de poder inferir. Las solicitudes posteriores se estabilizaron. Para el diseño final del sistema, debemos enviar un comando "dummy" o de calentamiento al arrancar el sistema para pre-cargar el modelo en la memoria.

5. **El Costo del Razonamiento (Latencia)**:
Pasar a 3B duplicó los tiempos de respuesta estabilizados (de ~3.8s a ~7.5s). Este retraso de 7 segundos significa que el sistema no es apto para evasión de obstáculos en tiempo real. La IA debe usarse como Planificador de Misiones de alto nivel, mientras que el microcontrolador (Pi Pico) debe manejar la capa reactiva (ej. detener los motores automáticamente si el sensor ultrasónico detecta una pared, sin esperar a la IA).

6. **El Salto Cuantitativo en Inteligencia (Precisión)**:
El sacrificio en tiempo valió la pena para comandos complejos. El modelo de 3B demostró un nivel de abstracción superior:

    Entendió que "escondete" significa detener los motores (frenar, 0).

    Corrigió el error del modelo anterior, entendiendo que "muuuy despacio" equivale a la velocidad mínima posible (velocidad: 1), mientras que el 1.5B le había asignado 100.

## ⚠️ Nota sobre la Ejecución del Hardware (Simulación UART)
Es importante destacar para el equipo que durante esta prueba de concepto solo se simuló la conexión serial. No se estableció conexión física con el microcontrolador.

El script operó en un modo de tolerancia a fallos (fallback): la IA generó las tramas JSON y la lógica de Python las procesó exitosamente en memoria, pero no hubo transmisión física por UART. Por lo tanto, las latencias medidas reflejan exclusivamente el tiempo de inferencia del modelo en la Raspberry Pi 5 y no incluyen el overhead de la transmisión física ni el tiempo de reacción mecánica de los motores.