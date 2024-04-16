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

from bumble.colors import color
from bumble.device import Device, Peer
from bumble.profiles.device_information_service import DeviceInformationServiceProxy
from bumble.transport import open_transport_or_link
from bumble.utils import AsyncRunner


# -----------------------------------------------------------------------------
class Listener(Device.Listener):
    def __init__(self, device):
        self.device = device

    @AsyncRunner.run_in_task()
    # pylint: disable=invalid-overridden-method
    async def on_connection(self, connection):
        print(f'=== Connected to {connection}')

# -----------------------------------------------------------------------------
async def main():
    if len(sys.argv) != 4:
        print(
            'Usage: alice.py <device-config> <transport-spec> <bluetooth-address>'
        )
        print('example: alice.py alice.json hci-socket:0 FA:F2:F2:F2:F2:F2')
        return

    print('<<< connecting to HCI...')
    async with await open_transport_or_link(sys.argv[2]) as (hci_source, hci_sink):
        device = Device.from_config_file_with_hci(sys.argv[1], hci_source, hci_sink)
        device.listener = Listener(device)
        await device.power_on()

        target_address = sys.argv[3]
        print(f'=== Connecting to {target_address}...')
        connection = await device.connect(target_address)
        print(f'=== Client: connected to {connection}')

        peer = Peer(connection)
        device_information_service = await peer.discover_service_and_create_proxy(
            DeviceInformationServiceProxy
        )
        if device_information_service.manufacturer_name is not None:
            print(
                color('Manufacturer Name: ', 'green'),
                await device_information_service.manufacturer_name.read_value(),
            )
        else:
            print(color('Manufacturer Name not available', 'red'))

        await asyncio.get_running_loop().create_future()

# -----------------------------------------------------------------------------
# logging.basicConfig(level=os.environ.get('BUMBLE_LOGLEVEL', 'DEBUG').upper())
asyncio.run(main())