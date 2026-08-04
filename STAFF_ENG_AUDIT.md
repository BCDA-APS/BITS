# apsbits — Staff Engineer Audit & Action Plan

Senior-staff review of the `apsbits` package. Each item is a checkbox an agent can execute
directly: it names the file, the symbol, and the exact change. Items are grouped into the four
requested buckets and ordered by severity within each.

**Method:** 6 parallel subsystem auditors (core, utils, api, packaging, testing, docs) read the
actual source; every "delete/redundant" and high-severity claim was then adversarially
re-verified against the code. 74 findings confirmed; 4 claims were checked and **rejected** (see
end). IDs in brackets trace back to the audit.

> **Re-audit — 2026-07-24.** Every checkbox below was re-verified against the current source
> (post `fa90755`). Checkboxes now reflect reality, not the original marks. Two corrections
> surfaced: **B2**'s originally-proposed fix was itself a bug (it would make `init_instrument(None)`
> construct a live instrument) — see the rewritten B2. **R12** is already fully done (alias removed),
> not "keep for now." **Anchor drift:** several original line numbers predate recent commits
> (e.g. `pyproject.toml` is 193 lines, not 250+); the **step-by-step plan in §6 carries
> re-verified anchors** and is the authoritative guide for execution. 19 newly-found issues are
> catalogued in §5 (S1–S19).

### Re-audit scoreboard (2026-07-24)

| Bucket | Done & verified | Still open | New (§5) |
|---|---|---|---|
| BAD (B) | B2, B3, B5, B8, B9, B11, B12, B14 | B4, B6, B7, B13 | — |
| REDUNDANT (R) | R1, R2, R3, R4, R5, R6, R7, R8, R11, R12, R13 | R9, R10 | — |
| NEEDS IMPROVEMENT (N) | N1, N2, N3, N7, N11, N14, N17, N18, N19, N20, N21 | N5, N6, N8, N9, N10, N12, N13, N15, N16, N22, N23, N24 (no N4) | — |
| DOES WELL (W) | W1–W15 *(verified still present)* | — | — |
| **New findings (§5)** | S1, S2, S3, S4, S5, S6, S10, S11, S12, S13, S19 | S7, S8, S9, S14–S18 | — |

**Totals (B/R/N/S): 41 done · 26 open · 15 strengths preserved (W1–W15).** §6 Batches 0–3 executed & verified 2026-07-24 (suite 95→**105** passed, +10 new tests; startup smoke OK); Batch 4 executed & verified 2026-08-03 (R8, N11, R7, S6, S13; +5 new tests → **108 passed, 2 failed** locally — both pre-existing APS-subnet EPICS timeouts unrelated to the change; 110 on an off-subnet host like CI; ruff + startup smoke OK); Batch 5 executed & verified 2026-08-03 (B9, S4, S5; +2 new tests → `test_stored_dict.py` **15 passed**; ruff + startup smoke OK). Full-suite failures are pre-existing and unrelated to Batch 5 — the two `test_delete_instrument` "invalid name './src'" failures reproduce identically with the Batch 5 changes stashed (an `os.chdir`-leak order-dependence), and the two `test_sim_plans` failures are the same flaky APS-subnet `S-DCCT` EPICS timeouts.

## Fix-first priority (highest impact, refreshed 2026-07-24)

1. **Silent device-load failures** — `make_devices` swallows loader exceptions (N2), returns
   normally on a missing device file (N3), and silently no-ops when handed the *string*
   `"guarneri"` instead of an `Instrument` (S3). A malformed/missing `devices.yml` yields an
   empty session with no error. `instrument_init.py:103-125`.
2. **Dead-conditional family** — `init_instrument`'s `or None` (B2) + no terminal `else` (S2),
   and `init_RE`'s unreachable `PersistentDict` branch (S1). `instrument_init.py:171`, `run_engine_init.py:99-106`.
3. **`StoredDict` data loss** — `flush()` is not durable while a background sync is in flight
   (B9) and `__delitem__`/`popitem` never persist deletions (S4). `stored_dict.py`.
   **(RESOLVED — Batch 5, 2026-08-03: B9/S4/S5 done.)**
4. **Test suite ERRORs without EPICS** — the `ioc` fixture hard-fails instead of skipping when
   `softIoc` is absent (B7). `tests/conftest.py`.
5. **Docs describe removed code** — `dm.rst` documents deleted `aps_dm_setup`/`dm_plans` (B4);
   `startup.rst` shows `RE(make_devices(...))` and wrong callback paths (B6).

> **B1 (`bits-run`) — RESOLVED by removal.** The broken `bits-run` CLI and its module/tests/docs were deleted rather than fixed (`run_instrument.py`, `test_run_instrument.py`, the `bits-run` entry point, and its docs/diagram references). N4 (which targeted the same module) is likewise dropped. *(Re-verified 2026-07-24: `run_instrument.py` gone; `[project.scripts]` at `pyproject.toml:190-192` exposes only `bits-create`/`bits-delete`.)*

---

## 1. BAD — must be changed or removed (real defects)

- [x] **B2 — Remove the dead `or None` in `init_instrument`** `src/apsbits/core/instrument_init.py:171`.
  `if device_manager == "guarneri" or None:` — `X or None` is truthy iff `X` is, so `or None` is
  pure dead code (identical to `== "guarneri"`).
  **⚠ Re-audit correction (2026-07-24):** the original claim that `None` "falls through to the error
  branch" is stale — an explicit `elif device_manager is None:` (lines 180-185) already returns
  `(None, None)` correctly. And the *originally proposed* action (`or device_manager is None`) was
  itself a bug: it would make `init_instrument(None)` **construct a live instrument**. Do **not** apply it.
  **Action:** Change line 171 to `if device_manager == "guarneri":`. Keep the `elif device_manager is None:`
  block. Add a terminal `else:` (see **S2**) so unknown strings don't return implicit `None`. Add
  regression tests for `init_instrument(None)` and `init_instrument("bogus")`.
  **Done (2026-07-24):** removed `or None`; added a terminal `else` (S2); regression tests in `tests/test_instrument_init.py`.

- [x] **B3 — Make `bits-delete` fail on a missing instrument** `src/apsbits/api/delete_instrument.py:114-117`.
  **Done & verified (2026-07-24):** prints to `stderr` then `sys.exit(1)` *before* the prompt/success path; covered by `test_delete_instrument.py::test_delete_main_nonexistent_instrument`.

- [ ] **B4 — Remove/rewrite stale Data-Management guide** `docs/source/guides/dm.rst` (in toctree at `guides/index.rst:21`).
  Documents the removed `dm_plans` module and deleted `aps_dm_setup()` (per `HISTORY.rst:115`).
  **Verified still open (2026-07-24):** `dm.rst` exists (references `aps_dm_setup` at lines 17/24/31/33 and `dm_plans` at line 44); `index.rst:21` still lists `dm`; stale `# aps_dm_setup(...)` comment at `startup.py:62`.
  **Action:** Delete `dm.rst` and remove line 21 from `guides/index.rst` (or rewrite to point at apstools DM helpers). Also delete the stale `# aps_dm_setup(iconfig.get("DM_SETUP_FILE"))` comment at `startup.py:62`. (See also **S16** — `setting_iconfig.rst` still documents the now-dead `DM_SETUP_FILE` key.)

