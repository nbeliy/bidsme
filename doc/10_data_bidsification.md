# Data bidsification

- [Data bidsification](#data-bidsification)
  - [<a name="wf_map"></a>Bidsmap configuration](#bidsmap-configuration)
  - [<a name="wf_plug"></a>Plugin configuration](#plugin-configuration)
  - [<a name="wf_bidsify"></a>Doing the actual bidsfication](#doing-the-actual-bidsfication)

Before you can bidsify your data set you must first prepare the bidsmap that describes how your prepared data will "map" 
onto the final data in the BIDS data set.

Then you must set up any plugin you want to use.

And finally you can bidsify your dataset.

## <a name="wf_map"></a>Bidsmap configuration

Bidsmap is the central piece of BIDSme. 

It tells you how to identify any data file, and what modality and bids labels 
to attribute.

It is a configuration file written in [YAML](http://yaml.org/) format, which is a 
compromise between human readability and machine parsing.

By default this file, once created is stored within bidsified dataset in 
`code/bidsme/bidsmap.yaml`.

The structure of a valid bidsmap is described in the section [Bidsmap file structure](../README.md#bidsmap).

The first step of creating a bidsmap is to prepare a reference dataset,
which is a subset of full dataset, containing only one or two subjects.
It is important to these subjects being complete (i.e. no missing scans)
and without errors made in protocol (no duplicated scans, scans in good order etc...).
This reference dataset will serve as a model for bidsmap.

Once the reference dataset is ready, the bidsmap is created by command `map`:
```
bidsme.py map prepared/ bidsified/
```

The `map` command accepts two additional parameters:

- `-b, --bidsmap` (default: `bidsmap.yaml`), with path to the bidsmap file.
As in `bidsify` command given file will be searched first locally, then in 
`bidsified/code/bidsme/` directory. 
- `-t, --template` (default: `bidsmap-template.yaml`), with path to template map.
This file will be searched in order in local directory, default configuration directory 
(`$HOME/$XDG_CONFIG/bidsme/` on \*NIX, `\User\AppData\bidsme\` on Windows),
and in the `bidsme` installation directory.

At first pass tool will scan reference dataset and try to guess 
correct parameters for bidsification. If it can't find correct
parameters or could not identify the run, a corresponding warning
or error will be shown on stdout (and reported in the log file).
These warnings and errors should be corrected before re-run of
`bidsmapper`. 
The final goal is to achieve a state so that `bidsmapper` will no longer produce
any warnings and errors.

> NB:If bidsifigation requires plugins, it is important to run `bidsmapper` 
with the same plugin.

Using [example 1](#ex1), the first pass of `bidsmapper` will produce around 500
warning, but they are repetitive. 

> WARNING MRI/001-localizer/0: No run found in bidsmap. Looking into template`

It means that give sample (first file - index `0`, of sequence `001-localizer`, 
of type `MRI`) wasn't identified in the bidsmap. `bidsmapper` will try to look 
in the template map to identify the sample. If sample is identified, then
`bidsmapper` will complete the bidsmap by information found in the template.
If sample is not identified in the template, a corresponding error will show
and samples attributes will be stored in `code/bidsmap/unknown.yaml`.
It is up to user to manually integrate this sample into bidsmap (and eventually
complete the template).

> `WARNING 002-cmrr_mbep2d_bold_mb2_invertpe/0: Placeholder found`

This warning tells that given sample is identified, but bids parameters
contains placeholder. To correct this warning it is enough to find
an corresponding entry in `bidsmap` and replaced placeholders by needed
values. 
The easiest way is to search for line `002-cmrr_mbep2d_bold_mb2_invertpe`:
```
- provenance: /home/beliy/Works/bidsme_example/example1/renamed/sub-001/ses-HCL/MRI/002-cmrr_mbep2d_bold_mb2_invertpe/f1513-0002-00001-000001-01.nii
        example: func/sub-001_ses-HCL_task-placeholder_acq-nBack_dir-PA_run-1_echo-1_bold
        template: true
        checked: false
        suffix: bold
        attributes:
          ProtocolName: cmrr_mbep2d_bold_mb2_invertpe
          ImageType: ORIGINAL\\PRIMARY\\M\\MB\\ND\\MOSAIC
        bids: !!omap
          - dir: PA
          - task: <<placeholder>>
....
```
and replace `task: <<placeholder>>` by `task: nBack`.

> NB: If the run is edited, it is a good practice to change `template: true`
to `template: false`. It will mark that this run is no more automatically
generated from template.

> `WARNING func/0: also checks run: func/1`
This warning indicates that first run of `func` modality and second one
checks the same scan. At first run it is normal, as samples are identified 
from template, and some overlaps are expected. If this warning remains in
subsequent passes, then the attributes of mentioned runs must be moved apart.

> `WARNING 012-t1_mpr_sag_p2_iso/0: Can't find 'ContrastBolusIngredient' attribute from '<ContrastBolusIngredient>'`
This warning means that `bidsmapper` can't extract given attribute from 
a scan. To correct the warning, cited attribute must be set manually, for ex.
in :
```
json: !!omap
          - ContrastBolusIngredient: <ContrastBolusIngredient>
```
change `<ContrastBolusIngredient>` to a used value (if contrast element is used),
or an empty string (otherwise).

> `WARNING 014-al_B1mapping/9: Naming schema not BIDS`
This warning appears when specified BIDS schema do not follow the standard. 
To correct this warning it will be enough to put bids section in bidsmap
to follow the BIDS specifications. 
Alternately, if the deviation from the standard is intentional (e.g. 
given data type is not officially supported by BIDS), the warning can be silenced 
by setting `checked` to `true`. 

Bidsmap contain several automatically filled fields that are to simplify the map 
adjustments:

  - provenance: contains the path to the first data file matched to this run. 
This field is updated at each run of `bidsmapper`, but only if `checked` is 
false 
  - example: this field shows an generated bids name for the file in `provenance`
  - template: indicates if run was generated from template map. This value is 
not updated, and should be set to `false` at first manual edit
  - checked: indicates if operator checked the run and is satisfied with the
results. In order to bidsify dataset, all runs must be checked.

Finally `bidsify` command can be run of reference dataset, to assure that there 
no conflicts in definitions and the bidsified dataset is correct.

## <a name="wf_plug"></a>Plugin configuration

Plugins in BIDSme are implemented as a functions (entry point) that are called at 
specific time during the execution of main program. All of the commands `prepare`, 
`map`, `process` and `bidsify` support the plugins.

All functions must be defined in the same python file, but it is possible include additional
files using the usual `import` instruction. The list of accepted functions is given in table below. 
Details on each of these functions can be found in [Plugins](./30_plug_in_functions.md#plug-in-functions) section

| Function | Entry point | Used for |
| ----------- | -------------- | ------------|
| `InitEP`  | At the start of program | Initialisation of plugin, setting global parameters |
| `SubjectEP` | After entering subject folder | Adjustment of subject Id |
| `SessionEP` | After entering session folder | Adjustment of session Id |
| `SequenceEP` | After loading first data file in sequence | Global sequence actions |
| `RecordingEP`| After loading a new data file in sequence | Adjustment of recording parameters |
| `FileEP`| After copying a data file to its dInitEP(source: str, destination: str,estination | Any post-copy adjustment |
| `SequenceEndEP`| After processing last file in the sequence | Any post-sequence treatments |
| `SessionEndEP`| After processing all sequences in session | Any post-session treatments |
| `SubjectEndEP`| After processing last subject | Any post-subject treatments |
| `FinaliseEP`| At the end of program | Any actions needed to finalise dataset |

Any of defined functions must accept a determined set of parameters, except `InitEP`, which
accept additional a set of optional named parameters, needed to setup any given plugin.

Each function is expected to return an integer return code:

- **0** -- successful execution, program continues normally
- **None** -- interpreted as **0**
- **[0-9]** -- an error in plugin occurred, program will stop execution
 and `PluginError` will be raised
- **<0** -- an error in plugin occurred, current entity will be skipped

The negative code will affect only some of plugins, where skipping current entity
will have a meaning, namely `SubjectEP`, `SessionEP`, `SequenceEP` and `RecordingEP`.
For other function, negative code is interpreted as **0**

> NB: Even if all scripts supports the same list of entry points, some of them 
are more adapted for data preparation and other for bidsification.
From practice, it is more convenient to perform all subject and session
determination, data retrieval and additional files treatment during
preparation, and bidisification is concentrated on just renaming and 
copying files. This way, there an opportunity of checking, correcting 
and/or completing data manually. 

## <a name="wf_bidsify"></a>Doing the actual bidsfication

Considering that the data is [prepared](./00_data_preparation.md#wf_prep) together with 
[bidsmap](#wf_map) and [plugins](#wf_plug), the bidsification is performed by `bidsify` command:
```
bidsme.py bidsify prepared bidsified
```

It will run over data-files in prepared dataset, determine the correct modalities
and BIDS entities, extract the meta-data needed for sidecar JSON files, and 
create BIDS dataset in destination folder.

Outside options cited [above](../README.md#gen_cli), `bidsify` accepts one parameter:

- `-b, --bidsmap` with path to the bidsmap file used to identify data files.
If omitted, the `bidsmap.yaml` will be used. Bidsmap will be searched first 
in local path, then in `bidsified/code/bidsme/`.

> N.B. It is advisable to first run bidsification in ["dry mode"](#gen_cli), using
switch `--dry-run`, then if there no errors detected run bidsification in normal mode.

The subjects and session Id are retrieved from folder structure, but still
can be modified in the plugins. It can be useful if one plan perform a random 
permutation on the subjects, for additional layer of anonymisation. 

> NB: The log files with messages and, separately the errors are stored in
destination directory in `source/bidsme/bidsify/log` sub-directory.
