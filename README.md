# napari-crop-and-mask

[![License](https://img.shields.io/pypi/l/napari-crop-and-mask.svg?color=green)](https://github.com/MosGeo/napari-crop-and-mask/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-crop-and-mask.svg?color=green)](https://pypi.org/project/napari-crop-and-mask)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-crop-and-mask.svg?color=green)](https://python.org)
[![tests](https://github.com/MosGeo/napari-crop-and-mask/workflows/tests/badge.svg)](https://github.com/MosGeo/napari-crop-and-mask/actions)
[![codecov](https://codecov.io/gh/MosGeo/napari-crop-and-mask/branch/main/graph/badge.svg)](https://codecov.io/gh/MosGeo/napari-crop-and-mask)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-crop-and-mask)](https://napari-hub.org/plugins/napari-crop-and-mask)

A napari plugin for cropping and masking. Everything is implemented in dask to allow scalbility. Core functionlity is seperated from the napari/UI to allow usablity. This is currently in prototyping phase and so it is not officially in PyPI yet. The following features are implemented.

1. Rectangular cropping in 2D and 3D images (RGB and non RGB), technically, it would work on an arbitery number of dimensions but I have not tested it heavily.
2. Masking images using any shape (irregular and regular/rectangular). Masking can be done using zero and nan values. Note that napari has issues displaying RGB images with nan values as nan values are floats.


## Installation (not yet)

<!-- You can install `napari-crop-and-mask` via [pip]:

    pip install napari-crop-and-mask -->


To install latest development version :

    pip install git+https://github.com/MosGeo/napari-crop-and-mask.git


## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

Things that I need to do/check on:
1. Best way to handle "errors" in napari. Now they are implemented as warnings.
2. Testing on n-dimensional images.
3. RGB nan masking.
4. Tests (at least for core.py file)
5. Better comments in code.
6. Maybe ability to switch between backends (dask and numpy)?
7. np2 commands vs widgets.
8. Location of command in napari menu (don't like the plugin location)
9. Fix napari disabled style (https://github.com/napari/napari/issues/3601)


## License

Distributed under the terms of the [MIT] license,
"napari-crop-and-mask" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/MosGeo/napari-crop-and-mask/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
