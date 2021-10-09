# Herencia de atributos y métodos
from ._base import BaseClass

# Ingeniería de variables
from numpy import nan
from typing import Dict
from pandas import DataFrame, cut, qcut

# Modelos
from kmodes.kmodes import KModes

class InterrupcionEmbarazo(BaseClass):
    def __init__(self, base_dir: str, file_name: str) -> None: 
        '''
        Hereda los atributos y métodos de la clase base
        '''
        super().__init__(base_dir, file_name)

    def wrangling_ile(self, df: DataFrame, clean_dict: Dict, vars_dict: Dict, date_col: str='fingreso', export_result: bool=True, **kwargs) -> tuple:
        '''
        Recibe un DataFrame y ejecuta la limpieza e ingeniería de variables según los diccionarios "clean_dict" y "vars_dict" proporcionados
        '''
        # Omitir renglones con todas las variables vacías
        df = self.rem_nan_rows(df, thres=1)
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
        if export_result: self.export_csv(df, name_suffix='limpio', index=False)

        # Lista de columnas para clustering posterior
        cluster_cols = (
            [x for x in vars_cat if x not in clean_dict['vars_just_clean']]+
            [f'rango_{col}' for col in clean_dict['vars_num'].keys()]+
            clean_dict['vars_numbin']+
            list(age_dict.keys())+
            ['antes_vs_despues','antes_vs_despues_detalle']
        )
        return df, sorted(cluster_cols)

    def clustering_ile(self, df: DataFrame, cluster_cols: list, export_result: bool=True, **kwargs) -> tuple:
        '''
        Crear grupos con los datos de ILE
        '''
        # Sólo tomar las columnas de interés para clustering
        X = df[cluster_cols].copy()
        # Obtener grupos por moda dado que todas las variables son categóricas
        X['cluster'], cluster_pipe = self.make_clusters(X, scaler=None, cluster_obj=KModes, init='Huang', n_jobs=-1, **kwargs)
        df = df.join(X[['cluster']])
        return df, cluster_pipe
        