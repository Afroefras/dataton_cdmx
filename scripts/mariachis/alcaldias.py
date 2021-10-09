# Herencia de atributos y métodos
from .base import BaseClass

# Ingeniería de variables
from pandas import DataFrame
from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon

class Alcaldias(BaseClass):
    def __init__(self, base_dir: str, file_name: str) -> None: 
        '''
        Hereda los atributos y métodos de la clase base
        '''
        super().__init__(base_dir, file_name)

    def poldict_to_geodf(self, df: DataFrame, geo_col: str, step: int=10) -> GeoDataFrame:
        '''
        Recibe un DataFrame con una columna que, dentro de un diccionario contiene los puntos que
        delimitan el polígono de la localidad, devuelve un GeoDataFrame con métricas de geolocalización importantes
        '''
        # Obtener lista de coordenadas para cada registro
        df['geometry'] = df[geo_col].map(lambda x: eval(x)['coordinates'][0])
        # Cada par de coordenadas se convierten a tipo Point,
        # Nota: range(10)[::2] --> (0,2,4,6,8) así que hay saltos de tamaño "step" para la lista de coordenadas
        df['geometry'] = df['geometry'].map(lambda x: [Point(tuple(y)) for y in x[::step]])
        # Para generar el polígono que delimita a la localidad
        df['geometry'] = df['geometry'].map(Polygon)
        # Convertir a GeoDataFrame
        df = GeoDataFrame(df, geometry='geometry')
        # Para obtener su área, límite, punto central y el polígono que contiene a cada localidad
        for metric in ['area','boundary','centroid','convex_hull']:
            df[metric] = eval(f'df.{metric}')
        # Obtener coordenadas del centroide
        coor = df['centroid'].map(lambda x: list(x.coords)[0])
        # Establecer una columna para la latitud y otra de longitud
        df[[f'{geo_col}_lat', f'{geo_col}_lon']] = DataFrame(coor.tolist(), index=df.index)
        return df

    def wrangling_alcaldias(self, df, col_to_correct: str, correct_list: str, geo_col: str='geo_shape', **kwargs) -> DataFrame:
        '''
        Recibe un DataFrame y realiza la limpieza del nombre de alcaldía, además obtiene su polígono de coordenadas y crea variables de geolocalización importantes
        '''
        # Elige el nombre de alcaldía que más se parece
        df = self.choose_correct(df, col_to_correct, correct_list)
        # Mantiene sólo el nombre correcto de alcaldía para mantenerla de índice y la columna con el polígono
        df = df[[f'{col_to_correct}_correct', geo_col]].set_index(f'{col_to_correct}_correct')
        # Construye el polígono y crea variables de geolocalización importantes
        gdf = self.poldict_to_geodf(df, geo_col=geo_col, **kwargs)
        gdf.drop(geo_col, axis=1, inplace=True)
        # Exporta los resultados en formato csv
        self.export_csv(gdf, name_suffix='geoloc')
        return gdf

    def merge_ile(self, ile: DataFrame, alc: DataFrame, ile_col: str='alc_o_municipio', alc_col: str='nomgeo_correct', how_merge: str='inner') -> DataFrame:
        '''
        Une el nombre de alcaldías de la tabla ILE con el catálogo de alcaldías ya con geolocalización en donde 
        los nombres tengan una similitud > 90%, el resto lo marca como zona foránea
        '''
        df = self.choose_correct(ile, ile_col, alc[alc_col].tolist(), fill_value='Zona Foránea', cutoff=0.9)
        df = df.merge(alc, how=how_merge, left_on=f'{ile_col}_correct', right_on=alc_col)
        # Exporta los resultados en formato csv
        self.export_csv(df, name_suffix='geoloc', index=False)
        return df
    