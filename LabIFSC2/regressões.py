import numpy as np
from numpy.polynomial import Polynomial

from .strong_typing import obrigar_tipos
from .operacoes_em_arrays import nominais
from .matematica import aceitamedida, exp
from .medida import Medida
from .operacoes_em_arrays import arrayM

from collections.abc import Sequence
from numbers import Number
import string

class MPolinomio():
    @obrigar_tipos(in_class_function=True)
    def __init__(self,coeficientes:Sequence[Number | Medida]):
        self._coeficientes=[]
        for index,coef in enumerate(coeficientes):
            if not (isinstance(coef,Number) or isinstance(coef,Medida)):
                raise ValueError('Todos os coeficientes precisam ser números/Medidas')
            self._coeficientes.append(coef)
            setattr(self,string.ascii_lowercase[index],coef)
        self._grau=len(coeficientes)-1

    def __call__(self,x:Number):
       avaliar=lambda x:sum(coef*x**(self._grau-i) for i,coef in enumerate(self._coeficientes))
       if isinstance(x,Number):
           return avaliar(x)
       else:
        return np.vectorize(avaliar)(x) 
    
    def __iter__(self):
        return iter(self._coeficientes)
    def __str__(self):
        return f"MPolinomio(coefs={self._coeficientes},grau={self._grau})"

    def __repr__(self):
        return self.__str__()

def regressao_polinomial(x_dados:np.ndarray,y_dados:np.ndarray,
                         grau:int) -> MPolinomio:
    if len(x_dados)!=len(y_dados):
        raise ValueError("x_dados e y_dados não tem o mesmo tamanho") 
    if isinstance(x_dados[0],Medida):
        x_dados=nominais(x_dados)
    if isinstance(y_dados[0],Medida):
        y_dados=nominais(y_dados)
    p, cov = np.polyfit(x_dados, y_dados, grau, cov=True)
    medidas_coeficientes = [Medida(valor, np.sqrt(cov[i, i]),'') for i, valor in enumerate(p)]
    return MPolinomio(medidas_coeficientes)

def regressao_linear(x:np.ndarray,y:np.ndarray) -> MPolinomio:
    '''Encontre a melhor reta (minímos quadrados)
    
    y = a * x + b

    Args:
        x , y iterables (arrays,list,...) com floats ou Medidas
    Return : 
        Array com Coeficientes
    '''
    return regressao_polinomial(x,y,1)

def regressao_exponencial(x,y,base=np.exp(1),func=False):
    '''Encontre a melhor exponencial da forma
    \(y = a * e^{kx}\) para os dados x,y

    É possível mudar a base, por exemplo, 
    base=2 ira encontrar a melhor função

    \(y=a*2^{kx}\)

    Args:
        x (iterable): Medidas ou floats
        y (iterable): Medidas ou floats
        base (float): Base da exponencial
        func (bool): retorna uma função ao invés do fitting
    
    Returns:
        Array (nd.array):  Medidas a , k se func=False
        Função (callable): retorna y(x) se func=True
        
    '''
    x=nominais(x) ; y=nominais(y)
    assert np.all(y>0), 'Todos y precisam ser positivos para uma modelagem exponencial'
    assert base>1, 'Bases precisam ser maiores que 1'
    coefs=regressao_linear(x,np.log(y)/np.log(base))
    coefs[0]=exp(coefs[0])
    if not func: return coefs
    else:  return aceitamedida(lambda x:coefs[0]*np.power(coefs[1]*x,base))

def regressao_potencia(x, y,func=False) :
    '''Com um conjunto de dados x,y,
    esse método encontra a melhor lei de 
    potência da forma  \(y=A * (x^n)\)

    Args:
        x (iterable): Medidas ou números
        y (iterable): Medidas ou números
        func (bool): Retorna uma função ao invés do fitting
        
    Returns:
        Array (nd.array):  Medidas a , k se func=False
        Função (callable): retorna y(x) se func=True
    '''
    x=nominais(x) ; y=nominais(y)
    coefs=regressao_linear(np.log(x),np.log(y))
    coefs[0]=exp(coefs[0])
    if not func: return coefs
    else: return aceitamedida(lambda x:coefs[0]*x**coefs[1])
