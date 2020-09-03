# Plug-in functions

- [Plug-in functions](#plug-in-functions)
	- [<a name="plug_init"></a> `InitEP(source: str, destination: str, dry: bool, **kwargs) -> int:`](#-initepsource-str-destination-str-dry-bool-kwargs---int)
	- [<a name="plug_sub"></a> `SubjectEP(scan: BidsSession) -> int`](#-subjectepscan-bidssession---int)
	- [<a name="plug_ses"></a> `SessionEP(scan: BidsSession) -> int`](#-sessionepscan-bidssession---int)
	- [<a name="plug_seq"></a> `SequenceEP(recording: object) -> int`](#-sequenceeprecording-object---int)
	- [<a name="plug_rec"></a> `RecordingEP(recording: object) -> int`](#-recordingeprecording-object---int)
	- [<a name="plug_recEnd"></a> `FileEP(path: str, recording: object) -> int`](#-fileeppath-str-recording-object---int)
	- [<a name="plug_seqEnd"></a> `SequenceEndEP(path: str, recording: object) -> int`](#-sequenceendeppath-str-recording-object---int)
	- [<a name="plug_sesEnd"></a> `SessionEndEP(scan: BidsSession) -> int`](#-sessionendepscan-bidssession---int)
	- [<a name="plug_subEnd"></a> `SubjectEndEP(scan: BidsSession) -> int`](#-subjectendepscan-bidssession---int)
	- [<a name="plug_End"></a> `FinaliseEP() -> int`](#-finaliseep---int)

## <a name="plug_init"></a> `InitEP(source: str, destination: str, dry: bool, **kwargs) -> int:`

The `InitEP` function is called immediately after start of main program. 
As name indicates, it initialise the plugin, store the global variables and parameters.

It accepts 3 mandatory parameters:
 - **source: str**: a path to the source directory, from where data files are processed.
 - **destination: str**: a path to destination directory, where processed data will be stored
 - **dry: bool**: a switch to indicate if it is a dry-run (i.e. a test run where nothing is written to disk)

> **Warning**: `dry` parameter must be always stored as global parameter, 
and **any** file and folder modification parts in the plugins **must** be protected 
by check if `dry` is `False`:
```python
if not dry:
	do stuff
	....
```
 
 The custom additional parameters can be received via `**kwargs`. These parameters are communicated 
 to the program via `-o` option:
 ```
 -o par1=val1 -o par2=val2
 ```
 
 These parameters will be parsed into dictionary and feeded to `InitEP`:
 ```
 {
 	"par1": "val1",
 	"par2": "val2"
 }
 ```, 
 or from within a `bidsmap.yaml` file, in the  `Option/PlugIns/options` section, directly as a dictionary. 

The `source`, `destination` and `dry` values must be stored as global parameters, so they can
be used in other plugins:

```python
global source_path
source_path = source
```

Outside the definition and storage of global parameters, `InitEP` can be used for loading
and parsing external files. For example, in [Example1](#ex1), the `Appariement.xlsx`
excel file, containing the list of subjects is parced. 
The parsed excel file is used later to identify sessions and fill the `participant.tsv` file.

If `--part-template` option is not used in `coinsort`, then the template
 json file for `participants.tsv` can be done there, using 
 `BidsSession.loadSubjectFields(cls, filename: str=None)` class
 function. 
 
> In order to maintain consistency between subjects, template json
file can be loaded only once. Subsequent loading will raise an exception.

## <a name="plug_sub"></a> `SubjectEP(scan: BidsSession) -> int`

The `SubjectEP` function is called after entering the subject's folder. 
The main action of this function is redefinition of subject Id and filling
meta-data associated with given subject.
The passed parameter `scan` ia s `BidsSession` mutable object,
with proprieties:
- **subject**: containing current subject Id
- **session**: containing current session Id
- **in_path**: containing current path
- **sub_values**: containing a dictionary of current subject
data destined for `participants.tsv`

In order to change subject, it will suffice to change the `subject`
property of BidsSession:
```python
scan.subject = scan.subject + "patient"
```

It is not necessary to add `ses-` to the subject name, it will be added
automatically, together with removal of all non alphanumerical characters.
So subject Id is guaranteed to be bids-compatible.

`sub_values` is a dictionary with `participants.tsv` columns as keys and `None` as values.
Filling values will populate the corresponding line in `participants.tsv`.

> The columns are normally defined by template JSON file during 
preparation step, but they can be loaded from within plugin
during `InitEP` execution.

## <a name="plug_ses"></a> `SessionEP(scan: BidsSession) -> int`

`SessionEP` is executed immediately after entering session folder, and 
mean to modify current session Id.
It accepts the same `BidsSession` object as `SubjectId`, with not yet bidsified
names.

> Immediately after execution of `SessionEP`, the `subject` and `session` 
properties of `scan` are bidsified and locked. No changes will be accepted,
any attempt will raise an exception. Howether it can be unlocked at your 
risk and peril by calling `scan.unlock_subject()` and 
`scan.unlock_session()`. It can broke the preparation/bidsification!

## <a name="plug_seq"></a> `SequenceEP(recording: object) -> int`

`SequenceEP` is executed at the start of each sequence.
It can be used to perform global sequence check and actions checking validity.

Passed parameter is an actual recording with loaded first file (in alphabetical 
order).
The current subject and session can be accessed via `recording.subId()`
and `recording.sesId()`, but other BIDS attributes are not yet defined.

In the [Example1](#ex1), during bidsification step, this plugin is used
to determine the destination of fieldmaps:
```python
if recid == "gre_field_mapping":
	if recording.sesId() in ("ses-HCL", "ses-LCL"):
		Intended = "HCL/LCL"
	elif recording.sesId() == "ses-STROOP":
		Intended = "STROOP"
```
The global intended variable used later in plugin to correctly fill
`IntendedFor` json file.

## <a name="plug_rec"></a> `RecordingEP(recording: object) -> int`

`RecordingEP` is executed immidiatly after loading a new file in each of 
recordings. It is used for locally adapting the attributes of recording.

For example, in [Example 1](#ex_1), sorting plugin executes:
```python
if Intended != "":
	recording.setAttribute("SeriesDescription", Intended)
```
, replacing the `SeriesDescription` by global variable `Intended`, defines
during `SequenceEP`.

> The changed attribute can be restored to it original value by executing
`recording.unsetAttribute("SeriesDescription")`

## <a name="plug_recEnd"></a> `FileEP(path: str, recording: object) -> int`

`FileEP` is called after the copy of recording file to its destination
(either during preparation or bidsification).

Outside the `recording` object, it accepts the `path` parameter containing
the path to copied file.

The utility of this plugin is data file manipulation, for example 
the convertion into another format, or anonymisation. 
Working only on the copy of original file do not compromise the source dataset.

## <a name="plug_seqEnd"></a> `SequenceEndEP(path: str, recording: object) -> int`

The `SequenceEndEP` is called after the treatment of all files in the sequence, 
and can be used to perform various checks and/or sequence files manipulation,
for example compressing files or packing 3D MRI images into 4D one.

Sa in `FileEP` function, `path` parameter contains the path to the directory
where last file of given sequence is copied. The `recording` object also
have last file in sequence loaded.

## <a name="plug_sesEnd"></a> `SessionEndEP(scan: BidsSession) -> int`

`SessionEndEP` is executed after treating the last sequence of recording.
As there no loaded recordings, it takes `BidsSession` as parameter. 
The mean goal of this function is check of compliteness of session,
and retrieving metadata of session, for example parcing various 
behevirial data.

## <a name="plug_subEnd"></a> `SubjectEndEP(scan: BidsSession) -> int`

`SubjectEndEP` is executed after treating the last session of a given
subject. 
It can be used for checking if all sessions are present, and for 
retrieval of phenotype data for given subject.

## <a name="plug_End"></a> `FinaliseEP() -> int`

`FinaliseEP` is called in the end of programm and can be used
for consolidation and final checks of destination dataset.