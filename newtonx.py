#!/usr/bin/env python

'''
 AUTHOR: Yue Liu
 EMAIL: yueliu96@uw.edu
 Created: 12/12/2018
 Edited: 12/15/2018

Usage: python newtonx.py gjf/com freq.log
Description:
 Need optimized guassian structure(gjf/com) and gaussian frequency output file(log) to run newtonx.
 In the end, besides the above two files,  we will TDDFT_SPEC folder in the working directory; freq.out, geom, initqp_input, newtonx.sh, split_initcond.log, JOB_AD(folder) and INITIAL_CONDITIONS(folder) in TDDFT_SPEC; gaussian.com ahd basis in JOB_AD; I1,I2,...In in INITIAL_CONDITIONS.
 freq.out is just gauss freq log file; geom and gaussian.com come from gauss opt gjf/com; iniqp_input generated by '$NX/nxinp'; newtonx.sh is bash scripted used to submitted jobs; split_initcond.log and INITIAL_CONDITIONS generated by '$NX/split_initcond.pl', this step must be executed after geom, freq.out, initqp_input and JOB_AD are ready. Only the name of geom and freq.out could be changed, but must be updated in initqp_input file.
 First, create TDDFT_SPEC/JOB_AD, if TDDFT_SPEC exists, it will be removed; copy gauss freq log file to TDDFT_SPEC/freq.out.
 Second, write xyz file, input file for $NX/nxinp, gaussian.com and basis file. xyz and gaussian.com based on gjf/com; gaussian.com and basis in JOB_AD, the other two in TDDFT_SPEC, input required. 
 Third, use '$NX/xyz2nx < xyzfile' to generate geom, run '$NX/nxinp < ???' to generate initqp_input and run '$NX/split_initcond.pl' to split this job to several smaller jobs.
 Fourth, wirte nx_submit.sh with different jobnames and directories and put it in corresponding I* folders who are in INITIAL_CONDITIONS.
 In the end, wirte a bash script called newtonx.sh in the TDDFT_SPEC folder, which can be used to submit all nx_submit.sh in INITIAL_CONDITIONS/I*.
After done, check and change partition, account or time in newtonx.sh; run 'bash newtonx.sh' 
Note:
 When running on ckpt, if iseed=-1, it might generate a super large random number for iseed, which makes newtonx dies. So I change the iseed to 1234,2468,...1234*n for I1,I2,...In.

'''

from __future__ import print_function
import sys,os,shutil,subprocess

def checkcommand():
    if len(sys.argv)!=3:
        raise SystemExit('\npython newtonx.py opt.gjf/com freq.log\n')
    else:
        fa,fb = sys.argv[1],sys.argv[2]
        if os.path.isfile(fa)and os.path.isfile(fb):
            return fa,fb
        else:
            raise SystemExit(':::>_<:::%s or/and %s Not Found!' % (fa,fb) )

def setinitcond():
#input function isn't same in python2 and python3
    if 1/2==0:
        myinput=raw_input
    else:
        myinput=input
    a = myinput('? How many states do you want to calculate: ')
    int(a)
    print('\'<_\': nstats = '+a)
    b = myinput('? method to use, default=[um062x]: ')
    if b=='':
        rb = 'um062x'
    else:
        rb = b
    print('\'<_\': method = '+rb)
    c = myinput('? basisset to use, default=[6-31+g(d,p)]: ')
    if c=='':
        rc = '6-31+g(d,p)'
    else:
        rc = c
    print('\'<_\': basis = '+rc)
    return a,rb,rc
    
def writeinputfiles(fl,d1,d2):
#take the first line only having two numbers as chg and mp
#take the next lines having 4 items as coordinates lines and count the lines as number of atoms 
    coordline = 'check'
    with open(fl,'r') as fo:
        lines = fo.readlines()
    for i in range(len(lines)):
        line = lines[i]
        ctt = line.split()
        if len(ctt)==2:
            try:
                chg=int(float(ctt[0]))
                mp=int(float(ctt[1]))
                coordline = i+1
                break
            except:
                continue
    if not isinstance(coordline,int):
        raise SystemExit(':::>_<:::Not Found Charge & Multiplicity; Fail to Convert %s to xyz format!' % fl)
    else:
        nm = fl.split('.')[0]
        xyzlines = [x for x in lines[coordline:] if len(x.split())==4]
        natoms = str(len(xyzlines))
        fxyz = nm+'.xyz'
#write xyz file in 'TDDFT_SPEC' directory, will be deleted after changed to nx format.
        with open(d1+'/'+fxyz,'w') as fo:
            fo.write(natoms+'\n\n')
            fo.writelines(xyzlines)
        print('\'<_\': natoms =', natoms)
        nst,mthd,bs = setinitcond()
#write input for $NX/nxinp in 'TDDFT_SPEC', will be deleted after that.
        fnx = nm+'_nxinp'
        with open(d1+'/'+fnx,'w') as fo:
            fo.write('1\n2\n'+natoms+'\n300\ngeom\n4\nfreq.out\n1\n310\nn\n1\n1\n'+nst+'\n1\n100\n6.5\n0\n1\n7\n')
