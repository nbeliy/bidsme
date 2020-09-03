# BIDSme

- [BIDSme](#bidsme)
  - [<a name="requirements"></a> Requirements](#-requirements)
  - [<a name="interface"></a> The BIDSme interface](#-the-bidsme-interface)
  - [<a name="workflow"> </a>The BIDSme workflow](#-the-bidsme-workflow)
  - [<a name="examples"></a>Examples](#examples)
    - [<a name="ex1"></a>Dataset 1](#dataset-1)
  - [<a name="new_formats"></a>Implementing additional formats](#implementing-additional-formats)
  - [<a name="bidsmap"></a>Bidsmap file structure](#bidsmap-file-structure)


BIDSme is a user friendly
[open-source](https://gitlab.uliege.be/CyclotronResearchCentre/Public/bidstools/bidsme/bidsme)
python toolkit that converts ("bidsifies") source-level (raw) neuroimaging 
data-sets to [BIDS-conformed](https://bids-specification.readthedocs.io/en/stable).
Rather then depending on complex or ambiguous programmatic logic for the 
identification of imaging modalities, BIDSme uses a direct mapping approach to 
identify and convert the raw source data into BIDS data. The information sources 
that can be used to map the source data to BIDS are retrieved dynamically from 
source data header files (DICOM, BrainVision, nifti etc...) and file source data-set 
file structure (file- and/or directory names, e.g. number of files).

The retrieved information can be modified/adjusted by a set of plugins, 
described [here](#plugins). Plugins can also be used to complete the bidsified 
dataset, for example by parsing log files. 

> NB: BIDSme support variety of formats listed in [supported formats](#formats). 
Additional formats can be implemented following instructions [here](#new_formats).

The mapping information is stored as key-value pairs in the human readable and 
widely supported [YAML](http://yaml.org/) files, generated from a template yaml-file.

## <a name="requirements"></a> Requirements
- python >= 3.6
- pandas
- ruamel.yaml>=0.15.35
- coloredlogs
- pydicom>=1.4.2
- nibabel>=3.1.0

## <a name="interface"></a> The BIDSme interface

All interactions with BIDSme occurs from command-line interface, by a master script `bidsme.py`.

This script accepts a small set of parameters and one of the command 

- `prepare` to [prepare dataset](./doc/00_data_preparation.md#wf_prep)
- `process` to [process dataset](./doc/00_data_preparation.md#wf_process)
- `bidsify` to [bidsify dataset](./doc/10_data_bidsification.md#wf_bids)
- `map` to [create bidsmap](./doc/10_data_bidsification.md#wf_map)

Outside the standard `-h`, `-v` options that shows help and version, `bidsme` accepts 
`-c, --configuration` options which takes a path to configuration file. 
This file is searched in (in order) current directory, user-standard directory and 
bids code directory (when available).

The `--conf-save` switch saves the current configuration (affected by command-line
options) in the given location. It is useful to run this option once to update configuration.

> N.B. both `-c` and `--conf-save` must be given **before** the command.

The individual commands accepts common and individual arguments. 
In what follows only common arguments are described, and individual ones are 
described in corresponding sections.

- <a name="gen_cli"></a>Logging options, corresponds to *logging* section of configuration file:
    *  `-q`, `--quiet` suppress the standard output, useful for running in the script
    * `--level` sets the message verbosity of the log output, from very verbose *DEBUG*
    to showing only critical message *CRITICAL*
    * `--formatter` sets the log line format message 
- Plug-in options, corresponds to *plugins* section of configuration file. Affects only
relevant command: 
    * `--plugin` sets the path to plugin file
    * `-o Name=Value` sets the options passed to plugin
- Subject and session selection, corresponds to *selection* section of configuration file
    * `--participants` space separated list of participants to process. Listed participants
    are considered after the bidsification, with `sub-` prefix
    * `--skip-in-tsv` switch that skips participants that already present in destination
    * `--skip-existing` switch that skips participants with corresponding folders existing
    in destination
    * `--skip-existing-sessions` same as above but for sessions
- General options, non existing in configuration file:
    * `--dry-run`, run in the simulation mode, without writing anything outside the
    logs

The full list of commands parameters can be seen using `-h` option:
`bidsme.py [command] -h`.
If a configuration file is set, then the shown default values corresponds to configuration file
parameters.

## <a name="workflow"> </a>The BIDSme workflow

The BIDSme workflow is composed in 3 steps (1 being optional):

  1. [Data preparation](./doc/00_data_preparation.md#wf_prep) is where the source dataset is reorganized into standard "bids-like" structure (the files are only moved into different folders)
  2. [Data processing](./doc/00_data_preparation.md#-data-processing) is an optional step between data preparation and bidsification
  3. [Data bidsification](./doc/10_data_bidsification.md#data-bidsification) is where the prepared data is actually bidsified.

This organisation allow to user intervene before the bidsification in case of 
presence of errors, or to complete the data manually if it could not be completed numerically.


## <a name="examples"></a>Examples

### <a name="ex1"></a>Dataset 1

## <a name="new_formats"></a>Implementing additional formats

## <a name="bidsmap"></a>Bidsmap file structure
