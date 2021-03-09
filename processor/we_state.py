# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

import hashlib

from sawtooth_sdk.processor.exceptions import InternalError


WE_NAMESPACE = hashlib.sha512('we'.encode("utf-8")).hexdigest()[0:6]




def _make_we_address(name):
    return WE_NAMESPACE + \
        hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]

class Energy:
    def __init__(self, name, listId, listConsumption):
        self.name = name
        self.listId = listId
        self.listConsumption = listConsumption




class WeState:
    TIMEOUT = 3

    def __init__(self,context):
        self._context = context
        self._address_cache = {}
        print('we_state: init ok')

    def _deserialize(self, data):
        """Take bytes stored in state and deserialize them into Python
        Energy objects.

        Args:
            data (bytes): The UTF-8 encoded string stored in state.

        Returns:
            (dict): energy name (str) keys, Energy values.
        """

        energies = {}
        try:
            for energy in data.decode().split("|"):
                name, listId, listConsumption = energy.split("-")

                energies[name] = Energy(name, listId, listConsumption)
        except ValueError as e:
            raise InternalError("Failed to deserialize energy data") from e
        return energies

    def _serialize(self, energies):
        """Takes a dict of energy objects and serializes them into bytes.

        Args:
            energies (dict): energy name (str) keys, Energy values.

        Returns:
            (bytes): The UTF-8 encoded string stored in state.
        """

        energy_strs = []
        for name, g in energies.items():
            energy_str = "-".join(
                [name, g.listId, g.listConsumption])
            energy_strs.append(energy_str)

        return "|".join(sorted(energy_strs)).encode()


    def _load_energy(self, energy_name):
        address = _make_we_address(energy_name)

        if address in self._address_cache:
            if self._address_cache[address]:
                serialized_energy = self._address_cache[address]
                energies = self._deserialize(serialized_energy)
            else:
                energies = {}
        else:
            state_entries = self._context.get_state(
                [address],
                timeout=self.TIMEOUT)
            if state_entries:

                self._address_cache[address] = state_entries[0].data

                energies = self._deserialize(data=state_entries[0].data)

            else:
                self._address_cache[address] = None
                energies = {}

        return energies

    def _store_energy(self, energy_name, energies):
        address = _make_we_address(energy_name)

        state_data = self._serialize(energies)

        self._address_cache[address] = state_data

        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)
    
    def set_energy(self, energy_name, energy):
        """Store the energy in the validator state.

        Args:
            energy_name (str): The name.
            energy (Energy): The information specifying the current energy.
        """

        energies = self._load_energy(energy_name=energy_name)

        energies[energy_name] = energy
        print("set_energy in we_state")

        self._store_energy(energy_name, energies=energies)

    def get_energy(self, energy_name):
        """Get the energy associated with energy_name.

        Args:
            energy_name (str): The name.

        Returns:
            (Energy): All the information specifying a energy.
        """
        print("get_energy in we_state")
        return self._load_energy(energy_name=energy_name).get(energy_name)