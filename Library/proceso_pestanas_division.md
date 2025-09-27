# Proceso de División de Tipos de Producto en Pestañas del Browser

## Descripción General

Este documento describe el proceso de optimización para el procesamiento de tipos de producto en una categoría específica. El objetivo es dividir el trabajo en múltiples pestañas del browser para mejorar la eficiencia y reducir el tiempo total de procesamiento, evitando sobrecargar el sistema con demasiadas operaciones simultáneas.

## Lógica de División

Al cargar una categoría, el script analiza el total de tipos de producto disponibles en esa categoría y determina la estrategia de división basada en la cantidad total:

### Rango 1: Menos de 50 tipos de producto
- **División**: 5 pestañas
- **Cálculo**: Cada pestaña procesa aproximadamente `total_tipos / 5` tipos de producto
- **Ejemplo**: Si la categoría tiene 40 tipos de producto:
  - Pestaña 1: Tipos 1-8
  - Pestaña 2: Tipos 9-16
  - Pestaña 3: Tipos 17-24
  - Pestaña 4: Tipos 25-32
  - Pestaña 5: Tipos 33-40

### Rango 2: 50 a 299 tipos de producto
- **División**: 10 pestañas
- **Cálculo**: Cada pestaña procesa aproximadamente `total_tipos / 10` tipos de producto
- **Ejemplo**: Si la categoría tiene 400 tipos de producto:
  - Pestaña 1: Tipos 1-40
  - Pestaña 2: Tipos 41-80
  - Pestaña 3: Tipos 81-120
  - Pestaña 4: Tipos 121-160
  - Pestaña 5: Tipos 161-200
  - Pestaña 6: Tipos 201-240
  - Pestaña 7: Tipos 241-280
  - Pestaña 8: Tipos 281-320
  - Pestaña 9: Tipos 321-360
  - Pestaña 10: Tipos 361-400

### Rango 3: 300 o más tipos de producto
- **División**: 20 pestañas
- **Cálculo**: Cada pestaña procesa aproximadamente `total_tipos / 20` tipos de producto
- **Ejemplo**: Si la categoría tiene 1000 tipos de producto:
  - Pestaña 1: Tipos 1-50
  - Pestaña 2: Tipos 51-100
  - Pestaña 3: Tipos 101-150
  - ...continúa hasta...
  - Pestaña 20: Tipos 951-1000

## Implementación Técnica

### Pseudocódigo

```python
def determinar_estrategia(total_tipos):
    if total_tipos < 50:
        num_pestanas = 5
    elif total_tipos < 300:
        num_pestanas = 10
    else:
        num_pestanas = 20
    
    tipos_por_pestana = total_tipos // num_pestanas
    resto = total_tipos % num_pestanas
    
    return num_pestanas, tipos_por_pestana, resto

def dividir_tipos_en_pestanas(tipos, num_pestanas):
    divisiones = []
    inicio = 0
    
    for i in range(num_pestanas):
        fin = inicio + tipos_por_pestana
        if i < resto:
            fin += 1
        divisiones.append(tipos[inicio:fin])
        inicio = fin
    
    return divisiones
```

### Consideraciones

- **Distribución equitativa**: Se utiliza división entera con manejo de resto para asegurar que todas las pestañas tengan aproximadamente la misma carga de trabajo.
- **Paralelismo controlado**: Cada pestaña opera independientemente, permitiendo procesamiento paralelo sin interferencias.
- **Gestión de recursos**: El número limitado de pestañas (máximo 20) previene sobrecarga del sistema.
- **Escalabilidad**: La estrategia se adapta automáticamente al tamaño de la categoría.

## Beneficios

- **Eficiencia**: Reduce el tiempo total de procesamiento al paralelizar operaciones.
- **Estabilidad**: Evita bloqueos del browser al limitar el número de pestañas simultáneas.
- **Flexibilidad**: Se adapta automáticamente a diferentes tamaños de categorías.
- **Mantenibilidad**: Lógica clara y predecible para debugging y optimizaciones futuras.

## Registro de Cambios

- **Fecha de creación**: 26 de septiembre de 2025
- **Versión**: 1.0
- **Autor**: IA Asistente
- **Propósito**: Documentar la estrategia de división de tipos de producto en pestañas para optimización del procesamiento.

## Lineamientos para Incorporación al Script

Esta sección describe cómo integrar la lógica de división en pestañas al script `CHECKPOINT 04 FUNCIONAL (pestanas) - extract_products_to_products_collection copy 3.py`. Los cambios se centran en modificar la función `process_single_category` para implementar procesamiento paralelo por pestañas.

### 1. Importaciones Adicionales
Agregar al inicio del script:
```python
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
```

