"""
tarea1_agenda_papa.py
=====================
Pipeline ETL – Fase 1 & 2: Estructuración de agenda + Geocodificación
Visita papal a Gran Canaria · 11–12 junio 2026

Salida: agenda_papa.geojson  (Points)
        cortes_trafico.geojson (LineStrings/Polygons placeholder)
        guaguas_impacto.geojson (Points)

Uso:
    pip install pandas geopandas geopy shapely
    python tarea1_agenda_papa.py
"""

import time
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATOS FUENTE  (editar cuando llegue info oficial del Cabildo/Diócesis)
# ─────────────────────────────────────────────────────────────────────────────

AGENDA_RAW = [
    {
        "id": "A01",
        "evento": "Llegada al Aeropuerto de Gran Canaria",
        "fecha": "2026-06-11",
        "hora_inicio": "10:00",
        "hora_fin": "11:00",
        "lugar_texto": "Aeropuerto de Gran Canaria, Las Palmas de Gran Canaria",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Evita la GC-1 dirección sur desde las 08:00. "
            "Usa la GC-21 o el tranvía hasta Las Palmas Centro."
        ),
        "icono_color": "red",
    },
    {
        "id": "A02",
        "evento": "Recepción oficial en el Cabildo de Gran Canaria",
        "fecha": "2026-06-11",
        "hora_inicio": "12:00",
        "hora_fin": "13:30",
        "lugar_texto": "Cabildo de Gran Canaria, Las Palmas de Gran Canaria",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "El centro histórico de Vegueta estará cortado. "
            "Aparca en Triana y accede a pie."
        ),
        "icono_color": "red",
    },
    {
        "id": "A03",
        "evento": "Visita a la Catedral de Santa Ana",
        "fecha": "2026-06-11",
        "hora_inicio": "13:30",
        "hora_fin": "15:00",
        "lugar_texto": "Catedral de Santa Ana, Vegueta, Las Palmas de Gran Canaria",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Zona peatonal total en Vegueta. "
            "Intercambiadores provisionales en Pérez Galdós."
        ),
        "icono_color": "red",
    },
    {
        "id": "A04",
        "evento": "Acto multitudinario – Estadio de Gran Canaria",
        "fecha": "2026-06-11",
        "hora_inicio": "18:00",
        "hora_fin": "21:00",
        "lugar_texto": "Estadio de Gran Canaria, Las Palmas de Gran Canaria",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Usa las líneas especiales de Guaguas desde los P+R de Vecindario, "
            "Jinamar y El Doctoral. Evita la GC-1 entre los km 8 y 15."
        ),
        "icono_color": "red",
    },
    {
        "id": "A05",
        "evento": "Misa masiva en Arguineguín",
        "fecha": "2026-06-12",
        "hora_inicio": "10:00",
        "hora_fin": "13:00",
        "lugar_texto": "Arguineguín, Mogán, Gran Canaria",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "GC-1 sur cortada desde Pasito Blanco. "
            "Acceso SOLO en guagua especial desde Maspalomas y San Bartolomé de Tirajana."
        ),
        "icono_color": "red",
    },
    {
        "id": "A06",
        "evento": "Despedida – Aeropuerto de Gran Canaria",
        "fecha": "2026-06-12",
        "hora_inicio": "16:00",
        "hora_fin": "17:30",
        "lugar_texto": "Aeropuerto de Gran Canaria, Las Palmas de Gran Canaria",
        "tipo_impacto": "Medio",
        "consejo_movilidad": (
            "Restricciones aéreas levantadas progresivamente. "
            "Espera tráfico de retorno intenso en GC-1 norte."
        ),
        "icono_color": "orange",
    },
]

