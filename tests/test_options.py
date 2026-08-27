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

from pathlib import Path

from pydantic import TypeAdapter

from invenio_publish.plugin import InvenioPublisherOptions


def test_attach_option_has_a_resolvable_runtime_annotation() -> None:
    field = InvenioPublisherOptions.model_fields["attach"]

    assert TypeAdapter(field.annotation).validate_python(["codemeta.json"]) == [
        Path("codemeta.json")
    ]


def test_attach_option_values_are_converted_to_paths() -> None:
    options = InvenioPublisherOptions.model_validate(
        {
            "base_url": "https://sandbox.zenodo.org/",
            "auth_token": "secret",
            "attach": ["codemeta.json"],
        }
    )

    assert options.attach == [Path("codemeta.json")]
