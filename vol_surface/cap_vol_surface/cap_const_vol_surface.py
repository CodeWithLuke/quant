from vol_surface.cap_vol_surface.abs_cap_surface import AbsCapSurface


class CapConstVolSurface(AbsCapSurface):

    def __init__(self, vol):
        self._vol = vol

    def interpolate_vol(self, expiry, tenor):
        return self._vol
