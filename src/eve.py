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

from bumble.device import Device
from bumble.profiles.device_information_service import DeviceInformationService
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
    if len(sys.argv) != 5:
        print('Usage: eve.py <alice-device-config-1> <alice-transport-spec-1> <bob-device-config-2> <bob-transport-spec-2>')
        print('example: eve.py alice.json hci-socket:0 bob.json hci-socket:1')
        return

    print('<<< connecting to HCI used for Bob ...')
    async with await open_transport_or_link(sys.argv[4]) as (bob_hci_source, bob_hci_sink):
        print('<<< connecting to HCI used for Alice ...')
        async with await open_transport_or_link(sys.argv[2]) as (alice_hci_source, alice_hci_sink):
            alice_device = Device.from_config_file_with_hci(sys.argv[1], alice_hci_source, alice_hci_sink)
            alice_device.listener = Listener(alice_device)
            await alice_device.power_on()

            bob_device = Device.from_config_file_with_hci(sys.argv[3], bob_hci_source, bob_hci_sink)
            bob_device.add_service(DeviceInformationService(
                manufacturer_name="Bob hates Alice!",
            ))
            bob_device.listener = Listener(bob_device)
            await bob_device.power_on()
            bob_address = bob_device.config.address

            print(f'=== Connecting to Bob {bob_address}...')
            await alice_device.connect(bob_address)

            print(f'=== Starting to advertise as Bob {bob_address}')
            await bob_device.start_advertising()

        await asyncio.get_running_loop().create_future()

# -----------------------------------------------------------------------------
# logging.basicConfig(level=os.environ.get('BUMBLE_LOGLEVEL', 'DEBUG').upper())
asyncio.run(main())