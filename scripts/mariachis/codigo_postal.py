# Control de datos
from io import BytesIO
from zipfile import ZipFile
from requests import get as get_req

# Ingeniería de variables
from pandas import DataFrame
from geopandas import GeoDataFrame, points_from_xy

class PostalCodes:
    def __init__(self, iso_country_code: str='MX') -> None:
        '''
        Obtiene las coordenadas por comunidad de algún país desde <http://download.geonames.org/export/zip>
        '''
        self.country = iso_country_code
        self.zip_url = f'http://download.geonames.org/export/zip/{self.country}.zip'
        self.cols = [
            'country_code',
            'postal_code',
            'place_name',
            'state_name',
            'state_code',
            'province_name',
            'province_code',
            'community_name',
            'community_code',
            'lat',
            'lon',
            'accuracy',
        ]

    def get_data(self, decode_to: str='utf-8') -> DataFrame:
        # Obtiene la información del request
        req_data = get_req(self.zip_url).content
        # Optimizando memoria, obtiene los datos del zip
        zipfile = ZipFile(BytesIO(req_data))
        # Lista vacía para agregar cada renglón del archivo de interés
        data = []
        # Para cada renglón del archivo txt con la información de interés
        for line in zipfile.open(f'{self.country}.txt').readlines():
            # Añadirlo a la lista ya decodificado
            data.append(line.decode(decode_to))
        # Estructurarlo en un DataFrame para manipulación posterior
        df = DataFrame(map(lambda x: x.replace('\n','').split('\t'),data), columns=self.cols)
        return df

    def create_polygon(self, df: DataFrame, group_by: str=None, crs_code: str='EPSG:6372', lat_col: str='lat', lng_col: str='lon', just_geodf: bool=False) -> DataFrame:
        '''
        Crea el polígono desde un DataFrame con una columna de latitud y otra de longitud,
        puede devolver sólo la transformación o agrupar a nivel municipio, por ejemplo
        '''
        gdf = GeoDataFrame(df, crs=crs_code, geometry=points_from_xy(df[lat_col], df[lng_col]))
        # Si sólo se desea la transformación
        if just_geodf: return gdf
        # O si se desdea agrupar a un nivel de geolocalización superior
        df = gdf.dissolve(by=group_by)
        # Asegurarse de tener un polígono, porque probablemente el nivel de agregación resulta en una o dos coordenadas
        df['geometry'] = df['geometry'].buffer(0.05)
        # El nivel de agregación queda como índice, pasar a columna
        df.reset_index(inplace=True)
        return df
