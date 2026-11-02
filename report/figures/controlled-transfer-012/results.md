# Controlled transfer pilot results

Frozen plan: `fddddb72f75b21e6b98f89506ea7634c2ec348f76ee4e5e4a2ccd2d5c035ebb3`.

One authored source pool; unchanged cached model repairs; nine new controlled cases. No additional inference.

| Policy | Verified / cases | Functional | Fresh | Explicit refusals |
| --- | ---: | ---: | ---: | ---: |
| parent | 3 / 9 | 9 | 3 | 0 |
| repair-00 | 9 / 9 | 9 | 9 | 0 |
| repair-01 | 9 / 9 | 9 | 9 | 0 |
| authored-rerun | 9 / 9 | 9 | 9 | 0 |

| Selector | Previously selected policy | Verified / cases |
| --- | --- | ---: |
| failure-family | repair-00 | 9 / 9 |
| generic | repair-00 | 9 / 9 |
| source-only | repair-00 | 9 / 9 |

Failure-family minus source-only and generic verified-completion differences: source-only: +0.000, generic: +0.000.
No interval: one source pool. Equal outcomes do not establish equivalence or a selector advantage.

36 trials; 57 Docker workers; 59.54 summed worker seconds. Zero new model calls or API calls; shared generation subscription dollar cost remains unknown.

The authored reference is not selectable. Task implementations are authored; the generated programs choose completion/verification actions. This does not evaluate native Sakana evolution, naturally occurring model failures, or interactive repair of new repositories.
