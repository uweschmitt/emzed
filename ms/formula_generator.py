#encoding: latin-1



def formulaTable(min_mass, max_mass, C=(0,0),
                                     H=(0,0),
                                     N=(0,0),
                                     O=(0,0),
                                     P=(0,0),
                                     S=(0,0)):

    import mass
    import math

    from libms.DataStructures.Table import Table

    cmin, cmax = C
    hmin, hmax = H
    nmin, nmax = N
    omin, omax = O
    pmin, pmax = P
    smin, smax = S


    hcmax = 6  # 3
    ncmax = 4  # 2
    ocmax = 3  # 1.2
    pcmax = 6  # 0.32
    scmax = 2  # 0.65

    valh = -1
    valc = +2
    valn = 1
    valo = 0
    valp = 3
    vals = 4

    frange = lambda a, b: xrange(int(a), int(b))

    rows = []

    for c in range(cmin, cmax+1):

        resmc_max = max_mass - c*mass.C
        s1 = min(smax, math.floor(resmc_max/mass.S), scmax * c)

        for s in frange(smin, s1+1):
            resms_max = resmc_max - s*mass.S
            p1 = min(pmax, math.floor(resms_max/mass.P), pcmax * c)

            for p in frange(pmin, p1+1):
                resmp_max = resms_max - p*mass.P
                o1 = min(omax, math.floor(resmp_max/mass.O), ocmax * c)

                for o in frange(omin,o1+1):
                    resmo_max = resmp_max - o*mass.O
                    n1 = min(nmax, math.floor(resmo_max/mass.N), ncmax * c)

                    for n in frange(nmin, n1+1):
                        resmn_max = resmo_max - n*mass.N
                        h1 = min(hmax, math.floor(resmn_max/mass.H), hcmax * c)

                        bond0 = c*valc + n*valn + o*valo + p*valp + s*vals
                        for h in frange(hmin, h1+1):
                            resmh_max = resmn_max - h*mass.H
                            if 0 <= resmh_max <= max_mass-min_mass:
                                bond = (2.0 + bond0 + h*valh)  / 2.0
                                if bond>= 0 and bond % 1 != 0.5:

                                    mf = "C%d.H%d.N%d.O%d.P%d.S%d." % (c, h, n, o, p, s)
                                    mf = mf.replace("C0.", ".")
                                    mf = mf.replace("H0.", ".")
                                    mf = mf.replace("N0.", ".")
                                    mf = mf.replace("O0.", ".")
                                    mf = mf.replace("P0.", ".")
                                    mf = mf.replace("S0.", ".")
                                    mf = mf.replace("C1.", "C.")
                                    mf = mf.replace("H1.", "H.")
                                    mf = mf.replace("N1.", "N.")
                                    mf = mf.replace("O1.", "O.")
                                    mf = mf.replace("P1.", "P.")
                                    mf = mf.replace("S1.", "S.")
                                    mf = mf.replace(".", "")

                                    rows.append([mf, max_mass - resmh_max])
    return Table(["mf", "m0"],[str, float], ["%s", "%.5f"], rows)


ta = formulaTable(0, 1000, (22, 100), (35, 100), (7, 100), (17, 100), (3, 100), (1, 100))




# vim: ts=4 et sw=4 sts=4