CORTES_RAW = [
    {
        "id": "C01",
        "descripcion": "Cierre GC-1 – Nudo Tafira hasta Aeropuerto",
        "fecha": "2026-06-11",
        "hora_inicio": "08:00",
        "hora_fin": "13:00",
        "tipo_impacto": "Alto",
        "via": "GC-1",
        "tramo": "km 3 – km 10",
        # Coordenadas: [lon, lat] del trazado simplificado
        "coords_linea": [
            (-15.461, 27.960),  # Nudo Tafira
            (-15.438, 27.940),
            (-15.419, 27.927),  # Aeropuerto
        ],
    },
    {
        "id": "C02",
        "descripcion": "Cierre GC-1 sur – Pasito Blanco a Arguineguín",
        "fecha": "2026-06-12",
        "hora_inicio": "07:00",
        "hora_fin": "15:00",
        "tipo_impacto": "Alto",
        "via": "GC-1",
        "tramo": "km 68 – km 75",
        "coords_linea": [
            (-15.690, 27.740),  # Pasito Blanco
            (-15.717, 27.760),
            (-15.738, 27.780),  # Arguineguín
        ],
    },
    {
        "id": "C03",
        "descripcion": "Cierre Vegueta – Centro histórico",
        "fecha": "2026-06-11",
        "hora_inicio": "10:00",
        "hora_fin": "16:00",
        "tipo_impacto": "Alto",
        "via": "Vegueta",
        "tramo": "Calle Colón / Dr. Chil / Mendizábal",
        "coords_linea": [
            (-15.415, 28.098),
            (-15.417, 28.102),
            (-15.420, 28.100),
        ],
    },
]

