import matplotlib.pyplot as plt

from LabIFSC2 import *

campo_magnético=arrayM([250,150,110,90,70,60,55,40,25,20],1,'muT')
distancias=linspaceM(1,10,10,0.5,'cm') 

unidade_x='cm'
unidade_y='muT'

plt.style.use('ggplot')
plt.errorbar(x=nominais(distancias,unidade_x),
             y=nominais(campo_magnético,unidade_y),
             xerr=incertezas(distancias,unidade_x),
             yerr=incertezas(campo_magnético,unidade_y),
             fmt='o')

plt.xlabel(f"Distancia ({unidade_x})")
plt.ylabel(f"Campo magnético ({unidade_y})")
plt.savefig('docs/images/graficos_scatter.jpg',dpi=300) 
plt.cla()