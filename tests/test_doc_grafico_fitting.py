import time

import matplotlib.pyplot as plt
import numpy as np

from LabIFSC2 import *

campo_magnético=arrayM([210,90,70,54,39,32,33,27,22,20],1,'muT')
distancias=linspaceM(1,10,10,0.01,'cm') 

unidade_x='cm'
unidade_y='muT'

regressao=regressao_potencia(distancias,campo_magnético)
print(regressao) 
#MLeiDePotencia(a=(2,0 ± 0,1)x10² cm⁰⋅⁹⁸⁶³⁵⁵·µT, b=(-9,9 ± 0,3)x10⁻¹ )
plt.style.use('ggplot')
plt.errorbar(x=nominais(distancias,unidade_x),
             y=nominais(campo_magnético,unidade_y),
             xerr=incertezas(distancias,unidade_x),
             yerr=incertezas(campo_magnético,unidade_y),
             fmt='o',label='Dados experimentais',color='red')

x=np.linspace(1,10,100)
tempo=time.time()
plt.plot(x,regressao.amostrar(x,unidade_x,unidade_y),
         color='blue',label="Curva teórica")
print(time.time()-tempo)
tempo=time.time()
plt.fill_between(x=x,
                 y1=regressao.curva_min(),
                 y2=regressao.curva_max(),
                 color='blue',alpha=0.3)
print(time.time()-tempo)
plt.legend()
plt.savefig('docs/images/graficos_fitting.jpg',dpi=300) 
plt.cla()