from collections.abc import Callable
from numbers import Number
from typing import Callable
from functools import total_ordering


import numpy as np
from .strong_typing import obrigar_tipos
from .formatações import *
from enum import Enum
from . import ureg
from pint import Quantity

def montecarlo(func : Callable, 
               *parametros : Number,N:int=100_000) -> 'Medida':
    x_samples=np.empty(len(parametros),dtype=Quantity)
    for index,parametro in enumerate(parametros):
        if not (len(parametro._histograma)):
            x_samples[index]=np.random.normal(parametro.nominal,
                                              parametro.incerteza,size=N)*parametro._nominal.units
        else:
            x_samples[index]=parametro._histograma
  
    histograma=func(*x_samples)
    mean=np.mean(histograma)
    std=np.std(histograma,mean=mean)
    resultado=Medida(mean.magnitude,std.magnitude,str(histograma.units))
    resultado._histograma=histograma
    resultado._gaussiana=False
    return resultado

class Medida:
    @obrigar_tipos(in_class_function=True)
    def __init__(self,nominal:Number,incerteza : Number,
                 unidade : str ):
        """
        Inicializa uma instância da classe Medida com um valor nominal, incerteza e unidade.
        Valor numérico se entende como qualquer objeto que possa interagir normalmente com floats,

        Parâmetros:
            - nominal: Um valor numérico que representa o valor nominal da medida.
            - incerteza: Um valor numérico que representa a incerteza associada à medida.
            - unidade: Uma string que descreve a unidade da medida.

        Raises:
            - TypeError: Se o nominal ou incerteza não puderem ser convertidos para um número.
            - TypeError: A unidade precisa ser uma string
        """
        if incerteza<0: raise ValueError("Incerteza não pode ser negativa")
        self._nominal= ureg.Quantity(nominal,unidade).to_reduced_units()
        self._incerteza=ureg.Quantity(incerteza,unidade).to_reduced_units()
        self._gaussiana=True
        self._histograma=np.array([])
        self._nominal.ito_reduced_units


    def _erro_por_mudar_atributo(self):
        raise PermissionError("Para garantir a integridade da Medida realizada \
o LabIFSC2 não permite a alteração direta de nominal, incerteza, unidade (somente leitura).\
Caso precise de uma nova Medida, crie outra com o \
construtor padrão Medida(nominal, incerteza, unidade)")

    @property
    def nominal(self) -> Number: return self._nominal.magnitude
    
    @nominal.setter
    def nominal(self, value):self._erro_por_mudar_atributo()
    
    @nominal.deleter
    def nominal(self): self._erro_por_mudar_atributo()

    @property
    def incerteza(self) -> Number: return self._incerteza.magnitude
    
    @incerteza.setter
    def incerteza(self, value): self._erro_por_mudar_atributo()
    
    @incerteza.deleter
    def incerteza(self): self._erro_por_mudar_atributo()

    @property
    def unidade(self) -> str: 
        return str(self._nominal.units)
    
    @unidade.setter
    def unidade(self, value): self._erro_por_mudar_atributo()
    
    @unidade.deleter
    def unidade(self): self._erro_por_mudar_atributo()

    def converter_para_si(self):
        self._nominal.ito_base_units()
        self._incerteza.ito_base_units()
        self._histograma.ito_base_units()

    def __eq__(self,outro):
        raise TypeError("Como a comparação entre Medidas pode gerar três resultados \
diferentes: iguais, diferentes, ou inconclusivo, optamos por fazer uma função separada \
chamada compara_medidas(x:Medida,y:Medida) -> [Iguais | Diferentes | Inconclusivo], por favor \
não use !=,==,<=,<,>,>= diretamente com Medidas")
    __neq__=__lt__=__le__=__gt__=__ge__=__eq__
        

    def __str__(self) -> str:
        incerteza_magnitude=int(np.floor(np.log10(self.incerteza)))
        incerteza_arredonda=round(self.incerteza,-incerteza_magnitude+1)
        incerteza_str = f"{incerteza_arredonda:.1e}"
        significant_digit_position = incerteza_str.find('e')
        significant_digits = int(incerteza_str[significant_digit_position + 1:])
        
        # Truncate nominal to the same number of significant digits
        nominal_truncated = round(self.nominal, -significant_digits)
        incerteza_truncated = round(self.incerteza, -significant_digits)
        # Get the pretty unit string
        unidade_bonita = f"{self._nominal:~P}".split()
        if len(unidade_bonita) == 1: unidade_bonita=''
        if len(unidade_bonita) == 2: unidade_bonita=unidade_bonita[1]

        return f"({nominal_truncated}±{incerteza_truncated}) {unidade_bonita}"
    
    def __repr__(self) -> str:
        return f"Medida({self.nominal=},{self.incerteza=},'{self.unidade=}')"

    def converter_para(self,unidade:str):
        self._nominal.ito(unidade)
        self._incerteza.ito(unidade)

    def _adicao_subtracao(self,outro: 'Medida',positivo:bool) -> 'Medida':
        if self._nominal.is_compatible_with(outro._nominal):
            if self is outro: 
                return 2*self if positivo else Medida(0,0,self.unidade)

            elif (self._gaussiana and outro._gaussiana):
                #Como existe solução analítica da soma/subtração entre duas gaussianas
                #iremos usar esse resultado para otimizar o código
                if positivo: media=self._nominal+outro._nominal
                else: media=self._nominal-outro._nominal
                desvio_padrao=(self._incerteza**2 + outro._incerteza**2)**(1/2)
                desvio_padrao.ito(media.units)
                return Medida(media.magnitude,desvio_padrao.magnitude,
                              str(media.units))
            else:
                if positivo: return montecarlo(lambda x,y: x+y,self,outro)
                else : return montecarlo(lambda x,y: x-y,self,outro)
        else:
            raise ValueError(f"A soma/subtração entre {self._nominal.dimensionality} e \
{outro._nominal.dimensionality} não é possível")

    def __add__(self,outro) -> 'Medida':
        return self._adicao_subtracao(outro,True)
    def __sub__(self,outro)-> 'Medida':
        return self._adicao_subtracao(outro,False)
    
    def __mul__(self,outro)-> 'Medida':
        if self is outro: return montecarlo(lambda x: x**2,self)
        elif isinstance(outro,Medida):
            return montecarlo(lambda x,y: x*y,self,outro)
        elif isinstance(outro,Number):
            resultado=Medida(self.nominal*outro,abs(self.incerteza*outro),self.unidade)
            resultado._histograma=self._histograma*outro
            return resultado
    
    def __truediv__(self, outro) -> 'Medida':
        if self is outro: return Medida(1,0,self.unidade)
        elif isinstance(outro,Number):
            resultado=Medida(self.nominal/outro,(self.incerteza/abs(outro)),self.unidade)
            resultado._histograma=self._histograma/outro
            return resultado
        elif isinstance(outro,Medida):
            return montecarlo(lambda x,y: x/y,self,outro)
        
    def __rtruediv__(self,outro) -> 'Medida':
        if isinstance(outro,Number):
            return montecarlo(lambda x: outro/x,self)
        raise ValueError(f"Operação entre {type(self)} e {type(outro)} não suportada")
    
    def __pow__(self,outro) -> 'Medida':
        if isinstance(outro,Number):
           return montecarlo(lambda x: np.pow(x,outro),self)
        elif isinstance(outro,Medida):
            return montecarlo(lambda x,y: x**y,self,outro)


    __radd__=__add__
    __rsub__=__sub__
    __rmul__=__mul__
    __rpow__=__pow__

    def __abs__(self) -> 'Medida':
        return Medida(abs(self.nominal),self.incerteza,self.unidade)
    
    def __neg__(self) -> 'Medida': 
        resultado=Medida(-self.nominal,self.incerteza,self.unidade)
        resultado._histograma=-self._histograma
        return resultado
        
    def __pos__(self) -> 'Medida': 
        resultado=Medida(self.nominal,self.incerteza,self.unidade)
        resultado._histograma=self._histograma
        return resultado
    

    def probabilidade(self,a:Number,b:Number) -> Number:
        ''' Retorna a probabilidade que a Medida
        esteja entre [a,b] usando o histograma como
        referencia

        Args:
            `a` (Number): Extremo inferior
            `b`(Number): Extremo superior

        Returns:
            `probabilidade`: (Number) probabilidade de estar entre [a,b]
        
        Raises:
            ValueError: Se `a` for maior que `b`
        '''

        if a>b: raise ValueError("a deve ser menor que b")

        if not len(self._histograma):
            self._histograma=np.random.normal(self.nominal,
                        self.incerteza,10_000) #hard coded 
            
        return np.mean((self._histograma >= a) & (self._histograma <= b))



