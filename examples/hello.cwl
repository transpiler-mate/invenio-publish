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
