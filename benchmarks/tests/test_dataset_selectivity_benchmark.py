import copy

import pytest

from .. import _sources
from .. import dataset_selectivity_benchmark
from ..tests._asserts import assert_cli, assert_context


HELP = """
Usage: conbench dataset-selectivity [OPTIONS] SOURCE

  Run dataset-selectivity benchmark(s).

  For each benchmark option, the first option value is the default.

  Valid benchmark combinations:
  --selectivity=1%
  --selectivity=10%
  --selectivity=100%

  To run all combinations:
  $ conbench dataset-selectivity --all=true

Options:
  --selectivity [1%|10%|100%]
  --all BOOLEAN                [default: False]
  --cpu-count INTEGER
  --iterations INTEGER         [default: 1]
  --drop-caches BOOLEAN        [default: False]
  --gc-collect BOOLEAN         [default: True]
  --gc-disable BOOLEAN         [default: True]
  --show-result BOOLEAN        [default: True]
  --show-output BOOLEAN        [default: False]
  --run-id TEXT                Group executions together with a run id.
  --run-name TEXT              Name of run (commit, pull request, etc).
  --help                       Show this message and exit.
"""


nyctaxi_parquet = _sources.Source("nyctaxi_multi_parquet_s3_sample")
nyctaxi_ipc = _sources.Source("nyctaxi_multi_ipc_s3_sample")
chi_traffic = _sources.Source("chi_traffic_sample")
benchmark = dataset_selectivity_benchmark.DatasetSelectivityBenchmark()
cases, case_ids = benchmark.cases, benchmark.case_ids


def assert_benchmark(result, case, source):
    munged = copy.deepcopy(result)

    expected = {
        "cpu_count": None,
        "dataset": source,
        "name": "dataset-selectivity",
        "selectivity": case[0],
    }
    assert munged["tags"] == expected
    assert_context(munged)


def assert_run(run, index, case, source):
    result, output = run[index]
    assert_benchmark(result, case, source.name)
    assert output > 0


@pytest.mark.parametrize("case", cases, ids=case_ids)
def test_dataset_selectivity(case):
    run = list(benchmark.run("TEST", case, iterations=1))
    assert len(run) == 3
    assert_run(run, 0, case, nyctaxi_parquet)
    assert_run(run, 1, case, nyctaxi_ipc)
    assert_run(run, 2, case, chi_traffic)


def test_dataset_selectivity_cli():
    command = ["conbench", "dataset-selectivity", "--help"]
    assert_cli(command, HELP)