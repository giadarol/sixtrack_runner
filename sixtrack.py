import numpy as np
import os
import sixtracktools
import pysixtrack


def track_particle_sixtrack(particles, n_turns):

    n_part = len(particles.x)

    wfold = 'temp_trackfun'

    if not os.path.exists(wfold):
        os.mkdir(wfold)

    os.system('cp fort.* %s' % wfold)

    with open('fort.3', 'r') as fid:
        lines_f3 = fid.readlines()

    # Set initial coordinates
    i_start_ini = None
    for ii, ll in enumerate(lines_f3):
        if ll.startswith('INITIAL COO'):
            i_start_ini = ii
            break

    lines_f3[i_start_ini + 2] = '    0.\n'
    lines_f3[i_start_ini + 3] = '    0.\n'
    lines_f3[i_start_ini + 4] = '    0.\n'
    lines_f3[i_start_ini + 5] = '    0.\n'
    lines_f3[i_start_ini + 6] = '    0.\n'
    lines_f3[i_start_ini + 7] = '    0.\n'

    lines_f3[i_start_ini + 2 + 6] = '    0.\n'
    lines_f3[i_start_ini + 3 + 6] = '    0.\n'
    lines_f3[i_start_ini + 4 + 6] = '    0.\n'
    lines_f3[i_start_ini + 5 + 6] = '    0.\n'
    lines_f3[i_start_ini + 6 + 6] = '    0.\n'
    lines_f3[i_start_ini + 7 + 6] = '    0.\n'

    lines_f13 = []

    if np.mod(n_part, 2) != 0:
        raise ValueError('SixTrack does not like this!')

    for i_part in range(n_part):
        lines_f13.append('%.10e\n' % ((particles.x[i_part]) * 1e3))
        lines_f13.append('%.10e\n' % ((particles.px[i_part]) * particles.rpp[i_part] * 1e3))
        lines_f13.append('%.10e\n' % ((particles.y[i_part]) * 1e3))
        lines_f13.append('%.10e\n' % ((particles.py[i_part]) * particles.rpp[i_part] * 1e3))
        lines_f13.append('%.10e\n' % ((particles.zeta[i_part]) * 1e3))
        lines_f13.append('%.10e\n' % ((particles.delta[i_part])))
        if i_part % 2 == 1:
            lines_f13.append('%.10e\n' % (particles.energy0[i_part] * 1e-6))
            lines_f13.append('%.10e\n' % (particles.energy[i_part-1] * 1e-6))
            lines_f13.append('%.10e\n' % (particles.energy[i_part] * 1e-6))

    with open(wfold + '/fort.13', 'w') as fid:
        fid.writelines(lines_f13)


    i_start_tk = None
    for ii, ll in enumerate(lines_f3):
        if ll.startswith('TRACKING PAR'):
            i_start_tk = ii
            break
    # Set number of turns and number of particles
    temp_list = lines_f3[i_start_tk + 1].split(' ')
    temp_list[0] = '%d' % n_turns
    temp_list[2] = '%d' % (n_part / 2)
    lines_f3[i_start_tk + 1] = ' '.join(temp_list)
    # Set number of idfor = 2
    temp_list = lines_f3[i_start_tk + 2].split(' ')
    temp_list[2] = '2'
    lines_f3[i_start_tk + 2] = ' '.join(temp_list)

    # Setup turn-by-turn dump
    i_start_dp = None
    for ii, ll in enumerate(lines_f3):
        if ll.startswith('DUMP'):
            i_start_dp = ii
            break

    lines_f3[i_start_dp + 1] = 'StartDUMP 1 664 101 dumtemp.dat\n'

    with open(wfold + '/fort.3', 'w') as fid:
        fid.writelines(lines_f3)

    os.system('./runsix_trackfun')

    # Load sixtrack tracking data
    sixdump_all = sixtracktools.SixDump101('%s/dumtemp.dat' % wfold)

    x_tbt = np.zeros((n_turns, n_part))
    px_tbt = np.zeros((n_turns, n_part))
    y_tbt = np.zeros((n_turns, n_part))
    py_tbt = np.zeros((n_turns, n_part))
    sigma_tbt = np.zeros((n_turns, n_part))
    delta_tbt = np.zeros((n_turns, n_part))

    for i_part in range(n_part):
        sixdump_part = sixdump_all[i_part::n_part]
        x_tbt[:, i_part] = sixdump_part.x
        px_tbt[:, i_part] = sixdump_part.px
        y_tbt[:, i_part] = sixdump_part.y
        py_tbt[:, i_part] = sixdump_part.py
        sigma_tbt[:, i_part] = sixdump_part.sigma
        delta_tbt[:, i_part] = sixdump_part.delta

    return x_tbt, px_tbt, y_tbt, py_tbt, sigma_tbt, delta_tbt

