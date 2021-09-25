from time import sleep
from typing import Dict
from pathlib import Path
from requests import get as get_req
from pandas import DataFrame, read_csv
from IPython.display import clear_output

class BaseClass:
    def __init__(self, base_dir:str) -> None:
        self.base_dir = Path(base_dir)

    def cool_print(self, text:str, sleep_time:float=0.03, by_word:bool=False) -> None:
        '''
        Imprimir como si se fuera escribiendo
        '''
        acum = ''
        for x in text.split() if by_word else text:
            acum += x+' ' if by_word else x
            clear_output(wait=True)
            sleep(sleep_time*(9 if by_word else 1))
            print(acum)
        sleep(0.9)
        clear_output()
        return acum
    
    def __str__(self) -> str:
        return self.cool_print(f'Directorio:\t{self.base_dir}')
    
    def __len__(self) -> str:
        return self.cool_print(f"{len(str(self.base_dir).split('/'))-1} folders en {self.base_dir}")

    def get_api(self, resource_id:str, base_url:str='https://datos.cdmx.gob.mx/api/3/action/datastore_search?resource_id=', distinct_rows:bool=True, row_limit:int=32000) -> DataFrame:
        '''
        Obtener tabla via API
        '''
        params = f'&distinct={"true" if distinct_rows else "false"}&limit={row_limit}'
        full_url = base_url+resource_id+params
        try:
            df = DataFrame(get_req(full_url).json()['result']['records'])
            df_shape = df.shape
            self.cool_print(f'Archivo importado desde: {full_url}\nCon {df_shape[0]} renglones y {df_shape[-1]} columnas')
            return df
        except: 
            self.cool_print(f'Error al obtener desde: {full_url}\nIntenta de nuevo!')

    def get_csv(self, file_name:str, **kwargs) -> DataFrame:
        '''
        Obtener tabla a partir de un archivo .csv
        '''
        try: 
            df = read_csv(self.base_dir.joinpath(file_name), **kwargs)
            self.cool_print(f'Archivo con nombre "{file_name}" fue encontrado en {self.base_dir}')
            return df
        except: self.cool_print(f'Archivo con nombre "{file_name}" no fue encontrado en {self.base_dir}\nIntenta de nuevo!')
    
    def export_csv(self, df:DataFrame, file_name:str, **kwargs) -> None:
        df.to_csv(self.base_dir.joinpath(file_name), **kwargs)
        print(f'Archivo: {file_name} fue exportado exitosamente en: {self.base_dir}')

    def api_export(self, export_kwargs:Dict={}, **api_kwargs) -> DataFrame:
        data = self.get_api(**api_kwargs)
        self.export_csv(df=data, **export_kwargs)
        return data

####################################################################################################################