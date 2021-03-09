# Copyright 2016-2018 Intel Corporation
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
# ------------------------------------------------------------------------------

import logging

from sawtooth_we.processor.we_payload import WePayload
from sawtooth_we.processor.we_state import Energy
from sawtooth_we.processor.we_state import WeState
from sawtooth_we.processor.we_state import WE_NAMESPACE


from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError


LOGGER = logging.getLogger(__name__)


class WeTransactionHandler(TransactionHandler):
    # Disable invalid-overridden-method. The sawtooth-sdk expects these to be
    # properties.
    # pylint: disable=invalid-overridden-method
    @property
    def family_name(self):
        return 'we'

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [WE_NAMESPACE]

    def apply(self, transaction, context):
        header = transaction.header
        signer = header.signer_public_key

        we_payload = WePayload.from_bytes(transaction.payload)
        print('apply in handler ok 2!')

        we_state = WeState(context)

        if we_payload.action == 'set':
            energy = we_state.get_energy(we_payload.name)

            if energy is None:
                energy = Energy(name = we_payload.name, listId = we_payload.listId, listConsumption = we_payload.listConsumption)
                

            
            energy.listId = we_payload.listId
            energy.listConsumption = we_payload.listConsumption
            energy.name = we_payload.name

            we_state.set_energy(we_payload.name, energy)
            
        else:
            raise InvalidTransaction('Unhandled action in WeTransaction Handler apply: {}'.format(
                we_payload.action))
        
        print('end apply')

