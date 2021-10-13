# Herencia de atributos y métodos
import typing
from ._base import BaseClass

# Control de datos
from io import BytesIO
from typing import Dict
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

    def get_data(self, decode_to: str='utf-8', replace_dict: Dict={'México':'Estado de México','Distrito Federal':'Ciudad de México'}) -> DataFrame:
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

        df = df.replace(replace_dict)
        
        # Exporta los resultados en formato csv
        self.export_csv(df, index=False, sep='\t', encoding='utf-16')
        return df

    def wrangling_geo(self, data: DataFrame, filter_places: Dict={'state_name':['Ciudad de México','Estado de México']}, group_by_cols: list=['state_name','province_name']) -> DataFrame:
        # Filtra los lugares indicados en el parámetro "filter_places"
        df = DataFrame()
        for level, places in filter_places.items():
            sub_df = data[data[level].isin(places)].copy()
            df = df.append(sub_df, ignore_index=True)

        df['group'] = df[group_by_cols].apply(', '.join, axis=1)

        # Construye el polígono de geolocalización
        df = self.geo_polygon(df, group_by='group')

        # Crea variables de geolocalización importantes
        df = self.geo_metrics(df)
        
        # Exporta los resultados en formato csv
        self.export_csv(df, name_suffix='geoloc', index=False)
        return df

    def merge_with_ile(self, ile: DataFrame, geo: DataFrame, ile_cols: str=['entidad','alc_o_municipio'], geo_cols: str=['state_name','province_name'], rename_to: str='estado, municipio', to_drop: list=['geometry','lat','lon','area','boundary','convex_hull']) -> DataFrame:
        # Unir las columnas para evitar duplicidad de nombres
        ile[rename_to] = ile[ile_cols].apply(', '.join, axis=1).map(lambda x: self.clean_text(x, lower=True).title())
        geo[rename_to] = geo[geo_cols].apply(', '.join, axis=1).map(lambda x: self.clean_text(x, lower=True).title())
        # Unir ILE con la geolocalización, manteniendo un registro original
        df = ile.reset_index().merge(geo, on=rename_to).drop_duplicates('index')
        # Exporta los resultados en formato csv
        self.export_csv(df.drop(to_drop, axis=1), name_suffix='geoloc', index=False)
        return df
