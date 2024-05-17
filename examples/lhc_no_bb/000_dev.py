import xtrack as xt
import xobjects as xo
from sixtrack import track_particle_sixtrack

particles = xt.Particles(x=[1e-4, 2e-4, 3e-4, 4e-4],
                         p0c=7e12)

out_ebe = track_particle_sixtrack(particles, n_turns=1, dump='EBE')
out_tbt = track_particle_sixtrack(particles, n_turns=100000, dump=None)

import json
with open('sixout.json', 'w') as fid:
    json.dump({'ebe':out_ebe, 'tbt':out_tbt},
              fid, cls=xo.JEncoder)
