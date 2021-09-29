
import cufflinks as cf
from time import sleep
from pathlib import Path
from re import sub, UNICODE
from numpy import nan, array
from datetime import datetime
from unicodedata import normalize
from string import ascii_uppercase
from typing import Dict, Type, Union
from requests import get as get_req
from IPython.display import clear_output, display
from pandas import DataFrame, Series, read_csv, date_range, to_datetime

# SKLEARN
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler

cf.go_offline()

class BaseClass: 
    
    def __init__(self, base_dir: str) -> None: 
        '''
        Obtener un directorio como texto y convertirlo a tipo Path
        '''
        self.base_dir = Path(base_dir)

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
        # Esperar con el texto completo
        sleep(1.7)
        # Borrar el texto de pantalla
        clear_output()
        return acum
    
    def __str__(self) -> str: 
        return self.cool_print(f'Directorio: \t{self.base_dir}')
    
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
            self.cool_print(f'Archivo importado desde:  {full_url}\nCon {df_shape[0]} renglones y {df_shape[-1]} columnas')
            return df
        except:  self.cool_print(f'Error al obtener desde:  {full_url}\nIntenta de nuevo!')

    def get_csv(self, file_name: str, **kwargs) -> DataFrame: 
        '''
        Obtener tabla a partir de un archivo .csv
        '''
        try:  
            df = read_csv(self.base_dir.joinpath(f'{file_name}.csv'), low_memory=False, **kwargs)
            self.cool_print(f'Archivo con nombre {file_name}.csv fue encontrado en {self.base_dir}')
            return df
        except:  self.cool_print(f'No se encontró el archivo con nombre {file_name}.csv en {self.base_dir}\nSi el archivo csv existe, seguramente tiene un encoding y/o separador diferente a "utf-8" y "," respectivamente\nIntenta de nuevo!')
    
    def export_csv(self, df: DataFrame, file_name: str, **kwargs) -> None: 
        '''
        Exportar un archivo en formato csv
        '''
        df.to_csv(self.base_dir.joinpath(f'{file_name}.csv'), **kwargs)
        self.cool_print(f'Archivo:  {file_name}.csv fue exportado exitosamente en:  {self.base_dir}')

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
            if api_export:  df = self.api_export(**kwargs)
            # O sólo leer de API
            else:  df = self.get_api(**kwargs)
        # De otro modo, importar desde csv
        else:  df = self.get_csv(**kwargs)
        return df

    def date_vars(self, df: DataFrame, date_col: str='fecha') -> DataFrame: 
        # Convertir a tipo datetime
        df[date_col] = to_datetime(df[date_col])
        # Para extraer la división de año
        df[f'{date_col}_year'] = df[date_col].dt.year.map(int).map(str)
        # Trimestre a dos caracteres
        df[f'{date_col}_quarter'] = df[date_col].dt.quarter.map(lambda x:  str(int(x)).zfill(2))
        # Y mes a dos caracteres
        df[f'{date_col}_month'] = df[date_col].dt.month.map(lambda x:  str(int(x)).zfill(2))
        # Concatenar el año, tanto trimestre como con el mes
        df[f'{date_col}_yearquarter'] = df[f'{date_col}_year']+' - '+df[f'{date_col}_quarter']
        df[f'{date_col}_yearmonth'] = df[f'{date_col}_year']+' - '+df[f'{date_col}_month']
        return df

    def clean_text(self, text: str, pattern: str="[^a-zA-Z0-9\s]", lower: bool=True) -> str: 
        # Eliminar acentos áàäâã
        clean = normalize('NFD', str(text).replace('\n',' \n ')).encode('ascii', 'ignore')
        clean = sub(pattern, ' ', clean.decode('utf-8'),flags=UNICODE)
        # Mantener sólo un espacio
        clean = sub(r'\s{2,}', ' ', clean)
        # str(null) = "nan", omitir dicho texto
        clean = sub(r'^nan$', '', clean)
        # Minúsculas si el parámetro lo indica
        if lower:  clean = clean.lower()
        return clean

    def clean_number(self, text: str): 
        # Omitir todo lo que no sea número o "."
        clean = sub('[^0-9\.]', '', str(text))
        # Si el registro estaba vacío, indicar nulo
        if clean=='':  clean = nan
        return clean

    def multishift(self, df: DataFrame, id_cols: list[str], date_col: str='fecha', shifts: Union[list,tuple,range]=range(1,22), **pivot_args): 
        '''
        Escalona los valores para crear una Tabla Analítica de Datos con formato:  valor hoy, valor 1 día antes, dos días antes, etc
        '''
        df[date_col] = df[date_col].map(to_datetime).dt.date

        # Sólo una columna que servirá como ID
        id_col = ','.join(id_cols)
        df[id_col] = df[id_cols].apply(lambda x: ','.join(x.dropna().astype(str)),axis=1)

        # Omitir aquellos IDs con menor frequencia que el máximo valor de "shifts", porque inevitablemente tendrán shift vacíos
        freq = df[id_col].value_counts().to_frame()
        omit_idx = freq[freq[id_col]<=max(shifts)].index.to_list()
        if len(omit_idx)>0: 
            df = df[~df[id_col].isin(omit_idx)].copy()
        
        # Estructurar una tabla pivote, de donde se partirá para "recorrer" los días
        df = df.pivot_table(index=[id_col,date_col], **pivot_args, fill_value=0)
        df.columns = ['_'.join([x for x in col]) if not isinstance(df.columns[0],str) else col for col in df.columns]
        
        df = df.reset_index()
        total = DataFrame()
        for row in set(df[id_col]): 
            # Para cada grupo de renglones por ID
            df_id = df.set_index(id_col).loc[row,: ]
            # Asegurar todas las fechas
            tot_dates = DataFrame(date_range(start=df_id[date_col].min(), end=df_id[date_col].max()).date, columns=[date_col])
            df_id = df_id.merge(tot_dates, on=date_col, how='right').fillna(0)
            cols = df_id.columns[1: ]
            # Comenzar el "escalonado" de la tabla pivote inicial
            aux = df_id.copy()
            for i in shifts: 
                aux = aux.join(df_id.iloc[: ,1: ].shift(i).rename(columns={x: f'{x}_{str(i).zfill(2)}' for x in cols}))
            aux[id_col] = row
            total = total.append(aux,ignore_index=True)
        try:  total.set_index(id_cols+[date_col], inplace=True)
        except:  pass
        finally:  return total

    def apply_multishift(self, df: DataFrame, file_name: str, export_shifted: bool=True, **kwargs) -> tuple[DataFrame, array]: 
        # Aplicar la función "multishift" con los parámetros personalizados
        df = self.multishift(df, **kwargs)
        df.dropna(inplace=True)
        df = df[sorted(df.columns)].copy()

        # Tal vez el usuario quiere exportar los resultados
        if export_shifted:  self.export_csv(df, f'{file_name}_shifted.csv')

        # Obtener la lista de las columnas de todos los días previos
        prev = df.head(1).filter(regex='_\d+').columns.tolist()
        actual = [x for x in df.columns if x not in prev]

        # Seleccionar los datos para construir f(X)=y
        X = df[prev].copy()
        y = df[actual].sum(axis=1).values
        return X, y

    def train_reg_model(self, X: Union[DataFrame,array], y: array, scaler: Type[Union[MinMaxScaler, StandardScaler, RobustScaler]]=RobustScaler, model: Type[Union[LinearRegression, RandomForestRegressor]]=LinearRegression): 
        '''
        Escala y entrena un modelo, devuelve el score, el objeto tipo Pipeline y la relevancia de cada variable
        '''
        # Conjunto de entrenamiento y de test
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.77, random_state=22, shuffle=True)

        # Define los pasos del flujo
        pipe_obj = Pipeline(steps=[('prep', scaler()), ('model', model(n_jobs=-1))])

        # Entrena y guarda el score en test
        test_score = pipe_obj.fit(X_train,y_train).score(X_test, y_test)
        test_show = f"Score:  {'{:.2%}'.format(test_score)}"
        # Guarda el score en train, para revisar sobreajuste
        train_score = pipe_obj.score(X_train,y_train)
        train_show = f"Training score:  {'{:.2%}'.format(train_score)}"

        # Imprime los scores
        to_show = [test_show, train_show, "Estas son las variables más relevantes: "]
        for x in to_show:  self.cool_print(x)
        print(to_show)

        # Elige la forma de obtener las variables más representativas
        most_important_features = pipe_obj[-1].coef_ if model==LinearRegression else pipe_obj[-1].feature_importances_
        # Las ordena descendentemente
        coef_var = DataFrame(zip(X.columns, most_important_features)).sort_values(1, ascending=False).reset_index(drop=True)
        return pipe_obj, coef_var

    def real_vs_est(self, X, y, model): 
        # De todo el conjunto de datos...
        df = X.join(DataFrame(y, index=X.index, columns=['real']))
        # Predice el el valor...
        df['est'] = model.predict(X)
        # Y devuelve sólo las columna real y la estimada
        return df[['real','est']]

    def plot_real_vs_est(self, X, y, model, id_col, date_col='fecha', from_year: int=1900, to_year: int=datetime.now().year): 
        # Obtener real vs estimado
        pred = self.real_vs_est(X, y, model).reset_index()

        # Filtrar sólo años de interés
        pred['year'] = to_datetime(pred[date_col]).dt.year
        df = pred[(pred['year']>=from_year)&(pred['year']<=to_year)].copy()
        df.drop(columns='year', inplace=True)

        # Mostrar comportamiento real vs estimado por línea del metro
        df.set_index(id_col, inplace=True)
        for x in set(df.index): 
            df_id = df.loc[x,: ].reset_index(drop=True).set_index(date_col)
            df_id.iplot(title=x)

    def make_clusters(self, df: DataFrame, cluster_cols: list, n_clusters: int=5, kmeans: bool=False, scaler: Type[Union[MinMaxScaler, StandardScaler, RobustScaler]]=RobustScaler) -> tuple([Series,Pipeline]): 
        # Definir objeto para clustering
        cluster_obj = KMeans(n_clusters, random_state=22) if kmeans else GaussianMixture(n_clusters, random_state=22)
        # Primero escalar, después agrupar
        pipe_clust = Pipeline(steps=[('scaler', scaler()), ('cluster', cluster_obj)])
        # Nueva columna definiendo el clúster
        df['cluster'] = pipe_clust.fit_predict(df[cluster_cols])
        # Diccionario para reemplazar A: 1, B: 2, etc
        cluster_dict = dict(zip(range(n_clusters), ascii_uppercase[: n_clusters]))
        df['cluster'] = df['cluster'].map(cluster_dict)
        return df['cluster'], pipe_clust

    def profiles(self, df: DataFrame, cluster_col: str='cluster', number_format: str="{:.0f}") -> DataFrame: 
        prof = {}
        # Obtener las variables numéricas
        num_cols = df.sample(frac=0.01).describe().columns.tolist()
        # Promedio de cada variable numérica según el clúster
        prof['numeric'] = df.pivot_table(index=cluster_col, values=num_cols)
        # Obtener las variables categóricas
        cat_cols = [x for x in df.columns if x not in num_cols]
        # Columna auxiliar para contabilizar
        df['n'] = 1
        for col in cat_cols: 
            # Cuenta de registros para cada variable categórica según el clúster
            prof[col] = df.pivot_table(index=col, columns=cluster_col, aggfunc={'n': sum})
        # Mostrar cada perfilamiento en un DataFrame con formato condicional
        for var in prof.values(): 
            print(var)
            display(var.fillna(0).style.format(number_format).background_gradient('Blues'))