- [x] **B5 — Fix wrong CLI names in API docs** `docs/source/api/api.rst:23-33`.
  **Done & verified (2026-07-24):** Example Usage now shows `bits-create my_instrument` / `bits-delete my_instrument` (positional, correct).

- [ ] **B6 — Update outdated startup guide** `docs/source/guides/startup.rst:55-129`.
  Describes an active `aps_dm_setup` block, `RE(make_devices(...))`, and old callback import paths that no longer match `demo_instrument/startup.py`.
  **Verified still open (2026-07-24), three concrete divergences:** (a) `startup.rst:60` shows `aps_dm_setup(...)` as an active step; real `startup.py:62` has it commented out. (b) `startup.rst:127-129` shows `RE(make_devices(clear=False, file="devices.yml"))` and a typo'd `device_aps_only.yml`; real `startup.py:105` is `make_devices(clear=False, file="devices.yml", device_manager=instrument)` (not wrapped in `RE()`) and the APS file is `devices_aps_only.yml`. (c) `startup.rst:89,102` import from `.callbacks.nexus_data_file_writer` / `.callbacks.spec_data_file_writer`; real `startup.py:76-83` uses `.callbacks.demo_nexus_callback` / `.callbacks.demo_spec_callback` and calls `nxwriter_init(RE, iconfig)`.
  **Action:** Rewrite to mirror current `startup.py` on all three points.

- [ ] **B7 — Skip EPICS tests when `softIoc` is absent** `src/apsbits/tests/conftest.py:74-111`.
  The `ioc` fixture `subprocess.Popen(["softIoc", ...])` inside a `try/finally` with **no `except`**; without EPICS base it raises `FileNotFoundError` and dependent tests ERROR instead of skipping.
  **Verified still open (2026-07-24):** no `shutil.which("softIoc")` guard anywhere.
  **Action:** At the top of the fixture: `import shutil; if shutil.which("softIoc") is None: pytest.skip("softIoc (EPICS base) not available")`, and wrap the `Popen` in `try/except FileNotFoundError: pytest.skip(...)`.

- [x] **B8 — Fix misleading `with_registry` error message** `src/apsbits/core/instrument_init.py:198-200`.
  **Done & verified (2026-07-24):** message now reads `'Instrument not set. Call init_instrument("guarneri") first.'`.

- [x] **B9 — Make `StoredDict.flush()` durable** `src/apsbits/utils/stored_dict.py:154-160`.
  When a background sync is in progress, `flush()` returns without writing, risking data loss on shutdown.
  **Verified still open (2026-07-24):** `flush()` short-circuits on `if not self.sync_in_progress:` and there is **no lock primitive** in the class.
  **Action:** Add `self._lock = threading.RLock()` in `__init__`; in `flush()` acquire the lock, unconditionally `StoredDict.dump(self._file, self._cache, title=self._title)`, then set `_sync_deadline=time.time()` and `sync_in_progress=False`. Remove the `if not sync_in_progress` short-circuit. (See also **S4** — deletions are never persisted.)
  **Done (2026-08-03):** added `self._lock = threading.RLock()`; `flush()` now cancels any pending debounce timer, unconditionally `StoredDict.dump(...)` under the lock, then resets `_sync_deadline`/`sync_in_progress` (short-circuit removed). The background writer (`_sync_to_storage`) also holds the lock, so flush and the timer can't write the file concurrently. Regression test `test_flush_durable_during_sync` in `test_stored_dict.py`.

- [x] **B11 — Fix wrong-project milestones link** `HISTORY.rst:27`.
  **Done & verified (2026-07-24):** now `https://github.com/BCDA-APS/BITS/milestones`.

- [x] **B12 — Fix release-note typo** `HISTORY.rst:107`: `Documentation overhaul1` → `Documentation overhaul`.
  **Done & verified (2026-07-24).**

- [ ] **B13 — Fix `ioc` fixture prefix mismatch** `src/apsbits/tests/conftest.py:109`.
  Yields `prefix="test1:"` but the record is `test:scan_id`.
  **Verified still open (2026-07-24) — but inert:** no test reads `ioc["prefix"]` (consumers hardcode `"test:scan_id"`), so this is cosmetic. Still worth fixing to avoid a future foot-gun.
  **Action:** Change to `prefix="test:"` so `prefix + "scan_id"` reconstructs the PV (or drop the unused key).

- [x] **B14 — Drop false "TestPyPI" claim** `.github/workflows/pypi.yml:1,17`.
  Names said "PyPI and TestPyPI" but no TestPyPI step exists.
  **Done (2026-07-24):** stripped "and TestPyPI" from the workflow `name` (line 1) and job `name` (line 17).

---

## 2. REDUNDANT — no longer needed / safe to delete

- [x] **R1 — Delete dead `[tool.black]` config** — **Done & verified (2026-07-24):** no `[tool.black]` in `pyproject.toml`. *(Note: CLAUDE.md still calls it a "legacy section in pyproject.toml" — now stale; see **S19**.)*

- [x] **R2 — Delete dead `[tool.flake8]` config** — **Done & verified (2026-07-24):** no `[tool.flake8]` in `pyproject.toml`.

- [x] **R3 — Delete dead `[tool.isort]` config + dep** — **Done & verified (2026-07-24):** no `[tool.isort]` block (only `[tool.ruff.lint.isort]` remains, which is ruff config); `"isort"` absent from the dev extra.

- [x] **R4 — Drop the bogus `"dot"` doc dependency** — **Done & verified (2026-07-24):** absent from the doc extra (`pyproject.toml:62-76`).

- [x] **R5 — Replace `tomli` with stdlib `tomllib`** — **Done & verified (2026-07-24):** `config_loaders.py:15` `import tomllib`; `tomllib.load`/`tomllib.TOMLDecodeError`; `"tomli"` gone from runtime deps.

- [x] **R6 — Recategorize `tomli-w` as a test-only dep** — **Done & verified (2026-07-24):** `tomli-w` appears only in the `dev` extra (`pyproject.toml:59`); absent from `dependencies` and `doc`.

- [x] **R7 — Delete dead `validate_instrument_path`** `src/apsbits/utils/config_loaders.py:173-239`.
  No callers; also buggy (requires *both* `iconfig.yml` AND `iconfig.toml`).
  **Verified still open (2026-07-24):** function present; repo-wide grep shows zero functional callers (only the def + auto-generated `config_loaders.rst`); still requires both files (`expected_files = ["iconfig.yml", "iconfig.toml"]`).
  **Action:** Delete the function. (If kept instead, change the file check to require *either* format.)
  **Done (2026-08-03):** function deleted; re-confirmed zero functional callers before removal; no imports orphaned (`Path`/`Optional`/`pathlib` still used). Note: the auto-generated `docs/source/api/generated/apsbits.utils.config_loaders.rst` still lists it — it regenerates on `make docs` (cleared with Batch 9).

