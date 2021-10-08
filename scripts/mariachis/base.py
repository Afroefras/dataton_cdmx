# Control de datos
from time import sleep
from typing import Dict
from pathlib import Path
from requests import get as get_req
from IPython.display import clear_output, display

# Ingeniería de variables
from numpy import nan
from re import sub, UNICODE
from unicodedata import normalize
from string import ascii_uppercase
from pandas import DataFrame, read_csv, to_datetime

# Modelos
from sklearn.pipeline import Pipeline
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import RobustScaler

class BaseClass: 
    '''
    Clase con métodos en común para diferentes clases "hijas"
    '''
    def __init__(self, base_dir: str, file_name:str) -> None: 
        '''
        Obtener un directorio como texto y convertirlo a tipo Path para unir directorios, buscar archivos, etc.
        '''
        self.base_dir = Path(base_dir)
        self.file_name = file_name

    def __str__(self) -> str: 
        return f'Directorio: \t{self.base_dir}'

    def cool_print(self, text: str, sleep_time: float=0.03, by_word: bool=False) -> None: 
        '''
        Imprimir como si se fuera escribiendo
        '''
        acum = ''
        for x in (text.split() if by_word else text): 
            # Acumular texto
            acum += x+' ' if by_word else x
            # Limpiar pantalla
            clear_output(wait=True)
            # Esperar un poco para emular efecto de escritura
            sleep(sleep_time*(9 if by_word else 1))
            # Imprimir texto acumulado
            print(acum)
        sleep(1.7)
    
    def __len__(self) -> str: 
        '''
        Obtener el número de carpetas en el directorio base
        '''
        folders = len(str(self.base_dir).split('/'))-1
        self.cool_print(f"{folders} carpetas en {self.base_dir}")
        return folders

    def get_api(self, resource_id: str, base_url: str='https://datos.cdmx.gob.mx/api/3/action/datastore_search?resource_id=', distinct_rows: bool=True, row_limit: int=32000) -> DataFrame: 
        '''
        Obtener tabla via API
        '''
        # Parámetros de renglones únicos y límite de renglones
        params = f'&distinct={"true" if distinct_rows else "false"}&limit={row_limit}'
        # Unir url base con el id de los datos y los parámetros definidos
        full_url = base_url+resource_id+params
        try: 
            # Al devolver un objeto json, llamar a "records"
            df = DataFrame(get_req(full_url).json()['result']['records'])
            df_shape = df.shape
            self.cool_print(f'Archivo importado desde: {full_url}\nCon {df_shape[0]} renglones y {df_shape[-1]} columnas')
            return df
        except: self.cool_print(f'Error al obtener desde: {full_url}\nIntenta de nuevo!')

    def get_csv(self, **kwargs) -> DataFrame: 
        '''
        Obtener tabla a partir de un archivo .csv
        '''
        df = read_csv(self.base_dir.joinpath(f'{self.file_name}.csv'), low_memory=False, **kwargs)
        try: 
            df = read_csv(self.base_dir.joinpath(f'{self.file_name}.csv'), low_memory=False, **kwargs)
            df_shape = df.shape
            self.cool_print(f'Archivo con nombre {self.file_name}.csv fue encontrado en {self.base_dir}\nCon {df_shape[0]} renglones y {df_shape[-1]} columnas')
            return df
        except: self.cool_print(f'No se encontró el archivo con nombre {self.file_name}.csv en {self.base_dir}\nSi el archivo csv existe, seguramente tiene un encoding y/o separador diferente a "utf-8" y "," respectivamente\nIntenta de nuevo!')
    
    def export_csv(self, df: DataFrame, name_suffix=None, **kwargs) -> None: 
        '''
        Exportar un archivo en formato csv
        '''
        export_name = f'{self.file_name}.csv' if name_suffix==None else f'{self.file_name}_{name_suffix}.csv'
        df.to_csv(self.base_dir.joinpath(export_name), **kwargs)
        self.cool_print(f'Archivo: {export_name} fue exportado exitosamente en: {self.base_dir}')

    def api_export(self, export_kwargs: Dict={}, **api_kwargs) -> DataFrame: 
        '''
        Llamar método para leer API y luego exportar la tabla en formato csv
        '''
        data = self.get_api(**api_kwargs)
        self.export_csv(df=data, **export_kwargs)
        return data

    def full_import(self, api: bool=True, api_export: bool=True, **kwargs): 
        '''
        Función que permite elegir alguna de las 2 formas de importar los datos. Si es API permite exportar el resultado
        '''
        if api: 
            # Leer y exportar?
            if api_export: df = self.api_export(**kwargs)
            # O sólo leer de API
            else: df = self.get_api(**kwargs)
        # De otro modo, importar desde csv
        else: df = self.get_csv(**kwargs)
        return df

    def rem_nan_rows(self, df: DataFrame, thres: float=1.0):
        '''
        Omitir registros mayor o igual al porcentaje "thres" de valores nulos
        '''
        to_remove = []
        for i,row in enumerate(df.index):
            # Revisar por renglón
            sub_df = df.iloc[i,:].T
            # Obtener el porcentaje de nulos
            perc_nan = sub_df.isnull().mean()
            # Si dicho porcentaje es mayor, guardar en una lista
            if perc_nan >= thres: to_remove.append(row)
        # Omitir los registros de la lista con el porcentaje de valores nulos más grande que el parámetro "thres"
        df = df.loc[~df.index.isin(to_remove),:]
        # Informar cuántos renglones fueron omitidos
        self.cool_print(f'{len(to_remove)} renglones con {"{:.1%}".format(thres)}% o más valores nulos fueron eliminados')
        return df

    def date_vars(self, df: DataFrame, date_col: str='fecha') -> DataFrame: 
        '''
        Crear las columnas de divisiones de fechas
        '''
        # Convertir a tipo datetime
        df[date_col] = to_datetime(df[date_col])
        # Para extraer la división de año
        df[f'{date_col}_year'] = df[date_col].dt.year.map(int).map(str)
        # Trimestre a dos caracteres
        df[f'{date_col}_quarter'] = df[date_col].dt.quarter.map(lambda x: str(int(x)).zfill(2))
        # Y mes a dos caracteres
        df[f'{date_col}_month'] = df[date_col].dt.month.map(lambda x: str(int(x)).zfill(2))
        # Concatenar el año, tanto trimestre como con el mes
        df[f'{date_col}_yearquarter'] = df[f'{date_col}_year']+' - '+df[f'{date_col}_quarter']
        df[f'{date_col}_yearmonth'] = df[f'{date_col}_year']+' - '+df[f'{date_col}_month']
        df[date_col] = df[date_col].dt.date
        return df

    def clean_text(self, text: str, pattern: str="[^a-zA-Z0-9\s]", lower: bool=False) -> str: 
        '''
        Limpieza de texto
        '''
        # Eliminar acentos: áàäâã --> a
        clean = normalize('NFD', str(text).replace('\n',' \n ')).encode('ascii', 'ignore')
        clean = sub(pattern, ' ', clean.decode('utf-8'),flags=UNICODE)
        # Mantener sólo un espacio
        clean = sub(r'\s{2,}', ' ', clean)
        # Minúsculas si el parámetro lo indica
        if lower: clean = clean.lower()
        # Si el registro estaba vacío, indicar nulo
        if clean in ('','nan'): clean = nan
        return clean

    def clean_number(self, text: str) -> str: 
        '''
        Limpieza numérica
        '''
        # Omitir todo lo que no sea número o "."
        clean = sub('[^0-9\.]', '', str(text))
        # Si el registro estaba vacío, indicar nulo
        if clean in ('','nan'): clean = nan
        return clean

    def make_clusters(self, df: DataFrame, n_clusters: int=5, cols: list=None, scaler=RobustScaler, cluster_obj=GaussianMixture, **kwargs) -> tuple: 
        '''
        Recibe un DataFrame y lo devuelve con una columna adicional indicando el cluster asignado, además del objeto para predecir en nuevos datos
        '''
        cluster_cols = cols if cols!=None else df.columns
        # Primero escalar, después agrupar
        if scaler==None: pipe_clust = cluster_obj(n_clusters, random_state=22, **kwargs)
        else: pipe_clust = Pipeline(steps=[('scaler', scaler()), ('cluster', cluster_obj(n_clusters, random_state=22, **kwargs))])
        # Nueva columna definiendo el clúster
        df['cluster'] = pipe_clust.fit_predict(df[cluster_cols])
        # Diccionario para reemplazar A: 1, B: 2, etc
        cluster_dict = dict(zip(range(n_clusters), ascii_uppercase[: n_clusters]))
        df['cluster'] = df['cluster'].map(cluster_dict)
        return df['cluster'], pipe_clust

    def profiles(self, df: DataFrame, cluster_col: str='cluster') -> None: 
        '''
        Recibe el resultado del método anterior para mostrar la diferencia numérica y categórica de cada clúster para todas las variables
        '''
        prof = {}
        # Obtener el tipo de variable para cada columna
        df_coltype = df.dtypes
        # Guardar las variables numéricas
        num_cols = [x for x,y in zip(df_coltype.index,df_coltype) if y!=object]
        # Promedio de cada variable numérica según el clúster
        if len(num_cols)>0: prof['numeric'] = df.pivot_table(index=cluster_col, values=num_cols)
        # Obtener las variables categóricas
        cat_cols = [x for x in df.columns if x not in num_cols]
        # Columna auxiliar para contabilizar
        df['n'] = 1
        for col in cat_cols: 
            # Cuenta de registros para cada variable categórica según el clúster
            prof[col] = df.pivot_table(index=cluster_col, columns=col, aggfunc={'n': sum})
        # Mostrar cada perfilamiento en un DataFrame con formato condicional
        for x in prof.values():
            x = x.fillna(0)
            by_clust = x.copy()
            by_var = x.T.copy()
            perc = x/x.sum().sum()
            for summary, to_format, to_axis in zip([by_clust, by_var, perc],["{:.0f}","{:.0f}","{:.1%}"],[0,0,None]):
                display(summary.style.format(to_format).background_gradient('Blues', axis=to_axis))


