# copyright ############################### #
# This file is part of the Xtrack Package.  #
# Copyright (c) CERN, 2021.                 #
# ######################################### #

import json
import itertools

import numpy as np
import pandas as pd
import statsmodels.api as sm

import sixtracktools
from sixtrack import track_particle_sixtrack

import xobjects as xo
import xtrack as xt
import xpart as xp
import xfields as xf


##############
# Build line #
##############

# Read sixtrack input
sixinput = sixtracktools.SixInput(".")
p0c_eV = sixinput.initialconditions[-3] * 1e6

# Build line from sixtrack input
line = sixinput.generate_xtrack_line()
line.particle_ref = xt.Particles(p0c=p0c_eV)

# Create knob to switch bb on/off
tt = line.get_table()
ttbb = tt.rows[(tt.element_type=='BeamBeamBiGaussian2D')
               |(tt.element_type=='BeamBeamBiGaussian3D')]

line.vars['beambeam_scale'] = 1.
for nn in ttbb.name:
    line.element_refs[nn].scale_strength = line.vars['beambeam_scale']


# Twiss bb off
line.vars['beambeam_scale'] = 0
tw_nobb = line.twiss()
line.vars['beambeam_scale'] = 1.

xf.configure_orbit_dependent_parameters_for_bb(line,
        particle_on_co=tw_nobb.particle_on_co)

sets = {}

for set_name in ['sixtrack', 'xsuite']:

    tag = {'sixtrack': '', 'xsuite': '_xsuite'}[set_name]

    r_min_lost = []
    r_min_sxt_lost = []

    for i_sim in range(64):

        with open(f'da_sim_{i_sim}{tag}.json', 'r') as fid:
            data = json.load(fid)

        particles = xp.Particles.from_dict(data['particles_init'])
        last_turn = np.array(data['last_turn'])

        norm = tw_nobb.get_normalized_coordinates(particles, nemitt_x=2.5e-6, nemitt_y=2.5e-6)

        r_init = np.sqrt(norm.x_norm**2 + norm.y_norm**2)

        mask_lost = last_turn < 100000

        min_r_lost_run = np.min(r_init[mask_lost])

        r_min_lost.append(min_r_lost_run)

        if 'f10' in data:
            amplitude_x_sxt = np.zeros_like(r_init)
            f10 = np.array(data['f10'])
            amplitude_x_sxt[::2] = f10[:,6]
            amplitude_x_sxt[1::2] = f10[:,7]

            amplitude_y_sxt = np.zeros_like(r_init)
            amplitude_y_sxt[::2] = f10[:,25]
            amplitude_y_sxt[1::2] = f10[:,26]

            r_init_sxt = np.sqrt(amplitude_x_sxt**2 + amplitude_y_sxt**2)
            r_init_sxt[r_init_sxt == 0] = np.nan
            min_r_sxt_lost_run = np.nanmin(r_init_sxt[mask_lost])
            r_min_sxt_lost.append(min_r_sxt_lost_run)

    sets[set_name] = {'r_min_lost': r_min_lost, 'r_min_sxt_lost': r_min_sxt_lost}

    obstat = sm.nonparametric.KDEUnivariate(r_min_lost)
    obstat.fit()
    obstat.fit(bw=0.2)
    density = obstat.evaluate
    sets[set_name]['density'] = density

x_density = np.linspace(3, 8, 10000)

import matplotlib.pyplot as plt
plt.close('all')

mean_sixtrack = np.mean(sets['sixtrack']['r_min_lost'])
mean_xsuite = np.mean(sets['xsuite']['r_min_lost'])
std_sixtrack = np.std(sets['sixtrack']['r_min_lost'])
std_xsuite = np.std(sets['xsuite']['r_min_lost'])

density_sixtrack_gauss = np.exp(-(x_density - mean_sixtrack)**2/(2*std_sixtrack**2))/np.sqrt(2*np.pi*std_sixtrack**2)
density_xsuite_gauss = np.exp(-(x_density - mean_xsuite)**2/(2*std_sixtrack**2))/np.sqrt(2*np.pi*std_sixtrack**2)
density_sixtrack_gauss = density_sixtrack_gauss/np.max(density_sixtrack_gauss)
density_xsuite_gauss = density_xsuite_gauss/np.max(density_xsuite_gauss)

plt.figure(1, figsize=(6.4, 4.8 * 1.5))
sp1 = plt.subplot(211)
sp2 = plt.subplot(212, sharex=sp1)
sp1.plot(sets['sixtrack']['r_min_lost'], np.zeros_like(sets['sixtrack']['r_min_lost']), '.', color='C0')
sp2.plot(sets['xsuite']['r_min_lost'], -np.zeros_like(sets['xsuite']['r_min_lost']), '.', color='C1')

sp1.axvline(np.mean(sets['sixtrack']['r_min_lost']), color='C0')
sp2.axvline(np.mean(sets['xsuite']['r_min_lost']), color='C1')

sp1.plot(x_density, density_sixtrack_gauss, color='C0')
sp2.plot(x_density, density_xsuite_gauss, color='C1')
sp1.set_title('Sixtrack (64 repetitions)')
sp2.set_title('Xsuite (64 repetitions)')

# Text box top right
info_sixtrack = '\n'.join((
    r'DA$_{mean}$ = ' + f'{mean_sixtrack:.2f}' + r' $\sigma$',
    r'DA$_{std}$ = ' + f'{std_sixtrack:.2f}' + r' $\sigma$'
    ))
info_xsuite = '\n'.join((
    r'DA$_{mean}$ = ' + f'{mean_xsuite:.2f}' + r' $\sigma$',
    r'DA$_{std}$ = ' + f'{std_xsuite:.2f}' + r' $\sigma$'
    ))
props = dict(boxstyle='round', facecolor='white', alpha=0.5)
sp1.text(0.03, 0.95, info_sixtrack, transform=sp1.transAxes, fontsize=12,
        verticalalignment='top', bbox=props)
sp2.text(0.03, 0.95, info_xsuite, transform=sp2.transAxes, fontsize=12,
        verticalalignment='top', bbox=props)

sp1.set_xlabel(r'DA [$\sigma$]')
sp2.set_xlabel(r'DA [$\sigma$]')
sp1.set_ylabel('Fitted density')
sp2.set_ylabel('Fitted density')

plt.subplots_adjust(hspace=0.31)
plt.show()


# plt.figure(1)
# plt.plot(r_init, last_turn, '.')

# plt.figure(2)
# plt.plot(norm.x_norm, norm.y_norm, '.')
# plt.plot(norm.x_norm[mask_lost], norm.y_norm[mask_lost], 'rx')

# plt.show()



