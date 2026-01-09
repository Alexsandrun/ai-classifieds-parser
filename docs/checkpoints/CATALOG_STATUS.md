# Catalog Status

Generated: 2026-01-09T06:14:40+02:00
Commit: 5d61a514beb5fc9ae4dc88f2cb138b16a1b68f1e

## Git status
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   docs/checkpoints/CATALOG_STATUS.md
	modified:   docs/checkpoints/INVENTORY.md

no changes added to commit (use "git add" and/or "git commit -a")

## Recent commits
5d61a51 Checkpoint: green run on 3d3611d
3d3611d Green run: stabilize admin API + repos; deps; ignore backups
a97f734 Add catalog status report (full, with checks+git status)
aaf8ea4 Update checkpoint inventory (full) + new green run
040a6e6 Add base documentation: rules, canonical fields, architecture, interfaces
8538680 Add base documentation: rules, canonical fields, architecture, interfaces
43432bb Add checkpoint: inventory + green test run
341dcdf Add Decision Engine v0.1 (hard list match + soft text heuristics + explainability)
988934c Add Decision Engine v0.1 (hard list match + soft text heuristics + explainability)
b6b0a69 Add runtime endpoint (deployment mode + config path)

## Checks
All checks passed!
Success: no issues found in 53 source files
..................                                                       [100%]
18 passed in 0.50s

## Infra
NAME              IMAGE                               COMMAND                  SERVICE      CREATED       STATUS       PORTS
aicp-clickhouse   clickhouse/clickhouse-server:24.8   "/entrypoint.sh"         clickhouse   2 hours ago   Up 2 hours   0.0.0.0:8123->8123/tcp, [::]:8123->8123/tcp, 0.0.0.0:9000->9000/tcp, [::]:9000->9000/tcp, 9009/tcp
aicp-minio        minio/minio:latest                  "/usr/bin/docker-ent…"   minio        2 hours ago   Up 2 hours   0.0.0.0:9002->9000/tcp, [::]:9002->9000/tcp, 0.0.0.0:9003->9001/tcp, [::]:9003->9001/tcp
aicp-postgres     postgres:16                         "docker-entrypoint.s…"   postgres     2 hours ago   Up 2 hours   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