- [x] **R8 — Consolidate the two YAML loaders** `src/apsbits/utils/config_loaders.py:24-95` & `118-170`.
  `load_config` and `load_config_yaml` duplicate the open/empty-check/except ladder and diverge on safety: `load_config_yaml` uses unsafe `yaml.load(content, yaml.Loader)`.
  **Verified still open (2026-07-24):** unsafe `yaml.load(content, yaml.Loader)` at line ~153; `load_config` uses `yaml.safe_load`. Note `StoredDict.load` and `configure_logging` call `load_config_yaml`.
  **Action (do regardless):** change line 153 to `yaml.safe_load(content)`. Then have one helper delegate to the other to remove duplication.
  **Done (2026-08-03):** `load_config_yaml` now uses `yaml.safe_load`. Safe because `StoredDict.__setitem__` enforces `json.dumps` and `dump` uses plain `yaml.dump`, so persisted files carry no `!!python/*` tags; logging configs are plain data too — both round-trip under `safe_load` (confirmed by `test_stored_dict` + startup smoke). `load_config` now delegates its `.yml` read to `load_config_yaml`; TOML stays inline because `tomllib.load` requires a binary handle and can't share the text-mode helper. **Behavior drift:** consolidating the except ladders changed some log wording, and the TOML path no longer emits bespoke `PermissionError`/generic `logger.error` lines (the exceptions still propagate unchanged).

- [ ] **R9 — Remove dead duplicate kwargs in `motors()`** `src/apsbits/utils/sim_creator.py:185-186`.
  Both assignments are immediately overwritten by the following `kwargs.update({...})`.
  **Verified still open (2026-07-24).**
  **Action:** Delete lines 185-186.

- [ ] **R10 — Remove empty `TYPE_CHECKING` blocks** `tests/test_config.py:7,15-16` and `tests/test_general.py:8,12-13`.
  **Verified still open (2026-07-24):** both are dead. **Do not touch** `test_make_devices.py` / `test_delete_instrument.py` — their `TYPE_CHECKING` blocks are *live*.
  **Action:** Delete the `from typing import TYPE_CHECKING` import and the `if TYPE_CHECKING: pass` blocks in those two files only (preserve the trailing comment in `test_general.py`).

- [x] **R11 — Remove commented future entry points** — **Done & verified (2026-07-24):** `[project.scripts]` (`pyproject.toml:190-192`) has no `# bits-device-*`/`# bits-plan-*` placeholders.

- [x] **R12 — Remove the `create-bits` back-compat alias** — **Done & verified (2026-07-24):** alias removed; `[project.scripts]` exposes only `bits-create`/`bits-delete`. *(Supersedes the original "keep for now" note.)*

- [x] **R13 — Drop redundant `--exitfirst` in CI** `.github/workflows/code.yml:113` — resolved with **N1**. **Done (2026-07-24):** `-x` removed from `addopts` (`pyproject.toml:87`); CI keeps `--exitfirst` on the `code.yml:113` line, so fail-fast is now CI-only.

---

## 3. NEEDS IMPROVEMENT — works but fragile / incomplete

*(Re-verified 2026-07-24; each item still open unless its box is checked / marked done.)*

### Error handling & robustness
- [x] **N1 — Stop hiding the full test-failure picture** `pyproject.toml:87`.
  `addopts` hard-codes `-x`, forcing fail-fast on every local run too.
  **Action:** Change line 87 to `addopts = ["--import-mode=importlib"]` (drop only `-x`; keep import-mode). Leave `--exitfirst` in `code.yml:113` so fail-fast is CI-only.
- [x] **N2 — Don't swallow device-load errors in `make_devices`** `src/apsbits/core/instrument_init.py:118-120`.
  The `try/except Exception` only logs, so a malformed `devices.yml` yields a silently empty session.
  **Action:** Re-raise after logging (or remove the catch) so startup fails fast, matching the re-raise convention in `init_RE`.
- [x] **N3 — `make_devices` should not "succeed" on a missing file** `instrument_init.py:103-104`.
  On missing `device_path` it logs an error, then still `time.sleep(pause)` and returns normally.
  **Action:** `return` (or raise `FileNotFoundError`) right after the not-found log.
- [ ] **N5 — Add rollback to `create_new_instrument`** `src/apsbits/api/create_new_instrument.py:124-142`.
  Partial failure leaves an un-rerunnable half-created `src/<name>`.
  **Action:** Wrap the three steps; on exception `shutil.rmtree(new_instrument_dir, ignore_errors=True)` and unlink the created `{name}_qs_host.sh` before `sys.exit(1)`.
- [ ] **N6 — Guard `create_qserver_script` assumptions** `create_new_instrument.py:27-31`.
  Assumes `qs_host.sh` exists before `os.rename`; on POSIX `os.rename` silently overwrites an existing `{name}_qs_host.sh`.
  **Action:** Assert the source exists with a clear error; copy the specific expected file rather than `glob('*')`; warn instead of overwriting an existing `{name}_qs_host.sh`.
- [x] **N7 — Warn when `clear=True` is ignored** `instrument_init.py:86`.
  Silently skipped unless `device_manager` is a `guarneri.Instrument`.
  **Action:** Add a `logger.warning` in the else case. (Related to **S3**.)
- [ ] **N8 — Guard `_setup_console_logger` handler indexing** `src/apsbits/utils/logging_setup.py:187-188`.
  `logger.handlers[0]` can `IndexError` / target the wrong handler. *(Currently masked by call order — `basicConfig(force=True)` installs one StreamHandler immediately before — but fragile.)*
  **Action:** Iterate handlers and set level on `logging.StreamHandler` instances.
- [ ] **N9 — Log the fallback in `host_on_aps_subnet`** `src/apsbits/utils/aps_functions.py:23-24`.
  Broad `except` makes a misconfig indistinguishable from "off subnet"; module has no logger.
  **Action:** Add a module logger and `logger.debug(...)` inside the except.
- [ ] **N10 — Warn on no-op `set_timeouts`** `src/apsbits/utils/controls_setup.py:128-135`.
  Silently does nothing if an `EpicsSignalBase` already exists.
  **Action:** Add an `else` branch logging a warning.

### Correctness hazards (latent)
- [x] **N11 — `load_config` must replace, not merge, global state** `src/apsbits/utils/config_loaders.py:65`.
  `_iconfig.update(config)` leaks stale keys across loads and between tests.
  **Action:** `_iconfig.clear(); _iconfig.update(config)`. Add a `reset_config()` helper for a conftest fixture. (Coordinate with **S6**.)
  **Done (2026-08-03):** `load_config` now does `_iconfig.clear(); _iconfig.update(config)`; added public `reset_config()`. Verified the `clear()` doesn't regress `test_general::test_iconfig` (which reads demo-config keys from the global) — the session fixture reloads demo config before those assertions, so ordering stays benign. Genuine fixture determinism is still **N24** (Batch 8).
- [ ] **N12 — Guard `logger.bsdev` calls** `src/apsbits/utils/helper_functions.py:77,117` (also `logging_setup.py:230,231,284`).
  `bsdev` only exists after `configure_logging()`; calling these utilities first raises `AttributeError`. *(Masked in the shipped flow because `startup.py:35` configures logging first.)*
  **Action:** Use `getattr(logger, "bsdev", logger.debug)(...)`, or register the level eagerly at `logging_setup` import.
- [ ] **N13 — Replace mutable default arg** `src/apsbits/utils/metadata.py:103`.
  `def re_metadata(iconfig = {})` (B006). *(Sibling `get_md_path` was already fixed to `= None`.)*
  **Action:** Default to `None` and assign `{}` inside.
- [x] **N14 — Reconcile `make_devices` `file` param + example** `instrument_init.py:39,49-51,59-67`.
  Docstring claims `file=None` defaults to `iconfig.yml`, but the signature makes `file` required (`file: str`) and the body errors+returns on `None`. The docstring param order (`device_manager` before `path`) is also inverted, and the `EXAMPLE` block shows `RE(make_devices(...))` — but `make_devices` returns `None` (not a plan), so `RE(make_devices(...))` is wrong (same bug as **B6**).
  **Action:** State `file` is required (no `iconfig.yml` fallback), fix the type annotation, reorder params (`path` before `device_manager`), and correct the EXAMPLE to `make_devices(file="custom_devices.yml")`.

