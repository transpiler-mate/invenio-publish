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

import hashlib
import time
from datetime import date
from pathlib import Path  # noqa: TC003 - Pydantic resolves this annotation at runtime.
from typing import TYPE_CHECKING, Annotated, Any
from urllib.parse import urlparse

from invenio_rest_api_client.api.drafts.publish_a_draft_record import (
    sync as publish_a_draft_record,
)
from invenio_rest_api_client.api.drafts.reserve_a_doi import sync as reserve_a_doi
from invenio_rest_api_client.api.drafts.update_a_draft_record import (
    sync as update_a_draft_record,
)
from invenio_rest_api_client.api.drafts_files_upload.step_1_start_draft_file_uploads import (
    sync as step_1_start_draft_file_uploads,
)
from invenio_rest_api_client.api.drafts_files_upload.step_2_upload_a_draft_files_content import (
    sync as step_2_upload_a_draft_files_content,
)
from invenio_rest_api_client.api.drafts_files_upload.step_3_complete_a_draft_file_upload import (
    sync as step_3_complete_a_draft_file_upload,
)
from invenio_rest_api_client.api.records.create_a_draft_record import (
    sync as create_a_draft_record,
)
from invenio_rest_api_client.api.records_versions.create_a_new_version import (
    sync as create_a_new_version,
)
from invenio_rest_api_client.client import AuthenticatedClient as InvenioClient
from invenio_rest_api_client.models import (
    Access,
    AccessFiles,
    AccessRecord,
    Affiliation,
    AlternateIdentifier,
    Contributor,
    CreateADraftRecordBody,
    Creator,
    Files,
    FileTransferItem,
    Identifier,
    IdentifierScheme,
    Metadata,
    PersonOrOrg,
    PersonOrOrgIdentifierScheme,
    PersonOrOrgType,
    RDMRecord,
    ResourceType,
    ResourceTypeId,
    Role,
    RoleId,
    UpdateDraftRecord,
    ZenodoRecord,
)
from invenio_rest_api_client.types import File as FileContent
from loguru import logger
from pydantic import AnyUrl, BaseModel, ConfigDict, Field
from transpiler_mate.api import (
    AuthorRole,
    ContributorRole,
    Person,
    transpiler_plugin,
)
from transpiler_mate.api import (
    Role as SWARole,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from transpiler_mate.api import TranspilerContext


class InvenioPublisherOptions(BaseModel):
    """Options accepted by the Invenio Publisher Transpiler-Mate Plugin plugin."""

    model_config = ConfigDict(extra="forbid")

    base_url: Annotated[AnyUrl, Field(description="The Invenio server base URL")]

    auth_token: Annotated[str, Field(description="The Invenio Access token")]

    attach: Annotated[
        list[Path],
        Field(
            default_factory=list,
            description="Generic textual/binary file(s) to attach to the Invenio record",
        ),
    ]


__ROLES_MAPPING_: Mapping[AnyUrl, RoleId] = {
    AnyUrl(
        "https://credit.niso.org/contributor-roles/conceptualization/"
    ): RoleId.PROJECTLEADER,
    AnyUrl(
        "https://credit.niso.org/contributor-roles/data-curation/"
    ): RoleId.DATACURATOR,
    AnyUrl(
        "https://credit.niso.org/contributor-roles/formal-analysis/"
    ): RoleId.RESEARCHER,
    AnyUrl(
        "https://credit.niso.org/contributor-roles/funding-acquisition/"
    ): RoleId.SPONSOR,
    AnyUrl(
        "https://credit.niso.org/contributor-roles/investigation/"
    ): RoleId.DATACOLLECTOR,
    AnyUrl("https://credit.niso.org/contributor-roles/methodology/"): RoleId.RESEARCHER,
    AnyUrl(
        "https://credit.niso.org/contributor-roles/project-administration/"
    ): RoleId.PROJECTMANAGER,
    AnyUrl("https://credit.niso.org/contributor-roles/resources/"): RoleId.DATAMANAGER,
    AnyUrl("https://credit.niso.org/contributor-roles/software/"): RoleId.RESEARCHER,
    AnyUrl("https://credit.niso.org/contributor-roles/supervision/"): RoleId.SUPERVISOR,
    AnyUrl("https://credit.niso.org/contributor-roles/validation/"): RoleId.RESEARCHER,
    AnyUrl(
        "https://credit.niso.org/contributor-roles/visualization/"
    ): RoleId.RESEARCHER,
    AnyUrl(
        "https://credit.niso.org/contributor-roles/writing-original-draft/"
    ): RoleId.RESEARCHER,
    AnyUrl(
        "https://credit.niso.org/contributor-roles/writing-review-editing/"
    ): RoleId.EDITOR,
}


def _md5(file: Path) -> str:
    # Invenio's file API requires an MD5 checksum; it is not used for security.
    hash_md5 = hashlib.md5(usedforsecurity=False)
    with file.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _to_identifier(url_identifier: str | AnyUrl) -> Identifier:
    _, netloc, path, _, _, _ = urlparse(str(url_identifier))
    return Identifier(
        scheme=PersonOrOrgIdentifierScheme(netloc.split(".")[0]),
        identifier=path.split("/")[-1],
    )


def _affiliation_identifier(url_identifier: str | AnyUrl) -> str:
    _, _, path, _, _, _ = urlparse(str(url_identifier))
    return path.split("/")[-1]


def _to_creator(author: Person | SWARole) -> Creator:
    role_id: RoleId = RoleId.OTHER

    if isinstance(author, SWARole):
        if author.additional_type:
            role_id = __ROLES_MAPPING_.get(author.additional_type, RoleId.OTHER)

        if isinstance(author, AuthorRole):
            author = author.author
        elif isinstance(author, ContributorRole):
            author = author.contributor

    creator: Creator = Creator(
        person_or_org=PersonOrOrg(
            type=PersonOrOrgType.PERSONAL,
            name=f"{author.family_name}, {author.given_name}"
            if isinstance(author, Person)
            else None,
            given_name=author.given_name if isinstance(author, Person) else None,
            family_name=author.family_name if isinstance(author, Person) else None,
            identifiers=[_to_identifier(author.identifier)]
            if isinstance(author, Person) and author.identifier
            else None,
        ),
        role=Role(id=role_id),
    )

    if isinstance(author, Person):
        creator.affiliations = []
        for affiliation in (
            author.affiliation
            if isinstance(author.affiliation, list)
            else [author.affiliation]
        ):
            creator.affiliations.append(
                Affiliation(
                    id=_affiliation_identifier(affiliation.identifier)
                    if affiliation.identifier
                    else None,
                    name=affiliation.name,
                )
            )

    return creator


def _to_contributor(contributor: Person | ContributorRole) -> Contributor:
    role_id: RoleId = RoleId.OTHER

    if isinstance(contributor, ContributorRole):
        if contributor.additional_type:
            role_id = __ROLES_MAPPING_.get(
                contributor.additional_type,
                RoleId.OTHER,
            )

        contributor = contributor.contributor

    invenio_contributor = Contributor(
        person_or_org=PersonOrOrg(
            type=PersonOrOrgType.PERSONAL,
            name=f"{contributor.family_name}, {contributor.given_name}",
            given_name=contributor.given_name,
            family_name=contributor.family_name,
            identifiers=[_to_identifier(contributor.identifier)]
            if contributor.identifier
            else None,
        ),
        role=Role(id=role_id),
        affiliations=[],
    )

    for affiliation in (
        contributor.affiliation
        if isinstance(contributor.affiliation, list)
        else [contributor.affiliation]
    ):
        invenio_contributor.affiliations.append(
            Affiliation(
                id=_affiliation_identifier(affiliation.identifier)
                if affiliation.identifier
                else None,
                name=affiliation.name,
            )
        )

    return invenio_contributor


def _finalize(
    draft_id: str,
    uploading_files: Iterable[Path],
    session_client: InvenioClient,
    invenio_metadata: Metadata,
) -> None:
    uploading_files_names = ", ".join([file.name for file in uploading_files])
    logger.info(
        f"Drafting file upload [{uploading_files_names}] to Record '{draft_id}'..."
    )

    step_1_start_draft_file_uploads(
        draft_id=draft_id,
        client=session_client,
        body=[
            FileTransferItem(
                key=file.name,
                size=file.stat().st_size,
                checksum=f"md5:{_md5(file)}",
            )
            for file in uploading_files
        ],
    )

    logger.success(
        f"File upload {uploading_files_names} drafted to Record '{draft_id}'"
    )

    for file in uploading_files:
        logger.info(f"Uploading file content '{file.name})' to Record '{draft_id}'...")

        with file.open("rb") as binary_stream:
            step_2_upload_a_draft_files_content(
                draft_id=draft_id,
                file_name=file.name,
                body=FileContent(
                    file_name=file.name,
                    mime_type="application/octet-stream",
                    payload=binary_stream,
                ),
                client=session_client,
            )

        logger.success(f"File content {file.name} uploaded to Record {draft_id}")

        logger.info(f"Completing file upload {file.name}] to Record '{draft_id}'...")

        step_3_complete_a_draft_file_upload(
            draft_id=draft_id, file_name=file.name, client=session_client
        )

        logger.success(f"File upload {file.name} to Record '{draft_id}' completed")

    update_a_draft_record(
        draft_id=draft_id,
        body=UpdateDraftRecord(
            access=Access(files=AccessFiles.PUBLIC, record=AccessRecord.PUBLIC),
            files=Files(enabled=True),
            metadata=invenio_metadata,
        ),
        client=session_client,
    )

    logger.success(f"Draft Record '{draft_id}' metadata updated!")

    logger.info(f"Publishing the Draft Record '{draft_id}'...")

    publish_a_draft_record(draft_id=draft_id, client=session_client)

    logger.success(f"Draft Record '{draft_id}' metadata updated!")


@transpiler_plugin(
    name="invenio-publish",
    description="Invenio Publisher Transpiler-Mate Plugin.",
    options_model=InvenioPublisherOptions,
)
def invenio_publish(
    context: TranspilerContext, options: InvenioPublisherOptions
) -> None:
    """Invenio Publisher Transpiler-Mate Plugin."""
    with InvenioClient(
        base_url=str(options.base_url), token=options.auth_token
    ) as invenio_rest_client:
        logger.debug("Setting up the HTTP logger...")
        from .utils import init_http_logging

        init_http_logging(invenio_rest_client.get_httpx_client())
        logger.debug("HTTP logger correctly setup")

        draft_id: str = ""

        if not context.metadata.identifier:
            logger.warning(
                "'identifier' key not found in source document, reserving a DOI..."
            )

            draft_record: Any | RDMRecord | ZenodoRecord | None = create_a_draft_record(
                client=invenio_rest_client, body=CreateADraftRecordBody()
            )

            if draft_record and isinstance(draft_record, (RDMRecord, ZenodoRecord)):
                draft_id = str(draft_record.id)

            logger.success(f"Successfully reserved a draft record with ID: {draft_id}")

            doi: Any | dict[str, Any] | None = reserve_a_doi(
                draft_id=draft_id, client=invenio_rest_client
            )

            if doi and isinstance(doi, dict):
                context.metadata.identifier = doi["doi"]
                context.metadata.same_as = doi["doi_url"]

                logger.success(
                    f"Successfully reserved a DOI with ID {context.metadata.identifier} (URL: {context.metadata.same_as})"
                )

                logger.warning(f"""Don't forget to update your source CWL Workflow with following metadata:
    s:identifier: {context.metadata.identifier}
    s:sameAs: {context.metadata.same_as}""")
        else:
            logger.info(
                f"Identifier {context.metadata.identifier} already assigned to {context.source}"
            )

            record_id: str = str(context.metadata.identifier).split(".")[-1]

            logger.info(
                f"Creating a new version for already existing Record {record_id}"
            )

            version: Any | RDMRecord | ZenodoRecord | None = create_a_new_version(
                record_id=record_id, client=invenio_rest_client
            )

            if (
                version
                and isinstance(version, (RDMRecord, ZenodoRecord))
                and version.id
            ):
                draft_id = str(version.id)

            logger.info(
                f"New version {draft_id} for already existing Record {record_id} created!"
            )

        invenio_metadata: Metadata = Metadata(
            identifiers=[
                AlternateIdentifier(
                    identifier=str(context.metadata.identifier),
                    scheme=IdentifierScheme.DOI,
                )
            ]
            if context.metadata.identifier
            else None,
            resource_type=ResourceType(id=ResourceTypeId.WORKFLOW),
            title=context.metadata.name,
            publication_date=date.fromtimestamp(time.time()).isoformat(),
            publisher=context.metadata.publisher.name,
            description=context.metadata.description
            if context.metadata.description
            else None,
            creators=list(
                map(
                    _to_creator,
                    context.metadata.author
                    if isinstance(context.metadata.author, list)
                    else [context.metadata.author],
                )
            ),
            contributors=list(
                map(
                    _to_contributor,
                    context.metadata.contributor
                    if isinstance(context.metadata.contributor, list)
                    else [context.metadata.contributor],
                )
            )
            if context.metadata.contributor
            else None,
            version=context.metadata.software_version,
        )

        _finalize(
            draft_id=draft_id,
            uploading_files=options.attach,
            session_client=invenio_rest_client,
            invenio_metadata=invenio_metadata,
        )

        logger.success(f"Record available on '{options.base_url}/records/{draft_id}'")
