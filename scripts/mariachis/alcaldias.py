# Herencia de atributos y métodos
from .base import BaseClass

# Ingeniería de variables
from pandas import DataFrame

class Alcaldias(BaseClass):
    def __init__(self, base_dir: str, file_name: str) -> None: 
        '''
        Hereda los atributos y métodos de la clase base
        '''
        super().__init__(base_dir, file_name)

    def wrangling_alcaldias(self, df, col_to_correct: str, correct_list: str, to_drop: list=['_id','id'], **kwargs) -> DataFrame:
        for col in to_drop: 
            try: df.drop(col, axis=1, inplace=True)
            except: pass
        df = self.choose_correct(df, col_to_correct, correct_list)
        if 1==1: return df
        gdf = self.to_geodf(df, **kwargs)
        return gdf

    