### API/UX polish
- [ ] **N15 — Fix stray backslash in create message** `create_new_instrument.py:111-114`.
  Line-continuation embeds a backslash + indentation into the printed path.
  **Action:** Collapse to one line: `print(f"Creating instrument '{args.name}' from demo_instrument into '{new_instrument_dir}'.")`.
- [ ] **N16 — Quiet/relocate `get_md_path` log** `src/apsbits/utils/metadata.py:99`.
  Logs "RunEngine metadata saved to:" at info level though it only computes a path.
  **Action:** Downgrade to `logger.debug` and reword; emit any "saved" message where the StoredDict is actually created.

### Packaging / tooling
- [x] **N17 — Document the load-bearing `databroker==1.2.5` pin (do NOT relax to 2.x)** `pyproject.toml:43`.
  **⚠ Re-audit correction (2026-07-24):** the original premise ("unexplained exact pin blocks the tiled/bluesky tree from resolving") is **false** — in `bits_dev`, `databroker==1.2.5` + `tiled==0.2.12` + `bluesky-tiled-plugins==2.0.6` + `pydantic==2.12.5` coexist and `pip check` is clean. tiled is a **separate** dependency (`tiled[all]` + `bluesky-tiled-plugins`, line 39/55), **not** provided by databroker, so **tiled needs no databroker bump.** The pin is load-bearing: `catalog_init.py:16-17,78,87` and `run_engine_init.py:19-20,142-143,147` import databroker **1.x private/v1 APIs** — `databroker._drivers.{msgpack.BlueskyMsgpackCatalog, mongo_normalized.BlueskyMongoCatalog}`, `databroker.temp().v2`, `databroker.catalog[...].v2`, `instance.v1.insert` — that databroker 2.x (a tiled-based rewrite) removed/changed. That is why 2.x "stops working." (databroker 1.2.5 also caps `intake<=0.6.4`.)
  **Action:** **Keep** the pin; add an inline comment explaining the constraint. Prefer `databroker >=1.2.5,<2` (the `<2` upper bound is the real guard against the 2.x rewrite) **or** keep `==1.2.5` for exact reproducibility — but do **not** move to 2.x without first migrating the two modules off the `_drivers`/`.temp()`/`.v1`/`.v2` APIs onto tiled-native catalogs (see the existing `catalog_init.py:40,50` TODOs — the codebase already treats databroker as "legacy use only" per `iconfig.yml:8` and prefers tiled). Verified coexistence: `pip check` clean in `bits_dev`.
  **Done (2026-07-24):** inline comment added above `pyproject.toml:43`; pin kept at `==1.2.5` (not raised).
- [x] **N18 — Register the `slow` marker** `pyproject.toml` `[tool.pytest.ini_options]`.
  `@pytest.mark.slow` (`test_import_purity.py:49`) is undeclared → `PytestUnknownMarkWarning`, no `-m "not slow"`.
  **Action:** Add `markers = ["slow: marks tests as slow (deselect with '-m \"not slow\"')"]` (and consider `--strict-markers`).
