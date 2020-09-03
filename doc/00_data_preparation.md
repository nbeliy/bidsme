# Data preparation 

- [Data preparation](#data-preparation)
	- [<a name="wf_process"></a> Data processing](#-data-processing)

In order to be bidsified, dataset should be put into the form of a prepared dataset:

```
sub-<subId>/ses-<sesId>/<DataType>/<seriesNo>-<seriesId>/<datafiles>
```

- `subId` and `sesId` are the subject and session label, as defined by BIDS standard. 
- `DataType` is an unique label identifying the modality of data, e.g. `EEG` or `MRI`.
- `seriesNo` and `seriesId` are the unique identification of given recording series 
which can be defined as a set of recording sharing the same recording parameters 
(e.g. set of 2D slices for same fMRI scan).

A generic data-set can be organized into a prepared dataset using the `prepare` command.

`prepare` does not modify/convert/rename data files, only copies them.

`prepare` iteratively scans the original dataset and determine the subjects and sessions Id from 
the folder names. Subject Id is taken from the name of top-most folder, and session from its sub-folder
(modulo the `prefix` parameters - see below for more information). 

The Id are taken as it, with removal of all non alphanumerical characters. For example, 
if subject folder is called `s0123-control`, the subject Id will be `sub-s0123control`.
If the folders name contain a prefix, that you don't want to be part of Id, 
you can then use the option `--sub-prefix s` and the subject folder `s0123-control` will 
result in subject Id `sub-0123control`.

If in the original dataset data is not organized in `subject/session` folders,
one should use options `--no-subject` and `--no-session`.
The session Id will be set to an empty string, and subject Id will be retrieved
from data files.

In addition of parameters cited [before](../README.md#gen_cli), some additional parameters are defined:

- `--part-template` with path to the sidecar json file (template) for the future `participant.tsv` file. 
	It is expected to follow the [BIDS-defined structure](https://bids-specification.readthedocs.io/en/stable/02-common-principles.html#tabular-files). 
	It should include **all** needed column descriptions, including the mandatory `participant_id`
- `--sub-prefix` sets the subject prefix in the original dataset and can include path. 
	For example if in the original dataset, subject folders are stored in `participants` folder 
	(`participants/001`, `participants/002` etc.. ), then setting `--sub-prefix` to `participants/` 
	(note the slash) will make `prepare` search for subjects in the correct folder. 
	The paths can contain wildcard character `*` in case if different participants 
	are stored in different folders (e.g. `patients/001` and `control/002`). Both can be 
	reached by  `--sub-prefix '*/'`. 
	If used, wildcard characters must be protected by single quote in order to avoid shell expansion. 
	The non-path part of prefix is removed from subject id. 
	For this reason wildcard is forbidden outside the path.
- `--ses-prefix` sets the session prefix in the same manner as `--sub-prefix` above
- `--no-subject` and `--no-session` are mandatory to indicate if the original dataset subjects and respectively
	sessions are not stored in dedicated folders. 
- `--recfolder folder=type` options indicates in what folders the actual data is stored, 
	and what is the type of data.
	For example `nii=MRI` tells that the `nii` subfolders contains MRI data. 
	The wildcard is allowed in the folder name.


> N.B. Even with subject and session folders present, there is a possibility to determine them directly from
data files. In order to do this in the corresponding [plugin](./30_plug_in_functions.md#wf_plugin) the `session.subject` must be set 
to `None`, making it undefined. But undefined subjects and sessions make subject selection unavailable.

If one need to rename subjects and/or sessions, it can be done with plug-in functions
`SubjectEP` and `SessionEP` or by renaming directly folders in the prepared dataset.


<!-- REPEATS of the intro -->

Once the data-files are identified, they are placed into prepared dataset, which follows 
loosely the basic BIDS structure:
```
sub-<subId>/ses-<sesId>/<DataType>/<Sequence>/data
```

The `sub-<subId>` and `ses-<sesId>` will be the bidsified version of subjects and sessions Id.
Note that if original dataset don't have sessions, the folder `sub-` will be present, with and empty 
`<sesId>`.

`<DataType>` folder will correspond to one of `bidsme` defined data types and will contain 
all data files identified as being of this type.

`<Sequence>` folders will group all data files corresponding to the same recording (for ex. 
different scanned volumes for the same MRI acquisition), it will be named as `<seqNo>-<secId>`
which will uniquely identify the sequence.

<!-- REPEATS of the intro -->


If an actual modification of data is needed (e.g. anonymisation, or conversion),
either in plugin functions `FileEP`, `SequenceEndEP` or manually in prepared
dataset. 
As long data files remains in the correct folders and data format is supported 
by BIDSme, bidsification should perform normally.

This structure has been chosen to be as rigid possible, in order to make it easier 
to treat numerically, but still human-readable.
It naturally supports multimodal dataset.

A working example of source dataset and `prepare` configuration can be found 
[there](https://gitlab.uliege.be/CyclotronResearchCentre/Public/bidstools/bidsme/bidsme_example).

> NB: The logs for standard output and separately errors and warnings are stored
in destination folder in `code/bidsme/prepare/log` directory.

## <a name="wf_process"></a> Data processing

The processing is completely optional step between data preparation and
bidsification. It is intended to allow a data modification based on data identification
of `bidsme`. It can be used to check, pre-process data, convert it, merge etc.

It is not intended to run without plugins. It does nothing without, except checking
if all data is identifiable. It can be easily be replaced by a custom script. 