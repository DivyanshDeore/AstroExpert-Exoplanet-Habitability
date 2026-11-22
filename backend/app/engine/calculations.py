import math

def stellar_flux(luminosity_solar: float, distance_au: float) -> float:
    if not math.isfinite(luminosity_solar) or luminosity_solar <= 0:
        raise ValueError("Stellar luminosity must be positive.")
    if not math.isfinite(distance_au) or distance_au <= 0:
        raise ValueError("Orbital distance must be positive.")
    return luminosity_solar / distance_au**2

def relative_density(mass_earth: float, radius_earth: float) -> float:
    if mass_earth <= 0 or radius_earth <= 0:
        raise ValueError("Mass and radius must be positive.")
    return mass_earth / radius_earth**3

def simplified_hz(luminosity_solar: float) -> dict:
    if luminosity_solar <= 0:
        raise ValueError("Luminosity must be positive.")
    scale = math.sqrt(luminosity_solar)
    return {"inner_au": 0.95 * scale, "outer_au": 1.67 * scale}
