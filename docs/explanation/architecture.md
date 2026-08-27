<!--
Copyright 2026 Transpiler-Mate

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Architecture

`invenio-publish` is an installed Transpiler-Mate plugin. The runtime resolves
the CWL source and normalizes its document-level Schema.org metadata as a
`SoftwareApplication`; the plugin owns the InvenioRDM interaction.

The plugin creates an authenticated `invenio-rest-api-client` session using
`base_url` and `auth_token`, then chooses one of two paths:

```text
No metadata identifier  -> create draft -> reserve DOI
Existing DOI identifier -> derive record ID -> create new-version draft
                                           |
                                           v
                         upload files -> update metadata -> publish
```

The metadata mapping uses the InvenioRDM workflow resource type and transfers
the title, description, publisher, software version, creators, contributors,
affiliations, ORCID-like identifiers, and supported contributor roles. Access
to the record and attached files is set to public before publication.

The generated client models both regular `RDMRecord` and `ZenodoRecord`
responses, which is why the same code path can target a compatible standalone
InvenioRDM service or Zenodo.

The package follows this layout:

```text
src/invenio_publish/
tests/
docs/
```

The package does not expose its own executable. Its Python entry point is
discovered by `transpiler-mate-runtime`, which generates the command options
from `InvenioPublisherOptions`.
