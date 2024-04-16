# Copyright 2021-2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import asyncio
import sys

from bumble.device import Device, Connection
from bumble.profiles.device_information_service import DeviceInformationService
from bumble.transport import open_transport_or_link


# -----------------------------------------------------------------------------
class Listener(Device.Listener, Connection.Listener):
    def __init__(self, device):
        self.device = device

    def on_connection(self, connection):
        print(f'=== Connected to {connection}')
        connection.listener = self

    def on_disconnection(self, reason):
        print(f'### Disconnected, reason={reason}')


# -----------------------------------------------------------------------------
async def main():
    if len(sys.argv) != 3:
        print('Usage: bob.py <device-config> <transport-spec> ')
        print('example: bob.py bob.json hci-socket:0')
        return

    print('<<< connecting to HCI...')
    async with await open_transport_or_link(sys.argv[2]) as (hci_source, hci_sink):
        device = Device.from_config_file_with_hci(sys.argv[1], hci_source, hci_sink)
        device.listener = Listener(device)
        device.add_service(DeviceInformationService(
            manufacturer_name="Bob loves Alice!",
        ))

        await device.power_on()

        print(f'=== Starting to advertise')
        await device.start_advertising(auto_restart=True)
        await hci_source.wait_for_termination()

# -----------------------------------------------------------------------------
# logging.basicConfig(level=os.environ.get('BUMBLE_LOGLEVEL', 'DEBUG').upper())
asyncio.run(main())
