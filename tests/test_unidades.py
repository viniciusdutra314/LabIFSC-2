import numpy as np
import pint
import pytest

import LabIFSC2 as lab


def test_dimensoes_incompativeis():
    x=lab.Medida(10,1,"m")
    y=lab.Medida(10,1,"s")
    with pytest.raises(ValueError):
        x+y
    z=lab.Medida(55,0.1,'cm')
    w=x+z
    assert np.isclose(w.nominal('m'),10.55)
    assert np.isclose(w.incerteza('m'),1)

def test_dimensoes_multiplicacao():
    x=lab.Medida(53,1,"C")
    y=lab.Medida(10,0.1,'mC')
    z=3*x+y
    assert str((3*x)._nominal.units)=='coulomb'
    assert np.isclose(z.nominal("coulomb"),159.01) 
    assert str(z._nominal.units)=='coulomb'

def test_trignometria():
    x = lab.Medida(45, 1, "m")
    with pytest.raises(pint.errors.DimensionalityError):
        np.sin(x)
    with pytest.raises(pint.errors.DimensionalityError):
        np.cos(x)
    with pytest.raises(pint.errors.DimensionalityError):
        np.tan(x)
    x = lab.Medida(45, 1, "rad")
    np.sin(x)
    np.cos(x)
    np.tan(x)

def test_angulos_notaveis():
    x=np.sin(lab.Medida(45,0.01,'degree'))
    y=np.cos(lab.Medida(60,0.01,'degree'))
    assert np.isclose(x.nominal(''),1/np.sqrt(2),rtol=1e-4)
    assert np.isclose(y.nominal(""),1/2,rtol=1e-4)

def test_exponencial_unidade():
    x=lab.Medida(1,0.01,'m')
    with pytest.raises(pint.errors.DimensionalityError):
        np.exp(x)
    with pytest.raises(pint.errors.DimensionalityError):
        np.log(x)

def test_soma_graus():
    theta=lab.Medida(45,0.01,'degree')
    theta2=lab.Medida(1,0.01,'radian')
    theta_soma=theta+theta2
    assert np.isclose(theta_soma.nominal('radian'),1+0.785398,rtol=1e-2)
    assert np.isclose(theta_soma.nominal('degree'),45+57.29,rtol=1e-2)


def test_converter_array():
    x_dados=lab.arrayM([1,2,3,4,5],0.01,'m/s')
    for i in range(len(x_dados)):
        assert np.isclose(x_dados[i].nominal('km/h'),(i+1)*3.6)

    x_dados=lab.arrayM([1,2,3,4,5],0.01,'km/h')
    for i in range(len(x_dados)):
        assert np.isclose(x_dados[i].nominal('m/s'),(i+1)/3.6)