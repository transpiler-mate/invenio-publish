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

# Publish your first InvenioRDM record

This tutorial publishes the metadata and source of a small CWL tool to
Zenodo Sandbox. The same command works with another InvenioRDM deployment by
changing its base URL and access token.

## 1. Install the runtime and plugin

Create and activate a virtual environment, then install both packages:

```console
python -m venv .venv
source .venv/bin/activate
python -m pip install invenio-publish transpiler-mate-runtime
```

Confirm that the runtime discovered the plugin:

```console
transpiler-mate invenio-publish --help
```

## 2. Create a metadata-bearing CWL file

Save this document as `hello.cwl`:

```yaml
cwlVersion: v1.2
$namespaces:
  s: https://schema.org/
s:name: Hello tool
s:description: Print a greeting.
s:dateCreated: "2026-08-27"
s:license: https://spdx.org/licenses/Apache-2.0
s:softwareVersion: 1.0.0
s:softwareHelp:
  s:name: Hello tool documentation
  s:url: https://example.org/hello/help
s:publisher:
  s:name: Example organization
s:author:
  s:givenName: Ada
  s:familyName: Lovelace
  s:email: ada@example.org
  s:identifier: https://orcid.org/0000-0000-0000-0000
  s:affiliation:
    s:name: Example organization
$graph:
  - id: hello
    class: CommandLineTool
    baseCommand: echo
    inputs:
      message:
        type: string
        default: Hello, world!
        inputBinding:
          position: 1
    outputs: []
```

You can also [download this example](../examples/hello.cwl).

There is deliberately no `s:identifier`: that tells the plugin to create a
record rather than a new version of an existing one. The Schema.org fields are
document-level metadata alongside `$graph`; the runtime separates them from
the CWL process and validates them before invoking the plugin.

## 3. Create and publish the record

Create a Zenodo Sandbox token with deposit permissions, then run:

```console
export INVENIO_TOKEN="your-sandbox-access-token"
transpiler-mate invenio-publish \
  --base-url https://sandbox.zenodo.org/ \
  --auth-token "$INVENIO_TOKEN" \
  --attach hello.cwl \
  hello.cwl
```

The plugin uses the Invenio REST API client to create a draft, reserve a DOI,
upload the attached CWL document, set public record and file access, and publish
the draft. The log reports the DOI and record URL.

Add the reported values to the document before publishing another release:

```yaml
s:identifier: 10.5281/zenodo.1234567
s:sameAs: https://doi.org/10.5281/zenodo.1234567
```

Replace the sample DOI with the one returned by the server. The plugin updates
the in-memory metadata during the first run; it cannot rewrite the source CWL
automatically.

## 4. Publish a new version

Increment `s:softwareVersion`, keep the existing DOI in `s:identifier`, and
run the same command again. The plugin extracts the record ID from the final
dot-separated DOI component, requests a new version, updates that draft, and
publishes it. The existing published version remains part of the record's
version history.

## Next steps

- See [Create or update a record](../how-to/publish-record.md) for concise
  production and attachment recipes.
- Review the [command options](../how-to/use-cli.md).
