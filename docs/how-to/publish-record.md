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

# Create or update an InvenioRDM record

The plugin selects the operation from the CWL document's Schema.org
`s:identifier` metadata.

## Create a record

Remove `s:identifier` (and any stale `s:sameAs`) from the document, then run:

```console
transpiler-mate invenio-publish \
  --base-url https://sandbox.zenodo.org/ \
  --auth-token "$INVENIO_TOKEN" \
  --attach workflow.cwl \
  workflow.cwl
```

The Invenio client performs this sequence:

1. Create a draft record and reserve its DOI.
2. Map the CWL Schema.org metadata to InvenioRDM metadata.
3. Upload every `--attach` file.
4. Set public access and publish the draft.

Copy the DOI and DOI URL printed in the log into the source document as
`s:identifier` and `s:sameAs`. This preserves the record identity for the next
release.

## Update a record

For a record previously created by this plugin, retain its DOI in the source:

```yaml
s:identifier: 10.5281/zenodo.1234567
s:sameAs: https://doi.org/10.5281/zenodo.1234567
s:softwareVersion: 1.1.0
```

Run the same command. Presence of `s:identifier` makes the plugin create a new
draft version, upload the selected files, replace that draft's mapped
metadata, and publish it. "Update" therefore means **publish a new version**;
the plugin does not modify a published version in place.

The current implementation derives the Invenio record ID from the last
dot-separated component of the DOI (`1234567` above). Use the DOI returned by
the target server and do not substitute an arbitrary identifier.

## Use another InvenioRDM service

Replace the Zenodo Sandbox URL and token with those of the target deployment:

```console
transpiler-mate invenio-publish \
  --base-url https://invenio.example.org/ \
  --auth-token "$INVENIO_TOKEN" \
  workflow.cwl
```

The service must expose compatible InvenioRDM record, draft, version, DOI, and
file APIs. The token must carry the permissions required to create and publish
records. Test the workflow against the service's sandbox or staging instance
before using a production repository.
