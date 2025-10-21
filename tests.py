
def test_model_creation():
    from src.models.component import Component

    component = Component(
        sku="ABC123",
        name="Resistor 10k Ohm",
        supplier="ElectroParts Inc.",
        category="Resistors",
        current_stock=1500
    )

    assert component.sku == "ABC123"
    assert component.name == "Resistor 10k Ohm"
    assert component.supplier == "ElectroParts Inc."
    assert component.category == "Resistors"
    assert component.current_stock == 1500

    print("Model creation test passed.")

def test_model_serialization():
    from src.models.component import Component

    component = Component(

        sku="XYZ789",
        name="Capacitor 100uF",
        supplier="CapacitorWorld",
        category="Capacitors",
        current_stock=500
    )

    json_data = component.to_json()
    reconstructed_component = Component.from_json(json_data)

    assert reconstructed_component.sku == component.sku
    assert reconstructed_component.name == component.name
    assert reconstructed_component.supplier == component.supplier
    assert reconstructed_component.category == component.category
    assert reconstructed_component.current_stock == component.current_stock

    print("Model serialization test passed.")

def test_file_service_creation():
    from src.services.file_service import FileService
    import os

    file_service = FileService("./test_data.json")
    
    assert os.path.exists("./test_data.json")

    print("File service creation test passed.")

def test_file_service_add_and_get():
    from src.services.file_service import FileService
    from src.models.component import Component
    import os

    file_service = FileService("./test_data.json")

    models = []
    for i in range(5):
        component = Component(
            sku=f"TEST{i}",
            name=f"Test Component {i}",
            supplier="TestSupplier",
            category="TestCategory",
            current_stock=100 + i
        )
        models.append(component)
        file_service.add_model(component)

    retrieved_models = file_service.sequential_read()

    for original, retrieved in zip(models, retrieved_models):
        assert original.sku == retrieved.sku
        assert original.name == retrieved.name
        assert original.supplier == retrieved.supplier
        assert original.category == retrieved.category
        assert original.current_stock == retrieved.current_stock
    
    print("File service add and get test passed.")


def main():
    test_model_creation()
    test_model_serialization()
    test_file_service_creation()
    test_file_service_add_and_get()

if __name__ == "__main__":
    main()