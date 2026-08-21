# Context routing performance baseline

This directory keeps reproducible synthetic measurements and one deliberately anonymous
production-shaped observation. Performance varies by repository, filesystem, Git state,
antivirus, and hardware; the values below are evidence for this release, not a universal
latency promise.

## Anonymous production-shaped observation

The source repository is intentionally not identified. No repository, remote, branch,
commit, task/session ID, query, feature title, code path, document body, log, configuration,
source content, username, host, or Resume Capsule body is stored here.

| Runtime | Cache | Packs | Fingerprint candidates | Route time | Initial Required reads | Resume Capsule |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| v0.5.10 | none | 59 | all live Packs | about 10.55 s | 1 file | 2,706 characters |
| v0.6.0 candidate | cold | 59 | 18 | 1.365 s | 1 file | not available in this rerun |
| v0.6.0 candidate | warm | 59 | 18 | 0.913 s | 1 file | not available in this rerun |

The candidate was about 7.7x faster cold and 11.6x faster warm in this observation. The
earlier route also exposed unrelated legacy evidence paths in its private Capsule. v0.6.0
ranks evidence against the selected Pack, omits unrelated legacy paths, and reports only the
omitted count. The rerun did not have an accessible matching private session, so it did not
invent or infer a replacement Capsule measurement.

## Reproducible synthetic benchmark

Run from the repository root:

```text
python benchmarks/context_router_benchmark.py
```

The script creates a temporary Git repository with 59 fake Context Packs, unique fake source
files, and one fake private checkpoint. It measures cold and warm JSON routes, verifies that
both select the same Pack and Required reads, checks the Context Bundle budget, and rejects
absolute temporary-root leakage. It uses no network and imports no data from another project.

The JSON result contains only aggregate fixture metrics. `packs_considered` is the bounded set
whose fingerprints were checked; all Pack metadata is still scanned cheaply as a correctness
safety net, and Required reads remain a starting route rather than a limit on code inspection.
