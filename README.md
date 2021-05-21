[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-2715/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-green.svg)](https://www.python.org/downloads/release/python-375/)
[![PyPI version](https://badge.fury.io/py/kagami.svg)](https://badge.fury.io/py/kagami)


# Kagami Library

The Kagami library is a Python package to accelerate the development of novel computational biology algorithms. 
It is currently under rapid growth. Although the APIs are aimed to remain consistent within a major version, compatible between releases are not guaranteed. 
Please note that there is no plan to include documents anytime soon. 

The Kagami library is distributed under the GNU Lesser General Public License v3.0.


## Dependencies

- Python >= 3.7.5
- numpy >= 1.17.4
- requests >= 2.22.0
- tables >= 3.6.1

For RWrapper:

- rpy2 >= 3.2.4
- R >= 3.6.1

For pytest, test coverage, and profiling:

- pytest >= 5.3.2
- pytest-cov >= 2.8.1
- pytest-profiling >= 1.7.0

Lower versions may work but have not been tested.


## Installation

Using pip:
```bash
pip install kagami
```


### Testing

```bash
python -c "import kagami; kagami.test()"
```


## Citation

If you use Kagami, DarkFusion or MOCA in a publication, we would appreciate citations: (coming soon)

<img src="https://i.imgur.com/p3207Et.png" alt="Kagami is part of Albert's scientific toolbox." width="100"/>
