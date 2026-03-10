# Shubra Project — Complete Documentation

> **Siemens TIA Portal HMI Project** — Industrial Automation Human-Machine Interface

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technical Specifications](#technical-specifications)
3. [Project Structure](#project-structure)
4. [File Inventory](#file-inventory)
5. [Configuration & Metadata](#configuration--metadata)
6. [Domain Model & Business Logic](#domain-model--business-logic)
7. [HMI Architecture](#hmi-architecture)
8. [Deployment & Runtime](#deployment--runtime)
9. [Data Flow & Integration](#data-flow--integration)
10. [Key Technologies](#key-technologies)
11. [Notes & Limitations](#notes--limitations)

---

## Project Overview

**Shubra** is a Siemens Totally Integrated Automation (TIA) Portal project focused on **HMI (Human-Machine Interface)** for industrial automation. It targets a PC-based operator panel running **WinCC RT Advanced** and is designed for monitoring and controlling industrial processes.

| Attribute | Value |
|-----------|-------|
| **Project Name** | Shubra |
| **Platform** | Siemens TIA Portal |
| **Version** | 16.0.0.0 |
| **Creation Date** | June 8, 2023 (UTC 03:35:28) |
| **Project Type** | HMI / WinCC RT Advanced |
| **Target** | SIMATIC PC station |

---

## Technical Specifications

### Version Information

| Component | Version |
|-----------|---------|
| TIA Portal | 16.0.0.0 |
| Project Compatibility | 16.0.0.0 |
| Runtime Release (RTCV) | 16.0.0.0 |
| Image Release | 16.0.0.0 |
| Product Release (PRCV) | 16.0.0.0 |
| Device Version | 16.0.0.0 |

### Target Device

| Property | Value |
|----------|-------|
| **Device Type** | PC-OP (PC Operator Panel) |
| **Runtime** | COLORADO |
| **Display Orientation** | 0 (Landscape) |
| **Runtime Name** | Shubra.PC-System_1[SIMATIC PC station - WinCC RT Advanced] |
| **License** | WinCC RT Advanced (512 tags) |
| **License Code** | WCRT021600 |

---

## Project Structure

```
islam/
└── shubra/
    ├── Shubra.ap16                          # Main project definition file
    │
    ├── AdditionalFiles/
    │   └── PLCM/
    │       └── plcmArchive.pma15_0          # PLC migration archive
    │
    ├── Vci/
    │   └── Vci.db                           # Version control / component database
    │
    ├── XRef/
    │   └── XRef.db                          # Cross-reference database
    │
    ├── System/
    │   ├── PEData.idx                        # Project data index
    │   ├── PEData.plf                        # Project data (binary)
    │   └── PEData/Meta/
    │       ├── ChangeListProvider/
    │       │   └── Siemens.Automation.DomainModel.xml
    │       └── ChangeListConsumer/
    │           ├── HmiBase.xml
    │           ├── Iecpl.xml
    │           ├── Siemens.Simatic.Lang.xml
    │           ├── Siemens.Simatic.Lang.Online.xml
    │           └── Siemens.Simatic.Lang.IPI.Target.xml
    │
    └── IM/                                   # Intermediate / Build artifacts
        ├── SearchIndex/                      # Lucene-style search index
        │   ├── _amp.frq, _amp.fnm, _amp.fdx, _amp.fdt
        │   ├── _amp.tii, _amp.tis, _amp.tvx, _amp.tvd, _amp.tvf
        │   ├── _amp.prx, _amw.cfs, _amv.cfs
        │   ├── segments.gen, segments_4ks
        │   └── _amp_1.del, _amv_1.del
        │
        ├── SPL/
        │   └── options                       # Compiler/build options
        │
        └── HMI/
            ├── DeviceFolders.dat
            ├── BrokerInfo.dat
            └── C/0/                          # HMI configuration 0
                ├── RtData.idx                # Runtime data index
                ├── RtData.plf                # Runtime data (binary)
                ├── ~RtData.1, ~RtData.2     # Runtime data temp files
                ├── intermediate.dti         # Intermediate format (binary)
                ├── SdalRTPluginInfo.dat      # Runtime plugin metadata
                ├── SdalRTPlugin.IntermediateFormat.{...}.gd
                ├── SdalRTPlugin.IntermediateFormat.{...}.gdbak
                └── Generates/                # Build output
                    ├── DownloadTask.xml     # Deployment configuration
                    ├── pdata.tfz            # Compressed project data
                    ├── pdata.fwc            # Full download package
                    ├── pdata.pwl1, pdata.pwl2
                    ├── ProjectSettings.hsf
                    ├── ProjectCharacteristics.rdf
                    └── pdata - Shortcut.lnk
```

---

## File Inventory

### Human-Readable / XML Files

| File | Purpose |
|------|---------|
| `Shubra.ap16` | Project root definition, name, version, icon |
| `DownloadTask.xml` | Runtime download/deployment configuration |
| `Siemens.Automation.DomainModel.xml` | Domain model change tracking (PLC tags) |
| `HmiBase.xml` | HMI base consumer metadata |
| `Iecpl.xml` | IEC-PL language consumer |
| `Siemens.Simatic.Lang.*.xml` | Language/compilation consumers |

### Binary / Proprietary Files

| File Type | Purpose |
|-----------|---------|
| `.plf`, `.idx` | Project/runtime data storage |
| `.tfz` | Compressed project package for download |
| `.fwc` | Full WinCC download package |
| `.hsf` | Project settings |
| `.rdf` | Project characteristics |
| `.db` | SQLite/DB for Vci, XRef |
| `.dti` | Intermediate format for HMI compiler |
| `.gd`, `.gdbak` | SdalRT plugin intermediate format |
| `_amp.*` | Search index (Lucene-style) |

---

## Configuration & Metadata

### Project Definition (`Shubra.ap16`)

- **Type**: `Project`
- **Name**: `Shubra`
- **BrowsableType**: `Siemens.Automation.DomainModel.ProjectData`
- **Namespace**: `http://www.siemens.com/2007/07/Automation/CommonServices/DataInfoValueData`
- **Icon**: Embedded base64 icon data

### Download Task (`DownloadTask.xml`)

Defines what is deployed to the runtime:

- **FullDownload** entries: `pdata.fwc`, `pdata.pwx`, `pdata.tfz`, `ProjectSettings.hsf`
- **License**: WinCC RT Advanced (512 tags)
- **Admin data**: `pdata.pwx` (type ADMINDATA)

---

## Domain Model & Business Logic

### PLC–HMI Integration

The project uses **ReferenceTagData** to link HMI screens to PLC tags. The domain model tracks:

| Object | Purpose |
|--------|---------|
| `ReferenceTagData` | References PLC tags from HMI |
| `ControllerRootTagBaseData` | Root of PLC tag structure |
| `EAMTZTagData` | Tag data with logical address |

### Tracked Attributes

- **CompileTime** — When structure was compiled
- **IsValid** — Structure validity
- **DataTypeName** — PLC data type
- **LogicalAddress** — Memory address in PLC
- **Name** — Tag name

### HMI Consumed Objects (from HmiBase.xml)

| Object | Role |
|--------|------|
| `SystemTextRangeListData` | System text lists |
| `UserTextRangeListData` | User-defined text lists |
| `GlobalProxyTextListData` | Alarm text lists |
| `StringTextListData` | String text lists |
| `SimpleControllerAlarmData` | Controller alarms |
| `HmiIlBase` | HMI intermediate language base |
| `ParameterSetTypeData` | Parameter control |
| `HmiBaseBL` | HMI base business logic |
| `HmiBinaryResourceData` | Images, etc. |
| `HmiTextData` | Localized texts |
| `ComponentTextlistData` | System diagnostics |
| `ErrorTextlistMetaProxyData` | Error text lists |
| `ErrorTextlistProxyData` | Error text proxy |

### Business Logic Summary

1. **Alarm handling** — Controller alarms, text lists, proxies
2. **Parameter control** — Parameter sets for PLC/HMI
3. **System diagnostics** — Component and error text lists
4. **Globalization** — Text and binary resources
5. **Tag binding** — PLC tags via logical addresses

---

## HMI Architecture

### Compiler Pipeline

1. **Source** → TIA Portal HMI editor
2. **Intermediate** → `intermediate.dti`, `SdalRTPlugin.IntermediateFormat.*.gd`
3. **Target** → `Siemens.Simatic.Hmi.Es2rt` (Es2rt = Editor to Runtime)
4. **Output** → `pdata.tfz`, `pdata.fwc`, etc.

### Runtime Target

- **Target compiler**: `Siemens.Simatic.Hmi.Es2rt` v2.0.0.0
- **Package**: `HmiBase` v2.0.0.0
- **Plugin**: `SdalRTPlugin.IntermediateFormat` (CeRt7 target)

### Core Attributes (ICoreAttributes)

- **Author**
- **Comment**
- **Name**

---

## Deployment & Runtime

### Deployment Steps (Conceptual)

1. Compile HMI in TIA Portal
2. Generate `pdata.fwc`, `pdata.tfz`, `ProjectSettings.hsf`
3. Use DownloadTask to deploy to PC station
4. Run WinCC RT Advanced with license WCRT021600

### Runtime Requirements

- SIMATIC PC station
- WinCC RT Advanced (512 tags)
- TIA Portal Runtime 16.0
- COLORADO runtime

---

## Data Flow & Integration

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   PLC / S7      │────▶│  ReferenceTag    │────▶│  HMI Screens        │
│   (Controller)  │     │  LogicalAddress  │     │  WinCC RT Advanced   │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
        │                          │                          │
        │                          │                          │
        ▼                          ▼                          ▼
  ControllerRootTag         EAMTZTagData              AlarmServices
  CompileTime, IsValid      DataTypeName              TextLists
                            Name                      ParameterControl
```

---

## Key Technologies

| Technology | Use |
|------------|-----|
| **TIA Portal** | Project authoring |
| **WinCC RT Advanced** | HMI runtime |
| **Siemens.Automation.ObjectFrame** | Object model |
| **ChangeList (ClMeta)** | Change tracking |
| **Lucene-style index** | Search in project |
| **SdalRT** | HMI compile/runtime plugin |

---

## Notes & Limitations

1. **Partial project** — This appears to be an export or subset. Full PLC logic, network config, and complete HMI screens are not present in this folder.
2. **Proprietary formats** — Most files are Siemens binary formats; editing outside TIA Portal is not supported.
3. **No source code** — HMI screens, scripts, and PLC logic are stored in binary form in `PEData.plf`, `RtData.plf`, etc.
4. **Project name** — “Shubra” may refer to Shubra (Cairo) or be a custom project name.
5. **PLC archive** — `plcmArchive.pma15_0` suggests PLC migration from TIA v15.

---

## Quick Reference

| Need | Location |
|------|----------|
| Project identity | `Shubra.ap16` |
| Deployment config | `IM/HMI/C/0/Generates/DownloadTask.xml` |
| Domain model | `System/PEData/Meta/ChangeListProvider/Siemens.Automation.DomainModel.xml` |
| HMI metadata | `System/PEData/Meta/ChangeListConsumer/HmiBase.xml` |
| Runtime package | `IM/HMI/C/0/Generates/pdata.fwc`, `pdata.tfz` |

---

*Document generated from project analysis. Last updated: March 7, 2025.*