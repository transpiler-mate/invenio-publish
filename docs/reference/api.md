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

# API reference

## Plugin

The package registers the following Transpiler-Mate entry point:

| Property | Value |
| --- | --- |
| Entry-point group | `transpiler_mate.plugins` |
| Entry-point name | `invenio-publish` |
| Entry-point object | `invenio_publish.plugin:invenio_publish` |

The execution function receives a normalized `TranspilerContext` and an
`InvenioPublisherOptions` instance. Normally the Transpiler-Mate runtime builds
both and invokes the plugin.

::: invenio_publish.plugin.invenio_publish

## Options

::: invenio_publish.plugin.InvenioPublisherOptions

## Client compatibility

The implementation uses `invenio-rest-api-client`'s authenticated client and
its draft, record-version, DOI, file-upload, metadata-update, and publication
operations. Responses may be either `RDMRecord` or `ZenodoRecord`, allowing the
same plugin flow to work with compatible InvenioRDM deployments and Zenodo.
