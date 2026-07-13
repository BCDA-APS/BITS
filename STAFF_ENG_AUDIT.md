# apsbits — Staff Engineer Audit & Action Plan

Senior-staff review of the `apsbits` package. Each item is a checkbox an agent can execute
directly: it names the file, the symbol, and the exact change. Items are grouped into the four
requested buckets and ordered by severity within each.

**Method:** 6 parallel subsystem auditors (core, utils, api, packaging, testing, docs) read the
actual source; every "delete/redundant" and high-severity claim was then adversarially
re-verified against the code. 74 findings confirmed; 4 claims were checked and **rejected** (see
end). IDs in brackets trace back to the audit.

## Fix-first priority (highest impact)

1. `init_instrument(None)` returns `(None, None)` instead of guarneri — `instrument_init.py:171` (B2)
2. `bits-delete <missing>` reports success — `delete_instrument.py` (B3)
3. Three in-toctree docs pages describe removed/renamed code — `dm.rst`, `api.rst`, `startup.rst` (B4–B6)
4. `softIoc` test fixture hard-fails (no skip) where EPICS base is absent — `conftest.py` (B7)

> **B1 (`bits-run`) — RESOLVED by removal.** The broken `bits-run` CLI and its module/tests/docs were deleted rather than fixed (`run_instrument.py`, `test_run_instrument.py`, the `bits-run` entry point, and its docs/diagram references). N4 (which targeted the same module) is likewise dropped.

---

## 1. BAD — must be changed or removed (real defects)

- [ ] **B2 — Remove the dead `or None` in `init_instrument`** `src/apsbits/core/instrument_init.py:171`.
  `if device_manager == "guarneri" or None:` reduces to `device_manager == "guarneri"`; passing `None` falls through to the error branch and returns `(None, None)`.
  **Action:** Change to `if device_manager == "guarneri" or device_manager is None:`, then delete the now-unreachable `elif device_manager is None:` block (lines 180-185) and convert the `happi` chain to a final `else:` that raises on unknown manager strings. Add a regression test for `init_instrument(None)`.

- [x] **B3 — Make `bits-delete` fail on a missing instrument** `src/apsbits/api/delete_instrument.py:114-120`.
  Currently prints `Error: ... does not exist` but does not exit, then proceeds to prompt and print "have been moved" success.
  **Action:** After the print at line 116 add `sys.exit(1)`. Leave the missing-qserver-script case non-fatal (it is only a warning), but do not claim success when nothing moved.

- [ ] **B4 — Remove/rewrite stale Data-Management guide** `docs/source/guides/dm.rst` (in toctree at `guides/index.rst:21`).
  Documents the removed `dm_plans` module and deleted `aps_dm_setup()` (per `HISTORY.rst:115`).
  **Action:** Delete `dm.rst` and remove line 21 from `guides/index.rst` (or rewrite to point at apstools DM helpers). Also delete the stale `# aps_dm_setup(iconfig.get("DM_SETUP_FILE"))` comment at `startup.py:62`.

- [x] **B5 — Fix wrong CLI names in API docs** `docs/source/api/api.rst:27-43`.
  Shows `create-bits --name … --path …`, `delete-bits …` — neither matches reality; real commands are `bits-create <name>`, `bits-delete <name>` (no `--name`/`--path` flags).
  **Action:** Replace the Example Usage blocks with the real command names and positional args.

- [ ] **B6 — Update outdated startup guide** `docs/source/guides/startup.rst:55-129`.
  Describes an active `aps_dm_setup` block, `RE(make_devices(...))`, and old callback import paths that no longer match `demo_instrument/startup.py`.
  **Action:** Rewrite to mirror current `startup.py`: DM call shown commented out, `make_devices(...)` called directly (not via `RE(...)`), callback imports `from .callbacks.demo_nexus_callback import nxwriter_init` / `from .callbacks.demo_spec_callback import init_specwriter_with_RE`.

