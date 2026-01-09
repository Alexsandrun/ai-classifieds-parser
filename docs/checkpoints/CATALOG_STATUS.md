# CATALOG_STATUS (full)

- generated_at_utc: 2026-01-09T03:56:17Z
- git_head: aaf8ea4fc32148de8551eb03976a026a50916725

## Checks summary
- ruff: FAIL(code=1)
- mypy: OK
- pytest: OK

## Notes
- flags column shows which tool output mentions a file (ruff/mypy/pytest).
- git column is derived from `git status --porcelain`.

## Areas summary

| area | files | tracked | untracked | modified_like | |
|---|---:|---:|---:|---:|---|
| APP_ADMIN_API | 18 | 10 | 8 | 11 | |
| APP_CORE | 8 | 7 | 1 | 1 | |
| APP_OTHER | 7 | 7 | 0 | 0 | |
| APP_SERVICES | 45 | 28 | 17 | 23 | |
| DOCS | 10 | 10 | 0 | 0 | |
| INFRA | 7 | 7 | 0 | 0 | |
| OTHER | 8 | 8 | 0 | 2 | |
| TESTS | 9 | 8 | 1 | 2 | |

## APP_ADMIN_API

| path | tracked | git | last_commit | size | mtime_utc | flags |
|---|---|---|---|---:|---|---|
| `app/admin_api/__init__.py` | YES | CLEAN | 1799cb7 | 0 | 2026-01-09T01:30:40Z | - |
| `app/admin_api/auth.py` | YES | CLEAN | 9e52011 | 3404 | 2026-01-09T03:25:32Z | - |
| `app/admin_api/auth.py.bak.2026-01-09-044327` | NO | UNTRACKED | - | 1892 | 2026-01-09T01:38:02Z | - |
| `app/admin_api/auth.py.bak.2026-01-09-052100` | NO | UNTRACKED | - | 2025 | 2026-01-09T02:43:27Z | - |
| `app/admin_api/auth.py.bak.2026-01-09-052351` | NO | UNTRACKED | - | 3468 | 2026-01-09T03:21:00Z | - |
| `app/admin_api/auth.py.bak.2026-01-09-052532` | NO | UNTRACKED | - | 3009 | 2026-01-09T03:23:51Z | - |
| `app/admin_api/help_registry.py` | YES | MODIFIED( M) | 1799cb7 | 5720 | 2026-01-09T02:44:11Z | - |
| `app/admin_api/main.py` | YES | CLEAN | b6b0a69 | 706 | 2026-01-09T01:48:06Z | - |
| `app/admin_api/routes/__init__.py` | YES | CLEAN | 1799cb7 | 0 | 2026-01-09T01:30:40Z | - |
| `app/admin_api/routes/help.py` | YES | CLEAN | 1799cb7 | 918 | 2026-01-09T01:33:04Z | - |
| `app/admin_api/routes/runtime.py` | YES | CLEAN | b6b0a69 | 556 | 2026-01-09T01:47:58Z | - |
| `app/admin_api/routes/settings.py` | YES | MODIFIED( M) | 9e52011 | 3157 | 2026-01-09T02:43:47Z | - |
| `app/admin_api/routes/settings.py.bak.2026-01-09-044347` | NO | UNTRACKED | - | 3118 | 2026-01-09T01:38:34Z | - |
| `app/admin_api/schemas.py` | YES | CLEAN | 1799cb7 | 849 | 2026-01-09T01:31:56Z | - |
| `app/admin_api/services.py` | YES | MODIFIED( M) | 9e52011 | 4171 | 2026-01-09T03:05:00Z | - |
| `app/admin_api/services.py.bak.2026-01-09-050059` | NO | UNTRACKED | - | 4155 | 2026-01-09T02:44:11Z | - |
| `app/admin_api/services.py.bak.2026-01-09-050500` | NO | UNTRACKED | - | 4166 | 2026-01-09T03:03:46Z | - |
| `app/admin_api/services.py.bak2.2026-01-09-050346` | NO | UNTRACKED | - | 4166 | 2026-01-09T03:00:59Z | - |

## APP_CORE

| path | tracked | git | last_commit | size | mtime_utc | flags |
|---|---|---|---|---:|---|---|
| `app/core/__init__.py` | YES | CLEAN | f0ffd62 | 0 | 2026-01-08T22:02:54Z | - |
| `app/core/config.py` | YES | CLEAN | 2423964 | 380 | 2026-01-08T22:06:52Z | - |
| `app/core/contracts.py` | YES | CLEAN | 53786e9 | 4723 | 2026-01-08T21:46:15Z | - |
| `app/core/crypto.py` | YES | CLEAN | 2423964 | 625 | 2026-01-08T22:09:16Z | - |
| `app/core/deployment.py` | YES | CLEAN | 2755418 | 632 | 2026-01-09T02:08:38Z | - |
| `app/core/events.py` | YES | CLEAN | be18378 | 1031 | 2026-01-09T00:17:22Z | - |
| `app/core/normalize.py` | YES | CLEAN | 2423964 | 875 | 2026-01-08T22:09:01Z | - |
| `app/core/runtime_config.py` | NO | UNTRACKED | - | 924 | 2026-01-09T02:37:51Z | - |

