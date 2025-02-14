class SpwCmdGrp:
    (
        Compression,
        Gpio,
        Peu,
        RamFs,
        Sdram,
        SoCWire,
        Spi,
        System
    ) = range(1, 9)


class CompressionCmds:
    (
        InitCwicom,
        StatusCwicom,
        InitCfpga,
        StatusCfpga
    ) = range(1, 5)


class GpioCmds:
    (
        Set,
        Get
    ) = range(1, 3)


class PeuCmds:
    (
        Read,
        Write
    ) = range(1, 3)


class RamFsCmds:
    (
        PrintFileList,
        Open,
        DeleteOpen,
        Close,
        Delete,
        Mount,
        Format,
        Exists,
        DownloadToGround
    ) = range(1, 10)


class SdramCmds:
    (
        Read,
        Write,
        Compress
    ) = range(1, 4)


class SoCWireCmds:
    (
        PrintRouting,
        Reset,
        IoBridgeStatus,
        RegisterRead,
        RegisterWrite,
        Stream,
        DebugReadRegs
    ) = range(1, 8)


class SpiCmds:
    (
        Send
    ) = range(1, 2)


class SystemCmds:
    (
        SetControlRegister,
        TriggerWdog,
        RtemsStackUsage
    ) = range(1, 4)
