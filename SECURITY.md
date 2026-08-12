# Security Policy

## Supported surface

Security support applies to the latest released DSLModel distribution and to the admitted production surface on `main`:

- deterministic OpenAPI-to-Pydantic model manufacture;
- strict semantic self-tests and status reporting;
- artifact receipt and replay;
- the packaged `dsl` CLI and production container/release path.

Historical command modules explicitly reported by `dsl dsl inventory --json` as `NOT_ADMITTED` or `UNSUPPORTED` are preserved for reversible recovery and are not represented as supported production capabilities. A report involving legacy source is still relevant when it can affect the default installation, admitted runtime, build, release, or supply chain.

## Reporting a vulnerability

Prefer GitHub Private Vulnerability Reporting from the repository Security tab when that facility is available. Otherwise contact `info@chatmangpt.com` with the subject `dslmodel security report`.

Include the affected version or commit SHA, the admitted surface involved, reproduction steps, expected impact, and any proposed mitigation. Do not include credentials, tokens, private customer data, or live exploit material beyond what is necessary to reproduce the issue safely.

Please avoid opening a public issue for an undisclosed vulnerability.

## Security boundary

The admitted core is local and deterministic: it does not grant ambient shell, GitHub, cloud, LLM, deployment, or autonomous-agent execution authority. Release publication is separated from pull-request verification; PR image builds have read-only repository authority and cannot publish packages. Release images are built with SBOM and provenance attestations.
