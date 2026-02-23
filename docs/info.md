
# Lio-Agent: Gestor de gastos con IA

## Descripción de Negocio

Lio-Agent es un asistente inteligente de finanzas personales diseñado para simplificar el registro de gastos diarios a través de Telegram. Su objetivo principal es eliminar la fricción que supone anotar gastos manualmente en hojas de cálculo o aplicaciones complejas.


El valor fundamental reside en su capacidad de procesamiento de lenguaje natural, permitiendo que cualquier persona (según su token del bot de telegram) registre un gasto simplemente enviando un mensaje de texto casual (ej. "Ayer pagué 50000 de medicina con Nequi"). El bot interpreta la intención, extrae los datos clave y los organiza automáticamente sin que el usuario deba llenar formularios.

## Descripción Técnica

El proyecto implementa una arquitectura moderna y robusta basada en Python asíncrono:

-   Lenguaje: Python 3.14+ con uso de asyncio.

-   Interfaz de Usuario: Bot de Telegram (vía python-telegram-bot).

-   Capa de IA (NLP): Utiliza LangChain para orquestar la comunicación con Ollama (ejecutando el modelo Llama 3.1). El sistema emplea ingeniería de prompts para garantizar que la IA devuelva datos en un formato JSON estructurado.

-   Capa de Datos: PostgreSQL como base de datos persistente, utilizando psycopg3 con soporte para Connection Pool asíncrono.


## Arquitectura de Procesamiento:

-   Patrón Productor-Consumidor: Los mensajes entrantes se encolan inmediatamente en una asyncio.Queue (Productor).

-   Workers en Segundo Plano: Múltiples trabajadores extraen los mensajes de la cola y realizan la inferencia de IA y la persistencia en la DB sin bloquear la recepción de nuevos mensajes (Consumidor).

-   Validación: Uso de Pydantic para definir modelos de datos estrictos y validar la salida de la IA.

-   Infraestructura: Totalmente contenedorizado con Docker y Docker Compose, incluyendo un sistema de telemetría SQL personalizado (Loggin Cursor).


## Requisitos Funcionales (RF)

El sistema debe ser capaz de:

1.  RF-01: Recepción de mensajes: Recibir mensajes de texto natural desde Telegram.

2.  RF-02: Extracción de Información: Extraer mediante IA el monto, la categoría, la descripción y el método de pago (fuente).

3.  RF-03: Gestión de Fechas Inteligente: Interpretar expresiones relativas como "hoy", "ayer" o "hace tres días" basándose en la fecha actual.

4.  RF-04: Clasificación Automática: Asignar los gastos a categorías predefinidas (Alimentación, Cuidado personal, Preferencias, Pagos).

5.  RF-05: Persistencia de Datos: Guardar cada gasto asociado al ID del usuario en la base de datos PostgreSQL.

6.  RF-06: Notificación de Éxito/Error: Confirmar al usuario mediante un mensaje cuando el gasto ha sido guardado o informar si hubo un error en el procesamiento.

7.  RF-07: Manejo de Datos incompletos: Si falta el método de pago, el sistema debe asumir "Efectivo" por defecto e indicarlo en la descripción.


## Requisitos No Funcionales (RNF)

1.  RNF-01: Concurrencia (Asincronismo): El bot no debe dejar de responder mientras la IA "piensa". Todo el procesamiento pesado ocurre de forma no bloqueante.

2.  RNF-02: Estabilidad (Resiliencia): Manejo de errores en la conexión con la base de datos y con el servicio de Ollama mediante excepciones personalizadas.

3.  RNF-03: Rendimiento: El uso de un pool de conexiones asegura un acceso eficiente a la base de datos bajo carga.

4.  RNF-04: Seguridad: Las credenciales (tokens de bot, claves de DB) se gestionan exclusivamente mediante variables de entorno (.env).

5.  RNF-05: Control de Recursos: Implementación de un Semáforo para limitar el número de inferencias de IA simultáneas y no saturar el hardware (CPU/GPU).

6.  RNF-06: Trazabilidad: Sistema de logs detallado para depurar el flujo de mensajes y las consultas SQL en tiempo real.


## Casos de Uso

**CU-01: Registro de gasto estándar**
	Actor: Usuario de Telegram.
	Flujo:
 - El usuario envía: "Almuerzo con amigos 45000 Nequi".
 - El sistema encola el mensaje.
 - El worker de IA extrae: Monto: 45000, Fuente:
   Nequi Leidy, Categoría: Alimentación y aseo.
 - El sistema guarda el registro en la base de datos.
 - El bot responde: "✅ ¡Gasto registrado con éxito!".

**CU-02: Registro de gasto con fecha relativa**
    Actor: Usuario de Telegram.
	Flujo:

 - El usuario envía: "Ayer pagué los servicios de la casa 120000 con
   Bancolombia".
 - La IA calcula la fecha de "ayer" basándose en el calendario actual.
 - El sistema registra el gasto con la fecha exacta del día anterior.

**CU-03: Manejo de error por ambigüedad**
   Actor: Usuario de Telegram.
	Flujo:

 - El usuario envía un mensaje sin sentido o sin monto económico: "Hola bot, ¿cómo estás?".
 - La IA intenta procesar pero el motor de validación (Pydantic) falla al no encontrar un total válido.
 - El bot responde: "❌ No pude procesar tu mensaje. Por favor, intenta de nuevo con más detalles."
