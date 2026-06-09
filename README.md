# 🕊️ León XIV en Canarias 2026 — Mapa de Impacto en la Movilidad

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![GeoPandas](https://img.shields.io/badge/GeoPandas-1.1-green?style=flat-square)
![Folium](https://img.shields.io/badge/Folium-0.20-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

Proyecto de **Data Engineering geoespacial** para visualizar el impacto logístico de la visita apostólica a Gran Canaria (11–12 junio 2026). Responde a la pregunta ciudadana: **¿cómo me afecta este evento a mi movilidad diaria?**

👉 **[Ver mapa interactivo](https://henry94bt.github.io/papa-gc-2026/)**  
👉 **[Ver dashboard informativo](https://henry94bt.github.io/papa-gc-2026/dashboard.html)**

---

## 📸 Preview

> *Mapa interactivo con marcadores por evento, cortes de tráfico y paradas de guagua afectadas.*

---

## 🎯 Objetivo

Construir un MVP de visualización geoespacial que centralice y procese datos logísticos dispersos (PDFs oficiales, notas del Cabildo, agenda diocesana) y los convierta en un mapa web interactivo accesible desde cualquier móvil.

---

## 🗂️ Estructura del proyecto

```
papa-gc-2026/
│
├── tarea1_agenda_papa.py      # ETL: geocodificación y generación de GeoJSON
├── tarea2_mapa_folium.py      # Visualización: mapa interactivo con Folium
│
├── agenda_papa.geojson        # Eventos papales (Points)
├── cortes_trafico.geojson     # Cortes de tráfico (LineStrings)
├── guaguas_impacto.geojson    # Lanzaderas de guaguas (Points)
├── aparcamientos.geojson      # Aparcamientos habilitados (Points)
│
├── index.html                 # Mapa interactivo (salida final)
├── dashboard.html             # Dashboard con cronología, cifras e historia
└── README.md
```

---

## ⚙️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Geocodificación | `geopy` + Nominatim (OpenStreetMap) |
| Procesamiento geoespacial | `geopandas`, `shapely` |
| Manipulación de datos | `pandas` |
| Visualización | `folium` (wrapper de Leaflet.js) |
| Frontend | HTML/CSS/JS estático |
| Hosting | GitHub Pages |

---

## 🔄 Pipeline de datos

```
Datos fuente          Fase 1 · Extract       Fase 2 · Transform      Fase 3 · Load
─────────────         ───────────────        ──────────────────       ─────────────
Agenda oficial   →    Diccionarios Python →  Geocodificación OSM  →  agenda_papa.geojson
Cortes tráfico   →    Coords manuales    →  GeoDataFrame          →  cortes_trafico.geojson
Impacto guaguas  →    Diccionarios Python →  Geocodificación OSM  →  guaguas_impacto.geojson
                                                                            ↓
                                                                      index.html (Folium)
```

---

## 🚀 Cómo ejecutar

**1. Clona el repositorio**
```bash
git clone https://github.com/henry94bt/papa-gc-2026.git
cd papa-gc-2026
```

**2. Instala las dependencias**
```bash
pip install pandas geopandas geopy shapely folium
```

**3. Genera los GeoJSON (Fase 1)**
```bash
python tarea1_agenda_papa.py
```
Esto geocodifica los eventos y genera los tres archivos `.geojson` en la carpeta.

**4. Genera el mapa interactivo (Fase 2)**
```bash
python tarea2_mapa_folium.py
```
Abre `index.html` en tu navegador para ver el resultado.

---

## 🗺️ Funcionalidades del mapa

- **Marcadores por evento** con código de color según nivel de impacto (Alto / Medio / Bajo)
- **Popups informativos** con horario, ubicación y consejo de movilidad personalizado
- **Líneas de cortes de tráfico** sobre las carreteras afectadas
- **Lanzaderas de guaguas** a Siete Palmas (Auditorio, Santa Catalina, San Telmo)
- **Aparcamientos habilitados** con plazas disponibles (7 Palmas, Hipercor, Infecar)
- **Control de capas** para activar/desactivar cada tipo de información
- **Diseño mobile-first** optimizado para compartir por WhatsApp

---

## 📊 Dashboard informativo

El archivo `dashboard.html` incluye:
- Cronología interactiva clickable de los dos días
- Estadísticas del evento (aforo, seguridad, transporte)
- Historia comparativa de visitas papales a España con gráfico de asistencia

---

## ⚠️ Limitaciones del MVP

- Las coordenadas de los cortes de tráfico son aproximaciones hasta que el Cabildo publique la resolución oficial
- Los datos de aforo y seguridad son estimaciones basadas en fuentes públicas

---

## 🔜 Próximas mejoras

- [x] Integrar cortes oficiales del Cabildo (GC-1, GC-3, Siete Palmas)
- [x] Añadir capa de aparcamientos habilitados
- [x] Cobertura de la agenda de Tenerife (día 12)
- [ ] Añadir time-slider para filtrar el mapa por hora del día
- [ ] Corregir geocodificación del aeropuerto con coordenadas fijas
- [ ] Publicar en GitHub Pages con dominio personalizado

---

## 📄 Licencia

MIT — libre para usar, modificar y distribuir con atribución.

---

*Proyecto desarrollado como parte de un portfolio de Data Engineering y visualización geoespacial.*