- [ ] **B7 — Skip EPICS tests when `softIoc` is absent** `src/apsbits/tests/conftest.py:48-124`.
  The `ioc` fixture unconditionally `subprocess.Popen(["softIoc", ...])`; without EPICS base it raises and dependent tests error instead of skipping.
  **Action:** At the top of the fixture: `import shutil; if shutil.which("softIoc") is None: pytest.skip("softIoc (EPICS base) not available")`, and wrap the `Popen` in `try/except FileNotFoundError: pytest.skip(...)`.

- [x] **B8 — Fix misleading `with_registry` error message** `src/apsbits/core/instrument_init.py:198`.
  References a non-existent `set_instrument()`.
  **Action:** Change to `raise RuntimeError('Instrument not set. Call init_instrument("guarneri") first.')`.

- [ ] **B9 — Make `StoredDict.flush()` durable** `src/apsbits/utils/stored_dict.py:154-160`.
  When a background sync is in progress, `flush()` returns without writing, risking data loss on shutdown.
  **Action:** Add `self._lock = threading.RLock()` in `__init__`; in `flush()` acquire the lock, unconditionally `StoredDict.dump(self._file, self._cache, title=self._title)`, then set `_sync_deadline=time.time()` and `sync_in_progress=False`. Remove the `if not sync_in_progress` short-circuit.

- [x] **B11 — Fix wrong-project milestones link** `HISTORY.rst:27`.
  Points to `github.com/prjemian/hklpy2/milestones` (copy-paste leftover).
  **Action:** Change to `https://github.com/BCDA-APS/BITS/milestones`.

- [x] **B12 — Fix release-note typo** `HISTORY.rst:101`: `Documentation overhaul1` → `Documentation overhaul`.

- [ ] **B13 — Fix `ioc` fixture prefix mismatch** `src/apsbits/tests/conftest.py:109`.
  Yields `prefix="test1:"` but the record is `test:scan_id`.
  **Action:** Change to `prefix="test:"` so `prefix + "scan_id"` reconstructs the PV.

- [ ] **B14 — Drop false "TestPyPI" claim** `.github/workflows/pypi.yml:1,17`.
  Names say "PyPI and TestPyPI" but no TestPyPI step exists.
  **Action:** Remove "and TestPyPI" from the workflow `name` (line 1) and job `name` (line 17).

---

## 2. REDUNDANT — no longer needed / safe to delete

- [x] **R1 — Delete dead `[tool.black]` config** `pyproject.toml:89-110`.
  Black is never installed or run; its `line-length=115` contradicts the enforced ruff `88`.
  **Action:** Delete the whole `[tool.black]` block. ruff-format is the sole formatter.

- [x] **R2 — Delete dead `[tool.flake8]` config** `pyproject.toml:113-125`.
  flake8 is not in dev extra, pre-commit, or CI; `max-line-length=115` again contradicts ruff.
  **Action:** Delete the block. Do *not* blindly port its ignores into ruff — the ruff config is already curated.

- [x] **R3 — Delete dead `[tool.isort]` config + dep** `pyproject.toml:127-131,61`.
  ruff's `I` rule (with `force-single-line`) handles import sorting.
  **Action:** Delete the `[tool.isort]` block and remove `"isort"` from the `dev` extra.

- [x] **R4 — Drop the bogus `"dot"` doc dependency** `pyproject.toml:78`.
  `dot` on PyPI is an unrelated ML package, not Graphviz; the real `dot` binary is installed via apt in `docs.yml:47` and python bindings via `graphviz` (line 77).
  **Action:** Delete the `"dot",` line.

- [x] **R5 — Replace `tomli` with stdlib `tomllib`** `src/apsbits/utils/config_loaders.py:15,51,83` + `pyproject.toml:57`.
  `requires-python >=3.11` ships `tomllib`; the `tomli` backport is unnecessary.
  **Action:** `import tomllib`; `tomllib.load(f)`; `except tomllib.TOMLDecodeError`. Delete `"tomli",` from runtime deps.

- [x] **R6 — Recategorize `tomli-w` as a test-only dep** `pyproject.toml:56,79`.
  Imported only in `tests/test_config.py`; currently listed as runtime *and* duplicated in the doc extra.
  **Action:** Delete `"tomli-w"` from both `dependencies` and the `doc` extra; add it to the `dev` extra.

