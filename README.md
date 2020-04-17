[![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-2715/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-green.svg)](https://www.python.org/downloads/release/python-375/)
[![PyPI version](https://badge.fury.io/py/kagami.svg)](https://badge.fury.io/py/kagami)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

# Kagami Library

The Kagami library is a Python package to **reinvent the wheel** and make some developments easier. It's neither designed as user-friendly nor for the purpose for a broad public to use. It may include documents in the future. But nothing under plan yet.

The Kagami library is under rapid development. Compatible between the major releases are not guaranteed. Be careful about the version required.

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

## Citation

If you use Kagami and/or MOCA in a publication, we would appreciate citations: (coming soon)

<img src="https://i.imgur.com/XIjLVV0.png" alt="Kagami is part of Albert's scientific toolbox." width="80"/>
