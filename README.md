# Kagami Library

The Kagami library is a Python package to **reinvent the wheel** and make my life easier. It's neither designed as user friendly nor for the purpose for others to use. It may include documents in the future. But nothing under plan yet. Think twice before you touch it.

The Kagami library supports Python 2.7 and will soon be compatible with Python 3.7. The Kagami library is distributed under the GNU Lesser General Public License v3.0.

## Dependencies

Kagami requires (recommend version):

- Python (>= 2.7.14)
- NumPy (>= 1.15.2)
- Pytables (>= 3.4.4)
- requests (>= 2.20.1)
- bidict (>= 0.17.5)
- pytest (>= 4.0.0)

To use RWrapper, you will also need:

- rpy2 (== 2.8.6)
- R (>= 3.4.4)

## Installation

Using pip:
```bash
pip install kagami-2.1.17-py2-none-any.whl
```

Using Pipenv:
```bash
pipenv install kagami-2.1.17-py2-none-any.whl
```

Using Docker
```bash
docker run -v $(pwd):/home --rm kagami-core:latest <your script>
```

## Testing

```python
import kagami
kagami.test()

============================================ test session starts =============================================
platform darwin -- Python 2.7.15, pytest-3.7.0, py-1.5.4, pluggy-0.7.1
rootdir: /Users/albert/Repository/Kagami, inifile:
plugins: profiling-1.3.0, cov-2.5.1
collected 47 items

kagami/tests/core_tests/test_etc.py ......                                                             [ 12%]
kagami/tests/core_tests/test_functional.py .....                                                       [ 23%]
kagami/tests/core_tests/test_path.py ...                                                               [ 29%]
kagami/tests/dtypes_tests/test_coreType.py ....                                                        [ 38%]
kagami/tests/dtypes_tests/test_factor.py ....                                                          [ 46%]
kagami/tests/dtypes_tests/test_namedIndex.py ....                                                      [ 55%]
....
```
