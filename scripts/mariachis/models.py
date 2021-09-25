
import cufflinks as cf
from time import sleep
from pathlib import Path
from datetime import datetime
from typing import Dict, Union
from requests import get as get_req
from IPython.display import clear_output
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from pandas import DataFrame, read_csv, date_range, to_datetime

cf.go_offline()

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
        sleep(1.7)
        clear_output()
        return acum
    
    def __str__(self) -> str:
        return self.cool_print(f'Directorio:\t{self.base_dir}')
    
    def __len__(self) -> str:
        folders = len(str(self.base_dir).split('/'))-1
        self.cool_print(f"{folders} folders en {self.base_dir}")
        return folders

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
        except: self.cool_print(f'Error al obtener desde: {full_url}\nIntenta de nuevo!')

    def get_csv(self, file_name:str, **kwargs) -> DataFrame:
        '''
        Obtener tabla a partir de un archivo .csv
        '''
        df = read_csv(self.base_dir.joinpath(file_name), **kwargs)
        try: 
            df = read_csv(self.base_dir.joinpath(file_name), **kwargs)
            self.cool_print(f'Archivo con nombre "{file_name}" fue encontrado en {self.base_dir}')
            return df
        except: self.cool_print(f'Archivo con nombre "{file_name}" no fue encontrado en {self.base_dir}\nIntenta de nuevo!')
    
    def export_csv(self, df:DataFrame, file_name:str, **kwargs) -> None:
        df.to_csv(self.base_dir.joinpath(file_name), **kwargs)
        self.cool_print(f'Archivo: {file_name} fue exportado exitosamente en: {self.base_dir}')

    def api_export(self, export_kwargs:Dict={}, **api_kwargs) -> DataFrame:
        data = self.get_api(**api_kwargs)
        self.export_csv(df=data, **export_kwargs)
        return data

    def multishift(self, data, date_col, id_cols, shifts, **pivot_args):
        df = data.copy()
        #Make sure the col just have the date (without time)
        df[date_col] = df[date_col].map(to_datetime).dt.date
        #Merge all column names as a string
        id_col = ','.join(id_cols)
        #And as a column
        df[id_col] = df[id_cols].apply(lambda x:','.join(x.dropna().astype(str)),axis=1)
        #Drop any "id_col"-set that has a lower frequency than the max of the "shifts-list"
        freq = df[id_col].value_counts().to_frame()
        omit_idx = freq[freq[id_col]<=max(shifts)].index.to_list()
        if len(omit_idx)>0:
            df = df[~df[id_col].isin(omit_idx)].copy()
        #Change data structure to build the "shifting"
        df = df.pivot_table(index=[id_col,date_col],
                            **pivot_args,
                            fill_value=0)
        #Concatenate multiple columns if they are
        df.columns = ['_'.join([x for x in col]) if 
                    not isinstance(df.columns[0],str) #First element is not a string
                    else col for col in df.columns]
        #Bring the id_col for taking the set (unique values) in the next loop
        df = df.reset_index()
        #Each shift must be calculated at "id_col" level
        total = DataFrame()
        for row in set(df[id_col]):
            #Set the id_col as index (again) to call all the rows with that id_col
            df_id = df.set_index(id_col).loc[row,:]
            #All possible dates from the min to the max of the subset
            tot_dates = DataFrame(date_range(start=df_id[date_col].min(), 
                                                end=df_id[date_col].max()).date, 
                                    columns=[date_col])
            df_id = df_id.merge(tot_dates,on=date_col,how='right').fillna(0)
            cols = df_id.columns[1:]
            #Start the "shifting"
            aux = df_id.copy()
            for i in shifts:
                aux = aux.join(df_id.iloc[:,1:].shift(i).rename(columns={x:f'{x}_{str(i).zfill(2)}' 
                                                                        for x in cols}))
            aux[id_col] = row
            total = total.append(aux,ignore_index=True)
        return total.set_index(id_cols+[date_col])

    def train_reg_model(self, X, y, scaler=MinMaxScaler, model=LinearRegression):
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.77, random_state=22, shuffle=True)

        pipe_obj = Pipeline(steps=[('prep', scaler()),
                                    ('model', model(n_jobs=-1))])

        test_score = pipe_obj.fit(X_train,y_train).score(X_test, y_test)
        test_show = f"Score: {'{:.2%}'.format(test_score)}"
        train_score = pipe_obj.score(X_train,y_train)
        train_show = f"Training score: {'{:.2%}'.format(train_score)}"
        to_show = [test_show, train_show, "\nThese are the most influential variables:"]
        for x in to_show: self.cool_print(x)
        print(to_show)
        coef_var = DataFrame(zip(X.columns,pipe_obj[-1].coef_)).sort_values(1, ascending=False).reset_index(drop=True)
        return pipe_obj, coef_var

    def real_vs_est(self, X, y, model):
        df = X.join(DataFrame(y, index=X.index, columns=['real']))
        df['est'] = model.predict(X)
        return df[['real','est']]

####################################################################################################################

class IngresoMetro(BaseClass):
    def __init__(self, base_dir: str) -> None:
        super().__init__(base_dir)

    def im_data_wrangling(self, all_shifts:Union[list,tuple,range]=range(1,22), api:bool=False, api_export:bool=False, export_shifted:bool=False, date_col:str='fecha', add_cols:list[str]=['tipo_ingreso'], to_drop:list[str]=['id','_id'], **kwargs):
        if api: 
            if api_export: df = self.api_export(**kwargs)
            else: df = self.get_api(**kwargs)
        else: df = self.get_csv(**kwargs)

        df.drop(columns=to_drop, inplace=True)
        df = df.melt(id_vars=[date_col]+add_cols, var_name='linea', value_name='ingreso')
        df = self.multishift(df, date_col=date_col, id_cols=['linea'], shifts=all_shifts, aggfunc={'ingreso':'sum'})
        df.dropna(inplace=True)
        
        if export_shifted: self.export_csv(df, 'ingreso_metro_shifted.csv')

        prev = df.head(1).filter(regex='_\d+').columns.tolist()
        actual = [x for x in df.columns if x not in prev]
        X = df[prev].copy()
        y = df[actual].sum(axis=1).values

        return X,y

    def ingreso_pred(self, X, y, model, from_year:int, to_year:int=datetime.now().year):
        pred = self.real_vs_est(X, y, model).reset_index()

        pred['year'] = to_datetime(pred['fecha']).dt.year
        df = pred[(pred['year']>=from_year)&(pred['year']<=to_year)].copy()
        df.drop(columns='year', inplace=True)
        df.set_index('linea', inplace=True)
        
        for x in set(df.index):
            df_id = df.loc[x,:].reset_index(drop=True).set_index('fecha')
            df_id.iplot(title=x)