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

[![PyPI - Version](https://img.shields.io/pypi/v/invenio-publish.svg)](https://pypi.org/project/invenio-publish)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/invenio-publish.svg)](https://pypi.org/project/invenio-publish)

`invenio-publish` publishes the Schema.org metadata of a CWL document as an
InvenioRDM record. It uses the dedicated `invenio-rest-api-client` for the
record, draft, DOI, file-upload, versioning, and publication APIs. The same
client and workflow are compatible with Zenodo.

- Without `s:identifier`, the plugin creates a draft, reserves a DOI, uploads
  any attachments, and publishes a new record.
- With an existing DOI in `s:identifier`, the plugin creates and publishes a
  new version of that record.

Install the plugin and the Transpiler-Mate runtime in the same environment:

```console
python -m pip install invenio-publish transpiler-mate-runtime
```

Then publish to an InvenioRDM instance (Zenodo Sandbox is shown here):

```console
export INVENIO_TOKEN="your-access-token"
transpiler-mate invenio-publish \
  --base-url https://sandbox.zenodo.org/ \
  --auth-token "$INVENIO_TOKEN" \
  --attach workflow.cwl \
  workflow.cwl
```

This command publishes the draft; use a sandbox instance while testing. See
the [documentation](https://Transpiler-Mate.github.io/invenio-publish/) for a
complete metadata example and the create/update workflow.

## Documentation

Project documentation is published at: https://Transpiler-Mate.github.io/invenio-publish/

## Contribute

Submit a [Github issue](https://github.com/Transpiler-Mate/invenio-publish/issues) if you have comments or suggestions.

### Local quality checks

Install [Hatch](https://hatch.pypa.io/) and [Taskfiles](https://taskfile.dev/docs/guide) then install the Git hook:

```console
task quality:pre-commit:install
```

Every commit runs Ruff (including the configured McCabe complexity limit),
Ruff formatting, strict mypy checks, and the pytest suite.

Run the complete hook explicitly with:

```console
task quality:pre-commit:run
```

## License

[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%20License%202.0-blue)](https://www.apache.org/licenses/LICENSE-2.0)
