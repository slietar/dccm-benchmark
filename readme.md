# DCCM benchmark


## Usage


### Part 1

The first part of the code is executed using R. Each argument should point to a directory containing a `file_list.txt` file and an optional `ligand.pdb`. The last argument should corresponding to the inactive PDB. The output will be produced on the standard output.

For this example:

```sh
$ Rscript main.r a-active_dpa b-active_brc c-inactive > output.dat
```

The corresponding file hierarchy would be the following:

```
.
├── a-active_dpa
│   ├── file_list.txt
│   └── ligand.pdb
├── b-active_brc
│   ├── file_list.txt
│   └── ligand.pdb
└── c-inactive
    └── file_list.txt
```

Where each `file_list.txt` file contains the path (relative to the file) of a PDB file for a mutant. It is necessary for mutants to be in the same order between source directories.

```
d2_dpa_A211I.pdb
d2_dpa_A211V.pdb
d2_dpa_F217M.pdb
d2_dpa_I125N.pdb
```


### Part 2

The second part is executed using Python 3.

```sh
$ pip3 install -r requirements.txt
$ python3 main.py output.dat --config config.json --mutants a-active_dpa/file_list.txt --ligands 2 > output.xlsx
```

The following options are necessary:

- `--config` – Path of a JSON file specifying hub numbers and scores for each test, ligand and state.
  ```json
  {
    "Gp biased": [
      // Ligand 1 (DPA)
      {
        "active": {
          "hubs": [261,264,256,205,188,38,112,115,105,119,209,251,268,100,200,182,120,193,114,253],
          "scores": [366, 335, 250, 186, 179, 166, 156, 133, 118, 101, 93, 85, 85, 81, 79, 72, 67, 67, 64, 62]
        },
        "inactive": {
          "hubs": [249,252,244,193,183,33,107,110,100,114,197,239,256,95,188,177,115,109,241],
          "scores": [366, 335, 250, 186, 179, 166, 156, 133, 118, 101, 93, 85, 85, 81, 79, 72, 67, 64, 62]
        }
      },

      // Ligand 2 (BRC)
      {
        "active": {
          "hubs": [188,264,203,105,205,209,189,182,118,259,208,213,100,38,198,261,220,111,186,254],
          "scores": [253, 223, 184, 162, 156, 137, 130, 127, 105, 103, 93, 88, 84, 83, 82, 82, 81, 76, 76, 70]
        },
        "inactive": {
          "hubs": [183,252,191,100,193,197,184,177,113,247,196,201,95,33,186,249,208,106,181,242],
          "scores": [253, 223, 184, 162, 156, 137, 130, 127, 105, 103, 93, 88, 84, 83, 82, 82, 81, 76, 76, 70]
        }
      }
    ],

    "Other": [
      {
        "active": {
          "hubs": [14, 16, 49,53,93,94,95,96,97,130,177],
          "scores": null <-- Scores are optional
        },
        "inactive": null <-- Inactive hub numbers will be computed later
      },
      {
        "active": {
          "hubs": [17,21,24,123,125,129,167,169,173,179,211,212,213,214],
          "scores": null
        },
        "inactive": null
      }
    ]
  }
  ```
- `--mutants` – Number of mutants or path of a file with the name of each mutant on a different line. Any prefix or suffix common to all names will be removed, therefore using `file_list.txt` from part 1 is the easiest way to provide mutant names.
- `--ligands` – Number of ligands tested, without the inactive one, therefore equal to the number of directories from part 1 minus one.

Again, the output is produced on the standard output but now consists in an .xlsx file.

If part 1 and part 2 are executed at the same time, the following command can be used instead:

```
$ Rscript main.r a-active_dpa b-active_brc c-inactive | python3 main.py --config config.json --mutants a-active_dpa/file_list.txt --ligands 2 > output.xlsx
```

