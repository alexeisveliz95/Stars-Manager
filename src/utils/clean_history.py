import os
import glob

# Configuración
HISTORY_DIR = "data/history_images"
KEEP_N = 30

def purge():
    if not os.path.exists(HISTORY_DIR):
        print("📁 La carpeta de historial no existe. Nada que limpiar.")
        return
        
    # Buscamos .jpg y .png
    files = glob.glob(os.path.join(HISTORY_DIR, "*.jpg")) + glob.glob(os.path.join(HISTORY_DIR, "*.png"))
    # Ordenar por fecha de modificación
    files.sort(key=os.path.getmtime)
    
    if len(files) > KEEP_N:
        to_delete = files[:-KEEP_N]
        print(f"🧹 Se encontraron {len(files)} imágenes. Eliminando las {len(to_delete)} más antiguas...")
        for f in to_delete:
            os.remove(f)
            print(f"🗑️ Borrado: {os.path.basename(f)}")
    else:
        print(f"✅ Historial bajo control ({len(files)} imágenes). No hace falta borrar.")

if __name__ == "__main__":
    purge()