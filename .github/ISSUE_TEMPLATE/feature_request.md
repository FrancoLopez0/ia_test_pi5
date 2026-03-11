---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: ''
assignees: ''

---

---
name: "🚀 Implementación de Módulo/Driver"
about: "Template estándar para creación de nuevos módulos de firmware."
title: "[FEAT] Nombre del Módulo"
labels: enhancement, technical-debt
assignees: ''
---

## 📝 1. Resumen del Requerimiento
*Describir brevemente qué periférico o funcionalidad se va a controlar y por qué es necesario (Contexto).*

---

## ⚙️ 2. Especificaciones Técnicas (Hard Rules)
Para asegurar la calidad "Industrial-Grade", el desarrollo **debe** cumplir con:

- [ ] **Encapsulamiento:** Crear un `struct <nombre>_t` para manejar el estado/instancia.
- [ ] **Paso de Parámetros:** Si una función requiere >3 argumentos, usar un struct de configuración (`<nombre>_config_t`).
- [ ] **Tipado Estricto:** Prohibido el uso de "Magic Numbers". Definir `enums` para estados y `#define` para constantes.
- [ ] **Seguridad de Memoria:** Validar punteros `NULL` y rangos de variables al inicio de cada función.
- [ ] **Documentación:** Formato **Doxygen** completo en el archivo `.h` (brief, params, return).

---

## 🛠 3. Interfaz (API) Sugerida
*Definir aquí las funciones mínimas requeridas:*

1.  `_init()`: Inicialización de hardware/software.
2.  `_set_...()`: Funciones de configuración.
3.  `_get_...()`: Funciones de lectura de estado.
4.  `_process()`: (Opcional) Si requiere ejecución periódica.

---

## ✅ 4. Criterios de Aceptación
- [ ] Compilación limpia (Zero warnings).
- [ ] El archivo `.h` incluye guardas de inclusión (`#ifndef ...`).
- [ ] Se incluye un snippet de ejemplo o test unitario básico.
- [ ] Los nombres de funciones siguen el formato `prefijo_accion_sujeto`.

---

> [!IMPORTANT]
> **Nota sobre PID/Algoritmos complejos:** Si el módulo requiere lógica de control avanzada, dejar el "hook" listo pero postergar la implementación pesada para un Issue dedicado de "Control".