GUAGUAS_RAW = [
    {
        "id": "G01",
        "tipo": "Parada inhabilitada",
        "descripcion": "Parada Vegueta / Santa Ana – fuera de servicio",
        "fecha": "2026-06-11",
        "hora_inicio": "10:00",
        "hora_fin": "16:00",
        "lugar_texto": "Parada Santa Ana, Vegueta, Las Palmas de Gran Canaria",
        "alternativa": "Intercambiador provisional en Pérez Galdós",
    },
    {
        "id": "G02",
        "tipo": "Intercambiador provisional",
        "descripcion": "P+R Jinamar – acceso especial al Estadio",
        "fecha": "2026-06-11",
        "hora_inicio": "14:00",
        "hora_fin": "23:00",
        "lugar_texto": "Jinamar, Telde, Las Palmas de Gran Canaria",
        "alternativa": "Líneas L1-ESP y L2-ESP cada 10 min hasta Estadio",
    },
    {
        "id": "G03",
        "tipo": "Intercambiador provisional",
        "descripcion": "P+R Vecindario – acceso especial al Estadio",
        "fecha": "2026-06-11",
        "hora_inicio": "14:00",
        "hora_fin": "23:00",
        "lugar_texto": "Vecindario, Santa Lucía de Tirajana, Las Palmas de Gran Canaria",
        "alternativa": "Líneas L3-ESP y L4-ESP cada 15 min hasta Estadio",
    },
    {
        "id": "G04",
        "tipo": "Intercambiador provisional",
        "descripcion": "P+R Maspalomas – acceso especial a Arguineguín",
        "fecha": "2026-06-12",
        "hora_inicio": "06:00",
        "hora_fin": "16:00",
        "lugar_texto": "Maspalomas, San Bartolomé de Tirajana, Las Palmas de Gran Canaria",
        "alternativa": "Línea M1-ESP cada 20 min hasta zona de celebración",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# 2. GEOCODIFICADOR  (Nominatim / OpenStreetMap – sin API key)
# ─────────────────────────────────────────────────────────────────────────────

def geocodificar(geolocator: Nominatim, lugar: str, reintentos: int = 3) -> tuple[float, float] | None:
    """
    Geocodifica una dirección de texto usando Nominatim.
    Maneja timeouts y errores devolviendo None en caso de fallo.

    Args:
        geolocator: instancia de Nominatim ya configurada.
        lugar: cadena de texto con la dirección o nombre del lugar.
        reintentos: número máximo de intentos ante timeout.

    Returns:
        Tupla (latitud, longitud) o None si la geocodificación falla.
    """
    for intento in range(reintentos):
        try:
            # Nominatim requiere ≥1 s entre peticiones por ToS
            time.sleep(1.2)
            resultado = geolocator.geocode(
                lugar,
                country_codes="es",
                language="es",
                timeout=10,
            )
            if resultado:
                return resultado.latitude, resultado.longitude
            else:
                print(f"  [!] Sin resultado para: {lugar!r}")
                return None
        except GeocoderTimedOut:
            print(f"  [timeout] intento {intento + 1}/{reintentos} para {lugar!r}")
            time.sleep(2)
        except GeocoderServiceError as e:
            print(f"  [error] {e} para {lugar!r}")
            return None
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 3. CONSTRUCCIÓN DE DATAFRAMES Y GEODATAFRAMES
# ─────────────────────────────────────────────────────────────────────────────

def construir_agenda_gdf(raw: list[dict], geolocator: Nominatim) -> gpd.GeoDataFrame:
    """
    Geocodifica cada hito de la agenda y devuelve un GeoDataFrame de puntos.

    Esquema del GeoDataFrame resultante:
    ┌────────────┬──────────┬────────────────────┬───────┬──────────────────────────────┬──────────────┬───────┬──────────┬──────────────────┬──────────────────┐
    │ id         │ evento   │ lugar_texto        │ fecha │ hora_inicio / hora_fin       │ tipo_impacto │ lat   │ lon      │ consejo_movilidad │ icono_color      │
    │ str        │ str      │ str                │ str   │ str                          │ Alto/Med/Bajo│ float │ float    │ str               │ str              │
    └────────────┴──────────┴────────────────────┴───────┴──────────────────────────────┴──────────────┴───────┴──────────┴──────────────────┴──────────────────┘
    La columna 'geometry' es siempre Point(lon, lat).
    """
    registros = []
    for item in raw:
        print(f"  Geocodificando [{item['id']}] {item['evento'][:50]}…")
        coords = geocodificar(geolocator, item["lugar_texto"])

        lat, lon = (coords[0], coords[1]) if coords else (None, None)
        geometry = Point(lon, lat) if coords else None

        registros.append({
            "id":               item["id"],
            "evento":           item["evento"],
            "fecha":            item["fecha"],
            "hora_inicio":      item["hora_inicio"],
            "hora_fin":         item["hora_fin"],
            "lugar_texto":      item["lugar_texto"],
            "tipo_impacto":     item["tipo_impacto"],
            "consejo_movilidad": item["consejo_movilidad"],
            "icono_color":      item["icono_color"],
            "lat":              lat,
            "lon":              lon,
            "geometry":         geometry,
        })

    df = pd.DataFrame(registros)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    return gdf


def construir_cortes_gdf(raw: list[dict]) -> gpd.GeoDataFrame:
    """
    Construye un GeoDataFrame de LineStrings a partir de las coordenadas
    de los cortes de tráfico. No requiere geocodificación (coords manuales).

    Esquema:
    ┌──────┬─────────────────────┬───────┬──────────────┬──────────────┬──────────────┬──────────┐
    │ id   │ descripcion         │ fecha │ hora_inicio  │ hora_fin     │ tipo_impacto │ geometry │
    │ str  │ str                 │ str   │ str          │ str          │ str          │ LineStr. │
    └──────┴─────────────────────┴───────┴──────────────┴──────────────┴──────────────┴──────────┘
    """
    registros = []
    for item in raw:
        # coords_linea: lista de (lon, lat)
        geometria = LineString([(lon, lat) for lon, lat in item["coords_linea"]])
        registros.append({
            "id":           item["id"],
            "descripcion":  item["descripcion"],
            "fecha":        item["fecha"],
            "hora_inicio":  item["hora_inicio"],
            "hora_fin":     item["hora_fin"],
            "tipo_impacto": item["tipo_impacto"],
            "via":          item["via"],
            "tramo":        item["tramo"],
            "geometry":     geometria,
        })

    return gpd.GeoDataFrame(pd.DataFrame(registros), geometry="geometry", crs="EPSG:4326")


def construir_guaguas_gdf(raw: list[dict], geolocator: Nominatim) -> gpd.GeoDataFrame:
    """
    Geocodifica las paradas e intercambiadores y devuelve un GeoDataFrame.

    Esquema:
    ┌──────┬──────────────────┬─────────────────────┬───────┬─────────────┬─────────────┬──────────────┬──────────────┐
    │ id   │ tipo             │ descripcion         │ fecha │ hora_inicio │ hora_fin    │ alternativa  │ geometry     │
    │ str  │ str              │ str                 │ str   │ str         │ str         │ str          │ Point        │
    └──────┴──────────────────┴─────────────────────┴───────┴─────────────┴─────────────┴──────────────┴──────────────┘
    """
    registros = []
    for item in raw:
        print(f"  Geocodificando [{item['id']}] {item['descripcion'][:50]}…")
        coords = geocodificar(geolocator, item["lugar_texto"])
        lat, lon = (coords[0], coords[1]) if coords else (None, None)
        geometry = Point(lon, lat) if coords else None

        registros.append({
            "id":           item["id"],
            "tipo":         item["tipo"],
            "descripcion":  item["descripcion"],
            "fecha":        item["fecha"],
            "hora_inicio":  item["hora_inicio"],
            "hora_fin":     item["hora_fin"],
            "alternativa":  item["alternativa"],
            "lat":          lat,
            "lon":          lon,
            "geometry":     geometry,
        })

    df = pd.DataFrame(registros)
    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")


# ─────────────────────────────────────────────────────────────────────────────
# 4. EXPORTACIÓN A GEOJSON
# ─────────────────────────────────────────────────────────────────────────────

def exportar_geojson(gdf: gpd.GeoDataFrame, ruta: str) -> None:
    """
    Filtra filas sin geometría válida y exporta a GeoJSON.
    Además imprime un resumen con la estructura del archivo generado.
    """
    gdf_valido = gdf[gdf.geometry.notna()].copy()
    n_descartados = len(gdf) - len(gdf_valido)

    if n_descartados:
        print(f"  [!] {n_descartados} registro(s) sin geometría no incluidos en {ruta}")

    gdf_valido.to_file(ruta, driver="GeoJSON", encoding="utf-8")
    print(f"  ✓ Exportado: {ruta}  ({len(gdf_valido)} features)")

    # Resumen de estructura
    print(f"\n  Columnas en {ruta}:")
    for col in gdf_valido.columns:
        dtype = str(gdf_valido[col].dtype)
        sample = gdf_valido[col].iloc[0] if len(gdf_valido) else "–"
        # Truncar muestras largas
        if isinstance(sample, str) and len(sample) > 60:
            sample = sample[:57] + "…"
        print(f"    · {col:<22} {dtype:<15} ejemplo: {sample}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("═" * 60)
    print("  Papa en Canarias 2026 – Pipeline ETL Tarea 1")
    print("═" * 60)

    # Nominatim requiere un user-agent identificativo (ToS OSM)
    geolocator = Nominatim(user_agent="papa_gc_2026_mvp_v1")

    # ── Agenda ────────────────────────────────────────────────────────────────
    print("\n[1/3] Geocodificando agenda papal…")
    gdf_agenda = construir_agenda_gdf(AGENDA_RAW, geolocator)
    exportar_geojson(gdf_agenda, "agenda_papa.geojson")

    # ── Cortes de tráfico ─────────────────────────────────────────────────────
    print("\n[2/3] Construyendo capa de cortes de tráfico…")
    gdf_cortes = construir_cortes_gdf(CORTES_RAW)
    exportar_geojson(gdf_cortes, "cortes_trafico.geojson")

    # ── Guaguas ───────────────────────────────────────────────────────────────
    print("\n[3/3] Geocodificando impacto en guaguas…")
    gdf_guaguas = construir_guaguas_gdf(GUAGUAS_RAW, geolocator)
    exportar_geojson(gdf_guaguas, "guaguas_impacto.geojson")

    # ── Vista previa del DataFrame de agenda ──────────────────────────────────
    print("\n" + "─" * 60)
    print("  Vista previa – agenda_papa (sin columna geometry):")
    print("─" * 60)
    cols_preview = ["id", "evento", "fecha", "hora_inicio", "hora_fin",
                    "tipo_impacto", "lat", "lon"]
    print(gdf_agenda[cols_preview].to_string(index=False))

    print("\n" + "═" * 60)
    print("  Tarea 1 completada. Archivos generados:")
    print("    · agenda_papa.geojson")
    print("    · cortes_trafico.geojson")
    print("    · guaguas_impacto.geojson")
    print("  → Pasa estos archivos a tarea2_mapa_folium.py")
    print("═" * 60)


if __name__ == "__main__":
    main()
