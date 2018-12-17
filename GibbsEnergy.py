#!/usr/bin/env python

'''
 AUTHOR: Yue Liu
 EMAIL: yueliu96@uw.edu
 CREATED: 12/08/2018
read HFenergies.csv(generated by HFenergies.py, delimiter:','):
the first column is structure name(x), and its freqency file should be named with 'x_freq.csv'(generated by freq_thermal.py) 
the second column is energy in Hartree.
Use the minimum energy one as a reference to calculate relative Gibbs free energy.
'''
import csv,os,sys

def checkcommand():
    print('Reminder: If conformer in energy file is x, its freq.csv must be x_freq.csv. Delimiter must be \',\'')
    if len(sys.argv)!=2:
        raise SystemExit('Usage: python GibbsEnergy.py energyfile')
    else:
        if os.path.isfile(sys.argv[1]):
            return sys.argv[1]
        else:
            raise SystemExit(':::>_<::: %s NOT FOUND!' % sys.argv[1])

def mergefreq2E(ef):
    with open(ef,'r') as fo:
        csvrows = csv.reader(fo)
        rows = [x for x in csvrows]
    title = rows[0]
    ctts = rows[1:]
    eng = [float(x[1]) for x in ctts]
    ref = eng.index(min(eng)) #find minimum energy index
    check=0 #use to write title
    for i in range(len(ctts)):
        nm = ctts[i][0]+'_freq.csv'
        if os.path.isfile(nm):
            with open(nm,'r') as fo:
                csvrows = csv.reader(fo)
                rows = [x for x in csvrows]
            if check==0:
                T = float(rows[5][0])
                title.append('Ehf(kJ/mol)')
                title.extend(rows[7])
                title.append('dG(kJ/mol)')
                title.append('G=Ehf+cZPVE+H(T)-T*S(T)')
            ctts[i].append(float(ctts[i][1])*2625.5)
            ctts[i].extend(list(map(float,rows[8])))
            check += 1
        else:
            print('warning'.center(15,':')+'%s NOT FOUND!' % nm)
            continue
    return title,ctts,ref,T,check
    

def calcG(T,lss):
    try:
        return lss[0]+lss[1]+lss[2]-T*lss[3]/1000
    except:
        return 'NA'

def GibbsEnergy(ef):
    lss1,lss2,ref,T,nstruct = mergefreq2E(ef)
    Gref = calcG(T,lss2[ref][2:])
    for i in range(len(lss2)):
        try:
            lss2[i].append(calcG(T,lss2[i][2:])-Gref)
        except:
            continue
    out = 'gibbs.csv'
    with open(out,'w') as fo:
        wrfo=csv.writer(fo)
        wrfo.writerow(lss1)
        wrfo.writerows(lss2)
    print('**\(^O^)/** %d Conformers Found! Please Check %s File' % (nstruct,out))


if __name__=='__main__':
    efl = checkcommand()
    GibbsEnergy(efl)
