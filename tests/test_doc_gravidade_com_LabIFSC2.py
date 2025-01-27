from LabIFSC2 import *


def test_doc_gravidade_com_LabIFSC2():
    #g=4π²L/T²
    pi=constantes.pi
    L=Medida(15,'cm',0.1)
    T=Medida(780,'ms',1)
    gravidade=(4*pi**2)*L/T**2
    print(f"{gravidade:si}") #(9,73 ± 0,07) m/s²
    print(f"{gravidade:si_latex}") 
    '''(9,73 \, \pm \, 0,07) \, 
    \frac{\mathrm{m}}{\mathrm{s}^{2}}'''

    assert f"{gravidade:si}" == "(9,73 ± 0,07) m/s²"
    assert f"{gravidade:si_latex}" ==r"(9,73 \, \pm \, 0,07) \, \frac{\mathrm{m}}{\mathrm{s}^{2}}"
