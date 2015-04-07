"""
## Sterile neutrinos decoupling above $\Lambda_{QCD}$

<img src="plots.png" width=100% />
<img src="particles.png" width=100% />

This tests simulates the decoupling of sterile neutrinos in the quark-gluon plasma.

[Log file](log.txt)
[Distribution functions](distributions.txt)


"""

import os
import numpy
import matplotlib

from collections import defaultdict

from plotting import plt
from particles import Particle
from library.SM import particles as SMP, interactions as SMI
from library.NuMSM import particles as NuP, interactions as NuI
from evolution import Universe
from common import UNITS, Params, GRID


params = Params(T_initial=1.5 * UNITS.GeV,
                T_final=100 * UNITS.MeV,
                dy=0.025)

universe = Universe(params=params,
                    logfile='tests/sterile_decoupling_quarks/log.txt')

photon = Particle(params=params, **SMP.photon)

electron = Particle(params=params, **SMP.leptons.electron)
muon = Particle(params=params, **SMP.leptons.muon)
tau = Particle(params=params, **SMP.leptons.tau)

neutrino_e = Particle(params=params, **SMP.leptons.neutrino_e)
neutrino_mu = Particle(params=params, **SMP.leptons.neutrino_mu)
neutrino_tau = Particle(params=params, **SMP.leptons.neutrino_tau)

up = Particle(params=params, **SMP.quarks.up)
down = Particle(params=params, **SMP.quarks.down)
# charm = Particle(params=params, **SMP.quarks.charm)
strange = Particle(params=params, **SMP.quarks.strange)
# top = Particle(params=params, **SMP.quarks.top)
# bottom = Particle(params=params, **SMP.quarks.bottom)

sterile = Particle(params=params, **NuP.sterile_neutrino(300 * UNITS.MeV))
sterile.decoupling_temperature = params.T_initial

completely_sterile = Particle(params=params, **NuP.sterile_neutrino(300 * UNITS.MeV))
completely_sterile.decoupling_temperature = params.T_initial

universe.particles += [
    photon,

    electron,
    muon,
    tau,

    neutrino_e,
    neutrino_mu,
    neutrino_tau,

    up,
    down,
    # charm,
    strange,
    # top,
    # bottom,

    sterile,
    completely_sterile,
]

thetas = defaultdict(float, {
    'electron': 1e-4,
})

universe.interactions += (
    # SMI.neutrino_interactions(
    #     leptons=[electron, muon, tau],
    #     neutrinos=[neutrino_e, neutrino_mu, neutrino_tau]
    # ) +
    NuI.sterile_leptons_interactions(
        thetas=thetas, sterile=sterile,
        neutrinos=[neutrino_e, neutrino_mu, neutrino_tau],
        leptons=[electron, muon, tau]
    )
    + NuI.sterile_quark_interactions(
        thetas=thetas, sterile=sterile,
        neutrinos=[neutrino_e, neutrino_mu, neutrino_tau],
        leptons=[electron, muon, tau],
        quarks=[up, down, strange]
        # quarks=[up, down, charm, strange, top, bottom]
    )
)

universe.graphics.monitor(particles=[
    neutrino_e,
    completely_sterile,
    sterile,
])


universe.evolve()

universe.graphics.save(__file__)


""" ## Plots for comparison with articles """

folder = os.path.split(__file__)[0]
plt.ion()

""" ### JCAP10(2012)014, Figure 9
    <img src="figure_9.png" width=100% /> """

plt.figure(9)
plt.title('Figure 9')
plt.xlabel('MeV/T')
plt.ylabel(u'aT')
plt.xscale('log')
plt.xlim(UNITS.MeV/universe.params.T_initial, UNITS.MeV/universe.params.T_final)
plt.plot(UNITS.MeV / numpy.array(universe.data['T']), numpy.array(universe.data['aT']) / UNITS.MeV)
plt.show()
plt.savefig(os.path.join(folder, 'figure_9.png'))

""" ### JCAP10(2012)014, Figure 10
    <img src="figure_10.png" width=100% />
    <img src="figure_10_full.png" width=100% /> """

plt.figure(10)
plt.title('Figure 10')
plt.xlabel('Conformal momentum y = pa')
plt.ylabel('f/f_eq')
plt.xlim(0, 20)

f_sterile = sterile._distribution
feq_sterile = sterile.equilibrium_distribution()
plt.plot(GRID.TEMPLATE/UNITS.MeV, f_sterile/feq_sterile, label="sterile")

f_inert = completely_sterile._distribution
feq_inert = completely_sterile.equilibrium_distribution()
plt.plot(GRID.TEMPLATE/UNITS.MeV, f_inert/feq_inert, label="inert")

plt.legend()
plt.draw()
plt.show()
plt.savefig(os.path.join(folder, 'figure_10_full.png'))

plt.xlim(0, 10)
plt.ylim(0.99, 1.06)
plt.draw()
plt.show()
plt.savefig(os.path.join(folder, 'figure_10.png'))

# Distribution functions arrays
distributions_file = open(os.path.join(folder, 'distributions.txt'), "w")
numpy.savetxt(distributions_file, (f_sterile, feq_sterile, f_sterile/feq_sterile),
              header=str(sterile), footer='-'*80, fmt="%1.5e")
numpy.savetxt(distributions_file, (f_inert, feq_inert, f_inert/feq_inert),
              header=str(completely_sterile), footer='-'*80, fmt="%1.5e")

distributions_file.close()

# Just to be sure everything is okay
import ipdb
ipdb.set_trace()

raw_input("...")
