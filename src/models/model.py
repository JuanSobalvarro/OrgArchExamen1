"""
Este archivo definira el modelo utilizado en la aplicacion. Este modelo sera
la base de todos los datos serializados y guardados en formato JSON.
"""
import json


class Model:
    def __init__(self, model_name: str, *args, **kwargs):
        self.model_name = model_name
        self.fields = kwargs
        self.fields_verbose = None
        self.json_data = {}
    
    def to_json(self):
        self.json_data = {key: value for key, value in self.fields.items()}
        return self.json_data
    
    def set_field_verbose(self, field, verbose):
        if self.fields_verbose is None:
            self.fields_verbose = {}
        self.fields_verbose[field] = verbose

    def set_fields_verbose(self, fields_verbose):
        # sanitize that each key exists in fields
        if self.fields_verbose is None:
            self.fields_verbose = {}
        for key, value in fields_verbose.items():

            if key not in self.fields:
                raise KeyError(f"Field '{key}' does not exist in model fields.")
            
            self.fields_verbose[key] = value

    @classmethod
    def from_json(cls, model_name: str, json_data: dict):
        instance = cls(model_name=model_name, **json_data)
        return instance