### 2. Función para Determinar Estrategia de Pestañas
Crear una nueva función antes de `process_single_category`:
```python
def determine_tab_strategy(total_product_types):
    """Determine number of tabs and types per tab based on total product types"""
    if total_product_types < 50:
        num_tabs = 5
    elif total_product_types < 300:
        num_tabs = 10
    else:
        num_tabs = 20
    
    types_per_tab = total_product_types // num_tabs
    remainder = total_product_types % num_tabs
    
    return num_tabs, types_per_tab, remainder

def divide_product_types_into_tabs(product_types, num_tabs, types_per_tab, remainder):
    """Divide product types list into tab groups"""
    divisions = []
    start_idx = 0
    
    for i in range(num_tabs):
        end_idx = start_idx + types_per_tab
        if i < remainder:
            end_idx += 1
        divisions.append(product_types[start_idx:end_idx])
        start_idx = end_idx
    
    return divisions
```

### 3. Modificación de `process_single_category`
Después de obtener `all_product_types`, agregar la lógica de división:

```python
# Determinar estrategia de pestañas
num_tabs, types_per_tab, remainder = determine_tab_strategy(len(all_product_types))
product_type_groups = divide_product_types_into_tabs(all_product_types, num_tabs, types_per_tab, remainder)

logging.warning(f"Dividing {len(all_product_types)} product types into {num_tabs} tabs")

# Crear pestañas adicionales
tab_handles = [driver.current_window_handle]  # Primera pestaña ya existe
for i in range(1, num_tabs):
    driver.execute_script("window.open('');")
    new_handles = driver.window_handles
    tab_handles.append(new_handles[-1])  # Última handle es la nueva pestaña

# Procesar cada grupo en una pestaña separada usando ThreadPoolExecutor
def process_tab_group(tab_idx, product_types_group, tab_handle):
    """Process a group of product types in a specific tab"""
    try:
        driver.switch_to.window(tab_handle)
        
        # Navegar a la categoría en esta pestaña
        driver.get(category_url)
        time.sleep(2)
        
        # Configurar filtros (igual que antes)
        # ...existing code...
        
        # Procesar los tipos de producto asignados a esta pestaña
        local_successful = []
        local_partial = []
        local_failed = []
        local_products_saved = 0
        
        for product_type in product_types_group:
            # Lógica de procesamiento individual (igual que antes)
            # ...existing code...
        
        return local_successful, local_partial, local_failed, local_products_saved
    
    except Exception as e:
        logging.error(f"Error in tab {tab_idx}: {e}")
        return [], [], [], 0

# Ejecutar procesamiento en paralelo
with ThreadPoolExecutor(max_workers=num_tabs) as executor:
    futures = []
    for tab_idx, (group, handle) in enumerate(zip(product_type_groups, tab_handles)):
        future = executor.submit(process_tab_group, tab_idx, group, handle)
        futures.append(future)
    
    # Recopilar resultados
    for future in as_completed(futures):
        successful, partial, failed, saved = future.result()
        local_successful_types.extend(successful)
        local_partial_types.extend(partial)
        local_failed_types.extend(failed)
        total_products_saved += saved

# Cerrar pestañas adicionales
for handle in tab_handles[1:]:
    try:
        driver.switch_to.window(handle)
        driver.close()
    except:
        pass

# Regresar a la pestaña principal
driver.switch_to.window(tab_handles[0])
```

### 4. Consideraciones de Implementación

- **Sincronización**: Usar locks para acceso a base de datos si es necesario:
  ```python
  db_lock = threading.Lock()
  # Dentro de funciones que acceden a DB: with db_lock:
  ```

- **Gestión de Memoria**: Monitorear uso de memoria con múltiples pestañas abiertas.

- **Timeouts**: Aumentar timeouts para operaciones en paralelo.

- **Logging**: Agregar identificadores de pestaña a logs para debugging.

- **Error Handling**: Implementar recuperación individual por pestaña.

### 5. Testing y Validación

- Probar con categorías pequeñas primero (<50 tipos).
- Verificar que todas las pestañas procesen correctamente.
- Monitorear rendimiento y ajustar `max_workers` si es necesario.
- Validar integridad de datos en la base de datos.

### 6. Beneficios Esperados

- **Reducción de tiempo**: Procesamiento paralelo acelera la extracción.
- **Mejor estabilidad**: Menos sobrecarga por pestaña individual.
- **Escalabilidad**: Se adapta automáticamente a diferentes tamaños de categoría.

### 7. Riesgos y Mitigaciones

- **Conflictos de navegación**: Usar `driver.switch_to.window()` correctamente.
- **Límite de recursos**: Monitorear CPU y memoria; reducir `num_tabs` si es necesario.
- **Detección anti-bot**: Implementar delays aleatorios por pestaña.

Esta implementación mantiene la estructura modular del script original mientras agrega paralelismo controlado para optimizar el procesamiento de grandes volúmenes de tipos de producto.