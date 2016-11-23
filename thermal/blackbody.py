###################################################################
#   BLACKBODY THERMAL MODEL
###################################################################

import numpy as N
import astropy.units as U

###########################################################
# Calculates the fourth power of the equilibrium temperature at a given time and lat/lon, given a rotation period and "nightside" minimum temperature.
########################################################### 
def equilibrium_temperatures4(planet_object,
                             prot,
                             Tn,
                             albedo):

    #Define the stellar luminosity and the instantaneous star-planet separations.
    l = planet_object.R**2 * planet_object.Teff**4
    r = planet_object.a * (1-planet_object.e**2)/(1+planet_object.e*N.cos(planet_object.anomaly(planet_object.times)['true']))
    
    #Alpha is the attenuation factor due to the apparent angle of the star to the horizon at a given point on the planet. Set to zero on the night side.
    #alpha = N.cos(planet_object.thetas) * N.cos( (-2*N.pi*U.rad*planet_object.times/prot[...,N.newaxis] + planet_object.anomaly(planet_object.times)['true'])[...,N.newaxis,N.newaxis] + planet_object.phis)
    sub_sol = planet_object.subsolar_longitude(planet_object.times, rotation_period = prot[...,N.newaxis])
    alpha = N.cos(planet_object.thetas) * N.cos(sub_sol[...,N.newaxis,N.newaxis] - planet_object.phis)
    alpha[alpha < 0] = 0
    
    visible_flux = (l/r**2) * N.einsum('...tuv->...uvt', alpha)
    Teq4 = (1 - albedo) * N.einsum('...uvt->tuv...', visible_flux)*visible_flux.unit + Tn**4

    return Teq4.to('K4')

###########################################################
# Produces a new 2D array of surface temperatures from an initial temperature array and a time step.
########################################################### 
def temperatures(planet_object, 
                 parameters = [N.array([5])*U.h, N.array([10])*U.h, N.array([1000])*U.K, N.array([0.2])]):

    prot, t1000, Tn, albedo = parameters
    prot, t1000, Tn, albedo = N.meshgrid(prot, t1000, Tn, albedo)
    
    eq_T4 = equilibrium_temperatures4(planet_object, prot, Tn, albedo)
    
    temperature_timeseries = []
    temperature_timeseries.append(N.einsum('...uv->uv...', Tn[...,N.newaxis,N.newaxis]/U.K * N.ones_like(planet_object.thetas/U.deg))*U.K)

    trad = t1000 * ((1000*U.K)**4 / eq_T4)**0.75
    timestep = planet_object.times[1] - planet_object.times[0]

    for t, time in enumerate(planet_object.times):
        if t > 0:
            dT = 0.25 * eq_T4[t]**0.25/trad[t] * (1 - temperature_timeseries[t-1]**4/eq_T4[t]) * timestep
            evolved_temperatures = N.where(N.abs(dT)>N.abs(temperature_timeseries[t-1]-(eq_T4[t])**0.25), eq_T4[t]**0.25, temperature_timeseries[t-1]+dT)*U.K
            temperature_timeseries.append(evolved_temperatures)
        
    return N.array(temperature_timeseries)*U.K
