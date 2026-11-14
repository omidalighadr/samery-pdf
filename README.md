# Samery PDF

A local command-line tool for merging PDFs and extracting consecutive pages.

Install the released version with Git and Python 3.10 or newer.

```sh
python -m pip install 'git+https://github.com/omidalighadr/samery-pdf.git@v0.1.0'
```

From a local checkout, run `python -m pip install .`.

## Example

Given `first.pdf` with three pages and `second.pdf` with two, `combined.pdf` contains five pages and `excerpt.pdf` contains three.

```sh
samery-pdf merge first.pdf second.pdf -o combined.pdf
samery-pdf extract combined.pdf 2-4 -o excerpt.pdf
```

Merge follows the input order. Page numbers start at 1 and the range includes both ends. Choose an output path that does not exist on a filesystem that supports hard links. The tool imports pages and is intended for page content. Document-level features such as bookmarks and digital signatures are outside its scope.

See the [Linux and macOS test runs](https://github.com/omidalighadr/samery-pdf/actions/workflows/tests.yml). Run the tests locally with `python -m unittest discover -s tests -v`.

Project idea inspired by [xeptore/qpdf](https://github.com/xeptore/qpdf). This CLI uses pypdfium2.
