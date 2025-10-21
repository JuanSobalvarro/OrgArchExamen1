"""
Ejecucion princial del programa aca se puede inicializar la CLI para realizar operaciones es practicamente el frontend
"""
from src.services.file_service import FileService
from src.models.component import Component
import datetime as dt
import os

def _call_service(fs, candidates, *args, **kwargs):
	"""
	Intentar llamar al primer método disponible en `fs` cuyo nombre esté en candidates.
	"""
	for name in candidates:
		if hasattr(fs, name) and callable(getattr(fs, name)):
			return getattr(fs, name)(*args, **kwargs)
	raise NotImplementedError(f"Ninguno de los metodos {candidates} está implementado en FileService")

def _format_item(item):
	"""
	Convierte un componente o dict en un dict normalizado para impresión tabular.
	"""
	if item is None:
		return {"sku": "-", "name": "<None>", "category": "-", "stock": "-", "date": "-"}

	def get(v, *keys, default=None):
		for k in keys:
			if isinstance(v, dict) and k in v:
				return v[k]
			if hasattr(v, k):
				return getattr(v, k)
		return default

	return {
		"sku": get(item, "sku", "SKU", default="-"),
		"name": get(item, "name", "nombre", default="-"),
		"category": get(item, "category", "categoria", default="-"),
		"stock": get(item, "current_stock", "stock", default="-"),
		"date": str(get(item, "last_entry_date", "fecha_alta", "date", default="-")),
	}


def _print_list(items):
	"""
	Imprime una lista de componentes con formato tabular y colores ANSI.
	"""
	if items is None:
		print("\033[33mNo hay resultados.\033[0m")
		return

	if not isinstance(items, (list, tuple)):
		items = [items]

	if len(items) == 0:
		print("\033[33mNo se encontraron registros.\033[0m")
		return

	# Normalizar
	rows = [_format_item(i) for i in items]
	# Calcular anchos de columna
	headers = ["SKU", "Nombre", "Categoría", "Stock", "Fecha"]
	widths = {h: len(h) for h in headers}
	for r in rows:
		widths["SKU"] = max(widths["SKU"], len(str(r["sku"])))
		widths["Nombre"] = max(widths["Nombre"], len(str(r["name"])))
		widths["Categoría"] = max(widths["Categoría"], len(str(r["category"])))
		widths["Stock"] = max(widths["Stock"], len(str(r["stock"])))
		widths["Fecha"] = max(widths["Fecha"], len(str(r["date"])))

	# Línea superior
	line = "+" + "+".join("-" * (widths[h] + 2) for h in headers) + "+"
	print("\033[36m" + line + "\033[0m")

	# Encabezado
	print(
		"\033[1m|\033[0m "
		+ " | ".join(
			f"\033[1;37m{h:<{widths[h]}}\033[0m" for h in headers
		)
		+ " \033[1m|\033[0m"
	)

	print("\033[36m" + line + "\033[0m")

	# Filas
	for r in rows:
		color = ""
		reset = "\033[0m"
		# Resaltar bajo stock
		try:
			if isinstance(r["stock"], int) and r["stock"] < 10:
				color = "\033[31m"
		except Exception:
			pass
		print(
			f"| {r['sku']:<{widths['SKU']}} | "
			f"{r['name']:<{widths['Nombre']}} | "
			f"{r['category']:<{widths['Categoría']}} | "
			f"{color}{r['stock']:<{widths['Stock']}}{reset} | "
			f"{r['date']:<{widths['Fecha']}} |"
		)

	print("\033[36m" + line + "\033[0m")
	print(f"\033[1;32mTotal de registros: {len(rows)}\033[0m\n")


