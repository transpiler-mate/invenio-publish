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

# Invenio Publisher Transpiler-Mate Plugin

`invenio-publish` turns the Schema.org metadata attached to a Common Workflow
Language (CWL) document into a published InvenioRDM record. It is a
Transpiler-Mate plugin, not a standalone command.

The plugin uses `invenio-rest-api-client`, a dedicated client for the
InvenioRDM REST API. It supports both InvenioRDM installations and Zenodo:

- metadata without an identifier creates a new draft and reserves a DOI;
- metadata with an existing DOI creates a new version of that record;
- in both cases, requested files are uploaded, the metadata is updated, and
  the draft is published.

!!! warning

    Running the plugin publishes the resulting draft. Start with an
    InvenioRDM test instance or Zenodo Sandbox.

Use these docs by intent:

- [Tutorials](tutorials/index.md): learn by completing a guided path.
- [How-to guides](how-to/index.md): solve specific tasks.
- [Reference](reference/index.md): look up commands, APIs, and configuration.
- [Explanation](explanation/index.md): understand design decisions and concepts.

## Quick start

```bash
python -m pip install invenio-publish transpiler-mate-runtime
export INVENIO_TOKEN="your-access-token"
transpiler-mate invenio-publish \
  --base-url https://sandbox.zenodo.org/ \
  --auth-token "$INVENIO_TOKEN" \
  --attach workflow.cwl \
  workflow.cwl
```

Follow [Publish your first record](tutorials/first-steps.md) for a complete CWL
example, or go directly to [create or update a record](how-to/publish-record.md).
