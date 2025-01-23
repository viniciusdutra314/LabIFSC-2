import numpy as np
import pytest

import LabIFSC2 as lab


def test_initialization():
    coeficientes = lab.linspaceM(1,3,3,'',0)
    with pytest.raises(TypeError):
        lab._regressões.MPolinomio(np.array([1, 2, 3]))
    polinomio=lab._regressões.MPolinomio(coeficientes)
    assert np.array_equal(polinomio._coeficientes,coeficientes)
    assert polinomio.grau == 2
    assert polinomio.a.nominal("") == 1
    assert polinomio.b.nominal("") == 2
    assert polinomio.c.nominal("") == 3

def test_call():
    coeficientes = lab.linspaceM(1,3,3,'',0)
    polinomio=lab._regressões.MPolinomio(coeficientes)
    with pytest.raises(TypeError):
        polinomio(0)
    pontos=lab.linspaceM(0,2,3,'',0)
    assert np.isclose(polinomio.amostrar(pontos[0],''), 3)
    assert np.isclose(polinomio.amostrar(pontos[1],''),6)
    assert np.isclose(polinomio.amostrar(pontos[2],''), 11)



def test_unpacking():
    coeficientes = lab.linspaceM(1,3,3,'',0)
    polinomio = lab._regressões.MPolinomio(coeficientes)
    a, b, c = polinomio
    assert a.nominal("") == 1
    assert b.nominal("") == 2
    assert c.nominal("") == 3