def main():
	# Preparar ruta por defecto y crear carpeta si hace falta
	file_path = "./data/data.json"
	os.makedirs(os.path.dirname(file_path), exist_ok=True)
	fs = FileService(file_path)

	menu = """\nSeleccione una opción:
1) Leer secuencial: listar todos los registros
2) Buscar por SKU
3) Acceso indexado por categoría
4) Ver stock bajo (umbral)
5) Ver artículos antiguos y de bajo stock (días)
6) Agregar componente
7) Salir
Elija una opción (1-7): """

	while True:
		opt = input(menu).strip()
		if opt == "1":
			# lectura secuencial
			try:
				res = fs.sequential_read()
			except Exception as e:
				print("Error al leer secuencial:", e)
				continue
			_print_list(res)

		elif opt == "2":
			sku = input("Ingrese SKU a buscar: ").strip()
			if not sku:
				print("SKU vacío.")
				continue
			try:
				res = fs.find_by_sku(sku)
			except Exception as e:
				print("Error en búsqueda por SKU:", e)
				continue
			_print_list(res)

		elif opt == "3":
			# actualizar índice y listar categorías
			fs.update_index()
			cat_index = fs.category_index or {}
			if not cat_index:
				print("No hay categorías indexadas.")
				continue
			print("Categorías disponibles:")
			for i, (cat, indices) in enumerate(cat_index.items(), start=1):
				print(f"{i}) {cat} (registros: {len(indices)})")
			choice = input("Ingrese número de categoría para listar modelos, o 'q' para volver: ").strip()
			if choice.lower() == "q":
				continue
			try:
				choice_i = int(choice) - 1
				if choice_i < 0 or choice_i >= len(cat_index):
					print("Opción inválida.")
					continue
			except ValueError:
				print("Valor inválido.")
				continue
			selected_cat = list(cat_index.keys())[choice_i]
			# listar modelos de la categoria
			models = fs.get_models_by_category(selected_cat)
			print(f"Modelos en categoría '{selected_cat}':")
			# mostramos con sus índices en archivo
			indices = fs.category_indices(selected_cat)
			for idx, m in zip(indices, models):
				print(f"[line {idx}] {_format_item(m)}")
			# permitir ver uno por índice
			see = input("Ver modelo por índice de línea? Ingrese índice (o Enter para volver): ").strip()
			if see == "":
				continue
			try:
				line_idx = int(see)
			except ValueError:
				print("Índice inválido.")
				continue
			model = fs.get_model_by_index(line_idx)
			if model is None:
				print("No se encontró modelo en ese índice.")
			else:
				print(_format_item(model))

		elif opt == "4":
			umbral_s = input("Ingrese umbral de stock (número, por defecto 10): ").strip()
			try:
				umbral = int(umbral_s) if umbral_s else 10
			except ValueError:
				print("Umbral inválido.")
				continue
			try:
				all_models = fs.sequential_read()
			except Exception as e:
				print("Error leyendo modelos:", e)
				continue
			low = [m for m in all_models if (m.current_stock is not None and m.current_stock < umbral)]
			if not low:
				print("No hay artículos con stock por debajo del umbral.")
			else:
				_print_list(low)

		elif opt == "5":
			dias_s = input("Ingrese cantidad de días para considerar 'antiguo' (por defecto 365): ").strip()
			try:
				dias = int(dias_s) if dias_s else 365
			except ValueError:
				print("Valor inválido.")
				continue
			# queremos obtener items antiguos y de bajo stock según la función disponible en FileService
			end_date = dt.date.today() - dt.timedelta(days=dias)
			start_date = dt.date(1900, 1, 1)
			try:
				res = fs.get_old_and_low_models(start_date=start_date, end_date=end_date)
			except Exception as e:
				print("Error consultando artículos antiguos y de bajo stock:", e)
				continue
			_print_list(res)

		elif opt == "6":
			# Agregar componente
			print("Agregar nuevo componente. SKU es obligatorio.")
			sku = input("SKU: ").strip()
			if not sku:
				print("SKU obligatorio. Operación cancelada.")
				continue
			name = input("Nombre: ").strip() or "Sin nombre"
			supplier = input("Proveedor: ").strip() or "Desconocido"
			category = input("Categoría: ").strip() or "General"
			cs = input("Stock actual (número, por defecto 0): ").strip()
			try:
				current_stock = int(cs) if cs else 0
			except ValueError:
				print("Stock inválido. Operación cancelada.")
				continue
			led_s = input("Fecha última entrada (YYYY-MM-DD) o Enter para hoy: ").strip()
			if led_s:
				try:
					last_entry = dt.date.fromisoformat(led_s)
				except ValueError:
					print("Fecha inválida. Operación cancelada.")
					continue
			else:
				last_entry = dt.date.today()
			try:
				new_comp = Component(
					sku=sku,
					name=name,
					supplier=supplier,
					category=category,
					current_stock=current_stock,
					last_entry_date=last_entry
				)
				fs.add_model(new_comp)
				print("Componente agregado correctamente.")
			except Exception as e:
				print("Error al agregar componente:", e)

		elif opt == "7":
			print("Saliendo.")
			break

		else:
			print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
	main()