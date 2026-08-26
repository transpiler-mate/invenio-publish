# Copyright 2026 Transpiler-Mate
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

"""transpiler-mate plugin for Invenio Publisher Transpiler-Mate Plugin."""

from __future__ import annotations

from loguru import logger
from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field
from transpiler_mate.api import (
    PluginExecutionError,
    PluginFailureError,
    transpiler_plugin,
)

if TYPE_CHECKING:
    from transpiler_mate.api import TranspilerContext

class InvenioPublisherOptions(BaseModel):
    """Options accepted by the Invenio Publisher Transpiler-Mate Plugin plugin."""

    model_config = ConfigDict(extra="forbid")


@transpiler_plugin(
    name="invenio-publish",
    description="Invenio Publisher Transpiler-Mate Plugin.",
    options_model=InvenioPublisherOptions,
)
def invenio_publish(context: TranspilerContext, options: InvenioPublisherOptions) -> None:
    """Invenio Publisher Transpiler-Mate Plugin."""
    pass