## APP_OTHER

| path | tracked | git | last_commit | size | mtime_utc | flags |
|---|---|---|---|---:|---|---|
| `app/__init__.py` | YES | CLEAN | f0ffd62 | 0 | 2026-01-08T22:02:54Z | - |
| `app/main.py` | YES | CLEAN | 2423964 | 6408 | 2026-01-08T22:10:16Z | - |
| `app/tools/backup_monitor.py` | YES | CLEAN | 37ecef9 | 4528 | 2026-01-09T00:39:02Z | - |
| `app/tools/backup_report.py` | YES | CLEAN | 37ecef9 | 1857 | 2026-01-09T00:38:52Z | - |
| `app/tools/leads_janitor.py` | YES | CLEAN | 5aefac9 | 1164 | 2026-01-09T01:28:26Z | - |
| `app/tools/retention_run.py` | YES | CLEAN | ba461d4 | 1699 | 2026-01-09T00:27:55Z | - |
| `app/tools/settings_init.py` | YES | CLEAN | 5aefac9 | 1108 | 2026-01-09T01:26:48Z | - |

## APP_SERVICES

| path | tracked | git | last_commit | size | mtime_utc | flags |
|---|---|---|---|---:|---|---|
| `app/services/__init__.py` | YES | CLEAN | 2423964 | 0 | 2026-01-08T22:06:26Z | - |
| `app/services/audit/repo.py` | YES | MODIFIED( M) | 9e52011 | 1528 | 2026-01-09T03:12:59Z | ruff |
| `app/services/audit/repo.py.bak.2026-01-09-045015` | NO | UNTRACKED | - | 1495 | 2026-01-09T01:37:53Z | - |
| `app/services/audit/repo.py.bak.2026-01-09-050040` | NO | UNTRACKED | - | 1509 | 2026-01-09T02:50:15Z | - |
| `app/services/audit/repo.py.bak.2026-01-09-050335` | NO | UNTRACKED | - | 1509 | 2026-01-09T03:00:40Z | - |
| `app/services/audit/repo.py.bak.2026-01-09-050550` | NO | UNTRACKED | - | 1509 | 2026-01-09T03:03:35Z | - |
| `app/services/audit/repo.py.bak.2026-01-09-050740` | NO | UNTRACKED | - | 1509 | 2026-01-09T03:05:50Z | - |
| `app/services/audit/repo.py.bak.2026-01-09-050932` | NO | UNTRACKED | - | 1509 | 2026-01-09T03:07:40Z | - |
| `app/services/audit/repo.py.bak.2026-01-09-051259` | NO | UNTRACKED | - | 1509 | 2026-01-09T03:09:32Z | - |
| `app/services/backup/__init__.py` | YES | CLEAN | 37ecef9 | 0 | 2026-01-09T00:36:16Z | - |
| `app/services/backup/monitor_logic.py` | YES | CLEAN | 37ecef9 | 4116 | 2026-01-09T00:38:32Z | - |
| `app/services/backup/monitor_repo.py` | YES | MODIFIED( M) | 37ecef9 | 11887 | 2026-01-09T03:00:31Z | - |
| `app/services/backup/monitor_repo.py.bak.2026-01-09-045716` | NO | UNTRACKED | - | 11777 | 2026-01-09T00:38:00Z | - |
| `app/services/backup/monitor_repo.py.bak.2026-01-09-050031` | NO | UNTRACKED | - | 11887 | 2026-01-09T02:57:16Z | - |
| `app/services/decision/__init__.py` | YES | CLEAN | 988934c | 0 | 2026-01-09T01:58:51Z | - |
| `app/services/decision/engine.py` | YES | CLEAN | 341dcdf | 3289 | 2026-01-09T01:59:46Z | - |
| `app/services/decision/lists_facade.py` | YES | CLEAN | 988934c | 2429 | 2026-01-09T01:52:52Z | - |
| `app/services/decision/models.py` | YES | CLEAN | 341dcdf | 502 | 2026-01-09T01:59:05Z | - |
| `app/services/leads/__init__.py` | YES | CLEAN | 0c6994f | 0 | 2026-01-09T00:32:31Z | - |
| `app/services/leads/queue_repo.py` | YES | MODIFIED( M) | 5aefac9 | 11998 | 2026-01-09T03:00:21Z | - |
| `app/services/leads/queue_repo.py.bak.2026-01-09-050021` | NO | UNTRACKED | - | 11943 | 2026-01-09T01:27:56Z | - |
| `app/services/lists/__init__.py` | YES | CLEAN | 2423964 | 0 | 2026-01-08T22:06:26Z | - |
| `app/services/lists/blacklist_store.py` | YES | CLEAN | 2423964 | 3485 | 2026-01-08T22:09:28Z | - |
| `app/services/lists/import_csv.py` | YES | CLEAN | 2423964 | 2593 | 2026-01-08T22:09:56Z | - |
| `app/services/lists/providers.py` | YES | CLEAN | 2755418 | 1960 | 2026-01-09T01:41:42Z | - |
| `app/services/lists/whitelist_store.py` | YES | CLEAN | 2423964 | 3198 | 2026-01-08T22:09:45Z | - |
| `app/services/notify/__init__.py` | YES | CLEAN | 37ecef9 | 0 | 2026-01-09T00:36:16Z | - |
| `app/services/notify/telegram.py` | YES | CLEAN | 37ecef9 | 1407 | 2026-01-09T00:36:44Z | - |
| `app/services/retention/__init__.py` | YES | CLEAN | ba461d4 | 0 | 2026-01-09T00:20:11Z | - |
| `app/services/retention/cleaners.py` | YES | MODIFIED( M) | ba461d4 | 4888 | 2026-01-09T02:44:11Z | - |
| `app/services/retention/manager.py` | YES | CLEAN | ba461d4 | 2896 | 2026-01-09T00:27:44Z | - |
| `app/services/retention/policy.py` | YES | MODIFIED( M) | ba461d4 | 3841 | 2026-01-09T02:44:11Z | - |
| `app/services/settings/__init__.py` | YES | CLEAN | 5aefac9 | 0 | 2026-01-09T01:22:21Z | - |
| `app/services/settings/defaults.py` | YES | CLEAN | 5aefac9 | 870 | 2026-01-09T01:25:13Z | - |
| `app/services/settings/repo.py` | YES | MODIFIED( M) | 5aefac9 | 2577 | 2026-01-09T03:13:09Z | ruff |
| `app/services/settings/repo.py.bak.2026-01-09-045027` | NO | UNTRACKED | - | 2544 | 2026-01-09T02:44:11Z | - |
| `app/services/settings/repo.py.bak.2026-01-09-050049` | NO | UNTRACKED | - | 2558 | 2026-01-09T02:50:27Z | - |
| `app/services/settings/repo.py.bak.2026-01-09-050335` | NO | UNTRACKED | - | 2558 | 2026-01-09T03:00:49Z | - |
| `app/services/settings/repo.py.bak.2026-01-09-050550` | NO | UNTRACKED | - | 2558 | 2026-01-09T03:03:35Z | - |
| `app/services/settings/repo.py.bak.2026-01-09-050740` | NO | UNTRACKED | - | 2558 | 2026-01-09T03:05:50Z | - |
| `app/services/settings/repo.py.bak.2026-01-09-050932` | NO | UNTRACKED | - | 2558 | 2026-01-09T03:07:40Z | - |
| `app/services/settings/repo.py.bak.2026-01-09-051309` | NO | UNTRACKED | - | 2558 | 2026-01-09T03:09:32Z | - |
| `app/services/storage/__init__.py` | YES | CLEAN | be18378 | 0 | 2026-01-09T00:17:12Z | - |
| `app/services/storage/ch_events.py` | YES | CLEAN | be18378 | 2463 | 2026-01-09T00:17:56Z | - |
| `app/services/storage/pg_repo.py` | YES | CLEAN | be18378 | 3845 | 2026-01-09T00:18:13Z | - |