#write the new gausse input file must named with gaussian.com, which will be put in 'JOB_AD' folder.
        with open(d2+'/gaussian.com','w') as fo:
            fo.write('%rwf='+nm+'\n%NoSave\n%chk='+nm+'\n%mem=32GB\n%nprocshared=28\n')
            fo.write('# TD(NStates='+nst+') '+mthd+'/'+bs+' pop=none scf=(xqc,tight) Symmetry=None\n\n')
            fo.write(nm+' newtonx\n\n')
            fo.writelines(lines[coordline-1:])
#write basis file in JOB_AD
        with open(d2+'/basis','w') as fo:
            fo.write(bs)
        return fxyz,fnx
'''
#write initqp_input file in TDDFT_SPEC.
        with open(d1+'/initqp_input','w') as fo:
            fo.write('&dat\n nact = 2\n numat = '+str(natoms)+'\n')
            fo.write(' npoints = 300\n file_geom = geom\n iprog = 4\n file_nmodes = freq.out\n')
            fo.write(' anh_f = 1\n temp = 310\n ics_flg = n\n chk_e = 1\n nis = 1\n nfs = '+nst+'\n')
            fo.write(' kvert = 1\n de = 100\n prog = 6.5\n iseed = 0\n lvprt = 1\n/\n')
'''

def nx_submit(nm,d):
    with open(d+'/nx_submit.sh','w') as fo:
        fo.write('#!/bin/bash\n#SBATCH --job-name='+nm+'\n')
        fo.write('#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=28\n#SBATCH --time=10:00:00\n#SBATCH --mem=100G\n')
        fo.write('#SABTCH --workdir='+d+'\n#SBATCH --partition=ckpt\n#SBATCH --account=stf-ckpt\n\n')
        fo.write('echo \'This job will run on\' $SLURM_JOB_NODELIST\n')
        fo.write('#set up time\nbegin=$(date +%s)\n\n')
        fo.write('#load newtonx and gauss09 environment\nmodule load contrib/newton-x\n\n')
        fo.write('$NX/initcond.pl > initcond.log\n\n')
        fo.write('end=$(date +%s)\necho \'Elapsed Time: \'$(($end-$begin))\'s\'')

def newtonx(opt,log):
    try:
        pwd = os.path.abspath('.')
        myd1 = 'TDDFT_SPEC'
        myd2 = 'TDDFT_SPEC/JOB_AD'
        myd3 = 'TDDFT_SPEC/INITIAL_CONDITIONS'
        if os.path.exists(myd1):
            print('%s Exists......' % myd1)
            shutil.rmtree(myd1)
            print(myd1,'is deleted......')
        os.makedirs(myd2)
        shutil.copy(log,myd1+'/freq.out')
        fxyz,fnx = writeinputfiles(opt,myd1,myd2)
        sdo  = 'cd TDDFT_SPEC;module load contrib/newtonX;'
        sdo += '$NX/xyz2nx < '+fxyz+';'
        sdo += '$NX/nxinp < '+ fnx+';'
        sdo += 'rm '+fxyz+' '+fnx+';'
        sdo += 'echo \"\'<_\': 300 initial conditions will be calculated...\n\";'
        sdo += 'echo \"\'<_\': The anwer to the second question is [n]\n\";'
        sdo += '$NX/split_initcond.pl'
        subprocess.call(sdo,shell=True)
        allI = os.listdir(pwd+'/'+myd3)
        allI.sort(key=lambda x: (len(x),x))
        numI = len(allI)
        seed = 1234
        for I in allI:
#for every splitting job, change 'iseed = -1' to 'iseed = 1234++'; write a nx_submit.sh with its directory and different jobname(structname+I).
            subprocess.call('sed -i \'s/iseed = -1/iseed = '+str(seed)+'/g\' '+ myd3+'/'+I+'/initqp_input', shell=True)
            seed += 1234
            nx_submit(opt.split('.')[0]+'_'+I,pwd+'/'+myd3+'/'+I)
        with open(myd1+'/newtonx.sh','w') as fo:
            fo.writelines(['cd '+'/'.join([pwd,myd3,I])+'; sbatch -p ckpt -A stf-ckpt --time=20:00:00 nx_submit.sh\n' for I in allI])
        print('**\(^O^)/**Please check your TDDFT_SPEC folder.To submit all of your jobs do:\n cd TDDFT_SPEC\n bash newtonx.sh')
        print('FYI:\n 28cores 32atoms\n   16states 30initconds ---  13h\n   16states 10initconds --- 4.6h\n   20states   3initconds ---  2.5h\n   20states   2initconds --- 1.6h')
    except:
        err=sys.exc_info()
        print('\npython error in line %d: ' % err[2].tb_lineno)
        raise SystemExit(err[1])


if __name__=='__main__':
    fopt,flog = checkcommand()
    newtonx(fopt,flog)
