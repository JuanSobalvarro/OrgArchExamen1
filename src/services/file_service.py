"""
Este archivo definira el servicio de manejo de archivos para lal lectura secuencial,
busqueda directa y acceso indexado de archivos. Esto manejando modelos serializados en JSON.
"""
import json
import datetime as dt

from src.models.component import Component


class FileService:
    def __init__(self, file_path):
        self.file_path = self.sanitize_file(file_path)
        # index principal, es automatico dado que cada linea es un modelo, por lo tanto el indice categorico guardara dadas ciertas categorias los indice de los modelos a estas
        self.category_index = {}
    
    def sanitize_file(self, path: str):
        """
        Crea el archivo si no existe y retorna la ruta saneada.
        """
        try:
            with open(path, 'r+') as f:
                pass
        except FileNotFoundError:
            with open(path, 'w+') as f:
                pass
        return path


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
                model = Component.from_json(data)
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
                models.append(Component.from_json(data))
        return models
    
    def find_by_sku(self, sku: str) -> Component | None:
        """
        Busca un modelo por su SKU en el archivo y lo devuelve si lo encuentra.
        """
        with open(self.file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                if data.get('sku') == sku:
                    return Component.from_json(data)
        return None

    def get_model_by_index(self, index: int) -> Component | None:
        """
        Acceso indexado, accede al archivo y retorno el modelo dado el indice. Los offsets deben
        estar definidos por el index.
        """
        with open(self.file_path, 'r') as f:
            for current_index, line in enumerate(f):
                if current_index == index:
                    data = json.loads(line)
                    return Component.from_json(data)
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
                    models.append(Component.from_json(data))
        return models

    def get_old_and_low_models(self, start_date: dt.date, end_date: dt.date) -> list[Component]:
        """
        Esta funcion devuelve todos los modelos que tienen un stock menor a 10 u
        y last entry dentro del rango especificado
        """
        old_models = []
        with open(self.file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                model = Component.from_json(data)
                if model.current_stock and model.last_entry_date is not None:
                    if model.current_stock < 10 and start_date <= model.last_entry_date <= end_date:
                        old_models.append(model)
        return old_models

    def clear_file(self):
        """
        Limpia el contenido del archivo.
        """
        with open(self.file_path, 'w') as f:
            pass
        self.category_index = {}
    
    def delete_file(self):
        """
        Elimina el archivo fisico.
        """
        import os
        os.remove(self.file_path)
        self.category_index = {}
