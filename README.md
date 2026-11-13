# Ciudad Limpia AI 🌱

Prototipo web en Python y Streamlit para reportar acumulaciones de basura con fotografía, ubicación, categoría y tamaño estimado; visualizar reportes en un mapa y exportar un CSV para gestión municipal.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud

1. Sube este repositorio a GitHub.
2. Entra a [share.streamlit.io](https://share.streamlit.io/) y conecta GitHub.
3. Selecciona el repositorio y `app.py` como archivo principal.
4. Pulsa **Deploy**.

## Alcance del MVP

- Registro de una fotografía, categoría, descripción, referencia del barrio y coordenadas.
- Mapa y tabla de reportes comunitarios.
- Panel municipal sencillo, cambio de estado y exportación CSV.
- Datos y fotos guardados localmente en `data/`.

**Importante:** la app no ejecuta todavía un modelo de visión artificial. La identificación se basa en los datos confirmados por quien reporta. El almacenamiento local puede ser efímero en servicios de hosting; para producción se recomienda base de datos y almacenamiento de imágenes persistentes, autenticación, moderación y política de privacidad. No subir fotografías con rostros, placas u otros datos personales.
