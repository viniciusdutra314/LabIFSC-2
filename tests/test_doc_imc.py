from LabIFSC2 import *

massa= Medida(75,0.1,'kg')
altura= Medida(1.75,0.01,'m')
imc=massa/altura**2
print(imc) #(2,45 ± 0,03)x10¹ kg/m²
print(imc.nominal) #24.5
print(imc.incerteza) #0.3


assert abs(imc.nominal-24.5)<1e-2
assert abs(imc.incerteza-0.28)<1e-1