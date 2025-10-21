from .model import Model

import datetime as dt

class Component(Model):
    def __init__(self, sku: str, name: str, supplier: str, category: str, current_stock: int, last_entry_date: dt.date | None = None):
        # doble conversion rara pero aguanta jaja
        if type(last_entry_date) is str:
            last_entry_date = dt.date.fromisoformat(last_entry_date)
        super().__init__(
            model_name="Componente",
            sku=sku,
            name=name,
            supplier=supplier,
            category=category,
            current_stock=current_stock,
            last_entry_date=last_entry_date.isoformat() if last_entry_date else None
        )
        self.set_fields_verbose({
            "sku": "ID de parte",
            "name": "Nombre",
            "supplier": "Proveedor",
            "category": "Categoría",
            "current_stock": "Stock Actual",
            "last_entry_date": "Última Fecha de Entrada"
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
    
    @property
    def last_entry_date(self) -> dt.date | None:
        # parse date from string if not None
        led = dt.date.fromisoformat(self.fields['last_entry_date']) if self.fields['last_entry_date'] else None
        return led
