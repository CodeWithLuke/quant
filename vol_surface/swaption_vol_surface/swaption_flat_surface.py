from vol_surface.swaption_vol_surface.abs_swaption_surface import AbsSwaptionSurface


class SwaptionFlatVolSurface(AbsSwaptionSurface):
    def __init__(self, vol: float):
        self._vol = vol

    def interpolate_vol(self, expiry, tenor):
        return self._vol

    def bump_surface(self, n_bps_bump=1):
        raise NotImplementedError("Bumping Surface not supported for constant vol.")