from .model import Model


class Component(Model):
    def __init__(self, sku: str, name: str, supplier: str, category: str, current_stock: int):
        super().__init__(
            sku=sku,
            name=name,
            supplier=supplier,
            category=category,
            current_stock=current_stock
        )
        