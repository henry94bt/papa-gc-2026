"""
tarea1_agenda_papa.py
=====================
Pipeline ETL – Fase 1 & 2: Estructuración de agenda + Geocodificación
Viaje apostólico de León XIV a Canarias · 11–12 junio 2026

AGENDA OFICIAL VERIFICADA (fuentes: Diócesis de Canarias, Cabildo GC, Canarias7)

Salida: agenda_papa.geojson  (Points)
        cortes_trafico.geojson (LineStrings)
        guaguas_impacto.geojson (Points)
        aparcamientos.geojson  (Points)  ← NUEVO

Uso:
    pip install pandas geopandas geopy shapely
    python tarea1_agenda_papa.py
"""

import time
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# ─────────────────────────────────────────────────────────────────────────────
# 1. AGENDA OFICIAL  (11 junio Gran Canaria · 12 junio Tenerife)
# ─────────────────────────────────────────────────────────────────────────────

AGENDA_RAW = [
    # ── 11 JUNIO · GRAN CANARIA ──
    {
        "id": "A01",
        "evento": "Llegada a la Base Aérea de Gando",
        "fecha": "2026-06-11",
        "hora_inicio": "10:50",
        "hora_fin": "11:00",
        "lugar_texto": "Base Aérea de Gando, Telde, Gran Canaria",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Recepción institucional. Evita la GC-1 a primera hora; "
            "el dispositivo de tráfico arranca temprano."
        ),
        "icono_color": "red",
    },
    {
        "id": "A02",
        "evento": "Encuentro con migrantes en el Muelle de Arguineguín",
        "fecha": "2026-06-11",
        "hora_inicio": "11:40",
        "hora_fin": "12:25",
        "lugar_texto": "Muelle de Arguineguín, Mogán, Gran Canaria",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Acto humanitario ante unas 2.000 personas, con la presencia del "
            "presidente Pedro Sánchez. NO es una misa abierta. Acceso muy "
            "restringido en el muelle; sigue las indicaciones del operativo."
        ),
        "icono_color": "red",
    },
    {
        "id": "A03",
        "evento": "Encuentro con el clero en la Catedral de Santa Ana",
        "fecha": "2026-06-11",
        "hora_inicio": "13:30",
        "hora_fin": "14:30",
        "lugar_texto": "Catedral de Santa Ana, Vegueta, Las Palmas de Gran Canaria",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Encuentro con obispos, sacerdotes, religiosos y agentes de pastoral. "
            "Vegueta peatonalizada: aparca en Triana y accede a pie."
        ),
        "icono_color": "red",
    },
    {
        "id": "A04",
        "evento": "Apertura de la Fan Zone — Anexo del Estadio",
        "fecha": "2026-06-11",
        "hora_inicio": "14:00",
        "hora_fin": "18:30",
        "lugar_texto": "Estadio de Gran Canaria, Las Palmas de Gran Canaria",
        "tipo_impacto": "Medio",
        "consejo_movilidad": (
            "Actividades culturales y música canaria antes de la misa "
            "(Los Gofiones, Cristina Ramos, Yeray Rodríguez…). "
            "Usa las lanzaderas de guaguas a Siete Palmas."
        ),
        "icono_color": "orange",
    },
    {
        "id": "A05",
        "evento": "Misa multitudinaria en el Estadio de Gran Canaria",
        "fecha": "2026-06-11",
        "hora_inicio": "18:30",
        "hora_fin": "20:00",
        "lugar_texto": "Estadio de Gran Canaria, Las Palmas de Gran Canaria",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Acto central: +46.000 preinscritos. Música de la Orquesta "
            "Filarmónica de Gran Canaria y su Coro. Siete Palmas cerrada al "
            "tráfico desde las 09:00 hasta medianoche. Ve en guagua o lanzadera."
        ),
        "icono_color": "red",
    },
    # ── 12 JUNIO · TENERIFE ──
    {
        "id": "A06",
        "evento": "Llegada al Aeropuerto Tenerife Norte",
        "fecha": "2026-06-12",
        "hora_inicio": "09:10",
        "hora_fin": "09:30",
        "lugar_texto": "Aeropuerto Tenerife Norte, La Laguna, Tenerife",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Inicio de la jornada en Tenerife. La TF-5 tendrá restricciones "
            "desde primera hora. Usa el tranvía Santa Cruz–La Laguna."
        ),
        "icono_color": "red",
    },
    {
        "id": "A07",
        "evento": "Visita al Centro de Acogida Las Raíces",
        "fecha": "2026-06-12",
        "hora_inicio": "09:30",
        "hora_fin": "10:00",
        "lugar_texto": "Las Raíces, La Laguna, Tenerife",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Encuentro con migrantes acogidos en el centro. "
            "Zona con acceso restringido por seguridad."
        ),
        "icono_color": "red",
    },
    {
        "id": "A08",
        "evento": "Encuentro con organizaciones de integración",
        "fecha": "2026-06-12",
        "hora_inicio": "10:10",
        "hora_fin": "11:30",
        "lugar_texto": "Plaza del Cristo, La Laguna, Tenerife",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Casco histórico de La Laguna cortado. "
            "Accede en tranvía (parada La Trinidad / La Laguna)."
        ),
        "icono_color": "red",
    },
    {
        "id": "A09",
        "evento": "Santa Misa en el Puerto de Santa Cruz",
        "fecha": "2026-06-12",
        "hora_inicio": "12:15",
        "hora_fin": "14:00",
        "lugar_texto": "Puerto de Santa Cruz de Tenerife",
        "tipo_impacto": "Alto",
        "consejo_movilidad": (
            "Misa ante la Virgen de Candelaria, patrona del archipiélago. "
            "Santa Cruz con cortes importantes; usa el tranvía o guaguas especiales."
        ),
        "icono_color": "red",
    },
    {
        "id": "A10",
        "evento": "Ceremonia de despedida — Tenerife Norte",
        "fecha": "2026-06-12",
        "hora_inicio": "14:30",
        "hora_fin": "15:00",
        "lugar_texto": "Aeropuerto Tenerife Norte, La Laguna, Tenerife",
        "tipo_impacto": "Medio",
        "consejo_movilidad": (
            "Despedida del Rey Felipe VI y salida hacia Roma a las 15:00. "
            "Tráfico de retorno intenso en la TF-5 por la tarde."
        ),
        "icono_color": "orange",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 2. CORTES DE TRÁFICO  (datos oficiales del Cabildo de Gran Canaria)
# ─────────────────────────────────────────────────────────────────────────────

CORTES_RAW = [
    {
        "id": "C01",
        "descripcion": "Corte GC-1 dirección Las Palmas",
        "fecha": "2026-06-11",
        "hora_inicio": "12:00",
        "hora_fin": "13:30",
        "tipo_impacto": "Alto",
        "via": "GC-1",
        "tramo": "Acceso a LPGC",
        "coords_linea": [
            (-15.430, 27.990),
            (-15.420, 28.030),
            (-15.416, 28.070),
        ],
    },
    {
        "id": "C02",
        "descripcion": "Corte GC-3 dirección Las Palmas",
        "fecha": "2026-06-11",
        "hora_inicio": "17:30",
        "hora_fin": "18:30",
        "tipo_impacto": "Alto",
        "via": "GC-3",
        "tramo": "Circunvalación → LPGC",
        "coords_linea": [
            (-15.460, 28.075),
            (-15.445, 28.090),
            (-15.435, 28.100),
        ],
    },
    {
        "id": "C03",
        "descripcion": "Cierre total de Siete Palmas (entorno del Estadio)",
        "fecha": "2026-06-11",
        "hora_inicio": "09:00",
        "hora_fin": "23:59",
        "tipo_impacto": "Alto",
        "via": "Siete Palmas",
        "tramo": "Entorno Estadio de Gran Canaria",
        "coords_linea": [
            (-15.458, 28.097),
            (-15.456, 28.100),
            (-15.453, 28.102),
            (-15.456, 28.099),
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. GUAGUAS  (lanzaderas y refuerzos oficiales)
# ─────────────────────────────────────────────────────────────────────────────

GUAGUAS_RAW = [
    {
        "id": "G01",
        "tipo": "Lanzadera Guaguas Municipales",
        "descripcion": "Lanzadera a Siete Palmas desde el Auditorio Alfredo Kraus",
        "fecha": "2026-06-11",
        "hora_inicio": "14:00",
        "hora_fin": "23:00",
        "lugar_texto": "Auditorio Alfredo Kraus, Las Palmas de Gran Canaria",
        "alternativa": "Servicio directo al Estadio. Frecuencia reforzada.",
    },
    {
        "id": "G02",
        "tipo": "Lanzadera Guaguas Municipales",
        "descripcion": "Lanzadera a Siete Palmas desde Santa Catalina",
        "fecha": "2026-06-11",
        "hora_inicio": "14:00",
        "hora_fin": "23:00",
        "lugar_texto": "Parque Santa Catalina, Las Palmas de Gran Canaria",
        "alternativa": "Servicio directo al Estadio. Frecuencia reforzada.",
    },
    {
        "id": "G03",
        "tipo": "Lanzadera Guaguas Municipales",
        "descripcion": "Lanzadera a Siete Palmas desde San Telmo / Pérez Galdós",
        "fecha": "2026-06-11",
        "hora_inicio": "14:00",
        "hora_fin": "23:00",
        "lugar_texto": "San Telmo, Las Palmas de Gran Canaria",
        "alternativa": "Servicio directo al Estadio. Frecuencia reforzada.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 4. APARCAMIENTOS HABILITADOS  (datos oficiales del Cabildo) ← NUEVO
# ─────────────────────────────────────────────────────────────────────────────

APARCAMIENTOS_RAW = [
    {
        "id": "P01",
        "nombre": "Centro Comercial 7 Palmas",
        "plazas": 1500,
        "lugar_texto": "Centro Comercial 7 Palmas, Las Palmas de Gran Canaria",
        "requisito": "Mínimo 4 ocupantes por vehículo",
    },
    {
        "id": "P02",
        "nombre": "Hipercor",
        "plazas": 1500,
        "lugar_texto": "Hipercor, Avenida Mesa y López, Las Palmas de Gran Canaria",
        "requisito": "Mínimo 4 ocupantes por vehículo",
    },
    {
        "id": "P03",
        "nombre": "Infecar",
        "plazas": 400,
        "lugar_texto": "Infecar, Las Palmas de Gran Canaria",
        "requisito": "Mínimo 4 ocupantes por vehículo",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# 5. GEOCODIFICADOR
# ─────────────────────────────────────────────────────────────────────────────

def geocodificar(geolocator, lugar, reintentos=3):
    """Geocodifica una dirección con Nominatim. Devuelve (lat, lon) o None."""
    for intento in range(reintentos):
        try:
            time.sleep(1.2)  # ToS de OSM: 1 petición/segundo
            resultado = geolocator.geocode(
                lugar, country_codes="es", language="es", timeout=10
            )
            if resultado:
                return resultado.latitude, resultado.longitude
            print(f"  [!] Sin resultado para: {lugar!r}")
            return None
        except GeocoderTimedOut:
            print(f"  [timeout] intento {intento + 1}/{reintentos}")
            time.sleep(2)
        except GeocoderServiceError as e:
            print(f"  [error] {e}")
            return None
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 6. CONSTRUCTORES DE GEODATAFRAMES
# ─────────────────────────────────────────────────────────────────────────────

def construir_agenda_gdf(raw, geolocator):
    registros = []
    for item in raw:
        print(f"  Geocodificando [{item['id']}] {item['evento'][:48]}…")
        coords = geocodificar(geolocator, item["lugar_texto"])
        lat, lon = coords if coords else (None, None)
        registros.append({
            **{k: item[k] for k in (
                "id", "evento", "fecha", "hora_inicio", "hora_fin",
                "lugar_texto", "tipo_impacto", "consejo_movilidad", "icono_color")},
            "lat": lat, "lon": lon,
            "geometry": Point(lon, lat) if coords else None,
        })
    return gpd.GeoDataFrame(pd.DataFrame(registros), geometry="geometry", crs="EPSG:4326")


def construir_cortes_gdf(raw):
    registros = []
    for item in raw:
        geometria = LineString([(lon, lat) for lon, lat in item["coords_linea"]])
        registros.append({
            **{k: item[k] for k in (
                "id", "descripcion", "fecha", "hora_inicio", "hora_fin",
                "tipo_impacto", "via", "tramo")},
            "geometry": geometria,
        })
    return gpd.GeoDataFrame(pd.DataFrame(registros), geometry="geometry", crs="EPSG:4326")


def construir_guaguas_gdf(raw, geolocator):
    registros = []
    for item in raw:
        print(f"  Geocodificando [{item['id']}] {item['descripcion'][:48]}…")
        coords = geocodificar(geolocator, item["lugar_texto"])
        lat, lon = coords if coords else (None, None)
        registros.append({
            **{k: item[k] for k in (
                "id", "tipo", "descripcion", "fecha",
                "hora_inicio", "hora_fin", "alternativa")},
            "lat": lat, "lon": lon,
            "geometry": Point(lon, lat) if coords else None,
        })
    return gpd.GeoDataFrame(pd.DataFrame(registros), geometry="geometry", crs="EPSG:4326")


def construir_aparcamientos_gdf(raw, geolocator):
    registros = []
    for item in raw:
        print(f"  Geocodificando [{item['id']}] {item['nombre']}…")
        coords = geocodificar(geolocator, item["lugar_texto"])
        lat, lon = coords if coords else (None, None)
        registros.append({
            **{k: item[k] for k in ("id", "nombre", "plazas", "lugar_texto", "requisito")},
            "lat": lat, "lon": lon,
            "geometry": Point(lon, lat) if coords else None,
        })
    return gpd.GeoDataFrame(pd.DataFrame(registros), geometry="geometry", crs="EPSG:4326")


# ─────────────────────────────────────────────────────────────────────────────
# 7. EXPORTACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def exportar_geojson(gdf, ruta):
    gdf_valido = gdf[gdf.geometry.notna()].copy()
    n_descartados = len(gdf) - len(gdf_valido)
    if n_descartados:
        print(f"  [!] {n_descartados} registro(s) sin geometría no incluidos en {ruta}")
    gdf_valido.to_file(ruta, driver="GeoJSON", encoding="utf-8")
    print(f"  ✓ Exportado: {ruta}  ({len(gdf_valido)} features)")


# ─────────────────────────────────────────────────────────────────────────────
# 8. MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("═" * 60)
    print("  León XIV en Canarias 2026 – Pipeline ETL Tarea 1")
    print("═" * 60)

    geolocator = Nominatim(user_agent="papa_gc_2026_mvp_v2")

    print("\n[1/4] Geocodificando agenda papal…")
    gdf_agenda = construir_agenda_gdf(AGENDA_RAW, geolocator)
    exportar_geojson(gdf_agenda, "agenda_papa.geojson")

    print("\n[2/4] Construyendo capa de cortes de tráfico…")
    gdf_cortes = construir_cortes_gdf(CORTES_RAW)
    exportar_geojson(gdf_cortes, "cortes_trafico.geojson")

    print("\n[3/4] Geocodificando lanzaderas de guaguas…")
    gdf_guaguas = construir_guaguas_gdf(GUAGUAS_RAW, geolocator)
    exportar_geojson(gdf_guaguas, "guaguas_impacto.geojson")

    print("\n[4/4] Geocodificando aparcamientos habilitados…")
    gdf_aparcamientos = construir_aparcamientos_gdf(APARCAMIENTOS_RAW, geolocator)
    exportar_geojson(gdf_aparcamientos, "aparcamientos.geojson")

    print("\n" + "─" * 60)
    print("  Vista previa – agenda (sin geometry):")
    print("─" * 60)
    cols = ["id", "evento", "fecha", "hora_inicio", "tipo_impacto", "lat", "lon"]
    print(gdf_agenda[cols].to_string(index=False))

    print("\n" + "═" * 60)
    print("  Tarea 1 completada. Archivos generados:")
    print("    · agenda_papa.geojson      · cortes_trafico.geojson")
    print("    · guaguas_impacto.geojson  · aparcamientos.geojson")
    print("  → Ejecuta ahora: python tarea2_mapa_folium.py")
    print("═" * 60)


if __name__ == "__main__":
    main()
