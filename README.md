Mini-API de Operaciones de Restaurante (RETO A)

Este proyecto es una API REST funcional para gestionar el inventario y los pedidos de una cocina, esto es parte parte de la prueba de fase Técnica para ingresar a Andes AI.

La API permite crear productos, procesar pedidos (descontando stock automáticamente), verificar el inventario, actualizar y eliminar productos, y calcular un KPI de cobertura de stock. La API se ejecuta dentro de un contenedor de Docker.

--------------------------------------

Stack y Librerías Utilizadas

* Lenguaje: Python 3.11
* Framework API: FastAPI
* Validación de Datos: Pydantic
* Manejo de Datos en Memoria: Pandas
* Servidor ASGI: Uvicorn
* Contenerización: Docker

---------------------------------

Instrucciones para Ejecutar
Se puede ejecutar de 2 maneras el proyecto

Método 1: Con Docker
Este método utiliza la imagen de Docker pre-construida (.tar) para una reproducibilidad total y offline.

1. Cargar la imagen de Docker:
   docker load -i api-restaurante-imagen.tar

2. Ejecutar el contenedor:
   docker run -d -p 8000:8000 api-restaurante

3. La API estará disponible en http://127.0.0.1:8000

Método 2: Localmente (en este caso seria para Desarrollo y ejecuta la API directamente en la máquina usando un entorno virtual)

1. Clonar el repositorio:
   git clone https://github.com/Cryptic17/andesai-challenge-CristhianLizcano.git
   cd andesai-challenge-CristhianLizcano

2. Crear y activar el entorno virtual:
   python -m venv venv
   source venv/bin/activate  # En Mac/Linux
   .\venv\Scripts\activate   # En Windows

3. Instalar dependencias:
   pip install -r requirements.txt

4. Ejecutar la API:
   uvicorn main:app --reload

5. La API estará disponible en http://127.0.0.1:8000

---------------------------------

Ejemplos de Requests (Endpoints)

Se pueden probar todos los endpoints de forma interactiva en la documentación automática que genera FastAPI en: http://127.0.0.1:8000/docs, aqui dejo algunos ejemplos para crear un nuevo producto y procesar un pedido.

1. Obtener todos los productos:
   curl -X GET "http://127.0.0.1:8000/items"

2. Crear un nuevo producto:
   curl -X POST "http://127.0.0.1:8000/items" -H "Content-Type: application/json" -d '{"sku": "prod_007", "name": "aros_cebolla_x8", "stock": 150, "unit_cost": 6.50}'

3. Procesar un nuevo pedido:
   curl -X POST "http://127.0.0.1:8000/orders" -H "Content-Type: application/json" -d '{"order_id": "mi_pedido_curl_001", "items": [{"sku": "prod_001", "qty": 2}, {"sku": "prod_002", "qty": 1}]}'

4. Obtener KPI de Cobertura de Stock:
   curl -X GET "http://127.0.0.1:8000/kpi/stock-coverage?days=7"

5. Actualizar un producto:
   curl -X PUT "http://127.0.0.1:8000/items/prod_007" -H "Content-Type: application/json" -d '{"name": "Aros de Cebolla (NUEVO NOMBRE)", "stock": 200}'

6. Eliminar un producto:
   curl -X DELETE "http://127.0.0.1:8000/items/prod_007"

---------------------------------

Limitaciones y Posibles Mejoras

* Persistencia de Datos: La API actual usa Pandas en memoria. Esto significa que cualquier cambio (nuevo stock, pedidos) se pierde si el servidor se reinicia. La mejora más crítica sería conectar la API a una base de datos real (como PostgreSQL o MongoDB) para que los datos sean persistentes.
* Autenticación: La API está abierta. Se podría implementar un sistema de autenticación (ej. OAuth2) para proteger los endpoints, esto ya para un caso de uso en la vida real, pensando en la seguridad del restaurante.
* Frontend: Se podría desarrollar una interfaz de frontend (ej. con React o Vue) para consumir esta API y proveer una experiencia de usuario visual para los administradores del restaurante, y asi facilitar su uso y entendimiento.