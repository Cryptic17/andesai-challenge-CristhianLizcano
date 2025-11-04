import pandas as pd
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional  # <--- MODIFICADO (Añadido Optional)
import numpy as np

# --- Modelos de Datos (Pydantic) ---

class ItemCreate(BaseModel):
    """ Modelo para crear un item (requiere todos los campos) """
    sku: str
    name: str
    stock: int
    unit_cost: float

# <--- AÑADIDO ---
class ItemUpdate(BaseModel):
    """ 
    Modelo para actualizar un item. 
    Todos los campos son opcionales (para PUT/PATCH).
    """
    name: Optional[str] = None
    stock: Optional[int] = None
    unit_cost: Optional[float] = None
# --- FIN DE LO AÑADIDO ---

class OrderItem(BaseModel):
    """ Modelo para un item dentro de un pedido """
    sku: str
    qty: int

class OrderCreate(BaseModel):
    """ Modelo para crear un nuevo pedido """
    order_id: str
    items: List[OrderItem] # Una lista de los items del pedido


# --- Configuración de la API ---
db = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... (Esta función queda exactamente igual) ...
    print("Iniciando la API y cargando datos...")
    
    db["items"] = pd.read_csv("./data/items.csv")
    db["orders_seed"] = pd.read_csv("./data/orders_seed.csv")
    
    db["items"] = db["items"].set_index("sku")
    
    print("--- Inventario Inicial (con SKU como índice) ---")
    print(db["items"])
    print("---------------------------------------")
    
    yield
    
    print("Apagando la API...")

# Crea la aplicación de FastAPI
app = FastAPI(
    title="API de Operaciones de Restaurante",
    description="API para gestionar inventario y pedidos de una cocina.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Endpoints (Rutas) de la API ---

@app.get("/")
def read_root():
    return {"message": "API de Restaurante funcionando"}

# --- Endpoints de Items (CRUD) ---

@app.get("/items")
def get_all_items():
    items_list = db["items"].reset_index().to_dict("records")
    return {"items": items_list}

@app.post("/items")
def create_new_item(item: ItemCreate):
    # ... (Esta función queda exactamente igual) ...
    print("Datos recibidos:", item)
    new_item_dict = item.model_dump()
    new_sku = new_item_dict.pop('sku')
    
    if new_sku in db["items"].index:
        raise HTTPException(status_code=400, detail=f"Item con SKU '{new_sku}' ya existe.")
    
    new_item_df = pd.DataFrame([new_item_dict], index=[new_sku])
    db["items"] = pd.concat([db["items"], new_item_df])
    
    print("--- Inventario Actualizado (Item Creado) ---")
    print(db["items"])
    
    return {"message": "Item creado exitosamente", "item": {"sku": new_sku, **new_item_dict}}

# <--- AÑADIDO: Endpoint para Actualizar (PUT) ---
@app.put("/items/{sku}")
def update_item(sku: str, item_update: ItemUpdate):
    """
    Actualiza los detalles de un item existente (nombre, stock, costo).
    """
    # 1. Verificar si el producto existe
    if sku not in db["items"].index:
        raise HTTPException(status_code=404, 
                            detail=f"Item con SKU '{sku}' no encontrado.")
    
    print(f"Actualizando SKU: {sku}. Datos recibidos: {item_update}")
    
    # 2. Actualizar los campos que no sean 'None'
    update_data = item_update.model_dump(exclude_unset=True) # Solo campos enviados
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar.")
        
    for key, value in update_data.items():
        db["items"].loc[sku, key] = value
    
    print("--- Inventario Actualizado (Item Modificado) ---")
    print(db["items"])
    
    # 3. Devolver el item actualizado
    updated_item_data = db["items"].loc[sku].to_dict()
    return {"message": "Item actualizado exitosamente", "sku": sku, "item": updated_item_data}
# --- FIN DE LO AÑADIDO ---


# <--- AÑADIDO: Endpoint para Eliminar (DELETE) ---
@app.delete("/items/{sku}")
def delete_item(sku: str):
    """
    Elimina un item del inventario usando su SKU.
    """
    # 1. Verificar si el producto existe
    if sku not in db["items"].index:
        raise HTTPException(status_code=404, 
                            detail=f"Item con SKU '{sku}' no encontrado.")
    
    print(f"Eliminando SKU: {sku}")
    
    # 2. Eliminar la fila (axis=0) usando .drop()
    db["items"] = db["items"].drop(sku, axis=0)
    
    print("--- Inventario Actualizado (Item Eliminado) ---")
    print(db["items"])
    
    return {"message": "Item eliminado exitosamente", "sku": sku}
# --- FIN DE LO AÑADIDO ---


# --- Endpoint de Pedidos ---

@app.post("/orders")
def create_new_order(order: OrderCreate):
    # ... (Esta función queda exactamente igual) ...
    print(f"Procesando pedido: {order.order_id}")
    items_a_actualizar = []
    
    for item_pedido in order.items:
        sku = item_pedido.sku
        qty_pedida = item_pedido.qty
        
        if sku not in db["items"].index:
            raise HTTPException(status_code=404, detail=f"Item con SKU '{sku}' no encontrado.")
        
        stock_actual = db["items"].loc[sku, "stock"]
        
        if stock_actual < qty_pedida:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para SKU '{sku}'. Pedido: {qty_pedida}, Stock: {stock_actual}")
        
        nuevo_stock = stock_actual - qty_pedida
        items_a_actualizar.append({"sku": sku, "nuevo_stock": nuevo_stock})

    print("Stock verificado. Aplicando descuentos...")
    for item_a_restar in items_a_actualizar:
        db["items"].loc[item_a_restar["sku"], "stock"] = item_a_restar["nuevo_stock"]

    print("--- Inventario Actualizado (Post-Pedido) ---")
    print(db["items"])
    
    return {"message": "Pedido procesado exitosamente", "order_id": order.order_id}

# --- Endpoint de KPI ---

@app.get("/kpi/stock-coverage")
def get_stock_coverage(days: int):
    # ... (Esta función queda exactamente igual) ...
    if days <= 0:
        raise HTTPException(status_code=400, detail="El parámetro 'days' debe ser un entero positivo.")

    total_sales_seed = db["orders_seed"].groupby("sku")["qty"].sum()
    avg_daily_demand = total_sales_seed / days
    current_stock = db["items"]["stock"]
    
    stock_coverage = current_stock.div(avg_daily_demand)
    stock_coverage = stock_coverage.replace([np.inf, -np.inf], None).fillna(0)
    
    print("--- KPI Calculado (Cobertura de Stock en días) ---")
    print(stock_coverage)
    
    coverage_dict = stock_coverage.to_dict()
    
    return {"stock_coverage_days": coverage_dict}