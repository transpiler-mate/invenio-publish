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

# Use the command line

Invoke the installed plugin through the Transpiler-Mate runtime:

```console
transpiler-mate invenio-publish [OPTIONS] SOURCE
```

`SOURCE` is a CWL document location supported by the runtime. Its
document-level Schema.org metadata must satisfy the Transpiler-Mate
`SoftwareApplication` model.

## Plugin options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `--base-url URL` | Yes | — | Base URL of the InvenioRDM service, for example `https://sandbox.zenodo.org/`. |
| `--auth-token TEXT` | Yes | — | Access token authorized to create and publish deposits. |
| `--attach PATH` | No | none | File to upload to the record. Repeat the option to upload multiple files. |

For example:

```console
transpiler-mate invenio-publish \
  --base-url https://invenio.example.org/ \
  --auth-token "$INVENIO_TOKEN" \
  --attach workflow.cwl \
  --attach README.md \
  workflow.cwl
```

The source document is not attached automatically; add it explicitly with
`--attach` when it should be part of the deposit. Each attachment must exist
and must have a distinct filename.

The runtime also exposes source-access options such as OCI credentials and an
OAuth bearer token. Inspect the installed interface for the complete list:

```console
transpiler-mate invenio-publish --help
```
