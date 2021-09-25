class PersonClass:
    def __init__(self, param_name, age=22) -> None:
        self.name = param_name
        self.age = age

    def __str__(self) -> str:
        return f'Nombre es {self.name} con {self.age} años'

    def add_years(self, n):
        return self.age+n

    def call_add_years(self):
        return f'Yo, {self.name} ahora tengo {self.add_years(n=100)}'

class StudentClass(PersonClass):
    def __init__(self, param_name:str, age:int=22, occupation:str='nini') -> None:
        super().__init__(param_name, age=age)
        self.ocup = occupation

    def get_occup(self) -> str:
        return self.ocup+' is the occupation!'

sc = StudentClass(param_name='Yetol', age=25)
print(sc.get_occup())