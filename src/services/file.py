"""
Este archivo definira el servicio de manejo de archivos para lal lectura secuencial,
busqueda directa y acceso indexado de archivos. Esto manejando modelos serializados en JSON.
"""
import json

from src.models.component import Component


class FileService:
    def __init__(self, file_path):
        self.file_path = file_path
        # index principal, es automatico dado que cada linea es un modelo, por lo tanto el indice categorico guardara dadas ciertas categorias los indice de los modelos a estas
        self.category_index = {}

    def load_models(self, models: list[Component]):
        with open(self.file_path, 'w') as f:
            for model in models:
                json.dump(model.to_json(), f)
                f.write('\n')
                # Construir indice basado en categoria
                category = model.category
                if category not in self.category_index:
                    self.category_index[category] = []
                self.category_index[category].append(model)
        self.update_index()

    def update_index(self):
        """
        Actualiza el indice categorico que guarda una lista de indices(lineas) donde se ubican los modelos de la categoria correspondiente
        """
        self.category_index = {}
        with open(self.file_path, 'r') as f:
            for line_number, line in enumerate(f):
                data = json.loads(line)
                model = Component.from_json("Componente", data)
                category = model.category
                if category not in self.category_index:
                    self.category_index[category] = []
                self.category_index[category].append(line_number)

    def add_model(self, model: Component):
        with open(self.file_path, 'a') as f:
            json.dump(model.to_json(), f)
            f.write('\n')
        self.update_index()

    def sequential_read(self) -> list[Component]:
        """
        Lee todos los modelos del archivo de manera secuencial y los devuelve en forma
        de lista.
        """
        models = []
        with open(self.file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                models.append(Component.from_json("Componente", data))
        return models
    
    def find_by_sku(self, sku: str) -> Component | None:
        """
        Busca un modelo por su SKU en el archivo y lo devuelve si lo encuentra.
        """
        with open(self.file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                if data.get('sku') == sku:
                    return Component.from_json("Componente", data)
        return None

    def get_model_by_index(self, index: int) -> Component | None:
        """
        Acceso directo por indice, accede al archivo y retorno el modelo dado el indice. Los offsets deben
        estar definidos por el index.
        """
        with open(self.file_path, 'r') as f:
            for current_index, line in enumerate(f):
                if current_index == index:
                    data = json.loads(line)
                    return Component.from_json("Componente", data)
        return None


    def category_indices(self, category: str) -> list[int]:
        """
        Indice basado en categoria del componente
        """
        return self.category_index.get(category, [])
    
    def get_models_by_category(self, category: str) -> list[Component]:
        """
        Devuelve una lista de modelos que pertenecen a la categoria dada.
        """
        indices = self.category_indices(category)
        models = []
        with open(self.file_path, 'r') as f:
            for current_index, line in enumerate(f):
                if current_index in indices:
                    data = json.loads(line)
                    models.append(Component.from_json("Componente", data))
        return models

