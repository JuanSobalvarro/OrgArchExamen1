from src.services.file_service import FileService
from src.models.component import Component
import datetime as dt
import os

def test_model_creation():

    component = Component(
        sku="ABC123",
        name="Resistor 10k Ohm",
        supplier="ElectroParts Inc.",
        category="Resistors",
        current_stock=1500,
        last_entry_date=dt.date(2024, 6, 1)
    )

    assert component.sku == "ABC123"
    assert component.name == "Resistor 10k Ohm"
    assert component.supplier == "ElectroParts Inc."
    assert component.category == "Resistors"
    assert component.current_stock == 1500

    print("Model creation test passed.")

def test_model_serialization():

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

    file_service = FileService("./test_data.json")
    
    assert os.path.exists("./test_data.json")

    print("File service creation test passed.")

def test_file_service_add_and_get():

    file_service = FileService("./test_data.json")

    models = []
    for i in range(5):
        component = Component(
            sku=f"TEST{i}",
            name=f"Test Component {i}",
            supplier="TestSupplier",
            category=f"TestCategory{i%2}",
            current_stock=100 + i,
            last_entry_date=dt.date(2024, 6, i+1)
        )
        models.append(component)
        file_service.add_model(component)

    # test sequential read
    retrieved_models = file_service.sequential_read()

    for original, retrieved in zip(models, retrieved_models):
        assert original.sku == retrieved.sku
        assert original.name == retrieved.name
        assert original.supplier == retrieved.supplier
        assert original.category == retrieved.category
        assert original.current_stock == retrieved.current_stock

    # test direct access by sku
    for original in models:
        retrieved = file_service.find_by_sku(original.sku)
        assert retrieved is not None
        assert original.sku == retrieved.sku
        assert original.name == retrieved.name
        assert original.supplier == retrieved.supplier
        assert original.category == retrieved.category
        assert original.current_stock == retrieved.current_stock

    # find by index
    for index, original in enumerate(models):
        retrieved = file_service.get_model_by_index(index)
        assert retrieved is not None
        assert original.sku == retrieved.sku
        assert original.name == retrieved.name
        assert original.supplier == retrieved.supplier
        assert original.category == retrieved.category
        assert original.current_stock == retrieved.current_stock

    # test access by category
    category_0_models = file_service.get_models_by_category("TestCategory0")
    assert len(category_0_models) == 3  # Should match the number of TestCategory0 components
    for model in category_0_models:
        assert model.category == "TestCategory0"

    print("File service add and get test passed.")


def test_file_service_old_components():
    components = []

    for i in range(20):
        component = Component(
            sku=f"OLD{i}",
            name=f"Old Component {i}",
            supplier="OldSupplier",
            category="OldCategory",
            current_stock=5,
            last_entry_date=dt.date(2022, i%12 + 1, (i*2)%28 + 1)  # Old date
        )
        components.append(component)

    file_service = FileService("./test_data.json")
    for component in components:
        file_service.add_model(component)

    old_components = file_service.get_old_and_low_models(start_date=dt.date(2022, 1, 1), end_date=dt.date(2023, 12, 31))

    assert len(old_components) == 20  # All components should be old and low stock
    for component in old_components:
        assert component.current_stock < 10
        assert component.last_entry_date is not None
        assert dt.date(2022, 1, 1) <= component.last_entry_date <= dt.date(2023, 12, 31)

    print("File service old components test passed.")


def test_file_service_cleanup():

    file_service = FileService("./test_data.json")
    file_service.delete_file()

    assert not os.path.exists("./test_data.json")

    print("File service cleanup test passed.")


def main():
    test_model_creation()
    test_model_serialization()
    test_file_service_creation()
    test_file_service_add_and_get()
    test_file_service_cleanup()
    test_file_service_old_components()

if __name__ == "__main__":
    main()