# 🧪 Ejercicio práctico: Agente de análisis de ventas con Agentic AI

## 📍 Contexto
Se desea construir un agente inteligente que permita analizar datos de ventas, interactuar con una base de datos SQL y realizar acciones adicionales como generar gráficos o guardar resultados en archivos. El objetivo es practicar la integración de frameworks de agentes con conectores existentes.

> **Nota:** Se recomienda usar conectores que implementen el protocolo **MCP (Multi-Connector Protocol)** para facilitar la interacción con bases de datos y sistemas externos.

## 🎯 Objetivo del ejercicio
Construir un agente que:
* Reciba preguntas en lenguaje natural sobre ventas.
* Traduzca las preguntas a consultas SQL.
* Devuelva resultados en tabla, gráfico o archivo CSV/Excel, según lo solicitado.
* Use un framework de agentes (ej. LangGraph, Strands, LangChain) con conectores preexistentes.
* Permita iterar consultas y generar nuevas acciones a partir de la interacción del usuario.

## 🔧 Requisitos técnicos

### 1. Base de datos de ejemplo
* **Tabla:** `ventas`
* **Columnas:** `id`, `vendedor`, `sede`, `producto`, `cantidad`, `precio`, `fecha`.
* **Origen:** Datos cargados desde CSV o SQL de ejemplo.

### 2. Framework de agentes y conectores
* Usar **LangGraph**, **Strands** o **LangChain**.
* Conector SQL que implemente **MCP** para ejecutar consultas y obtener resultados.
* *Opcional:* módulos para gráficos y persistencia en archivos.

### 3. Visualización y persistencia
* **Gráficos:** Plotly, Matplotlib o Altair.
* **Archivos:** CSV o Excel.

### 4. Interacción
Preguntas en lenguaje natural como:
* *"Top 5 productos más vendidos en Medellín"* → tabla o gráfico.
* *"Vendedor con más ventas por sede Bogotá"* → texto o gráfico.
* *"Guarda las ventas por vendedor en un archivo CSV"* → archivo.

## 📌 Alcance esperado
Agente capaz de:
1.  Interpretar preguntas y generar consultas SQL.
2.  Entregar resultados en tabla, gráfico o archivo, según la instrucción.
3.  Usar un framework de agentes con conectores MCP para interactuar con sistemas externos.
4.  Código modular, organizado y documentado.

## 💡 Ejemplo de flujo

**Caso 1: Consulta y Visualización**
* **Usuario:** "Top 5 productos más vendidos en Medellín"
* **SQL generado:**
    ```sql
    SELECT producto, SUM(cantidad) AS total_vendido
    FROM ventas
    WHERE sede='Medellín'
    GROUP BY producto
    ORDER BY total_vendido DESC
    LIMIT 5;
    ```
* **Agente:** Devuelve tabla y gráfico de barras.

**Caso 2: Exportación de Datos**
* **Usuario:** "Guarda las ventas por vendedor en un archivo CSV"
* **SQL generado:**
    ```sql
    SELECT vendedor, SUM(cantidad*precio) AS total_ventas
    FROM ventas
    GROUP BY vendedor;
    ```
* **Agente:** Exporta los resultados a `ventas_por_vendedor.csv`.

**Caso 3: Consulta Específica**
* **Usuario:** "Quién fue el vendedor con más ventas en Bogotá"
* **SQL generado:**
    ```sql
    SELECT vendedor, SUM(cantidad*precio) AS total_ventas
    FROM ventas
    WHERE sede='Bogotá'
    GROUP BY vendedor
    ORDER BY total_ventas DESC
    LIMIT 1;
    ```
* **Agente:** Entrega respuesta textual y opcional gráfico.

## ⏱ Tiempo estimado
3–4 horas.

## 📌 Sugerencias
* Empiecen usando conectores preexistentes **MCP** para no implementar desde cero.
* Mantener modularidad: separar consultas SQL, acciones (gráficos, archivos) y flujo de agente.
* Documentar claramente los pasos y cómo ejecutar la app.

---

### 📢 Dinámica de trabajo
Por favor sigan la dinámica que se ha recalcado:
1.  **Diseño:** Primero hagan un diseño de la solución.
2.  **Actividades:** Posteriormente diluciden *grosso modo* las actividades.
3.  **Trabajo en grupo:** Traten de trabajar la parte gruesa entre los 2, 3 o 4 integrantes.
4.  **División:** Posteriormente, si pueden dividir, planeen para hacerlo en actividades muy identificadas y granulares.
