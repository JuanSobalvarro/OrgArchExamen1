from .model import Model


class Component(Model):
    def __init__(self, sku: str, name: str, supplier: str, category: str, current_stock: int):
        super().__init__(
            model_name="Componente",
            sku=sku,
            name=name,
            supplier=supplier,
            category=category,
            current_stock=current_stock
        )
        self.set_fields_verbose({
            "sku": "ID de parte",
            "name": "Nombre",
            "supplier": "Proveedor",
            "category": "Categoría",
            "current_stock": "Stock Actual"
        })

    @property
    def sku(self) -> str:
        return self.fields['sku']
    
    @property
    def name(self) -> str:
        return self.fields['name']
    
    @property
    def supplier(self) -> str:
        return self.fields['supplier']
    
    @property
    def category(self) -> str:
        return self.fields['category']
    
    @property
    def current_stock(self) -> int:
        return self.fields['current_stock']
    