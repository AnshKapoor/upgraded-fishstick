# Pull Request Draft

## Summary
- Harden `Extendable.file_list()` by gathering file lists from extensions via `getattr` and logging once when an extension omits the attribute, preventing AttributeError during GUI aggregation.
- Provide a default `file_list` property on `RecordableSpaceWire` so SpaceWire-based hardware modules always expose a safe, empty list for file retrieval workflows.
- Implement a matching `file_list` property on the BrickMk4 hardware driver to align it with GUI expectations without exposing nonexistent files.

## Testing
- Not run (not requested).
