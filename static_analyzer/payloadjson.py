import json

file_path = 'Test.sol'
# ---------------------------------------------

def create_json_payload(path_to_sol_file):
    """
    Membaca file .sol, menempatkannya dalam struktur dictionary,
    dan mengubahnya menjadi string JSON yang valid dengan escaping otomatis.
    """
    try:
        with open(path_to_sol_file, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Buat dictionary Python
        payload_dict = {
            "source_code": source_code
        }

        # Gunakan library json untuk mengubah dictionary menjadi string JSON.
        # Library ini akan secara OTOMATIS menangani semua escaping yang diperlukan.
        json_string = json.dumps(payload_dict, indent=2)

        print("--- Payload JSON Siap untuk Disalin ke Thunder Client ---")
        print(json_string)
        print("\n--- Cukup salin semua yang ada di atas ---")

    except FileNotFoundError:
        print(f"Error: File tidak ditemukan di '{path_to_sol_file}'")
    except Exception as e:
        print(f"Terjadi error: {e}")

# Jalankan fungsi
create_json_payload(file_path)