####################################################################################################################

class IngresoMetro(BaseClass): 
    def __init__(self, base_dir: str) -> None: 
        super().__init__(base_dir)

    def wrangling_ingreso(self, df, date_col: str='fecha', add_cols: list[str]=['tipo_ingreso'], **kwargs): 
        df.drop(['id','_id'], axis=1, inplace=True)
        # Las líneas del metro son columnas, crear sólo una columna indicando a qué línea se refiere
        df = df.melt(id_vars=[date_col]+add_cols, var_name='linea', value_name='ingreso')
        # Obtener f(X)=y "escalonando" los valores de días previos
        X, y = self.apply_multishift(df, **kwargs)
        return X,y

####################################################################################################################

class AfluenciaTransporte(BaseClass): 
    def __init__(self, base_dir: str) -> None: 
        super().__init__(base_dir)

    def wrangling_afluencia(self, df, value_col='afluencia_total_preliminar', **kwargs): 
        df.drop(['id','_id'], axis=1, inplace=True)
        # Eliminar "," que convierten el valor a texto
        df[value_col] = df[value_col].map(str).str.replace(',', '')
        df[[value_col]] = df[[value_col]].replace({'': 0}).astype(int)
        # Obtener f(X)=y "escalonando" los valores de días previos
        X, y = self.apply_multishift(df, **kwargs)
        return X,y