# copyright ############################### #
# This file is part of the Xtrack Package.  #
# Copyright (c) CERN, 2021.                 #
# ######################################### #

import json

import numpy as np

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

two_co = xt.Particles.merge(2 * [tw_nobb.particle_on_co])

# out_ebe = track_particle_sixtrack(two_co, n_turns=1, dump='EBE')
out_2turns = track_particle_sixtrack(two_co, n_turns=2, dump=1)

# Check that xsuite orbit is closed also in sixtrack
xo.assert_allclose(out_2turns['x'][-1], tw_nobb.x[0], atol=1e-10, rtol=0)
xo.assert_allclose(out_2turns['y'][-1], tw_nobb.y[0], atol=1e-10, rtol=0)
xo.assert_allclose(out_2turns['delta'][-1], tw_nobb.delta[0], atol=1e-10, rtol=0)




