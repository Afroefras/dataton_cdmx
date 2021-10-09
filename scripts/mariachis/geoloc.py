# Herencia de atributos y métodos
from ._base import BaseClass

# Control de datos
from io import BytesIO
from zipfile import ZipFile
from requests import get as get_req

# Ingeniería de variables
from pandas import DataFrame

class GeoLoc(BaseClass):
    def __init__(self, base_dir: str, file_name: str, iso_country_code: str='MX') -> None:
        '''
        Obtiene las coordenadas por comunidad de algún país desde <http://download.geonames.org/export/zip>
        '''
        super().__init__(base_dir, file_name)
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
        self.cool_print(f'Códigos postales de {self.country} importados desde {self.zip_url}')
        # Exporta los resultados en formato csv
        self.export_csv(df, index=False, sep='\t', encoding='utf-16')
        return df

    def wrangling_cp(self, df: DataFrame, group_by: str, to_keep: list=['country_code','state_name','state_code','province_name','province_code','lat','lon']) -> DataFrame:
        # Construye el polígono de geolocalización
        df = df[to_keep].copy()
        # Construye el polígono de geolocalización
        df = self.geo_polygon(df, group_by=group_by)
        # Crea variables de geolocalización importantes
        df = self.geo_metrics(df)
        # Exporta los resultados en formato csv
        self.export_csv(df, name_suffix='geoloc', index=False)
        return df

