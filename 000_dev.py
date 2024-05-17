import xtrack as xt
from sixtrack import track_particle_sixtrack

particles = xt.Particles(x=[1e-4, 2e-4, 3e-4, 4e-4],
                         p0c=7e12)

out = track_particle_sixtrack(particles, n_turns=5)