## DOCS

| path | tracked | git | last_commit | size | mtime_utc | flags |
|---|---|---|---|---:|---|---|
| `docs/ARCHITECTURE.md` | YES | CLEAN | 040a6e6 | 648 | 2026-01-09T03:47:09Z | - |
| `docs/CANONICAL_FIELDS.md` | YES | CLEAN | 040a6e6 | 1193 | 2026-01-09T03:47:09Z | - |
| `docs/INTERFACES.md` | YES | CLEAN | 040a6e6 | 437 | 2026-01-09T03:47:09Z | - |
| `docs/RULES.md` | YES | CLEAN | 040a6e6 | 1497 | 2026-01-09T03:47:09Z | - |
| `docs/_CHECKPOINT_STATUS.txt` | YES | CLEAN | 8538680 | 1473 | 2026-01-09T02:09:10Z | - |
| `docs/_FILES_CURRENT.txt` | YES | CLEAN | 8538680 | 62924 | 2026-01-09T02:09:10Z | - |
| `docs/checkpoints/CHECKPOINT_2026-01-09_0529.md` | YES | CLEAN | 43432bb | 3356 | 2026-01-09T03:29:56Z | - |
| `docs/checkpoints/CHECKPOINT_2026-01-09_0551.md` | YES | CLEAN | aaf8ea4 | 3360 | 2026-01-09T03:51:48Z | - |
| `docs/checkpoints/INVENTORY.md` | YES | CLEAN | aaf8ea4 | 12585 | 2026-01-09T03:51:26Z | - |
| `docs/interfaces/IFACE-LISTS-MATCH-001.md` | YES | CLEAN | 6bd6bc3 | 891 | 2026-01-08T22:13:12Z | - |

