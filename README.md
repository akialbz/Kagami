[![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-2715/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-green.svg)](https://www.python.org/downloads/release/python-375/)
[![PyPI version](https://badge.fury.io/py/kagami.svg)](https://badge.fury.io/py/kagami)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

# Kagami Library

The Kagami library is a Python package to support the development of novel computational biology algorithms. 
It is currently under rapid development. Compatible between releases are not guaranteed. 
Although the APIs are aimed to remain consistant within a major version. 
Please note that there is no plan to include documents in the near future. 

The Kagami library is distributed under the GNU Lesser General Public License v3.0.

## Dependencies

Kagami requires:

- Python >= 3.7.5
- numpy >= 1.17.4
- rpy2 >= 3.2.4
- requests >= 2.22.0
- tables >= 3.6.1

To use RWrapper, you will also need:

- rpy2 >= 3.2.4
- R >= 3.6.1

To use pytest, test coverage, and profiling you will also need:

- pytest >= 5.3.2
- pytest-cov >= 2.8.1
- pytest-profiling >= 1.7.0

Lower versions may work but have not been tested.

## Installation

Using pip:
```bash
pip install kagami
```

Using Docker:
```bash
docker pull albertaki/kagami-core:latest
```

### Testing

```bash
python -c "import kagami; kagami.test()"
```

## Changelog

*Version 3.0*
- [x] Migrate to Python 3.7
- [x] Add disk base for the Table 
- [x] Add chunk mapping
- [x] Add numpy style indexing parameters for CoreTypes
- [x] Add attribute-like access to table index
- [x] Add dataframe-like assignment to table values
- [x] Add handy snippets and R-like functions
- [x] Clean None and na usage in map functions
- [x] Fix R wrapper init libraries multiple loading bug
- [x] Fix R wrapper library loading warning suppression
- [x] Update unit tests
- [ ] `Future` Add auto adjust nthreads and nprocs by memory usage
- [ ] `Future` Add CuPy and CuML compatible
- [ ] `Future` Add node4j compatible
- [ ] `Future` Add Spark / Apache Arrow compatible

*Version 2.2*
- [x] Add fixRepeat for NamedIndex and Table
- [x] Improve Table repr
- [x] Major refactor for package structure

*Version 2.1*
- [x] Add Dockerfile
- [x] Add setup script
- [x] Add level properties for factor type

*Version 2.0*
- [x] Add Factor CoreType
- [x] Add NamedIndex CoreType
- [x] Add StructuredArray CoreType
- [x] Add Table CoreType
- [x] Add HDF5 portals for StructuredArray and Table
- [x] Add RData portal for Table
- [x] Add Metadata class
- [x] Add functional programming support
- [x] Add BinWrapper
- [x] Add license
- [x] Update unit tests


## Citation

If you use Kagami and/or MOCA in a publication, we would appreciate citations: (coming soon)

<img src="https://i.imgur.com/XIjLVV0.png" alt="Kagami is part of Albert's scientific toolbox." width="80"/>
