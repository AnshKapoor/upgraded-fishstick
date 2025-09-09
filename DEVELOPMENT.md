# GSpy Development Guide

## Setting up debugging/development environment

## Including the DHU Simulator into a Custom View

Creating a new screen for a DHU Simulator requires interaction with four files inside the `gui` folder of the Python package. These files define the front end of the window for users, the back end of the window, and the interaction with the hardware for sending packets over the SpaceWire protocol.  

As an example of this process, a simulator for **Service 1** was created and will be used in this tutorial.

The implementation of Service 1 mainly relies on four files:

```bash
gspy_egse/
└─ gui/
   ├─ screens/
   │  └─ simulator.py                 # add the simulator to the GUI
   ├─ ui/
   │  └─ service1.ui                  # Qt Designer: button layout for simulator
   ├─ plugins/
   │  └─ juice/
   │     └─ BrickMk4_Plugin_service1.py  # bind buttons to background tasks
   └─ utils/
      └─ pus_parser.py                # TM message parser
```

---

### `simulator.py` (in `screens/`)

The `screens/` folder contains entry points for different GUI windows or screens. Each file in this folder acts as a bridge between the GUI framework and the plugin/widget implementation, making it easy to register new screens and keep the GUI modular.  

The `simulator.py` file registers the **Simulator screen** within the GUI framework of the `gspy_egse` package. It imports the `BrickMk4Service1Widget` class from the plugin (`plugins/juice/BrickMk4_Plugin_service1.py`) and exposes it as the **main widget** of this screen. It also defines metadata:

  - `SCREEN_NAME` → the name displayed in the GUI (`"Simulator"`).  
  - `VERSION` → version tag of this screen (currently `1`).  
  - `MAIN_WIDGET` → the widget that provides the graphical interface and logic.  

---

### `service1.ui` (in `ui/`)

The `ui/` folder stores Qt Designer interface files (`.ui`), which define the graphical layout of windows, dialogs, and widgets used in the GUI. These files are created visually with Qt Designer and later loaded dynamically by the application.  

The `service1.ui` file defines the layout for the Simulator screen. It specifies how the GUI elements (e.g., buttons, labels, containers) are arranged, leaving the functionality (logic and event handling) to be implemented in the corresponding Python plugin.  

TODO: Include a screenshot of Qt Designer with the Service 1 example.

---

### `BrickMk4_Plugin_service1.py` (in `plugins/juice/`)

This plugin implements the Simulator logic that communicates with the SpaceWire Brick Mk4 hardware and parses returned TM (Telemetry) packets. It:

- Loads the `service1.ui` form (via `importlib.resources` + `uic.loadUi`) and wires up buttons/signals.  
- Builds and sends CCSDS/PUS TM packets to the device.  
- Receives results, parses TM using `parse_tm_packet`, and updates the GUI.  
- Supports **dummy mode** (no hardware attached) to keep the UI usable for demos.  
- Provides helper methods for buffering, transmission, and quick stress testing.  

---

### `pus_parser.py` (in `utils/`)

The `pus_parser.py` module parses **CCSDS** primary headers and **PUS (Packet Utilisation Standard) TM** headers from raw byte lists. It produces a structured `ParsedTM` object used by the Simulator plugin to render concise telemetry summaries (e.g., `TM[1,5] Progress`) and optional `step_id` values.


<!-- 
- Create "simulator.py" file into "/screens" folder, add the simulator into the GUI.
- Create "service1.ui" file into "/ui" folder with Qt designer, implement the button layout for the simulator.
- Create "BrickMk4_Plugin_service1.py" file into "/plugins/juice" folder, bind the buttons to background tasks.
- Create "pus_parser.py" file into "/utils" folder, implement the parsing of TM message. -->

## Including SpaceWire into a custom view
- Use WidgetWithExtension, take BrickMk4_Plugin_Transmit.py as an example

## Including the Power Supply into a view

## Implementing a SpaceWire packet encoder and decoder

## Integrating the Recorder

## Planned features currently unavailable
- Recorder with main "replay mode" functionality stopping all external communication
- Data output views