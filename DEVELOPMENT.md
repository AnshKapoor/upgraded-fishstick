# GSpy Development Guide

## Setting up debugging/development environment

## Including the DHU simulator into a custom view
- Create "simulator.py" file into "/screens" folder, add the simulator into the GUI.
- Create "service1.ui" file into "/ui" folder with Qt designer, implement the button layout for the simulator.
- Create "BrickMk4_Plugin_service1.py" file into "/plugins/juice" folder, bind the buttons to background tasks.
- Create "pus_parser.py" file into "/utils" folder, implement the parsing of TM message.

## Including SpaceWire into a custom view
- Use WidgetWithExtension, take BrickMk4_Plugin_Transmit.py as an example

## Including the Power Supply into a view

## Implementing a SpaceWire packet encoder and decoder

## Integrating the Recorder

## Planned features currently unavailable
- Recorder with main "replay mode" functionality stopping all external communication
- Data output views