- [ ] **R7 — Delete dead `validate_instrument_path`** `src/apsbits/utils/config_loaders.py:173-239`.
  No callers; also buggy (requires *both* `iconfig.yml` AND `iconfig.toml`).
  **Action:** Delete the function. (If kept instead, change the file check to require *either* format.)

- [ ] **R8 — Consolidate the two YAML loaders** `src/apsbits/utils/config_loaders.py:24-95` & `118-170`.
  `load_config` and `load_config_yaml` duplicate the open/empty-check/except ladder and diverge on safety: `load_config_yaml` uses unsafe `yaml.load(content, yaml.Loader)`.
  **Action (do regardless):** change line 153 to `yaml.safe_load(content)`. Then have one helper delegate to the other to remove duplication.

- [ ] **R9 — Remove dead duplicate kwargs in `motors()`** `src/apsbits/utils/sim_creator.py:185-186`.
  Both assignments are immediately overwritten by the following `kwargs.update({...})`.
  **Action:** Delete lines 185-186.

- [ ] **R10 — Remove empty `TYPE_CHECKING` blocks** `tests/test_config.py:7,15-16` and `tests/test_general.py:8,12-13`.
  **Action:** Delete the `from typing import TYPE_CHECKING` import and the `if TYPE_CHECKING: pass` blocks (preserve the trailing comment in `test_general.py`).

- [x] **R11 — Remove commented future entry points** `pyproject.toml:244-250`.
  Six `# bits-device-*` / `# bits-plan-*` placeholders plus a lone `#`.
  **Action:** Delete lines 244-250; track planned CLIs in a GitHub issue/roadmap.

- [x] **R12 — Remove the `create-bits` back-compat alias** (done: removed; keep only `bits-create`) `pyproject.toml:239`.
  Duplicates `bits-create`; intentional but undocumented.
  **Action:** Keep for now; add a deprecation note (README/HISTORY) and a removal milestone, or remove line 239 if back-compat is no longer required.

- [ ] **R13 — Drop redundant `--exitfirst` in CI** `.github/workflows/code.yml:113` — see N1 (resolve together).

---

## 3. NEEDS IMPROVEMENT — works but fragile / incomplete

### Error handling & robustness
- [ ] **N1 — Stop hiding the full test-failure picture** `pyproject.toml:135`.
  `addopts` hard-codes `-x`, forcing fail-fast on every local run too.
  **Action:** Change line 135 to `addopts = ["--import-mode=importlib"]` (drop only `-x`; keep import-mode). Leave `--exitfirst` in `code.yml:113` so fail-fast is CI-only.
- [ ] **N2 — Don't swallow device-load errors in `make_devices`** `src/apsbits/core/instrument_init.py:109-120`.
  The `try/except Exception` only logs, so a malformed `devices.yml` yields a silently empty session.
  **Action:** Re-raise after logging (or remove the catch) so startup fails fast.
- [ ] **N3 — `make_devices` should not "succeed" on a missing file** `instrument_init.py:103-131`.
  On missing `device_path` it logs an error, then still `time.sleep(pause)` and returns normally.
  **Action:** `return` (or raise `FileNotFoundError`) right after the not-found log.
- [ ] **N5 — Add rollback to `create_new_instrument`** `src/apsbits/api/create_new_instrument.py:124-142`.
  Partial failure leaves an un-rerunnable half-created `src/<name>`.
  **Action:** Wrap the three steps; on exception `shutil.rmtree(new_instrument_dir, ignore_errors=True)` and unlink the created `{name}_qs_host.sh` before `sys.exit(1)`.
- [ ] **N6 — Guard `create_qserver_script` assumptions** `create_new_instrument.py:27-31`.
  Assumes `qs_host.sh` exists before `os.rename`.
  **Action:** Assert the source exists with a clear error; copy the specific expected file rather than `glob('*')`; warn instead of overwriting an existing `{name}_qs_host.sh`.
- [ ] **N7 — Warn when `clear=True` is ignored** `instrument_init.py:86`.
  Silently skipped unless `device_manager` is a `guarneri.Instrument`.
  **Action:** Add a `logger.warning` in the else case.
