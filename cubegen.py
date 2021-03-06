#!/usr/bin/env python

'''
 AUTHOR: Yue Liu
 EMAIL: yueliu96@uw.edu
 Created: 12/09/2018
Need tddft log and chk/fchk file in the same folder and generate cube files
From tddft log file find number of alpha electrons and virtual alpha electrons to calculate where to find beta electron orbital: mo(beta)+=mo(NAE)+mo(NVA)
From log to find the name of chk file to create fchk if fchk not found. fchk file shoud have the same name with chk file.
Read all orbitals in one excited state and turn them to cube files
Write a bash script to run parallelly(tN_logname.sh) and submit it to hyak-ckpt
'''

from __future__ import print_function
import sys,os,subprocess

def checkcommand():
    if len(sys.argv)!=3:
        raise SystemExit('Usage: python cubegen.py tddftlog Nstate')
    else:
        fa = sys.argv[1]
        if fa.split('.')[-1]!='log':
            raise SystemExit('Error: %s Must End with \'log\'' % fa)
        if os.path.isfile(fa):
            return fa,sys.argv[2]
        else:
            raise SystemExit('Error: %s Not Found!' % fa)

def readlog(fl,n):
    with open(fl,'r') as fo:
        lines = fo.readlines()
    i=-1
    es = 'Excited State%4s' % n
    proc = []
    for line in lines:
        i += 1
        if '%chk=' in line:
            chknm = line.strip().split('=')[-1].split('.')[0]
            fchk = chknm+'.fchk'
            chk = chknm+'.chk'
            if os.path.isfile(fchk):
                wrchk = '\n'
            elif os.path.isfile(chk):
                wrchk = 'formchk '+chk+'\n\n'
            else:
                raise SystemExit(':::>_<:::%s or %s Needed, But Not Found!' % (chk,fchk))
        elif 'alpha electrons' in line:
            nae = int(line.split()[0])
        elif 'NVA=' in line:
            nva = int(line.split('NVA=')[1].split()[0])
        elif es in line:
             keyi = i
             try:
                 while True:
                     keyi += 1
                     x = lines[keyi] 
                     int(x.lstrip()[0])
                     proc.append(x)
             except:
                 return chknm,wrchk,nae+nva,proc
    raise SystemExit(':::>_<::: Number of state out of range!')
        
def writecube(m,n,proc,nm,cnm):
    fchk = cnm+'.fchk'
    orbit = []
    for p in proc:
        g = p.split()[0]
        e = p.split()[2]
        if g not in orbit:
            orbit.append(g)
        if e not in orbit:
            orbit.append(e)
    cubes = []
    for x in orbit:
        fc = nm+'_'+x+'.cube'
        if os.path.isfile(fc):
            continue
        else:
            if 'A' in x:
                cubes.append('cubegen 0 mo='+x.strip('A')+' '+fchk+' '+fc+' 0 h\n')
            if 'B' in x:
                cubes.append('cubegen 0 mo='+str(int(x.strip('B'))+n)+' '+fchk+' '+fc+' 0 h\n')
    cubes.sort(key=lambda x: (len(x),x))
    task = 't'+str(m)+'_'+nm+'.txt'
    with open(task,'w') as fo:
        fo.writelines(cubes)
    return task,len(cubes)
                 
def writebash(chk,task,nt):
    mybash = task.split('.')[0]+'.sh'   
    with open(mybash,'w') as fsh:
        fsh.write('#!/bin/bash\n#SBATCH --job-name=fchk_cube\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=28\n#SBATCH --time=10:00\n#SBATCH --mem=100G\n')
        pwd = os.path.abspath('.')
        fsh.write('#SBATCH --workdir='+pwd+'\n')
        fsh.write('#SBATCH --partition=ckpt\n#SBATCH --account=stf-ckpt\n\n')
        fsh.write('echo \'This job will run on\' $SLURM_JOB_NODELIST\n')
        fsh.write('#set up time\nstart=$(date +%s)\n\n')
        fsh.write('#load Gaussian environment\nmodule load contrib/g16.b01\n\n')
        fsh.write(chk)
        fsh.write('#load parallel environment\nmodule load parallel-20170722\n')
        fsh.write('cat '+task+' | parallel -j 28\n\n')
        fsh.write('end=$(date +%s)\necho \'Elapsed Time: \'$(($end-$start))\'s\'')
    subprocess.call('sbatch '+mybash,shell=True)
    print('**\(^O^)/**%s submitted to ckpt, please wait a little bit!' % mybash)

def logchk2cube(flog,nstt):
    chknm,wrchk,nava,process = readlog(flog,nstt)
    tasklist,ntask = writecube(nstt,nava,process,flog.split('.')[0],chknm)
    writebash(wrchk,tasklist,ntask)

if __name__=='__main__':
    log,N = checkcommand()
    logchk2cube(log,N)
