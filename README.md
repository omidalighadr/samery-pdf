# Samery PDF

A local command-line tool for merging PDFs and extracting consecutive pages.

```sh
python -m pip install .
samery-pdf merge first.pdf second.pdf -o combined.pdf
samery-pdf extract combined.pdf 2-5 -o excerpt.pdf
```

Use Python 3.10 or newer. Merge follows the input order. Page numbers start at 1 and the range includes both ends. Choose an output path that does not exist on a filesystem that supports hard links. The tool imports pages and is intended for page content. Document-level features such as bookmarks and digital signatures are outside its scope.

Run the tests with `python -m unittest discover -s tests -v`.

Project idea inspired by [xeptore/qpdf](https://github.com/xeptore/qpdf). This CLI uses pypdfium2.