- [ ] **N8 — Guard `_setup_console_logger` handler indexing** `src/apsbits/utils/logging_setup.py:187-188`.
  `logger.handlers[0]` can `IndexError` / target the wrong handler.
  **Action:** Iterate handlers and set level on `logging.StreamHandler` instances.
- [ ] **N9 — Log the fallback in `host_on_aps_subnet`** `src/apsbits/utils/aps_functions.py:23-24`.
  Broad `except` makes a misconfig indistinguishable from "off subnet"; module has no logger.
  **Action:** Add a module logger and `logger.debug(...)` inside the except.
- [ ] **N10 — Warn on no-op `set_timeouts`** `src/apsbits/utils/controls_setup.py:128-135`.
  Silently does nothing if an `EpicsSignalBase` already exists.
  **Action:** Add an `else` branch logging a warning.

### Correctness hazards (latent)
- [ ] **N11 — `load_config` must replace, not merge, global state** `src/apsbits/utils/config_loaders.py:65`.
  `_iconfig.update(config)` leaks stale keys across loads and between tests.
  **Action:** `_iconfig.clear(); _iconfig.update(config)`. Add a `reset_config()` helper for a conftest fixture.
- [ ] **N12 — Guard `logger.bsdev` calls** `src/apsbits/utils/helper_functions.py:77,117` (also `logging_setup.py:230,231,284`).
  `bsdev` only exists after `configure_logging()`; calling these utilities first raises `AttributeError`.
  **Action:** Use `getattr(logger, "bsdev", logger.debug)(...)`, or register the level eagerly at `logging_setup` import.
- [ ] **N13 — Replace mutable default arg** `src/apsbits/utils/metadata.py:103`.
  `def re_metadata(iconfig = {})` (B006).
  **Action:** Default to `None` and assign `{}` inside.
- [ ] **N14 — Reconcile `make_devices` `file` param** `instrument_init.py:39,59-71`.
  Docstring claims `file=None` defaults to `iconfig.yml`, but the body errors and returns.
  **Action:** Either implement the documented fallback or update the docstring to "required"; fix the documented param order.

### API/UX polish
- [ ] **N15 — Fix stray backslash in create message** `create_new_instrument.py:111-114`.
  Line-continuation embeds a backslash + indentation into the printed path.
  **Action:** Collapse to one line: `print(f"Creating instrument '{args.name}' from demo_instrument into '{new_instrument_dir}'.")`.
- [ ] **N16 — Quiet/relocate `get_md_path` log** `src/apsbits/utils/metadata.py:99`.
  Logs "RunEngine metadata saved to:" though it only computes a path.
  **Action:** Downgrade to `logger.debug` and reword; emit any "saved" message where the StoredDict is actually created.

### Packaging / tooling
- [ ] **N17 — Document or relax the `databroker==1.2.5` pin** `pyproject.toml:43`.
  Unexplained exact pin blocks the tiled/bluesky tree from resolving.
  **Action:** Relax to `databroker >=1.2.5,<2` with an inline comment on why 2.x is incompatible.
- [ ] **N18 — Register the `slow` marker** `pyproject.toml` `[tool.pytest.ini_options]`.
  `@pytest.mark.slow` (`test_import_purity.py:49`) is undeclared → `PytestUnknownMarkWarning`, no `-m "not slow"`.
  **Action:** Add `markers = ["slow: marks tests as slow (deselect with '-m \"not slow\"')"]`.
- [ ] **N19 — Enforce or remove `mypy`** `pyproject.toml:61`.
  In dev extra but no `[tool.mypy]` and never run.
  **Action:** Add a `[tool.mypy]` + pre-commit/CI step, or drop `"mypy"` from the dev extra.
- [ ] **N20 — Add `pip` ecosystem to Dependabot** `.github/dependabot.yml`.
  Only `github-actions` is tracked; Python deps drift unmonitored.
  **Action:** Add a `package-ecosystem: "pip"` weekly entry.
