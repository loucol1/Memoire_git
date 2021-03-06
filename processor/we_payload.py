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

from sawtooth_sdk.processor.exceptions import InvalidTransaction


class WePayload:
    def __init__(self,payload):
        try:
            print('payload.decode() = ', payload.decode())
            name, action, listId, listConsumption = payload.decode().split("-")
        except ValueError as e:
            raise InvalidTransaction("Invalid payload serialization") from e
        if not listId:
            raise InvalidTransaction('The ID list is required')
        if not listConsumption:
            raise InvalidTransaction('The list of the consumption is required')
        if not action:
            raise InvalidTransaction('Action is required')
        if action not in ('set'):
            raise InvalidTransaction('Invalid action: {}'.format(action))
        self._name = name
        self._action = action
        self._listId = listId
        self._listConsumption = listConsumption

    @staticmethod
    def from_bytes(payload):
        return WePayload(payload=payload)

    
    @property
    def listId(self):
        return self._listId

    @property
    def listConsumption(self):
        return self._listConsumption

    @property
    def action(self):
        return self._action

    @property
    def name(self):
        return self._name