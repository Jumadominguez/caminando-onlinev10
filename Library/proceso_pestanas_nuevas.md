# Proceso de Implementación: Optimización con Pestañas Nuevas para Tipos de Producto

## Resumen Ejecutivo

Este documento describe la implementación de una optimización significativa en el proceso de scraping de Carrefour Argentina. En lugar de expandir los filtros de "Tipo de Producto" para cada tipo individualmente, se mantiene una pestaña "madre" con los filtros expandidos y se abre cada tipo de producto filtrado en pestañas "hijas" separadas.

## Problema Actual

- **Tiempo excesivo**: Expandir filtros ("Ver más") y seleccionar cada tipo de producto individualmente consume ~30-60 segundos por tipo
- **Repetición innecesaria**: El proceso de expansión se repite para cada uno de los ~50-100 tipos por categoría
- **Fragilidad**: Fallos en la expansión pueden detener todo el proceso de la categoría

## Solución Propuesta

Mantener una pestaña principal ("madre") con filtros expandidos y abrir URLs filtradas en pestañas nuevas ("hijas") para extracción.

## Arquitectura de la Solución

### 1. Pestaña Madre
- **Responsabilidad**: Mantener filtros expandidos y servir como base para generar URLs filtradas
- **Estado**: Filtros de "Tipo de Producto" expandidos con "Ver más"
- **Persistencia**: Se mantiene abierta durante todo el procesamiento de la categoría

### 2. Pestañas Hijas
- **Responsabilidad**: Extraer productos de un tipo específico
- **Ciclo de vida**: Crear → Extraer → Cerrar
- **Aislamiento**: Cada pestaña es independiente, fallos no afectan otras

## Flujo de Implementación

### Fase 1: Configuración Inicial (Pestaña Madre)

```python
# 1. Navegar a la categoría
driver.get(category_url)
handle_cookies(driver)

# 2. Abrir panel de filtros
open_filters_panel(driver)

# 3. Expandir menú "Tipo de Producto" UNA SOLA VEZ
product_types_container = expand_product_type_menu(driver)
scroll_and_click_ver_mas_product_types(driver, product_types_container)

# 4. Obtener lista completa de tipos de producto
all_product_types = get_all_product_types(driver)
```

### Fase 2: Procesamiento por Tipo (Pestañas Hijas)

```python
for product_type in all_product_types:
    # 2.1 Generar URL filtrada
    filtered_url = generate_filtered_url(category_url, product_type)
    
    # 2.2 Abrir en nueva pestaña
    driver.execute_script(f"window.open('{filtered_url}', '_blank');")
    
    # 2.3 Cambiar a nueva pestaña
    driver.switch_to.window(driver.window_handles[-1])
    
    try:
        # 2.4 Extraer productos de la pestaña hija
        products = extract_all_products_from_pages(driver, product_type, category_name)
        
        # 2.5 Guardar en base de datos
        save_products_to_db(products, category_name)
        
        # 2.6 Registrar éxito
        successful_types.append({'type': product_type, 'products': len(products)})
        
    except Exception as e:
        # 2.7 Registrar fallo
        failed_types.append({'type': product_type, 'reason': str(e)})
    
    finally:
        # 2.8 Cerrar pestaña hija
        driver.close()
        
        # 2.9 Volver a pestaña madre
        driver.switch_to.window(driver.window_handles[0])
        
        # 2.10 Limpiar selección en pestaña madre (opcional)
        clear_product_type_selection(driver, product_type)
```

### Fase 3: Función generate_filtered_url()

```python
def generate_filtered_url(base_url, product_type):
    """
    Genera URL con filtro de tipo de producto aplicado
    """
    # Estrategia 1: Inspeccionar patrón de URL de Carrefour
    # Ejemplo: https://www.carrefour.com.ar/.../categoria?tipo-de-producto=adaptador-usb
    
    # 3.1 Normalizar nombre del tipo de producto
    normalized_type = normalize_product_type_name(product_type)
    
    # 3.2 Construir URL con parámetro
    filtered_url = f"{base_url}?tipo-de-producto={normalized_type}"
    
    return filtered_url

def normalize_product_type_name(product_type):
    """
    Convierte nombre del tipo a formato URL
    """
    # Convertir a lowercase, reemplazar espacios con guiones, etc.
    return product_type.lower().replace(' ', '-').replace('á', 'a').replace('é', 'e')...
```