- [ ] **N21 — Align dev extras with CI test plugins** `pyproject.toml:61`.
  CI uses `pytest-cov`/`pytest-qt`/`pytest-xvfb`; dev extra has only `pytest`/`pytest-mock`.
  **Action:** Add `pytest-cov` and `pytest-qt` to the dev extra (note `pytest-xvfb` is Linux-CI-only).

### Test coverage
- [ ] **N22 — Add direct unit tests for untested modules**: `run_engine_init.init_RE`, `baseline_setup.setup_baseline_stream`, `aps_functions.host_on_aps_subnet`, `session_setup.prepare_bits`, `helper_functions.dynamic_import`. Start with `dynamic_import` happy-path + the two documented `ValueError`s.
- [ ] **N23 — Assert real post-startup invariants** (not just "import didn't throw"): `RE` is a `RunEngine`, `cat` is a catalog, `sd` subscribed, `oregistry` has `sim_motor`/`sim_det`.
- [ ] **N24 — Make `runengine_with_devices` deterministic** `tests/conftest.py:23-45`.
  Session-scoped fixture mutates module globals + `__main__`, creating order-dependence.
  **Action:** Use `scope="function"`, or call `make_devices(clear=True)` and document the shared-state contract.

---

## 4. DOES WELL — preserve (do not "fix" these)

- [ ] **W1 — Single linter/formatter via ruff**, enforced in pre-commit and gated before the test matrix (`needs: lint`). Keep ruff + ruff-format as the only source of truth when deleting R1–R3.
- [ ] **W2 — PyPI publish uses OIDC trusted publishing** (no stored token) with `twine check` first. Do not reintroduce a `PYPI_API_TOKEN`.
- [ ] **W3 — Import-purity subprocess test** (`test_import_purity.py`) blocks network I/O per-module in a fresh subprocess — strong safeguard. Keep it in CI even after registering the `slow` marker.
- [ ] **W4 — `init_RE` subscriber dispatch** is type-aware (Tiled → TiledWriter, databroker → `v1.insert`, else direct), logs with context, and re-raises rather than swallowing.
- [ ] **W5 — `init_catalog` fallback chain** (tiled profile → named databroker → temp databroker → temp tiled) isolates per-handler errors and uses `weakref.finalize` cleanup.
- [ ] **W6 — `guarneri_namespace_loader` diffs against a pre-load snapshot**, so incremental `make_devices` calls don't re-add devices.
- [ ] **W7 — BSDEV custom level registration is idempotent** (`hasattr` guard) with a regression test.
- [ ] **W8 — Metadata collection is lazily imported and cached** (`metadata.py`), keeping heavy imports out of module load.
- [ ] **W9 — `dynamic_import` validates dotted/absolute paths** before importing, giving actionable errors for bad `devices.yml` creators.
- [ ] **W10 — CLI name validation** (`^[a-z][_a-z0-9]*$`) applied before any filesystem work in both create and delete. Optionally DRY into `apsbits.api.__init__`.
- [ ] **W11 — `delete_instrument` is a reversible soft-delete** (timestamped move to `.deleted/`, `[y/N]` gate unless `--force`).
- [ ] **W12 — Deprecated docs are excluded from the Sphinx build** (`conf.py:47`).
- [ ] **W13 — README mermaid diagrams accurately mirror `startup.py`** — keep them in sync on future changes.
- [ ] **W14 — Parametrized happy/error coverage** in `test_catalog_init.py` and `test_controls_setup.py` (consider filling the TILED_PROFILE TODOs).
- [ ] **W15 — README ipython snippet is correct** — `sim_*_plan()` work zero-arg via `@with_registry`. Do not "fix" it.

---

## Checked but REJECTED by verification (do not act on these)

- **`baseline_setup` "mutates list while iterating / pops from oregistry"** — false; it iterates a fresh list and does not pop.
- **`StoredDict._sync_key` "assigned but never used"** — partly true (never read) but it *is* assigned/maintained; removal needs more care than a one-line delete. Re-evaluate before touching.
- **"Starter/template repo URL inconsistent across docs"** — the three URLs are each individually correct for their context, not a copy-paste error.
- **`demo_instrument/README.md` "lists configs/ subdir that no longer exists"** — false; the `configs/` layout is current. The proposed "fix" used wrong filenames.
