class SpwCmdGrp():
    (
        _unused,
        System,
        SoCWire,
        Rfpga1,
        Jtag,
        Gpio,
        Spi,
        RamFs,
        NorFs,
        NandFs,
        Acquisition,
        Preproc,
        Nand
    ) = range(13)


class AcquisitionCmds():
    _unused, \
    ChlinkRecord, \
    ChlinkReadout, \
    ChlinkRecord16, \
    ChlinkReadout16 = range(5)


class PreprocCmds():
    _unused, \
    Store, \
    StoreFromNand, \
    Load, \
    LoadToNand, \
    Add, \
    Sub, \
    Mult, \
    Fft, \
    Ifft, \
    Cmult, \
    Div = range(12)


class GpioCmds():
    _unused, \
    Set, \
    Get = range(3)


class JtagCmds():
    _unused, \
    Config, \
    ReadId, \
    Status, \
    ReadFAR, \
    StopScrubbing, \
    FaultInject, \
    ConfigNoScrub, \
    SetMaskfile, \
    SetFreq = range(10)


class NandCmds():
    _unused, \
    ReadId, \
    ReadUId, \
    BadBlocks, \
    EraseBlocks, \
    ReadBlocks, \
    ReadBlocksSoCWire, \
    ReadBlocksSoCWireToRfpga, \
    WriteBlocksSoCWire, \
    WriteBlocksSoCWire16, \
    FileSystemTest, \
    StoreFile, \
    ControllerReset, \
    ShortTest, \
    ReadErrorStat, \
    EnableInterrupts, \
    DisableInterrupts, \
    Power = range(18)


class NandFsCmds():
    _unused, \
    PrintFAT, \
    Mount, \
    Unmount, \
    Report, \
    Format, \
    EnableInterrupts, \
    DisableInterrupts, \
    Erase, \
    Clean, \
    Exists, \
    GetFilesize, \
    GetBadBlocks, \
    SetBadBlocks, \
    WriteFromMMviaCPU, \
    WriteFromMMviaSoCWire, \
    ReadToMMviaCPU, \
    ReadToMMviaSoCWire, \
    PrintFiles = range(19)


class NorFsCmds():
    _unused, \
    MoveMmToNor, \
    MoveNorToMm, \
    Delete, \
    PrintFileInfo, \
    PrintFAT, \
    Format = range(7)


class RamFsCmds():
    _unused, \
    PrintFileList, \
    Open, \
    DeleteOpen, \
    Close, \
    Delete, \
    Mount, \
    Format, \
    Exists, \
    DownloadToGround = range(10)


class Rfpga1Cmds():
    _unused, \
    Test = range(2)


class SoCWireCmds():
    _unused, \
    PrintRouting, \
    Reset, \
    IoBridgeStatus, \
    RegisterRead, \
    RegisterWrite, \
    SetupPathTable = range(7)


class SpiCmds():
    _unused, \
    Send = range(2)


class SystemCmds():
    _unused, \
    SetControlRegister, \
    RtemsStackUsage = range(3)
