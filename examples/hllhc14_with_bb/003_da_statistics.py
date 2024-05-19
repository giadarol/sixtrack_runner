# copyright ############################### #
# This file is part of the Xtrack Package.  #
# Copyright (c) CERN, 2021.                 #
# ######################################### #

import json
import itertools

import numpy as np
import pandas as pd

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

r_min_lost = []

for i_sim in range(16):

    with open(f'da_sim_{i_sim}.json', 'r') as fid:
        data = json.load(fid)

    particles = xp.Particles.from_dict(data['particles_init'])
    last_turn = np.array(data['last_turn'])

    norm = tw_nobb.get_normalized_coordinates(particles, nemitt_x=2.5e-6, nemitt_y=2.5e-6)

    r_init = np.sqrt(norm.x_norm**2 + norm.y_norm**2)

    mask_lost = last_turn < 100000

    min_r_lost_run = np.min(r_init[mask_lost])

    r_min_lost.append(min_r_lost_run)


# import matplotlib.pyplot as plt
# plt.close('all')
# plt.figure(1)
# plt.plot(r_init, last_turn, '.')

# plt.figure(2)
# plt.plot(norm.x_norm, norm.y_norm, '.')
# plt.plot(norm.x_norm[mask_lost], norm.y_norm[mask_lost], 'rx')

# plt.show()



