"""
Brief:\n
    STAR-System is the STAR-Dundee software suite provided with all new and future STAR-Dundee interface
    and router devices.\n
    This package is the Python API (wrapper) around the STAR-System C API.\n
    STAR-Dundee highly recommends to use a Python version of 3.8 with this API.\n

Prerequisites (required Python packages):\n
    In order to make use of the full functionality offered by the Python API of STAR-System, the user
    needs to install the (latest version of the) following packages:\n
    1. numpy\n
    2. psutil\n
    3. dill (for STAR-System version 5.02 or newer)\n

Changelog (from 5.03 to 5.04) :\n
    1. It is now possible to work with the contents of transfer operations in the registered
       callback function.\n

Author:\n
    STAR-Dundee Ltd \n
    STAR House \n
    166 Nethergate \n
    Dundee, DD1, 4EE \n
    Scotland, UK \n
    email: support@star-dundee.com \n

Copyright:\n
    2022 STAR-Dundee Ltd
"""

import os
import sys

STAR_API_LIB_LOAD_ERROR_STR = "STAR-API library not found!"
STAR_CONFIG_API_LIB_LOAD_ERROR_STR = "STAR-Config API library not found!"
STAR_TRIGGERING_API_LIB_LOAD_ERROR_STR = "STAR-Triggering API library not found!"
STAR_GENERIC_TRIGGERING_API_LIB_LOAD_ERROR_STR = "Generic STAR-Triggering API library not found!"
STAR_RMAP_TARGET_LIB_LOAD_ERROR_STR = "STAR RMAP Target Library not found!"
RMAP_API_LIB_LOAD_ERROR_STR = "RMAP Packet Library not found!"
CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR = "CCSDS/SPP/TF Packet Library not found!"

systemType = os.name
if systemType == ("nt" or "WINDOWS_NT"):
    STAR_LIB = "star-api.dll"
    CONFIG_LIB = "star_conf_api_generic.dll"
    RMAP_LIB = "rmap_packet_library.dll"
    CCSDS_SPP_TF_LIB = "ccsds_spp_packet_library.dll"
    TRIGGERING_LIB = "star_triggering.dll"
    GENERIC_TRIGGERING_LIB = "star_triggering_generic.dll"
    RMAP_TARGET_LIB = "star_rmap_target.dll"

elif systemType == "posix":
    STAR_LIB = "libstar-api.so"
    CONFIG_LIB = "libstar_conf_api_generic.so"
    RMAP_LIB = "librmap_packet_library.so"
    CCSDS_SPP_TF_LIB = "libccsds_spp_packet_library.so"
    TRIGGERING_LIB = "libstar_triggering.so"
    GENERIC_TRIGGERING_LIB = "libstar_triggering_generic.so"
    RMAP_TARGET_LIB = "libstar_rmap_target.so"

if "STAR_system.application" not in sys.modules:
    import STAR_system.application
if "STAR_system.channel" not in sys.modules:
    import STAR_system.channel
if "STAR_system.channel_listener" not in sys.modules:
    import STAR_system.channel_listener
if "STAR_system.config_port" not in sys.modules:
    import STAR_system.config_port
if "STAR_system.data_chunk" not in sys.modules:
    import STAR_system.data_chunk
if "STAR_system.device" not in sys.modules:
    import STAR_system.device
if "STAR_system.device_config" not in sys.modules:
    import STAR_system.device_config
if "STAR_system.device_listener" not in sys.modules:
    import STAR_system.device_listener
if "STAR_system.driver" not in sys.modules:
    import STAR_system.driver
if "STAR_system.driver_listener" not in sys.modules:
    import STAR_system.driver_listener
if "STAR_system.error_in_data" not in sys.modules:
    import STAR_system.error_in_data
if "STAR_system.external_port" not in sys.modules:
    import STAR_system.external_port
if "STAR_system.link_port" not in sys.modules:
    import STAR_system.link_port
if "STAR_system.link_speed_event" not in sys.modules:
    import STAR_system.link_speed_event
if "STAR_system.link_state_event" not in sys.modules:
    import STAR_system.link_state_event
if "STAR_system.packet" not in sys.modules:
    import STAR_system.packet
if "STAR_system.port" not in sys.modules:
    import STAR_system.port
if "STAR_system.remote_device" not in sys.modules:
    import STAR_system.remote_device
if "STAR_system.STAR_enums" not in sys.modules:
    import STAR_system.STAR_enums
if "STAR_system.STAR_exceptions" not in sys.modules:
    import STAR_system.STAR_exceptions
if "STAR_system.STAR_structure_classes" not in sys.modules:
    import STAR_system.STAR_structure_classes
if "STAR_system.STAR_structures" not in sys.modules:
    import STAR_system.STAR_structures
if "STAR_system.STAR_system" not in sys.modules:
    import STAR_system.STAR_system
if "STAR_system.stream_item" not in sys.modules:
    import STAR_system.stream_item
if "STAR_system.tcp_device" not in sys.modules:
    import STAR_system.tcp_device
if "STAR_system.tcp_driver" not in sys.modules:
    import STAR_system.tcp_driver
if "STAR_system.time_code" not in sys.modules:
    import STAR_system.time_code
if "STAR_system.timestamp_event" not in sys.modules:
    import STAR_system.timestamp_event
if "STAR_system.transfer_completion_listener" not in sys.modules:
    import STAR_system.transfer_completion_listener
if "STAR_system.transfer_operations" not in sys.modules:
    import STAR_system.transfer_operations
if "STAR_system.triggering_conf" not in sys.modules:
    import STAR_system.triggering_conf
if "STAR_system.triggering_types" not in sys.modules:
    import STAR_system.triggering_types

if "STAR_system.ccsds_spp_tf_enums" not in sys.modules:
    import STAR_system.ccsds_spp_tf_enums
if "STAR_system.ccsds_spp_tf_packet_library" not in sys.modules:
    import STAR_system.ccsds_spp_tf_packet_library
if "STAR_system.ccsds_spp_tf_structs_external" not in sys.modules:
    import STAR_system.ccsds_spp_tf_structs_external
if "STAR_system.ccsds_spp_tf_structs_internal" not in sys.modules:
    import STAR_system.ccsds_spp_tf_structs_internal

if "STAR_system.rmap_packet_library" not in sys.modules:
    import STAR_system.rmap_packet_library
if "STAR_system.rmap_target_pxi_if" not in sys.modules:
    import STAR_system.rmap_target_pxi_if