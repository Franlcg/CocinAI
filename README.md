# Proyecto: CocinAI

## Autores
* Francisco Luis Cara García
* Javier Martín Vega

## 1. Introducción

Este proyecto consiste en crear un sistema que ayude a las personas a encontrar recetas basadas en los ingredientes que tienen disponibles. En lugar de escribir los ingredientes, los usuarios también podrán decirlos en voz alta, y el sistema los convertirá en texto para hacer las recomendaciones o seleccionando imágenes de los ingredientes.  
El objetivo es aplicar inteligencia artificial para analizar una lista de recetas y sugerir las que mejor se adapten a los ingredientes que el usuario proporciona.

## 2. Objetivos

### Objetivo General

Desarrollar un sistema de recomendación de recetas que permita a los usuarios ingresar ingredientes mediante texto o voz y, a partir de esa lista, pedir a la IA generativa que diseñe recetas sugeridas de manera automática.

### Objetivos Específicos

- Utilizar un archivo CSV o varios con recetas para entrenar un modelo de recomendación.
- Convertir los ingredientes en un formato que la inteligencia artificial pueda entender.
- Posibilidad de generar/buscar imagen del plato.
- Implementar varios modelos.
- Integrar una función de reconocimiento de voz para que el usuario pueda hablar en lugar de escribir.
- Crear una interfaz sencilla en consola o web para que el usuario interactúe con el sistema.

## 3. Tecnologías y Herramientas

- **Lenguaje de Programación**: Python
- **Librerías**:
  - **Pandas**: Para manejar los datos del CSV.
  - **Scikit-learn**: Para entrenar el modelo de recomendación.
  - **SpeechRecognition**: Para convertir voz en texto.
  - **Flask** (opcional): Para crear una interfaz web sencilla.

## 4. Desarrollo del Proyecto

### 4.1 Conseguir y preparar los datos

Buscaremos un archivo CSV que contenga muchas recetas con los siguientes datos:
- Nombre de la receta.
- Lista de ingredientes.
- Categoría (vegetariano, sin gluten, etc.).

Limpiaremos los datos para asegurarnos de que el sistema pueda leerlos correctamente.

### 4.2 Convertir los ingredientes en un formato numérico

Los ingredientes están en texto, pero la IA no entiende palabras. Para solucionarlo, los transformaremos en listas de números utilizando una técnica llamada **TF-IDF**, que asigna un valor a cada palabra según su importancia en las recetas.

### 4.3 Crear el modelo de recomendación

Usaremos un modelo que compara los ingredientes ingresados con las recetas disponibles y devuelve las más similares.

### 4.4 Agregar reconocimiento de voz

Para que los usuarios puedan decir los ingredientes en lugar de escribirlos, usaremos la librería **SpeechRecognition**. Esta herramienta convierte la voz en texto para que el sistema lo procese.

### 4.5 Pruebas y creación de una interfaz sencilla

Diseñaremos una interfaz simple que muestre los resultados en consola o en una página web básica con **Flask**.

## 5. Planificación del Desarrollo

| **Fase** | **Tareas**                                          | **Tiempo Estimado** |
|----------|-----------------------------------------------------|---------------------|
| Fase 1   | Buscar y limpiar el CSV de recetas                 | 5 horas             |
| Fase 2   | Convertir los ingredientes en números con TF-IDF   | 10 horas            |
| Fase 3   | Crear y entrenar el modelo                         | 20 horas            |
| Fase 4   | Implementar reconocimiento de voz con SpeechRecognition | 20 horas            |
| Fase 5   | Hacer pruebas y crear una interfaz simple (consola o web) | 10 horas            |
| Fase 6   | Documentar el proceso y ajustes finales            | 5 horas             |

## 6. Entrega y Documentación

- Código en Python con el sistema funcionando.
- Informe técnico explicando los pasos realizados.
- Repositorio en GitHub con instrucciones para que otros puedan probarlo.

## 7. Conclusión

Este proyecto combinará inteligencia artificial con reconocimiento de voz, facilitando la búsqueda de recetas de forma rápida y sencilla. Aplicaremos lo aprendido en IA y análisis de datos para resolver un problema cotidiano de manera práctica y eficiente.

## 8. Instrucciones de uso

- Clonar
- Configurar .env con la clave de openai
- Instalar requirements.txt