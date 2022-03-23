from pathlib import Path
import argparse
import json
import math
import numpy as np
import os
import pandas as pd
import pyreadr
import sys
import tempfile


parser = argparse.ArgumentParser()
parser.add_argument("filepath", type=str, nargs="?")
parser.add_argument("--config", type=str, required=True)
parser.add_argument("--mutants", required=True)
parser.add_argument("--ligands", type=int, required=True)
parser.add_argument("--out", type=argparse.FileType("wb"), default=sys.stdout.buffer)

args = parser.parse_args()


if args.filepath:
  data = pyreadr.read_r(args.filepath)
else:
  input_file = tempfile.NamedTemporaryFile()
  input_file.write(sys.stdin.buffer.read())
  data = pyreadr.read_r(input_file.name)
  input_file.close()

data = np.array(data[None].iloc[:, 0])
config = json.load(Path(args.config).open())


def remove_affixes(items):
  prefix = os.path.commonprefix(items)
  suffix = os.path.commonprefix([item[::-1] for item in items])

  return [item[len(prefix):-len(suffix)] for item in items]

try:
  mutants = range(int(args.mutants))
except:
  mutants = remove_affixes(Path(args.mutants).open().read().strip().split("\n"))

dccm_size = 540


# -- Axes ----------------------------------
#  (0) dpa, brc, inactive (aka variant)
#  (1) mutants, wildtype
#  (2) without ligand, with ligand
#  (3) dccm
#  (4) dccm
data = data.reshape(args.ligands + 1, len(mutants), 2, dccm_size, dccm_size)


def transform_active(source):
  return {
    'hubs': [hub - (5 if hub < 190 else 12) for hub in source['hubs']],
    'scores': None
  }


# -- Axes ----------------------------------
# (0) test
# (1) inactive, active
# (2) non-weighted, weighted
# (3) variant
# (4) mutants, wildtype
# (5) without ligand, with ligand
dccm = np.zeros((len(config), 2, 2, data.shape[0] - 1, data.shape[1], data.shape[2]))

for test_index, test in enumerate(config.values()):
  for variant_index, variant in enumerate(test):
    for active_index, source in enumerate([variant['inactive'] or transform_active(variant['active']), variant['active']]):
      default_scores = [math.e] * len(source['hubs'])

      for score_index, scores in enumerate([default_scores, source['scores'] or default_scores]):
        for x, xscore in zip(source['hubs'], scores):
          for y, yscore in zip(source['hubs'], scores):
            if y > x:
              dccm[test_index, active_index, score_index, variant_index, :, :] += (data[variant_index, :, :, x - 1, y - 1] if active_index == 1 else data[-1, :, :, x - 1, y - 1]) * math.log(xscore) * math.log(yscore)

diff = dccm - np.repeat(dccm[:, :, :, :, -1, :][:, :, :, :, np.newaxis, :], dccm.shape[4], axis=4)
result = diff[:, 1, :, :, :, :] - diff[:, 0, :, :, :, :]

# np.set_printoptions(suppress=True)
# print(result[0, 0, 1, :, 1])


# np.save(open("d.npy", "wb"), result)
# result = np.load(open("d.npy", "rb")If not None, apply the key function to the index val

items = [
  [f"({i + 1}) {t}" for i, t in enumerate(config.keys())],
  ["no", "yes"],
  range(result.shape[2]),
  mutants,
  ["(1) without ligand", "(2) with ligand"]
]

# print([range(s) for s in result.shape])

names = ["Test", "Weighted", "Ligand", "Mutant", "With ligand"]
index = pd.MultiIndex.from_product([range(s) for s in result.shape], names=names)
index = pd.MultiIndex.from_product(items, names=names)
df = pd.DataFrame([result.flatten()], columns=index, index=None)

df = df.stack(level=3).reorder_levels([2, 0, 3, 1], axis=1).sort_index(axis=1)
df.to_excel(args.out)
