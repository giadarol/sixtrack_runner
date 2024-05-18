# copyright ############################### #
# This file is part of the Xtrack Package.  #
# Copyright (c) CERN, 2021.                 #
# ######################################### #

import json
import itertools
import argparse

import numpy as np
import pandas as pd

import sixtracktools
from sixtrack import track_particle_sixtrack

import xobjects as xo
import xtrack as xt
import xfields as xf

# Get ishift from command line
parser = argparse.ArgumentParser()
parser.add_argument('--ishift', type=int, default=0)
args = parser.parse_args()
ishift = args.ishift

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

two_co = xt.Particles.merge(2 * [tw_nobb.particle_on_co])

# out_ebe = track_particle_sixtrack(two_co, n_turns=1, dump='EBE')
out_2turns = track_particle_sixtrack(two_co, n_turns=2, dump=1)

# Check that xsuite orbit is closed also in sixtrack
xo.assert_allclose(out_2turns['x'][-1], tw_nobb.x[0], atol=1e-10, rtol=0)
xo.assert_allclose(out_2turns['y'][-1], tw_nobb.y[0], atol=1e-10, rtol=0)
xo.assert_allclose(out_2turns['delta'][-1], tw_nobb.delta[0], atol=1e-10, rtol=0)

tw = line.twiss()

shift_r_vector = np.linspace(-0.01, 0.01, 16)

r_min = 2
r_max = 10
n_r = 256
n_angles = 5
delta_max = 27.e-5
nemitt_x = 2.5e-6
nemitt_y = 2.5e-6

shift = shift_r_vector[ishift]

radial_list = np.linspace(r_min + shift, r_max + shift, n_r,
                           endpoint=False)
theta_list = np.linspace(0, 90, n_angles + 2)[1:-1]

# Define particle distribution as a cartesian product of the above
particle_list = [(particle_id, ii[1], ii[0]) for particle_id, ii
         in enumerate(itertools.product(theta_list, radial_list))]

particle_df = pd.DataFrame(particle_list,
            columns=["particle_id", "normalized amplitude in xy-plane",
                     "angle in xy-plane [deg]"])

r_vect = particle_df["normalized amplitude in xy-plane"].values
theta_vect = particle_df["angle in xy-plane [deg]"].values * np.pi / 180  # type: ignore # [rad]

A1_in_sigma = r_vect * np.cos(theta_vect)
A2_in_sigma = r_vect * np.sin(theta_vect)

particles = line.build_particles(
        x_norm=A1_in_sigma,
        y_norm=A2_in_sigma,
        delta=delta_max,
        scale_with_transverse_norm_emitt=(nemitt_x, nemitt_y),
)

out_da = track_particle_sixtrack(particles, n_turns=100000, dump=None)

with open(f'da_sim_{ishift}.json', 'w') as fid:
    json.dump({
             'ishift': ishift,
             'shift': shift,
             'particles_init': particles.to_dict(),
             'last_turn': out_da['last_turn']},
             'f10': out_da['f10'],
             fid, cls=xo.JEncoder)