- [x] **N19 — Enforce or remove `mypy`** `pyproject.toml:59`.
  In dev extra but no `[tool.mypy]` and never run.
  **Action:** Add a `[tool.mypy]` + pre-commit/CI step, or drop `"mypy"` from the dev extra. *(Recommend removing unless you'll wire it up — simplicity.)*
- [x] **N20 — Add `pip` ecosystem to Dependabot** `.github/dependabot.yml`.
  Only `github-actions` is tracked; Python deps drift unmonitored.
  **Action:** Add a `package-ecosystem: "pip"` weekly entry.
- [x] **N21 — Align dev extras with CI test plugins** `pyproject.toml:59`.
  CI installs `pytest-cov`/`pytest-qt`/`pytest-xvfb` via micromamba; dev extra has only `pytest`/`pytest-mock`, so `pip install -e .[dev]` can't run the full suite.
  **Action:** Add `pytest-cov` and `pytest-qt` to the dev extra (note `pytest-xvfb` is Linux-CI-only).

### Test coverage
- [ ] **N22 — Add direct unit tests for untested modules**: `run_engine_init.init_RE`, `baseline_setup.setup_baseline_stream`, `aps_functions.host_on_aps_subnet`, `session_setup.prepare_bits`, `helper_functions.dynamic_import`. **Verified (2026-07-24):** none of the five has a dedicated test. Start with `dynamic_import` happy-path + the two documented `ValueError`s.
- [ ] **N23 — Assert real post-startup invariants** (not just "import didn't throw"): `RE` is a `RunEngine`, `cat` is a catalog, `sd` subscribed, `oregistry` has `sim_motor`/`sim_det`. **Verified partial (2026-07-24):** `test_general.py::test_startup` only does non-None checks; behavioral coverage exists indirectly (`test_sim_plans` asserts catalog growth) but the explicit invariants and the `oregistry` membership check (currently done via brittle log-text in `test_make_devices.py`) are missing.
- [ ] **N24 — Make `runengine_with_devices` deterministic** `tests/conftest.py:23-45`.
  Session-scoped fixture mutates module globals + `__main__`, creating order-dependence.
  **Action:** Use `scope="function"`, or call `make_devices(clear=True)` and document the shared-state contract.

---

## 4. DOES WELL — preserve (do not "fix" these)

*(`[x]` here means "verified still present as of 2026-07-24" — strengths to preserve, not tasks completed.)*

- [x] **W1 — Single linter/formatter via ruff**, enforced in pre-commit and gated before the test matrix (`needs: lint`). Keep ruff + ruff-format as the only source of truth.
- [x] **W2 — PyPI publish uses OIDC trusted publishing** (no stored token) with `twine check` first. Do not reintroduce a `PYPI_API_TOKEN`.
- [x] **W3 — Import-purity subprocess test** (`test_import_purity.py`) blocks network I/O per-module in a fresh subprocess — strong safeguard. Keep it in CI even after registering the `slow` marker. *(Hardening idea: **S15**.)*
- [x] **W4 — `init_RE` subscriber dispatch** is type-aware (Tiled → TiledWriter, databroker → `v1.insert`, else direct), logs with context, and re-raises rather than swallowing.
- [x] **W5 — `init_catalog` fallback chain** (tiled profile → named databroker → temp databroker → temp tiled) isolates per-handler errors and uses `weakref.finalize` cleanup.
- [x] **W6 — `guarneri_namespace_loader` diffs against a pre-load snapshot**, so incremental `make_devices` calls don't re-add devices.
- [x] **W7 — BSDEV custom level registration is idempotent** (`hasattr` guard) with a regression test.
- [x] **W8 — Metadata collection is lazily imported and cached** (`metadata.py`), keeping heavy imports out of module load.
- [x] **W9 — `dynamic_import` validates dotted/absolute paths** before importing, giving actionable errors for bad `devices.yml` creators.
- [x] **W10 — CLI name validation** (`^[a-z][_a-z0-9]*$`, via `re.fullmatch`) applied before any filesystem work in both create and delete. Optionally DRY into `apsbits.api.__init__`.
- [x] **W11 — `delete_instrument` is a reversible soft-delete** (timestamped move to `.deleted/`, `[y/N]` gate unless `--force`).
- [x] **W12 — Deprecated docs are excluded from the Sphinx build** (`conf.py:47`, `deprecated/**`).
- [x] **W13 — README mermaid diagrams accurately mirror `startup.py`** — keep them in sync on future changes. *(Notably the diagram already shows the correct `nxwriter_init(RE, iconfig)` signature that `startup.rst` gets wrong — see B6.)*
- [x] **W14 — Parametrized happy/error coverage** in `test_catalog_init.py` and `test_controls_setup.py`. **Open TODO:** the `TILED_PROFILE_NAME` / `TILED_PATH_NAME` / `TILED_SAVE_PATH` parametrize cases in `test_catalog_init.py:76-88` are still stubbed — fill them.
- [x] **W15 — README ipython snippet is correct** — `sim_*_plan()` work zero-arg via `@with_registry`. Do not "fix" it.

---

## 5. ADDITIONAL — staff-engineer findings from the 2026-07-24 re-audit

New issues the first pass did not catalogue. Same format: file:line → problem → action. Grouped by subsystem; folded into the §6 plan.

### core/
- [x] **S1 — Delete the unreachable `PersistentDict` branch** `src/apsbits/core/run_engine_init.py:99,106`.
  `handler_name` is hard-coded to `"StoredDict"` on line 99, so `if handler_name == "PersistentDict":` (line 106) is dead — same class of smell as B2's `or None`.
  **Action:** Either drive `handler_name` from `iconfig` (if PersistentDict is a supported option) or delete the dead branch.
- [x] **S2 — Give `init_instrument` a terminal `else`** `src/apsbits/core/instrument_init.py:169-185`.
  Any unrecognized *truthy* arg (e.g. a typo `"guaneri"`) matches no branch → returns implicit `None`, so `instrument, oregistry = init_instrument(...)` raises an opaque `TypeError: cannot unpack non-iterable NoneType`.
  **Action:** Add `else: logger.error(...); return None, None` (or `raise ValueError`). Fold into the B2 fix.
- [x] **S3 — `make_devices` silently no-ops on the string `"guarneri"`** `src/apsbits/core/instrument_init.py:108-125`.
  Dispatch is `isinstance(device_manager, guarneri.Instrument)`, but the sibling `init_instrument` takes the *string* `"guarneri"`. `make_devices(file=..., device_manager="guarneri")` matches none of the branches → no load, no error, just `time.sleep` and return.
  **Action:** Add a final `else: logger.error("Unrecognized device_manager: %r", device_manager); raise ValueError(...)`. Coordinate with N7.

### utils/
- [x] **S4 — `StoredDict` deletions are never persisted** `src/apsbits/utils/stored_dict.py:78-88` (`__delitem__`) and `162-169` (`popitem`).
  Both mutate `self._cache` but (unlike `__setitem__`) never reset `_sync_deadline` / start `_delayed_sync_to_storage()`, so deleted keys silently persist on disk until the next `__setitem__` or `flush()`.
  **Action:** After mutating, schedule a sync exactly as `__setitem__` does. Fix alongside B9.
  **Done (2026-08-03):** `__delitem__` and `popitem` now call the shared `_schedule_sync()` after mutating `_cache`, so removals persist on the same debounce as writes (no explicit `flush()` needed). `popitem` schedules only after `_cache.popitem()` succeeds, so the empty-dict `KeyError` path is unchanged. Regression test `test_deletion_persisted`.
- [x] **S5 — `StoredDict` uses non-daemon busy-wait threads** `src/apsbits/utils/stored_dict.py:73,140-152`.
  Each idle `__setitem__` spawns a `threading.Thread` **without `daemon=True`** that busy-polls `time.sleep(0.005)`. Non-daemon threads can delay interpreter shutdown; the spin wastes CPU.
  **Action:** Use `daemon=True` and a `threading.Event`/`Timer` instead of a poll loop. *(Medium priority — working code; refactor carefully with tests.)*
  **Done (2026-08-03):** replaced the busy-poll (`_delayed_sync_to_storage` + the now-orphaned `_sync_loop_period`, both removed) with a debounced daemon `threading.Timer`: `_schedule_sync()` restarts the timer on each write/deletion; `_sync_to_storage()` performs the locked write when it fires. `_schedule_sync()` now sets `sync_in_progress=True` synchronously (previously set inside the thread), which also makes the pre-existing `assert sdict.sync_in_progress` in `test_StoredDict` deterministic. `_sync_key` left in place per the REJECTED-list caution. Added `sdict.flush()` after the trailing `del` in `test_StoredDict` to cancel the timer that the S4 fix now schedules (prevents a post-test daemon write to the unlinked temp file).
- [x] **S6 — `get_config()` returns the live mutable global** `src/apsbits/utils/config_loaders.py:98-105`.
  Any caller can do `get_config()["X"] = ...` and silently corrupt the single-source-of-truth for the whole session (compounds N11).
  **Action:** Return `types.MappingProxyType(_iconfig)` (or a copy). **Pre-check:** grep for `get_config()[...] =` mutations first (none found in a quick scan, but confirm before applying).
  **Done (2026-08-03):** `get_config()` returns `types.MappingProxyType(_iconfig)`; return annotation relaxed to `Mapping[str, Any]`. **Pre-check confirmed:** all 5 callers (`instrument_init`, `helper_functions`, `baseline_setup`, `test_general` ×2) only read — no `get_config()[...] =`, no aliased `iconfig[...] =`/`.update`/`.pop`/`del`, no `isinstance(...,dict)`/`dict(get_config())` — so no caller migration was needed. `load_config`'s return is intentionally left mutable (the write path), per this item's scope.

### api/
- [ ] **S7 — Stale/false docstrings** `src/apsbits/api/create_new_instrument.py:5` and `src/apsbits/api/__init__.py:4-5`.
  Module docstring claims it "updates pyproject.toml and .templatesyncignore" — `main()` does neither. `api/__init__.py` still advertises CLIs for "creating, deleting, and **running** instruments" after `bits-run` was deleted.
  **Action:** Correct both docstrings to describe actual behavior.
- [ ] **S8 — No test coverage for the create path** (`src/apsbits/tests/`).
  `test_delete_instrument.py` is robust, but there is **no `test_create_new_instrument.py`** — so the N5 (no rollback) and N6 (`os.rename`) defects are uncatchable in CI.
  **Action:** Add `test_create_new_instrument.py` covering the happy path + N5/N6 failure/rollback. *(Note: `test_delete_instrument.py` already exercises `create_new_instrument` indirectly; a dedicated file makes the failure modes first-class.)*
- [ ] **S9 — CLIs trust `os.getcwd()` as the workspace root with no validation** `create_new_instrument.py:103`, `delete_instrument.py:40,55`.
  Running from the wrong directory silently creates/deletes under an arbitrary path.
  **Action (optional / discuss):** require a workspace sentinel (`pyproject.toml` + `src/` in cwd) before any FS mutation. Behavior change — confirm with maintainers first.

### packaging / CI
- [x] **S10 — `setuptools_scm` uses deprecated `write_to`** `pyproject.toml:188`.
  setuptools_scm 8 (floor `>=8.0`) deprecated `write_to` in favor of `version_file`.
  **Action:** Rename `write_to` → `version_file`.
- [x] **S11 — No `concurrency:` guard on workflows** `.github/workflows/code.yml`, `docs.yml`.
  Rapid pushes spawn overlapping matrix + docs runs.
  **Action:** Add `concurrency: {group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true}` to each.
- [x] **S12 — No least-privilege `permissions:` on `code.yml`/`docs.yml`** (top level).
  `pypi.yml` scopes token perms correctly; the other two inherit the broad default `GITHUB_TOKEN`.
  **Action:** Add `permissions: {contents: read}` at workflow level (docs' gh-pages step can elevate locally).

### testing
- [x] **S13 — Config path-injection + `get_config()` round-trip untested** `tests/test_config.py`.
  `load_config()` is documented to inject `ICONFIG_PATH`/`INSTRUMENT_PATH`/`INSTRUMENT_FOLDER`, and `get_config()` should return the same populated dict — the core config contract, entirely untested.
  **Action:** Assert the injected keys and the `load_config → get_config` round-trip.
  **Done (2026-08-03):** added 5 tests to `test_config.py` — path-key injection, `load_config → get_config` round-trip, `get_config()` read-only view raises `TypeError` on write (S6), replace-not-merge (N11), and `reset_config()` clears.
- [ ] **S14 — NeXus writer enable-branch untested** `tests/test_general.py` (or new).
  Tests assert `specwriter` but never `nxwriter`; the `NEXUS_DATA_FILES.ENABLE` toggle has zero coverage.
  **Action:** Add a test that enables it and asserts the `nxwriter` global/callback appears (mirror the specwriter path).
- [ ] **S15 — Harden import-purity beyond TCP `connect`** `tests/test_import_purity.py`.
  The guard blocks only `socket.socket.connect`; EPICS CA uses UDP broadcast (`bind`/`sendto`), and purity also forbids fs writes/object construction at import.
  **Action:** Extend the subprocess script to also trip on UDP socket ops and stray file writes.

### docs
- [ ] **S16 — Remove/deprecate the dead `DM_SETUP_FILE` iconfig key** `docs/source/guides/setting_iconfig.rst:132-138`.
  Its only consumer (`aps_dm_setup`) is deleted; documenting it leads users to set a no-op key. Same root cause as B4, distinct file.
  **Action:** Delete or mark-deprecated the `DM_SETUP_FILE` rows.
- [ ] **S17 — Explain the `oregistry.clear()` two-phase pattern** `docs/source/guides/startup.rst` (after the B6 rewrite).
  The guide never explains `startup.py:56-59` ("discard oregistry items loaded above"), the least-obvious part of the real flow.
  **Action:** Add a short "why we clear the registry" note.
- [ ] **S18 — Widen the getting-started Python version** `README.md:21` + `CLAUDE.md`.
  Getting-started pins `python=3.11`, but CI tests 3.11 **and** 3.12 and `bits_dev` is 3.12.
  **Action:** State "3.11 or 3.12".
- [x] **S19 — Fix stale CLAUDE.md linter note** `CLAUDE.md` (Conventions/gotchas).
  It still says the `[tool.black]` / `[tool.flake8]` sections "are legacy … in `pyproject.toml`" — but R1/R2 already deleted them.
  **Action:** Reword to "ruff/ruff-format are the only configured tools; black/flake8 have been removed" (keep the "match 88, not 115" guidance historically if useful, but stop implying the blocks exist).

---

## 6. Step-by-step remediation plan (agent-executable)

Ordered so an agent can work top-to-bottom: safest/no-behavior-change first, then correctness,
then coverage, then docs. Each **batch is one PR**. Anchors re-verified 2026-07-24 (they may shift
by ±a few lines as edits land — re-`grep` the quoted token if an anchor misses). Preferred runner
per CLAUDE.md: `conda run -n bits_dev <cmd>`. Every changed line should trace to a listed item
(Karpathy §3: surgical — do not "improve" adjacent code).

### Batch 0 — Baseline (do first) — ✅ DONE 2026-07-24
- [x] Work off of the `legacy_cleanup` branch for all edits
- [x] Establish green baseline: `conda run -n bits_dev python -m pytest ./src` → **95 passed** (1 warning: unregistered `slow` marker, fixed by N18).
- **Pre-existing lint failure — FIXED standalone 2026-07-24:** `pre-commit run --all-files` had been **red** because ruff wanted `import tomllib` in the stdlib group in `src/apsbits/utils/config_loaders.py` (leftover from R5's `tomli`→`tomllib`). Applied that one-line import move as its own change (kept separate from the Batch 1 changeset); `pre-commit run --all-files` is now **fully green**. Batch 4's *other* config_loaders.py items (R8, N11, R7, S6) remain open.

### Batch 1 — Packaging & CI hygiene (no runtime behavior change) — R13/N1, N17, N18, N19, N20, N21, B14, S10, S11, S12, S19 — ✅ DONE & VERIFIED 2026-07-24
> Executed 2026-07-24: all items below applied. Verified — `pre-commit` passes on the changed files; `pytest` 65 (not slow) + 30 (slow) = **95 passed**, `PytestUnknownMarkWarning` gone; `pip install -e . --no-deps` rebuilds with `version_file` OK. N19 removed `mypy` from the dev extra (it wasn't installed in `bits_dev` anyway). A pre-existing ruff import-order issue in `config_loaders.py` surfaced by `--all-files` was fixed **standalone** (kept out of this Batch 1 changeset); `pre-commit run --all-files` is now green.
File `pyproject.toml`:
- [ ] N1/R13: line 87 `addopts = ["--import-mode=importlib", "-x"]` → `["--import-mode=importlib"]`.
- [ ] N18: in `[tool.pytest.ini_options]` add `markers = ["slow: marks tests as slow (deselect with '-m \"not slow\"')"]` (optionally add `"--strict-markers"` to addopts).
- [x] N17: line 43 — **(done 2026-07-24)** **keep** the pin (do NOT go to 2.x); add an inline comment, e.g. `# 2.x is a tiled-based rewrite that drops the v1 _drivers/.temp()/.v1/.v2 APIs used in catalog_init.py & run_engine_init.py. tiled support comes from bluesky-tiled-plugins/tiled, not databroker — no bump needed for tiled.` Optionally widen to `"databroker >=1.2.5,<2",` (the `<2` bound is the guard). Do not attribute the constraint to bluesky-tiled-plugins — it does not import databroker; apsbits' own catalog code does.
- [ ] N21: line 59 dev extra — add `"pytest-cov"`, `"pytest-qt"`.
- [ ] N19: line 59 — remove `"mypy"` from the dev extra **or** add a `[tool.mypy]` section + pre-commit hook + CI step. Default: remove (simplicity) unless maintainers want typing.
- [ ] S10: line 188 `write_to` → `version_file`.

File `.github/workflows/pypi.yml`:
- [ ] B14: strip "and TestPyPI" from `name` (line 1) and job `name` (line 17).

Files `.github/workflows/code.yml`, `docs.yml`:
- [ ] S11: add `concurrency: {group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true}` near the top of each.
- [ ] S12: add top-level `permissions:\n  contents: read` to each (docs' gh-pages deploy step gets a scoped `permissions:` of its own if needed).

File `.github/dependabot.yml`:
- [ ] N20: add a `- package-ecosystem: "pip"` block (`directory: "/"`, `schedule: {interval: "weekly"}`).

File `CLAUDE.md`:
- [ ] S19: reword the stale `[tool.black]`/`[tool.flake8]` "legacy sections" note (they no longer exist).

- **Verify:** `pre-commit run --all-files`; `conda run -n bits_dev python -m pytest -m "not slow" ./src` (proves the marker registered → `-m` works); `conda run -n bits_dev python -m pytest -m slow ./src`; `python -c "import apsbits"`; `conda run -n bits_dev pip install -e '.[dev]'` succeeds and can run the suite.

### Batch 2 — core/instrument_init.py correctness — B2, S2, S3, N2, N3, N7, N14 — ✅ DONE & VERIFIED 2026-07-24
> Executed 2026-07-24: all items applied. N3 chose **return** (not raise) on a missing file — `startup.py` calls `make_devices` for `devices_aps_only.yml` only `if host_on_aps_subnet()`, so a missing file shouldn't hard-crash startup; N2 (present-but-malformed file) re-raises. Added `tests/test_instrument_init.py` (8 tests). Verified: full suite **105 passed**, startup smoke OK, ruff clean.
File `src/apsbits/core/instrument_init.py`:
- [ ] B2: line 171 → `if device_manager == "guarneri":` (delete `or None`; keep the `elif device_manager is None:`).
- [ ] S2: add a terminal `else:` in `init_instrument` (169-185) → `logger.error("Unknown device_manager: %r", device_manager); return None, None`.
- [ ] N2: lines 118-120 — after the two `logger.error`s, `raise` (re-raise the caught exception).
- [ ] N3: lines 103-104 — after `logger.error("Device file not found: %s", device_path)`, `return`.
- [ ] S3/N7: line 86 + the 108-125 dispatch — add `else` branches: warn when `clear` is truthy but `device_manager` isn't a `guarneri.Instrument` (N7); error/raise on an unrecognized `device_manager` value in the load dispatch (S3).
- [ ] N14: docstring 49-67 — `file` is required (no `iconfig.yml` fallback); fix the type to `str`; reorder `path` before `device_manager`; change the EXAMPLE from `RE(make_devices(...))` to `make_devices(file="custom_devices.yml")`.
- [ ] Tests (feeds N22/N23): add `tests/test_instrument_init.py` (or extend `test_make_devices.py`) — `init_instrument(None) == (None, None)`; `init_instrument("bogus") == (None, None)`; `make_devices` with a missing file returns without sleeping/raising per N3; `make_devices` re-raises on a malformed device file (N2).
- **Verify:** new tests pass; `conda run -n bits_dev ipython -c "from apsbits.demo_instrument.startup import *"` (startup smoke) still succeeds; full `pytest ./src` green.

### Batch 3 — core/run_engine_init.py — S1 — ✅ DONE & VERIFIED 2026-07-24
> Executed 2026-07-24: removed the dead `PersistentDict` branch (iconfig has no handler key, so nothing to wire). Added `tests/test_run_engine_init.py` (2 tests, incl. `RE.md` is a `StoredDict`). Pure dead-code removal — no behavior change; full suite 105 passed, startup smoke OK.
- [ ] S1: `run_engine_init.py:99,106` — remove the dead `PersistentDict` branch (or drive `handler_name` from `iconfig` if it's meant to be configurable; confirm intent from `iconfig.yml` before choosing).
- **Verify:** `pytest ./src`; startup smoke; add/adjust an `init_RE` unit test (N22) that asserts the StoredDict handler path is taken.

### Batch 4 — utils/config_loaders.py — R8, N11, R7, S6, S13 — ✅ DONE & VERIFIED 2026-08-03
> Executed 2026-08-03: all items applied. R8 delegates `load_config`'s YAML read to `load_config_yaml` (now `safe_load`) and keeps TOML inline (`tomllib` needs a binary handle) — this narrows some error logs (see R8 note). N11 adds `clear()` + a public `reset_config()`. S6 pre-check confirmed all 5 `get_config()` callers are read-only. Added 5 tests to `test_config.py`. Verified: full suite **108 passed, 2 failed** — the 2 failures (`test_general::test_sim_plans`) are pre-existing `S-DCCT:CurrentM` EPICS timeouts (this host resolves as on-APS-subnet, so `devices_aps_only.yml` loads; proven identical on the stashed baseline), unrelated to this batch. `ruff`/`ruff-format` clean on changed files; IPython startup smoke OK.
File `src/apsbits/utils/config_loaders.py`:
- [x] R8: line ~153 `yaml.load(content, yaml.Loader)` → `yaml.safe_load(content)`; then make one loader delegate to the other to kill the duplicated open/empty/except ladder.
- [x] N11: line ~65 `_iconfig.update(config)` → `_iconfig.clear(); _iconfig.update(config)`; add a `reset_config()` helper.
- [x] R7: delete `validate_instrument_path` (173-239) — **first** `grep -rn validate_instrument_path src/` to confirm zero functional callers.
- [x] S6: `get_config()` (98-105) → return `types.MappingProxyType(_iconfig)`. **Pre-check** `grep -rn "get_config()\[" src/` for write-mutations; if any exist, fix those callers first.
- [x] S13: add tests in `tests/test_config.py` — injected `ICONFIG_PATH`/`INSTRUMENT_PATH`/`INSTRUMENT_FOLDER` present after `load_config`; `load_config → get_config` round-trip; `reset_config()` clears.
- **Verify:** `conda run -n bits_dev python -m pytest src/apsbits/tests/test_config.py -vvv`; confirm `StoredDict.load` + `configure_logging` still load YAML (they call `load_config_yaml`); startup smoke.

### Batch 5 — utils/stored_dict.py durability — B9, S4, S5 — ✅ DONE & VERIFIED 2026-08-03
> Executed 2026-08-03: all three items applied together (they share the sync machinery). S5's Timer redesign is what makes B9's "unconditional flush" safe — flush and the timer both write under the shared `_lock`, so there's no concurrent-write race. `_sync_loop_period` was removed (orphaned by dropping the poll loop); `_sync_key` kept (REJECTED-list caution). Added 2 tests → `test_stored_dict.py` **15 passed** (was 13); ruff clean; IPython startup smoke OK. Full-suite deltas are pre-existing/flaky, not from this batch (see the scoreboard totals note).
File `src/apsbits/utils/stored_dict.py`:
- [x] B9: add `self._lock = threading.RLock()` in `__init__`; rewrite `flush()` (154-160) to acquire the lock and unconditionally `StoredDict.dump(...)`, then reset `_sync_deadline`/`sync_in_progress`. Remove the `if not sync_in_progress` short-circuit.
- [x] S4: `__delitem__` (78-88) and `popitem` (162-169) — after mutating `_cache`, schedule a sync like `__setitem__` (both now call `_schedule_sync()`).
- [x] S5: make the sync thread `daemon=True` and replace the 5 ms poll with an `Event`/`Timer` (done via a debounced daemon `threading.Timer` in `_schedule_sync`/`_sync_to_storage`).
- [x] Tests: extended `tests/test_stored_dict.py` — `test_flush_durable_during_sync` (B9: mutate, flush while `sync_in_progress`, reload from disk, assert the value) and `test_deletion_persisted` (S4: `__delitem__`/`popitem` persist without an explicit flush).
- **Verify:** `conda run -n bits_dev python -m pytest src/apsbits/tests/test_stored_dict.py -vvv` → **15 passed**.

### Batch 6 — utils small robustness fixes — R9, N8, N9, N10, N12, N13, N16
- [ ] R9: `sim_creator.py:185-186` — delete the two dead kwargs assignments.
- [ ] N8: `logging_setup.py:187-188` — iterate handlers, set level on `logging.StreamHandler` instances (drop `handlers[0]`).
- [ ] N9: `aps_functions.py` — add `logger = logging.getLogger(__name__)` and `logger.debug(...)` in the `except` (23-24).
- [ ] N10: `controls_setup.py:128-135` — add `else: logger.warning(...)` when `EpicsSignalBase` already instantiated.
- [ ] N12: `helper_functions.py:77,117` + `logging_setup.py:230,231,284` — `getattr(logger, "bsdev", logger.debug)(...)` (or register BSDEV at import).
- [ ] N13: `metadata.py:103` — `re_metadata(iconfig=None)` + `iconfig = iconfig or {}`.
- [ ] N16: `metadata.py:99` — downgrade to `logger.debug` and reword ("RunEngine metadata path: %s").
- **Verify:** `pytest ./src`; startup smoke; `ruff` clean (B006 for N13).

### Batch 7 — api/create_new_instrument.py — N15, N6, N5, S7, S8, (S9)
File `src/apsbits/api/create_new_instrument.py` (+ `api/__init__.py`):
- [ ] N15: 111-114 — collapse the backslash-continued `print` to one line.
- [ ] N6: 27-31 — assert `qs_host.sh` exists before `os.rename`; copy the specific file instead of `glob('*')`; refuse/warn if `{name}_qs_host.sh` already exists.
- [ ] N5: 124-142 — wrap the create steps; on exception `shutil.rmtree(new_instrument_dir, ignore_errors=True)` + unlink the created `{name}_qs_host.sh`, then `sys.exit(1)`.
- [ ] S7: fix the module docstring (drop the false pyproject/.templatesyncignore claim) and `api/__init__.py` ("running instruments" → remove).
- [ ] S8: add `tests/test_create_new_instrument.py` — happy path in a tmp cwd, then N5 rollback (force a failure after copy → assert `src/<name>` removed) and N6 (missing `qs_host.sh` → clear error).
- [ ] S9 *(optional, behavior change — confirm first)*: validate a workspace sentinel before FS mutation in both CLIs.
- **Verify:** `conda run -n bits_dev python -m pytest src/apsbits/tests/test_create_new_instrument.py src/apsbits/tests/test_delete_instrument.py -vvv`; manual smoke in a scratch dir: `bits-create tmp_probe` then `bits-delete tmp_probe --force`.

### Batch 8 — tests — B7, B13, R10, N24, N22, N23, S14, S15, W14-TODO
File `src/apsbits/tests/conftest.py`:
- [ ] B7: `ioc` fixture — `import shutil; if shutil.which("softIoc") is None: pytest.skip(...)` and wrap `Popen` in `try/except FileNotFoundError: pytest.skip(...)`.
- [ ] B13: line 109 `prefix="test1:"` → `prefix="test:"`.
- [ ] N24: `runengine_with_devices` (23-45) — `scope="function"` (or reset `_iconfig`/`__main__` between tests using the new `reset_config()` from Batch 4) and document the shared-state contract.

Other test files:
- [ ] R10: delete dead `TYPE_CHECKING` import + `if TYPE_CHECKING: pass` in `test_config.py` and `test_general.py` **only**.
- [ ] N22: add direct unit tests for `init_RE`, `setup_baseline_stream`, `host_on_aps_subnet`, `prepare_bits`, `dynamic_import` (start with `dynamic_import` happy + two `ValueError`s).
- [ ] N23: strengthen `test_general.py::test_startup` — `isinstance(RE, RunEngine)`, catalog type on `cat`, `sd` present in `RE`'s subscriptions, `oregistry["sim_motor"]`/`["sim_det"]` resolve (replace the log-text check in `test_make_devices.py`).
- [ ] S14: add a `nxwriter` enable-branch test (mirror the specwriter path).
- [ ] S15: extend `test_import_purity.py` to also trip on UDP socket ops + stray file writes at import.
- [ ] W14-TODO: fill the `TILED_PROFILE_NAME`/`TILED_PATH_NAME`/`TILED_SAVE_PATH` parametrize cases in `test_catalog_init.py:76-88`.
- **Verify:** full suite green in `bits_dev` including `-m slow` and the `ioc` tests; confirm the suite also *skips* cleanly where `softIoc` is absent (temporarily rename it / test on a non-EPICS env if available).

### Batch 9 — docs — B4, B6, S16, S17, S18
- [ ] B4: delete `docs/source/guides/dm.rst`; remove `dm` from `guides/index.rst:21`; delete the `# aps_dm_setup(...)` comment at `startup.py:62`.
- [ ] B6: rewrite `docs/source/guides/startup.rst:55-129` to match real `startup.py` — DM commented-out, `make_devices(clear=False, file="devices.yml", device_manager=instrument)` (not `RE(...)`), `devices_aps_only.yml`, callbacks from `demo_nexus_callback`/`demo_spec_callback`, `nxwriter_init(RE, iconfig)`.
- [ ] S16: remove/deprecate the `DM_SETUP_FILE` rows in `setting_iconfig.rst:132-138`.
- [ ] S17: add the `oregistry.clear()` two-phase note to `startup.rst`.
- [ ] S18: `README.md:21` + `CLAUDE.md` — "3.11 or 3.12".
- **Verify:** `make -C docs clean html` builds with no warnings referencing `dm_plans`/`aps_dm_setup`/removed callback modules; grep `docs/` for `dm_plans|aps_dm_setup|device_aps_only|create-bits|delete-bits` returns nothing.

### Batch 10 — Final verification & changelog
- [ ] Full suite: `conda run -n bits_dev python -m pytest -vvv ./src` (expect green incl. slow + ioc).
- [ ] `pre-commit run --all-files`.
- [ ] `conda run -n bits_dev ipython -c "from apsbits.demo_instrument.startup import *"`.
- [ ] `make -C docs clean html`.
- [ ] Add a `HISTORY.rst` entry summarizing the fixes.
- **Verify:** all four commands succeed; PR description links each batch to its item IDs.

**Sequencing notes / dependencies:**
- N18 (register marker) must precede any use of `-m "not slow"` / `-m slow` in later verifies.
- N11 + `reset_config()` (Batch 4) is a prerequisite for the cleanest N24 fix (Batch 8).
- S6 (read-only `get_config`) can break mutating callers — run its grep pre-check before Batch 4.
- B6/N14 both concern the `make_devices` call shape — keep the docstring EXAMPLE (N14) and the guide (B6) consistent.
- Batches 1, 6, 9 are independent and low-risk; 2/3/4/5 change runtime behavior — land with their tests.

---

## Checked but REJECTED by verification (do not act on these)

- **`baseline_setup` "mutates list while iterating / pops from oregistry"** — false; it iterates a fresh list and does not pop.
- **`StoredDict._sync_key` "assigned but never used"** — partly true (never read) but it *is* assigned/maintained; removal needs more care than a one-line delete. Re-evaluate before touching.
- **"Starter/template repo URL inconsistent across docs"** — the three URLs are each individually correct for their context, not a copy-paste error.
- **`demo_instrument/README.md` "lists configs/ subdir that no longer exists"** — false; the `configs/` layout is current. The proposed "fix" used wrong filenames.
- **B2's original fix `if ... or device_manager is None:`** — *rejected on re-audit* (2026-07-24): it would make `init_instrument(None)` construct a live instrument. See the rewritten B2.
