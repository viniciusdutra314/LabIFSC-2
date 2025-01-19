import LabIFSC2 as lab

mu_0=lab.constantes.vacuum_mag_permeability
N=100
L=lab.Medida(30,0.1,'cm')
I=lab.Medida(2,0.01,'A')
B=mu_0*N*I/L
print(f"{B:mTesla}") #(8,38 ± 0,05)x10⁻¹ mT

assert f"{B:mTesla}"=="(8,38 ± 0,05)x10⁻¹ mT"