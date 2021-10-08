# Herencia de atributos y métodos
from .base import BaseClass

# Ingeniería de variables
from shapely.geometry import Point, Polygon
from geopandas import GeoDataFrame
from pandas import DataFrame

class Alcaldias(BaseClass):
    def __init__(self, base_dir: str, file_name: str) -> None: 
        '''
        Hereda los atributos y métodos de la clase base
        '''
        super().__init__(base_dir, file_name)

    def to_geodf(self, df: DataFrame, geo_col: str='geo_shape', step: int=10) -> GeoDataFrame:
        '''
        Recibe un DataFrame con una columna que, dentro de un diccionario contiene los puntos que
        delimitan el polígono de la localidad, devuelve un GeoDataFrame con métricas de geolocalización importantes
        '''
        # Obtener lista de coordenadas para cada registro
        df['geometry'] = df[geo_col].map(lambda x: eval(x)['coordinates'][0])
        # Cada coordenada se convierte a tipo Point
        df['geometry'] = df['geometry'].map(lambda x: [Point(tuple(y)) for y in x[::step]])
        # Para generar el polígono que delimita a la localidad
        df['geometry'] = df['geometry'].map(Polygon)
        # Convertir a DataFrame
        df = GeoDataFrame(df, geometry='geometry')
        # Para obtener su área,
        df['area'] = df.area
        # Límites,
        df['boundary'] = df.boundary
        # Punto central,
        df['centroid'] = df.centroid
        # Y el polígono que la contiene
        df['convex_hull'] = df.convex_hull
        return df