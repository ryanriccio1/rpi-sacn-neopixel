import customlogs
from universe import Universe
from customlogs import Log


class SacnUniverse(Universe):
    client = None

    def __init__(self, universe, pixel_strands):
        super().__init__(universe, pixel_strands)
        SacnUniverse.client.register_listener('universe', self._set_data, universe=self._universe)

        Log.write_log("Joining multicast stream...", Log.LogLevel.LEVEL3)
        SacnUniverse.client.join_multicast(self._universe)
        Log.write_log(f"Universe {self._universe} created...", Log.LogLevel.LEVEL1)
