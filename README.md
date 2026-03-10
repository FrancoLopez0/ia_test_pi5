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

| Instrucción Natural | Comando JSON Generado | Latencia | Observaciones |
| --- | --- | --- | --- |
| "Avanza a velocidad media" | `{"direccion": "adelante", "velocidad": 60}` | 3.50 s | Traducción semántica excelente. |
| "Retrocede lentamente" | `{"direccion": "atras", "velocidad": 50}` | 3.97 s | Formateo JSON multilinea correcto. |
| "Muevete muuuy despacio hacia la izquierda" | `{"direccion": "izquierda", "velocidad": 100}` | 4.99 s | **Fallo de razonamiento numérico:** Entendió la dirección pero asignó la máxima velocidad. |
| "Quedate quieto !" | `{"direccion": "frenar", "velocidad": 0}` | 3.69 s | Interpretación de comando de emergencia correcta. |
| "Rapido hacia la derecha" | `{"direccion": "derecha", "velocidad": 50}` | 3.49 s | Traducción funcional pero conservadora en velocidad. |

---

## 🔍 Hallazgos Técnicos 

Al revisar los logs de salida, hay tres comportamientos críticos que debemos tener en cuenta para la siguiente iteración de la arquitectura:

1. **Latencia Operativa:** El modelo promedia **~3.9 segundos** para deducir un comando. Esto confirma que el control por voz o texto es viable para planificación de rutas o comandos de alto nivel (Waypoints), pero no debemos usar la IA para la evasión de obstáculos de bajo nivel, que debe seguir delegada a los sensores del microcontrolador.
2. **Bypass de la API de Tools:** En los resultados, la IA imprimió el JSON directamente como texto libre (cayendo en el bloque `else` del código) en lugar de usar la estructura nativa de `tool_calls`. Este es un comportamiento típico en modelos de menos de 2B parámetros. El modelo es lo suficientemente inteligente para crear el JSON, pero su formato de salida no activó la ejecución automática del puerto serie.
3. **Desviación de Parámetros:** En la instrucción de girar "muy despacio", la IA alucinó un valor de velocidad de 100. Necesitamos implementar límites duros en el lado del microcontrolador y mejorar el `system prompt` de la herramienta.

## ⚠️ Nota sobre la Ejecución del Hardware (Simulación UART)
Es importante destacar para el equipo que durante esta prueba de concepto solo se simuló la conexión serial. No se estableció conexión física con el microcontrolador.

El script operó en un modo de tolerancia a fallos (fallback): la IA generó las tramas JSON y la lógica de Python las procesó exitosamente en memoria, pero no hubo transmisión física por UART. Por lo tanto, las latencias medidas reflejan exclusivamente el tiempo de inferencia del modelo en la Raspberry Pi 5 y no incluyen el overhead de la transmisión física ni el tiempo de reacción mecánica de los motores.