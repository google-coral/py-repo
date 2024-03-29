# py-repo

This repo provides an index of Coral Python wheels that's compliant with [PEP 503](https://www.python.org/dev/peps/pep-0503/). It includes `pycoral` and `tflite_runtime` Python wheels.

The pip-accessible index is at https://google-coral.github.io/py-repo/. The source for which is in the `gh-pages` branch.

**Note:** If you're on a Debian Linux system (including Raspberry Pi), you should install these Python libraries using `apt` instead of `pip`.
For example, `sudo apt-get install python3-pycoral`. (These Python wheels are primarily for Windows and Mac users.)

## Install a wheel

Install `pycoral` library:
```shell
python3 -m pip install --extra-index-url https://google-coral.github.io/py-repo/ pycoral
```

Install `tflite-runtime` library:
```shell
python3 -m pip install --extra-index-url https://google-coral.github.io/py-repo/ tflite-runtime
```

## Rebuild the index

The following command rebuilds the pip index:

```shell
python3 generate_repo.py
```
