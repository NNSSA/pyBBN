# -*- coding: utf-8 -*-
import numpy
from common import integrators
from interactions.boltzmann import BoltzmannIntegral


class ThreeParticleM(object):

    """ ## Three-particle interaction matrix element
        Matrix elements of the interest for three-particle interactions are constant """

    K = 0.

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __str__(self):
        return "K={: .2e}".format(self.K)

    def __iadd__(self, M):
        self.K += M.K
        return self

    def __idiv__(self, div):
        self.K /= div
        return self

    def __imul__(self, mul):
        self.K *= mul
        return self


class ThreeParticleIntegral(BoltzmannIntegral):

    def initialize(self):
        """
        Initialize collision integral constants and save them to the first involved particle
        """
        params = self.particle.params
        if params.T > self.decoupling_temperature and not self.particle.in_equilibrium:
            self.constant = sum(M.K for M in self.Ms)
            self.particle.collision_integrals.append(self)

    @staticmethod
    def integrate(particle, p0, integrand, bounds=None, kwargs=None):
        kwargs = kwargs if kwargs else {}

        if bounds is None:
            bounds = (particle.grid.MIN_MOMENTUM, particle.grid.MAX_MOMENTUM)

        if isinstance(integrand, list):
            def prepared_integrand(p1):
                return sum([i(p0, p1, **kwargs) for i in integrand])
        else:
            def prepared_integrand(p1):
                return integrand(p0, p1, **kwargs)

        integral, error = integrators.integrate_1D(
            prepared_integrand,
            bounds=bounds
        )
        constant = (particle.params.m / particle.params.x) / 16. / numpy.pi

        return constant * integral, error

    def integrand(self, p0, p1, fau=None):

        """
        Collision integral interior.
        """

        p = [p0, p1, 0]
        p, E, m = self.calculate_kinematics(p)

        integrand = self.in_bounds(p, E, m) * self.constant

        if p[0] != 0:
            integrand /= p[0] * E[0]

            # Avoid rounding errors and division by zero
            if m[1] != 0:
                integrand *= p[1] / E[1]
        else:
            if m[0] == 0:
                integrand *= 0
                return integrand

            integrand *= 2 * p[1]**2
            if m[1] != 0:
                integrand *= p[1] / E[1]
            if m[2] != 0:
                integrand *= p[1] / E[2]

        integrand *= numpy.array([fau([p[0], p[1][i], p[2][i]]) for i in range(len(p[1]))])

        return integrand

    """ ### Integration region bounds methods """

    def in_bounds(self, p, E=None, m=None):
        """ The kinematically allowed region in momentum space """
        if not E or not m:
            p, E, m = self.calculate_kinematics(p)

        is_in = (
            (E[2] >= m[2])
            * (p[0] + p[1] > p[2])
            * (p[0] + p[2] > p[1])
            * (p[1] + p[2] > p[0])
        )

        return is_in
