import elements
import mass
import abundance
import adducts

def testAccessAndConsistency():
    c12 = elements.C12
    assert c12["abundance"] == abundance.C12
    assert c12["abundance"] is not None
    assert abs(c12["abundance"]-0.989) < 0.001
    assert c12["mass"] ==  mass.C12
    assert c12["name"] == "Carbon"
    assert c12["number"] == 6
    assert  mass.of("[13]C") - mass.of("C") == mass.C13-mass.C12
    assert  mass.of("C", C=mass.C13) - mass.of("C") == mass.C13-mass.C12
    assert  mass.of("C", C=elements.C13) - mass.of("C") == mass.C13-mass.C12


def testAdducts():
    assert len(adducts.all) == 21, len(adducts.all)
    #test subgroups
    assert len(adducts.positive) == 14, len(adducts.positive)
    assert len(adducts.negative) == 21-14, len(adducts.negative)
    assert len(adducts.single_charged)>0
    assert len(adducts.double_charged)>0
    assert len(adducts.triple_charged )>0
    assert len(adducts.positive_single_charged)>0
    assert len(adducts.positive_double_charged)>0
    assert len(adducts.positive_triple_charged)>0
    assert len(adducts.negative_single_charged)>0
    assert len(adducts.negative_double_charged)>0
    assert len(adducts.negative_triple_charged )>0


    # tst namespace constants
    assert adducts.M_plus_H[-1] == +1
    assert adducts.M_plus_NH4[-1] == +1
    assert adducts.M_plus_Na[-1] == 1
    assert adducts.M_plus_H_minus_H2O[-1]  ==1
    assert adducts.M_plus_H_minus_H4O2[-1]  ==1
    assert adducts.M_plus_K[-1]  ==1
    assert adducts.M_plus_CH4O_plus_H[-1]  ==1
    assert adducts.M_plus_2Na_minus_H[-1]  ==1
    assert adducts.M_plus_H2[-1]  ==2
    assert adducts.M_plus_H3[-1]  ==3
    assert adducts.M_plus_Na_plus_H[-1]  ==2
    assert adducts.M_plus_H2_plus_Na[-1]  ==3
    assert adducts.M_plus_Na2[-1]  ==2
    assert adducts.M_plus_H_plus_Na2[-1]  ==3
    assert adducts.M_minus_H[-1]  ==-1
    assert adducts.M_minus_H_minus_H2O[-1] == -1
    assert adducts.M_plus_Na_minus_H2[-1]  ==-1
    assert adducts.M_plus_Cl[-1]  ==-1
    assert adducts.M_plus_K_minus_H2[-1]  ==-1
    assert adducts.M_minus_H2[-1]  ==-2
    assert adducts.M_minus_H3[-1]  ==-3
    assert adducts.M_plus_Na_minus_H2[-1] == -1

    t = adducts.positive.toTable()
    assert len(t) == 14
    assert len(t.colNames) == 3

def testfoumulaadd():
    import ms
    assert ms.addmf("H2O") == "H2O"
    assert ms.addmf("H2O", "O") == "H2O2"
    assert ms.addmf("H2O", "-O") == "H2"
    assert ms.addmf("H2O", "-H2") == "O"
    assert ms.addmf("H2O", "O", "O", "O2") == "H2O5"
    assert ms.addmf("(CH2)7", "COOH", "Cl", "-H2O") == "C8H13OCl"


