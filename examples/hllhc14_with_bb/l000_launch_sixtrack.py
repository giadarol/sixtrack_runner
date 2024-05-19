import os

n_jobs = 64

out = []

for ishift in range(n_jobs):
    out.append(f'python 000_single_da_sixtrack.py --ishift={ishift} &')

with open('run_sixtrack_jobs.sh', 'w') as fid:
    fid.write('\n'.join(out))

for ishift in range(n_jobs):
    out.append(f'python 002_single_da_xsuite.py --ishift={ishift} &')

with open('run_xsuite_jobs.sh', 'w') as fid:
    fid.write('\n'.join(out))
