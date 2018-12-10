# Kagami Library

The Kagami library is a Python package to **reinvent the wheel** and make some developments easier. It's neither designed as user-friendly nor for the purpose for a broad public to use. It may include documents in the future. But nothing under plan yet. Think twice before using it in your project.

The Kagami library is under rapid development. Compatible between the major releases are not guaranteed. Be careful about the version required.

The Kagami library supports Python 2.7 and will soon be compatible with Python 3. The Kagami library is distributed under the GNU Lesser General Public License v3.0.

## Dependencies

Kagami requires:

- Python (>= 2.7.14)
- Pytables (>= 3.4.4)
- requests (>= 2.20.1)
- bidict (>= 0.17.5)
- pytest (>= 4.0.0)

To use RWrapper, you will also need:

- rpy2 (== 2.8.6)
- R (>= 3.4.4)

To use pytest coverage and profiling, you will also need:

- pytest-cov (>= 2.6.0)
- pytest-profiling (>= 1.3.0)

## Installation

Using pip:
```bash
pip install kagami
```

Using Pipenv:
```bash
pipenv install kagami
```

Using Docker (publicly available soon)
```bash
docker run -v $(pwd):/home --rm kagami-core:latest <your script>
```

## Testing

```python
import kagami
kagami.test()

=================================== test session starts =================================== 
platform darwin -- Python 2.7.15, pytest-3.7.0, py-1.5.4, pluggy-0.7.1
rootdir: Kagami, inifile:
plugins: profiling-1.3.0, cov-2.5.1
collected 47 items

kagami/tests/core_tests/test_etc.py ......                                            [ 12%]
kagami/tests/core_tests/test_functional.py .....                                      [ 23%]
kagami/tests/core_tests/test_path.py ...                                              [ 29%]
....
```
