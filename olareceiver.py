import re
from universe import Universe
from ola.OlaClient import OlaClient
from customlogs import Log


class OlaUniverse(Universe):
    device = None
    wrapper = None
    client = None
    found_device = False

    def __init__(self, universe, pixel_strands):
        super().__init__(universe, pixel_strands)
        Log.write_log(f"Created OLA Universe {self._universe}.", Log.LogLevel.LEVEL3)
        OlaUniverse.unpatch_all(OlaUniverse.client)
        self.patch()
        Log.write_log(f"Registering OLA Universe {self._universe}.", Log.LogLevel.LEVEL3)
        OlaUniverse.client.RegisterUniverse(self._universe, OlaUniverse.client.REGISTER, self._set_data)
        Log.write_log(f"OLA Universe {self._universe} started...", Log.LogLevel.LEVEL1)

    def patch(self):
        Log.write_log(f"Patching OLA Universe {self._universe}...", Log.LogLevel.LEVEL1)
        OlaUniverse.client.PatchPort(OlaUniverse.device.alias, port=OlaUniverse.device.input_ports[self._universe].id,
                                     is_output=False, action=OlaClient.PATCH, universe=self._universe)

    @staticmethod
    def unpatch_all(client):
        Log.write_log("Unpatching all universes...", Log.LogLevel.LEVEL3)
        for port in OlaUniverse.device.input_ports:
            Log.write_log(f"Unpatching Port {port}...", Log.LogLevel.LEVEL4)
            client.PatchPort(OlaUniverse.device.alias, port.id, False, OlaClient.UNPATCH, 1)

    @staticmethod
    def get_device(status, devices):
        # check current devices
        if status.Succeeded():
            for current_device in sorted(devices):
                Log.write_log(f"Device: {current_device.name}", Log.LogLevel.LEVEL3)
                for port in current_device.input_ports:
                    Log.write_log(f"Port {port.id}: {port.description}", Log.LogLevel.LEVEL3)
                result = re.match(r"E1\.31", current_device.name)
                if result:
                    Log.write_log(f"Found OLA SACN Device {current_device.alias}: "
                                  f"{current_device.name}", Log.LogLevel.LEVEL2)
                    OlaUniverse.device = current_device
                    OlaUniverse.found_device = True
                    Log.write_log(f"{OlaUniverse.device}, found_device={OlaUniverse.found_device}: "
                                  f"Stopping wrapper...", Log.LogLevel.LEVEL4)
                    OlaUniverse.wrapper.Stop()
        else:
            Log.write_log(f"Error: {status.message}", Log.LogLevel.LEVEL1)
