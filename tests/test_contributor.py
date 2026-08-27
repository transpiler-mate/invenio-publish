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

from invenio_rest_api_client.models import Contributor, RoleId
from pydantic import AnyUrl
from transpiler_mate.api import ContributorRole, Organization, Person

from invenio_publish.plugin import _to_contributor


def _person() -> Person:
    return Person(
        given_name="Ada",
        family_name="Lovelace",
        email="ada@example.org",
        identifier="https://orcid.org/0000-0002-1825-0097",
        affiliation=Organization(
            name="Analytical Engine Institute",
            identifier="https://ror.org/03yrm5c26",
        ),
    )


def test_person_is_converted_to_contributor_with_other_role() -> None:
    contributor = _to_contributor(_person())

    assert isinstance(contributor, Contributor)
    assert contributor.person_or_org.name == "Lovelace, Ada"
    assert contributor.person_or_org.identifiers is not None
    assert contributor.person_or_org.identifiers[0].identifier == "0000-0002-1825-0097"
    assert contributor.role.id is RoleId.OTHER
    assert contributor.affiliations is not None
    assert contributor.affiliations[0].id == "03yrm5c26"
    assert contributor.affiliations[0].name == "Analytical Engine Institute"


def test_contributor_role_is_mapped_from_credit_role() -> None:
    contributor = _to_contributor(
        ContributorRole(
            role_name="Data curator",
            additional_type=AnyUrl(
                "https://credit.niso.org/contributor-roles/data-curation/"
            ),
            contributor=_person(),
        )
    )

    assert contributor.role.id is RoleId.DATACURATOR