## Desafíos Técnicos y Soluciones

### Desafío 1: Identificar Patrón de URL
**Problema**: Carrefour puede usar IDs internos o codificación compleja para tipos de producto.

**Soluciones**:
1. **Inspección manual**: Analizar URLs generadas al aplicar filtros manualmente
2. **Extracción de atributos**: Obtener `value` o `data-*` de los checkboxes
3. **Fallback**: Si URL directa falla, usar método tradicional en pestaña madre

### Desafío 2: Manejo de Múltiples Pestañas
**Problema**: Selenium debe manejar switches entre pestañas correctamente.

**Solución**:
```python
# Mantener referencia a pestaña madre
mother_window = driver.current_window_handle

# Abrir nueva pestaña
driver.execute_script("window.open('', '_blank');")
driver.switch_to.window(driver.window_handles[-1])

# Procesar...

# Volver a madre
driver.close()  # Cerrar hija
driver.switch_to.window(mother_window)
```

### Desafío 3: Rate Limiting
**Problema**: Múltiples pestañas pueden activar protección anti-bot.

**Soluciones**:
1. **Delay entre aperturas**: 2-3 segundos entre nuevas pestañas
2. **User agents rotativos**: Diferente UA por pestaña
3. **Límite concurrente**: Máximo 3 pestañas hijas simultáneas

## Beneficios Esperados

### Rendimiento
- **Reducción de tiempo**: ~70-80% menos tiempo en expansión de filtros
- **Procesamiento paralelo**: Múltiples pestañas pueden trabajar simultáneamente
- **Menor carga**: Menos interacciones con DOM de pestaña madre

### Robustez
- **Aislamiento de fallos**: Error en una pestaña hija no afecta otras
- **Recuperación automática**: Pestaña madre permanece intacta
- **Reinicio granular**: Solo reiniciar pestaña afectada si es necesario

### Mantenibilidad
- **Código más limpio**: Separación clara de responsabilidades
- **Debugging fácil**: Cada pestaña es independiente
- **Escalabilidad**: Fácil agregar más optimizaciones

## Plan de Implementación

### Iteración 1: Prototipo Básico
1. Implementar apertura de URLs filtradas en nuevas pestañas
2. Verificar que la extracción funciona correctamente
3. Medir mejora de rendimiento

### Iteración 2: Optimizaciones
1. Implementar rotación de user agents por pestaña
2. Agregar delays inteligentes entre aperturas
3. Optimizar manejo de memoria (cerrar pestañas promptly)

### Iteración 3: Manejo de Errores
1. Sistema de reintento por pestaña
2. Detección automática de bloqueos
3. Fallback a método tradicional si URLs fallan

## Métricas de Éxito

- **Tiempo de procesamiento**: Reducción del 60-70%
- **Tasa de éxito**: Mantener >95% de tipos procesados
- **Estabilidad**: <5% de fallos por bloqueos anti-bot
- **Mantenibilidad**: Código fácil de entender y modificar

## Riesgos y Mitigaciones

### Riesgo: Detección Anti-Bot
**Mitigación**: Implementar delays variables, user agents diversos, comportamiento humanoide

### Riesgo: URLs Incorrectas
**Mitigación**: Sistema de validación de URLs generadas, fallback automático

### Riesgo: Memoria del Browser
**Mitigación**: Limitar número de pestañas concurrentes, garbage collection periódica

## Conclusión

Esta optimización representa una mejora significativa en la eficiencia y robustez del scraper. Al eliminar la expansión repetitiva de filtros y aislar el procesamiento de cada tipo de producto, reduciremos drásticamente los tiempos de ejecución mientras aumentamos la resistencia a fallos.

La implementación requiere cambios moderados en la arquitectura actual pero proporciona beneficios sustanciales a largo plazo.</content>
<parameter name="filePath">d:\dev\caminando-onlinev8\Sandbox\Experiments\proceso_pestanas_nuevas.md