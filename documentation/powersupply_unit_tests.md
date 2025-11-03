# Power Supply Unit Test Guide

The `gspy-package/tests/test_powersupply.py` module exercises the defensive serial
connection logic implemented in `gspy_egse.gui.hardware_modules.powersupply`. Use
this guide to run the suite locally and extend it when new scenarios need
coverage.

## Running the tests

1. Open a terminal at the repository root.
2. Execute the dedicated test module:

   ```bash
   pytest gspy-package/tests/test_powersupply.py
   ```

   The test harness automatically injects lightweight stand-ins for optional GUI
   dependencies, so no additional environment configuration is required.

## Test structure overview

The module defines a set of helper stubs that emulate serial hardware,
background threads, and user-facing message handlers. Key components include:

- `DummySerial`: An in-memory serial implementation that supports opening,
  closing, reading, and writing behaviour expected by the driver.
- `DummyRecorder`: A test double for the global `external_recorder` dependency
  used by the driver to emit events.
- `DummyThread`: A minimal stand-in for `threading.Thread` that records when
  worker threads would have been started.

The fixtures expose these stubs through `pytest` so each test can operate in a
fully controlled environment.

## Adding new scenarios

When implementing new behaviours in the power supply module, follow these
steps to add coverage:

1. **Reuse the existing helpers.** The test harness already patches the serial
   constructor, recorder, and thread factory. You can access the configured
   doubles by requesting the appropriate fixtures.
2. **Model message handler interactions.** Instantiate `DummyMessageHandler` to
   inspect success, warning, and error messages issued by the driver.
3. **Extend or refine stubs cautiously.** If a new feature requires extra
   recorder or serial capabilities, update the local stub implementations with
   descriptive comments and docstrings to document the expectations.
4. **Assert disconnection safety.** Always verify that new features respect the
   `is_connected()` guard so failures remain graceful.

By following these guidelines, the power supply tests will remain easy to run
and maintain while providing thorough regression coverage for connection
handling.