class Comparacao(Enum):
    EQUIVALENTES = "iguais"
    DIFERENTES = "diferentes"
    INCONCLUSIVO = "inconclusivo"

@obrigar_tipos()
def comparar_medidas(medida1: Medida, medida2: Medida, 
    sigmas_customizados: list[Number] = [2, 3]) -> Comparacao:
    """
    Compara duas medidas considerando suas incertezas e retorna o resultado da comparação.

    Args:
        `medida1` (Medida) A primeira medida a ser comparada.

        `medida2` (Medida) A segunda medida a ser comparada.

        `sigmas_customizados` (list[Number], opcional): Lista contendo dois valores sigma. 
            O primeiro sigma é usado para determinar se as medidas são iguais. 
            O segundo sigma é usado para determinar se as medidas são diferentes. 
            O valor padrão é [2, 3].
    
    Returns:
        `Comparacao` (Enum):
        - `Comparacao.IGUAIS`: Se as medidas são consideradas iguais.
        - `Comparacao.DIFERENTES`: Se as medidas são consideradas diferentes.
        - `Comparacao.INCONCLUSIVO`: Se a comparação é inconclusiva.
        
    
    Raises:
        ValueError: Se o sigma para serem consideradas iguais for maior que o sigma para serem diferentes.
    """
                     
    diferenca_nominal=abs(medida1._nominal-medida2._nominal)
    soma_incertezas=medida1._incerteza+medida2._incerteza
    sigma_igual=sigmas_customizados[0]
    sigma_diferente=sigmas_customizados[1]
    if sigma_igual>sigma_diferente:
        raise ValueError("Sigma para serem consideradas iguais é maior que o sigma \
para serem diferentes")
    
    if diferenca_nominal<sigma_igual*soma_incertezas:
        return Comparacao.EQUIVALENTES
    elif diferenca_nominal>sigma_diferente*soma_incertezas:
        return Comparacao.DIFERENTES
    else:
        return Comparacao.INCONCLUSIVO
