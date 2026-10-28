<!-- AUTO-GENERATED FILE — regenerate through `make gen` from the workspace root. -->
<!-- Source of truth: `<workspace-root>/docs/guides/engine.md`; adjust that workspace source, never this member projection. -->

# flext-tap-oracle-wms - FLEXT Engine Law — Rope-Only Python Interpretation

<!-- TOC START -->

- [What stays canonical](#what-stays-canonical)
- [Isolation by repository](#isolation-by-repository)
- [Deprecation window](#deprecation-window)
- [Correction authority](#correction-authority)
- [Blocked capabilities](#blocked-capabilities)

<!-- TOC END -->

> Project profile: `flext-tap-oracle-wms`

| Workspace declaration | Accepted decision |
| --- | --- |
| This page; the living census and wave status (beads `flext-pipol`, `flext-u9h2i`). | ADR-028 Decision 17, amendment 2026-10-28 |

Operator law, 2026-10-28: **rope is the only accepted Python interpreter in
FLEXT's own code.** The flext-infra engine never parses, analyzes or rewrites
Python source with the `ast` module, `libcst`, or `re` applied to code — every
such site is deprecated and migrates to rope's PyModules from the single
indexed project.

## What stays canonical

| Engine | Domain |
| --- | --- |
| Rope | Python analysis and refactoring: one loop and native session/index per repository per invocation, shared by DI; small dependency-closed cohorts use the same publisher within the five-second transaction budget (ADR-028 Decision 17; ADR-018 transaction contract). This does not mean one physical transaction for the whole invocation. Native refactorings first (rename, move, restructure, ImportOrganizer); custom transforms operate on the indexed PyModules through rope's public API. |
| ast-grep | Declarative rules (detection AND fix), one generalized rule per law (ADR-028 Decision 11, Decision 18); the rules catalog is SSOT data. |
| sed | Non-Python text. |
| Generator (`make gen`) | Projections from declared templates. |

## Isolation by repository

The engine never resolves a member module through the interpreter: the
interpreter may elect stdlib modules only (`sys.stdlib_module_names` gate in the
rope native project); member code resolves through the repository's own rope
index. A fresh interpreter — where genuinely required — uses
`u.Infra.runtime_python(root)` and the physical environment elected by checkout
topology: the workspace-owned `.venv` for an attached member, or the checkout's
own `.venv` in standalone mode (ADR-003, Decision 5). It never borrows the engine's
ambient environment. Divergent member libraries never leak into engine analysis.

## Deprecation window

Superseded engine routes follow the workspace's deprecated-signature window:
a typed warning marks the route (`compat: <route> -> <new owner>; fix:
<rewire>`), every use is reported as a finding in the consumer (the census),
rewires land in waves through `make mod`, and the route is deleted when the
census reaches zero. Detection without a fix form is a rule defect.

## Correction authority

Violations in member code are corrected by the engine — declarative rule fixes
for mechanical shapes, rope refactorings for semantic ones — through
`make mod`. Manual member edits are the exception of the exception, justified
in the commit.

## Blocked capabilities

A site with no rope-expressible equivalent (for example, runtime-object
semantics: `is`-identity, `__mro__` of live classes, protocol checks) is
reported as `BLOCKED-ON-ROPE-CAPABILITY` with the rope API evaluated, and
stays untouched until the operator rules; an alternative parser is never
silently kept.
