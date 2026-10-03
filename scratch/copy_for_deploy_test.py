import os
import shutil

src_root = r"c:\Users\Gaston Silva\Apocuna"
dest_root = r"c:\Users\Gaston Silva\Apocuna_deploy_test"

# Folders and files to copy
items_to_copy = [
    "app.py",
    "config.py",
    "requirements.txt",
    "assets",
    "components",
    "data",
    "sections",
    "utils",
    ".streamlit"
]

if os.path.exists(dest_root):
    shutil.rmtree(dest_root)
os.makedirs(dest_root, exist_ok=True)

for item in items_to_copy:
    src = os.path.join(src_root, item)
    dest = os.path.join(dest_root, item)
    if os.path.isdir(src):
        shutil.copytree(src, dest)
    elif os.path.isfile(src):
        shutil.copy2(src, dest)

# Asegurar que secrets.toml NO existe en la copia
secrets_path = os.path.join(dest_root, ".streamlit", "secrets.toml")
if os.path.exists(secrets_path):
    os.remove(secrets_path)
    print("Eliminado secrets.toml de la copia")
else:
    print("Confirmado: secrets.toml no existe en la copia")

# Confirmar archivos en la copia
print("Copia creada en:", dest_root)
print("Contenido de .streamlit en copia:", os.listdir(os.path.join(dest_root, ".streamlit")))
