
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
from pandas import DataFrame, Series, read_csv, date_range, to_datetime, cut, qcut

from kmodes.kmodes import KModes
# SKLEARN
from sklearn.pipeline import Pipeline
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler

cf.go_offline()

class BaseClass: 
    
    def __init__(self, base_dir: str, file_name:str) -> None: 
        '''
        Obtener un directorio como texto y convertirlo a tipo Path
        '''
        self.base_dir = Path(base_dir)
        self.file_name = file_name

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
    
    def __str__(self) -> str: 
        return f'Directorio: \t{self.base_dir}'
    
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

    def date_vars(self, df: DataFrame, date_col: str='fecha') -> DataFrame: 
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
        # Omitir todo lo que no sea número o "."
        clean = sub('[^0-9\.]', '', str(text))
        # Si el registro estaba vacío, indicar nulo
        if clean in ('','nan'): clean = nan
        return clean

    def multishift(self, df: DataFrame, id_cols: list, date_col: str='fecha', shifts: Union[list,tuple,range]=range(1,22), **pivot_args): 
        '''
        Escalona los valores para crear una Tabla Analítica de Datos con formato: valor hoy, valor 1 día antes, dos días antes, etc
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
        # Unir las posibles multi-columnas en una
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
        return total.set_index(id_cols+[date_col], inplace=True)

    def apply_multishift(self, df: DataFrame, export_shifted: bool=True, **kwargs) -> tuple: 
        # Aplicar la función "multishift" con los parámetros personalizados
        df = self.multishift(df, **kwargs)
        df.dropna(inplace=True)
        df = df[sorted(df.columns)].copy()

        # Tal vez el usuario quiere exportar los resultados
        if export_shifted: self.export_csv(df, name_suffix='shifted')

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
        # Guarda el score en train, para revisar sobreajuste
        train_score = pipe_obj.score(X_train,y_train)

        # Imprime los scores
        self.cool_print(f"Score: {'{:.2%}'.format(test_score)}\nTraining score: {'{:.2%}'.format(train_score)}\nEstas son las variables más relevantes: ")

        # Elige la forma de obtener las variables más representativas
        most_important_features = pipe_obj[-1].coef_ if model==LinearRegression else pipe_obj[-1].feature_importances_
        # Las ordena descendentemente
        coef_var = DataFrame(zip(X.columns, most_important_features)).sort_values(1, ascending=False).reset_index(drop=True)
        return pipe_obj, coef_var

    def real_vs_est(self, X: DataFrame, y: array, model: Type[Union[LinearRegression, RandomForestRegressor]]) -> DataFrame: 
        # De todo el conjunto de datos...
        df = X.join(DataFrame(y, index=X.index, columns=['real']))
        # Predice el el valor...
        df['est'] = model.predict(X)
        # Y devuelve sólo las columna real y la estimada
        return df[['real','est']]

    def plot_real_vs_est(self, X: DataFrame, y: array, model: Type[Union[LinearRegression, RandomForestRegressor]], id_col: str, date_col='fecha', from_year: int=1900, to_year: int=datetime.now().year): 
        # Obtener real vs estimado
        pred = self.real_vs_est(X, y, model).reset_index()

        # Filtrar sólo años de interés
        pred['year'] = to_datetime(pred[date_col]).dt.year
        df = pred[(pred['year']>=from_year)&(pred['year']<=to_year)].copy()
        df.drop(columns='year', inplace=True)

        # Mostrar comportamiento real vs estimado
        df.set_index(id_col, inplace=True)
        for x in set(df.index): 
            df_id = df.loc[x,: ].reset_index(drop=True).set_index(date_col)
            df_id.iplot(title=x)

    def make_clusters(self, df: DataFrame, n_clusters: int=5, cols: list=None, scaler=RobustScaler, cluster_obj=GaussianMixture, **kwargs) -> tuple([Series,Pipeline]): 
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

    def profiles(self, df: DataFrame, cluster_col: str='cluster', number_format: str="{:.0f}") -> DataFrame: 
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
        for var in prof.values():
            display(var.fillna(0).style.format(number_format).background_gradient('Blues'))

####################################################################################################################

class IngresoMetro(BaseClass): 
    def __init__(self, base_dir: str, file_name: str) -> None:
        super().__init__(base_dir, file_name)

    def wrangling_ingreso(self, df: DataFrame, date_col: str='fecha', add_cols: list=['tipo_ingreso'], **kwargs): 
        df.drop(['id','_id'], axis=1, inplace=True)
        # Las líneas del metro son columnas, crear sólo una columna indicando a qué línea se refiere
        df = df.melt(id_vars=[date_col]+add_cols, var_name='linea', value_name='ingreso')
        # Obtener f(X)=y "escalonando" los valores de días previos
        X, y = self.apply_multishift(df, **kwargs)
        return X,y

####################################################################################################################

class AfluenciaTransporte(BaseClass): 
    def __init__(self, base_dir: str, file_name: str) -> None: 
        super().__init__(base_dir, file_name)

    def wrangling_afluencia(self, df: DataFrame, value_col='afluencia_total_preliminar', **kwargs): 
        df.drop(['id','_id'], axis=1, inplace=True)
        # Eliminar "," que convierten el valor a texto
        df[value_col] = df[value_col].map(str).str.replace(',', '')
        df[[value_col]] = df[[value_col]].replace({'': 0}).astype(int)
        # Obtener f(X)=y "escalonando" los valores de días previos
        X, y = self.apply_multishift(df, **kwargs)
        return X,y
        
####################################################################################################################
class InterrupcionEmbarazo(BaseClass):
    def __init__(self, base_dir: str, file_name: str) -> None: 
        super().__init__(base_dir, file_name)

    def wrangling_ile(self, df: DataFrame, clean_dict: Dict, vars_dict: Dict, date_col: str='fingreso', export_result: bool=True, **kwargs):
        # Apartar temporalmente los registros sin fecha
        no_date = df[df[date_col].isnull()].copy()
        # Mantener sólo registros con fecha ...
        df = df[df[date_col].notnull()].copy()
        # Para crear su subconjunto de variables
        df = self.date_vars(df, date_col)
        # Y mantener la tabla original
        df = df.append(no_date)

        # Obtener las variables numéricas
        vars_num = list(set(
            clean_dict['vars_numbin']+
            list(clean_dict['vars_num'].keys())
        ))
        
        # Limpiar si hay texto de variables numéricas
        for col in vars_num:
            df[col] = df[col].map(self.clean_number).astype(float)
        
        # Diferencia entre la edad de la primera menstruación, edad de inicio de vida sexual activa y edad actual
        age_vars = (vars_dict['edad_1a_menst'], vars_dict['edad_vida_sex'], vars_dict['edad_actual'])
        age_dict = {}
        for i, prev_age in enumerate(age_vars):
            for j, next_age in enumerate(age_vars):
                # Sólo comparar ascendentemente
                if j>i:
                    age_col = f'{next_age}_vs_{prev_age}'
                    df[age_col] = (df[next_age]-df[prev_age]).map(lambda x: max(x,0))
                    # Crear rangos
                    orig_bins = qcut(df[age_col], q=4, retbins=True, duplicates='drop')[-1]
                    age_dict[age_col] = list(orig_bins[:-1])

        # Función para convertir float:1.0 --> str:'01'
        def two_char(n): return str(int(n)).zfill(2)

        # Crear rangos de variables numéricas
        for col, to_group in {**clean_dict['vars_num'], **age_dict}.items():
            # Encontrar el bin al cual el dato pertenece
            df[f'rango_{col}'] = cut(df[col], bins=[-1]+to_group+[1000])
            # Convertirlo a texto: [1.0 - 5.0] --> '01 a 05'
            df[f'rango_{col}'] = df[f'rango_{col}'].map(lambda x: two_char(x.left+1)+' a '+two_char(x.right) if x!=nan else nan)
            # Corregir algunas etiquetas como: '01 a 01' --> '01' y también '03 a 1000' --> '>= 03'
            last_cut = two_char(to_group[-1]+1)
            df[[f'rango_{col}']] = df[[f'rango_{col}']].replace({
                **{last_cut+' a 1000': '>= '+last_cut},
                **{two_char(x)+' a '+two_char(x): two_char(x) for x in to_group}
            })
            # No perder de vista los valores ausentes. "La falta de información también es información"
            df[f'rango_{col}'] = df[f'rango_{col}'].map(lambda x: nan if str(x)=='nan' else str(x))
        
        # Sólo saber si son mayores a 0 o no, tomar en cuenta que NaN > 0 --> False
        for col in clean_dict['vars_numbin']:
            df[col] = df[col].map(lambda x: '> 0' if x>0 else x)

        # Obtener las variables que serán binarias
        vars_cat = list(set(
            clean_dict['vars_first_word']+
            list(clean_dict['vars_cat'].keys())+
            clean_dict['vars_yes_no']+
            clean_dict['vars_clean_keep']+
            clean_dict['vars_just_clean']
        ))

        # Omitir acentos de variables categóricas
        for col in vars_cat:
            df[col] = df[col].map(self.clean_text)

        # Obtener la primer palabra
        for col in clean_dict['vars_first_word']:
            df[col] = df[col].str.split().str[0]

        # Agrupar categorías
        for col,to_group in clean_dict['vars_cat'].items():
            df[col] = df[col].map(to_group)

        # Lo que quedo vacío, marcar como "DESCONOCIDO"
        df = df.fillna('DESCONOCIDO').astype(str)

        # Comparar el método antes y después de la interrupción del embarazo
        df['antes_vs_despues'] = ['IGUAL' if x==y else 'DIFERENTE' for x,y in zip(df[vars_dict['metodo_antes']],df[vars_dict['metodo_despues']])]
        df['antes_vs_despues_detalle'] = 'antes: '+df[vars_dict['metodo_antes']]+', después: '+df[vars_dict['metodo_despues']]

        # Tal vez el usuario quiere exportar los resultados
        if export_result: self.export_csv(df, name_suffix='clean', index=False)

        # Lista de columnas para clustering posterior
        cluster_cols = (
            [x for x in vars_cat if x not in clean_dict['vars_just_clean']]+
            [f'rango_{col}' for col in clean_dict['vars_num'].keys()]+
            clean_dict['vars_numbin']+
            list(age_dict.keys())+
            ['antes_vs_despues','antes_vs_despues_detalle']
        )
        return df, cluster_cols

    def clustering_ile(self, df, cluster_cols, export_result=True):
        # Sólo tomar las columnas de interés para clustering
        X = df[cluster_cols].copy()
        # Obtener grupos por moda dado que todas las variables son categóricas
        X['cluster'], cluster_pipe = self.make_clusters(X, scaler=None, cluster_obj=KModes, init='Huang', n_jobs=-1)
        df = df.join(X[['cluster']])
        # Tal vez el usuario quiere exportar los resultados
        if export_result: self.export_csv(df, name_suffix='cluster', index=False)
        return df, cluster_pipe
        