## INFRA

| path | tracked | git | last_commit | size | mtime_utc | flags |
|---|---|---|---|---:|---|---|
| `infra/clickhouse/init/001_schema.sql` | YES | CLEAN | be18378 | 1081 | 2026-01-09T00:10:07Z | - |
| `infra/docker-compose.yml` | YES | CLEAN | be18378 | 1769 | 2026-01-09T00:09:14Z | - |
| `infra/postgres/init/001_schema.sql` | YES | CLEAN | be18378 | 1769 | 2026-01-09T00:09:50Z | - |
| `infra/postgres/init/002_leads.sql` | YES | CLEAN | 0c6994f | 1229 | 2026-01-09T00:32:05Z | - |
| `infra/postgres/init/003_backup_monitor.sql` | YES | CLEAN | 37ecef9 | 2459 | 2026-01-09T00:36:26Z | - |
| `infra/postgres/init/004_tenant_settings.sql` | YES | CLEAN | 5aefac9 | 478 | 2026-01-09T01:22:46Z | - |
| `infra/postgres/init/005_audit_events.sql` | YES | CLEAN | 9e52011 | 922 | 2026-01-09T01:36:24Z | - |

## OTHER

| path | tracked | git | last_commit | size | mtime_utc | flags |
|---|---|---|---|---:|---|---|
| `.gitignore` | YES | CLEAN | c2c6d07 | 394 | 2026-01-09T01:46:07Z | - |
| `.python-version` | YES | CLEAN | 53786e9 | 5 | 2026-01-08T21:39:02Z | - |
| `README.md` | YES | CLEAN | a9aa1b5 | 162 | 2026-01-08T21:08:11Z | - |
| `config/retention.json` | YES | CLEAN | ba461d4 | 846 | 2026-01-09T00:20:24Z | - |
| `config/runtime.json` | YES | CLEAN | e89879a | 41 | 2026-01-09T01:45:37Z | - |
| `pyproject.toml` | YES | MODIFIED( M) | 53786e9 | 394 | 2026-01-09T02:38:17Z | - |
| `pytest.ini` | YES | CLEAN | f0ffd62 | 42 | 2026-01-08T22:00:12Z | - |
| `uv.lock` | YES | MODIFIED( M) | 53786e9 | 113867 | 2026-01-09T02:38:18Z | - |

## TESTS

| path | tracked | git | last_commit | size | mtime_utc | flags |
|---|---|---|---|---:|---|---|
| `tests/test_admin_api_help_settings.py` | YES | CLEAN | 9e52011 | 1754 | 2026-01-09T01:38:47Z | - |
| `tests/test_backup_monitor_logic.py` | YES | CLEAN | 37ecef9 | 3103 | 2026-01-09T00:39:44Z | - |
| `tests/test_decision_engine.py` | YES | CLEAN | 341dcdf | 1846 | 2026-01-09T02:00:03Z | - |
| `tests/test_leads_queue.py` | YES | MODIFIED( M) | 0c6994f | 1153 | 2026-01-09T02:45:09Z | - |
| `tests/test_leads_queue.py.bak.2026-01-09-044509` | NO | UNTRACKED | - | 1147 | 2026-01-09T00:34:34Z | - |
| `tests/test_lists.py` | YES | CLEAN | 2423964 | 2655 | 2026-01-08T22:10:52Z | - |
| `tests/test_retention.py` | YES | CLEAN | ba461d4 | 1255 | 2026-01-09T00:28:11Z | - |
| `tests/test_runtime.py` | YES | CLEAN | b6b0a69 | 445 | 2026-01-09T01:48:14Z | - |
| `tests/test_smoke.py` | YES | CLEAN | 2423964 | 394 | 2026-01-08T22:10:34Z | - |

