# Control de datos
from time import sleep
from typing import Dict
from pathlib import Path
from pickle import dump as save_pkl
from requests import get as get_req
from IPython.display import clear_output, display

# Ingeniería de variables
from re import sub, UNICODE
from numpy import nan, array
from datetime import datetime
from unicodedata import normalize
from string import ascii_uppercase
from difflib import get_close_matches
from geopandas import GeoDataFrame, GeoSeries, points_from_xy
from pandas import DataFrame, read_csv, to_datetime, options, date_range
options.mode.chained_assignment = None

# Modelos
from sklearn.pipeline import Pipeline
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Gráficas
import cufflinks as cf
cf.go_offline()

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

    def cool_print(self, text: str, sleep_time: float=0.0, by_word: bool=False) -> None: 
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
            self.cool_print(f'Archivo con nombre {self.file_name}.csv fue encontrado en\n{self.base_dir}\nCon {df_shape[0]} renglones y {df_shape[-1]} columnas')
            return df
        except: self.cool_print(f'No se encontró el archivo con nombre {self.file_name}.csv en {self.base_dir}\nSi el archivo csv existe, seguramente tiene un encoding y/o separador diferente a "utf-8" y "," respectivamente\nIntenta de nuevo!')
    
    def export_csv(self, df: DataFrame, name_suffix=None, **kwargs) -> None: 
        '''
        Exportar un archivo en formato csv
        '''
        export_name = f'{self.file_name}.csv' if name_suffix==None else f'{self.file_name}_{name_suffix}.csv'
        df.to_csv(self.base_dir.joinpath(export_name), **kwargs)
        self.cool_print(f'Archivo: {export_name} fue exportado exitosamente en:\n{self.base_dir}')

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
        self.cool_print(f'{len(to_remove)} renglones con {"{:.1%}".format(thres)}% o más de valores nulos fueron eliminados')
        return df

    def clean_number(self, text: str) -> str: 
        '''
        Limpieza numérica
        '''
        # Omitir todo lo que no sea número o "."
        clean = sub('[^0-9\.]', '', str(text))
        # Si el registro estaba vacío, indicar nulo
        if clean in ('','nan'): clean = nan
        return clean

    def clean_text(self, text: str, pattern: str="[^a-zA-Z0-9\s]", lower: bool=False) -> str: 
        '''
        Limpieza de texto
        '''
        # Reemplazar acentos: áàäâã --> a
        clean = normalize('NFD', str(text).replace('\n', ' \n ')).encode('ascii', 'ignore')
        # Omitir caracteres especiales !"#$%&/()=...
        clean = sub(pattern, ' ', clean.decode('utf-8'), flags=UNICODE)
        # Mantener sólo un espacio
        clean = sub(r'\s{2,}', ' ', clean.strip())
        # Minúsculas si el parámetro lo indica
        if lower: clean = clean.lower()
        # Si el registro estaba vacío, indicar nulo
        if clean in ('','nan'): clean = nan
        return clean

    def choose_correct(self, df: DataFrame, col: str, correct_list: list, fill_value: str='DESCONOCIDO', **kwargs) -> DataFrame:
        '''
        Recibe un DataFrame y una lista de posibilidades, especificando la columna a revisar
        elige la opción que más se parezca a alguna de las posibilidades
        '''
        # Aplicar limpieza de texto a la lista de posibilidades
        correct_clean = list(map(lambda x: self.clean_text(x, lower=True), correct_list))
        # Hacer un diccionario de posibilidades limpias y las originales recibidas
        correct_dict = dict(zip(correct_clean, correct_list))
        # Aplicar la limpieza a la columna especificada
        df[f'{col}_correct'] = df[col].map(lambda x: self.clean_text(x,lower=True))
        # Encontrar las posibilidades más parecidas
        df[f'{col}_correct'] = df[f'{col}_correct'].map(lambda x: get_close_matches(x, correct_clean, **kwargs))
        # Si existen parecidas, traer la primera opción que es la más parecida
        df[f'{col}_correct'] = df[f'{col}_correct'].map(lambda x: x[0] if isinstance(x,list) and len(x)>0 else nan)
        # Regresar del texto limpio a la posibilidad original, lo no encontrado se llena con "fill_value"
        df[f'{col}_correct'] = df[f'{col}_correct'].map(correct_dict).fillna(fill_value)
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
        # Mantener sólo la fecha
        df[date_col] = df[date_col].dt.date
        return df

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
        cluster_dict = dict(zip(range(n_clusters), ascii_uppercase[:n_clusters]))
        # Aplicar diccionario
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

    def geo_polygon(self, df: DataFrame, crs_code: str='EPSG:6372', just_geodf: bool=False, geom_col: str=None, coord_cols: tuple=('lat','lon'), group_by: str=None, create_geoshape: bool=False) -> DataFrame:
        '''
        Crea el polígono desde un DataFrame ya sea con una columna de "geometry" o dos columnas: latitud y otra de longitud,
        puede devolver sólo la transformación o agrupar a un nivel de geolocalización mayor
        '''
        # Omitir los registros nulos del nivel de geolocalización al que se va a agrupar
        if group_by != None: df = df[df[group_by].fillna('').astype(str).str.len()>0].copy()
        else: pass
        # Establecer la columna de geolocalización, ya sean las coordenadas o la columna de polígono
        geom = points_from_xy(df[coord_cols[-1]], df[coord_cols[0]]) if geom_col==None else geom_col
        # Crear GeoDataFrame
        gdf = GeoDataFrame(df, crs=crs_code, geometry=geom)
        if create_geoshape: 
            # Función auxiliar para extraer el formato que <kepler.gl> puede leer correctamente
            def extract_geoshape(x): return GeoSeries([x]).__geo_interface__['features'][0]['geometry']
            # Aplicar dicha función a geometry para crear la nueva columna
            gdf['geo_shape'] = df['geometry'].map(extract_geoshape)
        # Si sólo se desea la transformación
        if just_geodf: return gdf
        # O si se desdea agrupar a un nivel de geolocalización superior
        df = gdf.dissolve(by=group_by)
        # Asegurarse de tener un polígono, porque probablemente el nivel de agregación resulta en una o dos coordenadas
        df['geometry'] = df['geometry'].buffer(0.05)
        # El nivel de agregación queda como índice, pasar a columna
        df.reset_index(inplace=True)
        return df
    
    def geo_metrics(self, df: GeoDataFrame, metrics: list=['area','boundary','centroid','convex_hull']) -> GeoDataFrame:
        '''
        Obtiene las métricas más importantes de geolocalización
        '''
        # Obtener su área, límite, punto central y el polígono que contiene a cada localidad
        for metric in metrics:
            df[metric] = eval(f'df.{metric}')
        # Obtener coordenadas del centroide
        coor = df['centroid'].map(lambda x: list(x.coords)[0])
        # Establecer una columna para la latitud y otra de longitud
        df[['centroid_lat', 'centroid_lon']] = DataFrame(coor.tolist(), index=df.index)
        return df

    def multishift(self, df: DataFrame, id_cols: list, date_col: str='fecha', shifts: list=range(1,22), rem_sum_zero: bool=True,**pivot_args): 
        '''
        Escalona los valores para crear una Tabla Analítica de Datos con formato: valor hoy, valor 1 día antes, dos días antes, etc
        '''
        # Asegurarse que tiene solamente la fecha
        df[date_col] = df[date_col].map(to_datetime).dt.date

        # Sólo una columna que servirá como ID
        id_col = ','.join(id_cols)
        df[id_col] = df[id_cols].astype(str).apply(','.join, axis=1)

        # Omitir aquellos IDs con menor frequencia que el máximo valor de "shifts", porque inevitablemente tendrán shift vacíos
        freq = df[id_col].value_counts().to_frame()
        omit_idx = freq[freq[id_col]<=max(shifts)].index.to_list()
        if len(omit_idx)>0: 
            df = df[~df[id_col].isin(omit_idx)].copy()
        
        # Columna auxiliar para conteo de registros
        df['n'] = 1

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
            total = total.append(aux, ignore_index=True)
        total.set_index(id_cols+[date_col], inplace=True)
        if rem_sum_zero:
            total['sum'] = total.sum(axis=1)
            total = total[total['sum']>0].drop('sum', axis=1)
        return total

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

    def train_reg_model(self, X: DataFrame, y: array, scaler=RobustScaler, model=LinearRegression, **kwargs): 
        '''
        Escala y entrena un modelo, devuelve el score, el objeto tipo Pipeline y la relevancia de cada variable
        '''
        # Conjunto de entrenamiento y de test
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.85, random_state=7, shuffle=True)

        # Define los pasos del flujo
        pipe_obj = Pipeline(steps=[('prep', scaler()), ('model', model(**kwargs))])

        # Entrena y guarda el score en test
        test_score = pipe_obj.fit(X_train,y_train).score(X_test, y_test)
        # Guarda el score en train, para revisar sobreajuste
        train_score = pipe_obj.score(X_train,y_train)

        # Imprime los scores
        self.cool_print(f"Score: {'{:.2%}'.format(test_score)}\nTraining score: {'{:.2%}'.format(train_score)}")

        # Elige la forma de obtener las variables más representativas
        try: most_important_features = pipe_obj[-1].coef_ 
        except: 
            try: most_important_features = pipe_obj[-1].feature_importances_
            except: most_important_features = [0]*len(X.columns)
        # Las ordena descendentemente
        coef_var = DataFrame(zip(X.columns, most_important_features)).sort_values(1, ascending=False).reset_index(drop=True)
        return pipe_obj, (test_score,train_score), coef_var

    def train_chunk(self, X: DataFrame, y: array, model, id_cols: list, to_drop: list, **kwargs) -> tuple:
        '''
        Entrena un modelo diferente para cada valor único de la combinación de "id_cols"
        '''
        # Omitir columnas innecesarias
        df = X.reset_index().drop(to_drop, axis=1)
        # Sólo una columna que servirá como ID
        id_col = ','.join(id_cols)
        df[id_col] = df[id_cols].astype(str).apply(','.join, axis=1)
        # Unir el vector "y" con la matriz "X"
        df['real'] = y
        # Diccionarios para los resultados de cada modelo
        model_dict, score_dict, coef_dict = {}, {}, {}
        # Para cada valor único de "id_col"
        for id_x in set(df[id_col]):
            # Filtrar el subconjunto de datos pertenecientes a dicho valor único
            sub_df = df.set_index(id_col).loc[id_x,:].copy()
            # Dividir nuevamente la matriz "X"
            sub_X = sub_df.iloc[:,:-1]
            # Y el vector "y"
            sub_y = sub_df.iloc[:,-1].values
            self.cool_print(f'Para {id_x}:')
            # Entrena el modelo con los argumentos que se proporcionen y devuelve 3 objetos: modelo, tuple de scores (test,train) y los coeficientes
            model_dict[f'{id_x}'], score_dict[f'{id_x}'], coef_dict[f'{id_x}'] = self.train_reg_model(sub_X, sub_y, model=model, **kwargs)
        # Devuelve el diccionario, una llave para cada modelo
        return model_dict, score_dict, coef_dict

    def show_scores(self, score_dict: Dict) -> None:
        '''
        Del diccionario de scores recibido en el método anterior, imprime los scores de cada modelo ordenado descendentemente por test 
        '''
        to_display = DataFrame(score_dict, index=['Test_score','Train_score']).T.sort_values('Test_score', ascending=False)
        display(to_display.style.format("{:.1%}").background_gradient('Blues', axis=0))

    def real_vs_est(self, X: DataFrame, y: array, model, omit_zero: bool=True) -> DataFrame: 
        # De todo el conjunto de datos...
        df = X.join(DataFrame(y, index=X.index, columns=['real']))
        # Predice el el valor...
        df['estimado'] = model.predict(X)
        # Si el parámetro lo indica, reemplaza negativos por 0
        if omit_zero: df['estimado'] = df['estimado'].map(lambda x: max(0,x))
        # Y devuelve sólo las columna real y la estimada
        return df[['real','estimado']]

    def plot_real_vs_est(self, X: DataFrame, y: array, model, id_col: str, date_col: str, from_year: int=1900, to_year: int=datetime.now().year): 
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

    def multiplot(self, X: DataFrame, y: array, models_dict, id_cols: list, date_col='fingreso', **kwargs):
        model_cols = X.columns
        # Omitir columnas innecesarias
        df = X.reset_index()
        # Sólo una columna que servirá como ID
        id_col = ','.join(id_cols)
        df[id_col] = df[id_cols].astype(str).apply(','.join, axis=1)
        # Unir el vector "y" con la matriz "X"
        df['real'] = y
        # Para cada valor único de "id_col"
        for id_x, model_x in models_dict.items():
            # Filtrar el subconjunto de datos pertenecientes a dicho valor único
            sub_df = df.set_index(id_col).loc[id_x,:].copy()
            sub_df = sub_df.reset_index().set_index([id_col,date_col])
            # Dividir nuevamente la matriz "X"
            sub_X = sub_df.iloc[:,:-1]
            # Y el vector "y"
            sub_y = sub_df.iloc[:,-1].values
            # Mostrar el comportamiento de predicción vs real para cada modelo
            self.plot_real_vs_est(sub_X[model_cols], sub_y, model=model_x, id_col=id_col, date_col=date_col, **kwargs)

    def save_model(self, model, name: str) -> None:
        # Guarda el pickle con extensión ".xz" para comprimirlo
        with open(self.base_dir.joinpath(f'{name}.xz'), 'wb') as f:
            # Como diccionario para conocer su nombre
            save_pkl({name:model}, f)
        # Confirma que el archivo fue guardado exitosamente
        self.cool_print(f'El modelo {name}.xz fue guardado existosamente en:\n{self.base_dir}')