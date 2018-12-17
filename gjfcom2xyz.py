#!/usr/bin/env python

#AUTHOR: Yue Liu
#EMAIL: yueliu96@uw.edu
#Created on 11/28/2018

import sys,os

def checkcommand(n):
    if n==2:
        infl = sys.argv[1]
        if os.path.isfile(infl):
            return infl,infl[:-3]+'xyz'
        else:
            raise SystemExit('\n%s Not Found!\n' % infl)
    else:
        raise SystemExit('\npython gjfcom2xyz.py inputfile\n')

def ischgmp(lss):
    if len(lss)==2:
        try:
            int(float(lss[0]))
            int(float(lss[1]))
            return True
        except ValueError:
            return False
    else:
        return False

def findstrt(fl):
    keyline = 'check'
    with open(fl,'r') as fo:
        lines = fo.readlines()
    for i in range(len(lines)):
        line = lines[i]
        ctt = line.split()
        if ischgmp(ctt):
            keyline = i+1
            break
    if isinstance(keyline,int):
        return keyline
    else:
        raise SystemExit(':::>_<:::%s isn\'t real gjf/com!' % fl)

def gjfcom2xyz(fl1,fl2):
    strt = findstrt(fl1)
    with open(fl1,'r') as fo:
        lines = fo.readlines()
    newlines = [x for x in lines[strt:] if len(x.split())==4]
    natoms = len(newlines)
    with open(fl2,'w') as f2o:
        f2o.write(str(natoms)+'\n')
        f2o.write('\n')
        f2o.writelines(newlines)
    print('**\(^O^)/**%s --> %s: %s atoms found!' % (fl1,fl2,natoms))

if __name__=='__main__':
    gfile,xfile = checkcommand(len(sys.argv))
    gjfcom2xyz(gfile,xfile)
        
