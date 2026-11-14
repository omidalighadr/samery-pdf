"""Merge PDFs or extract a range of pages."""
import argparse
from contextlib import ExitStack
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

from pypdfium2 import PdfDocument
from pypdfium2 import PdfiumError


def page_range(value):
    try:
        start, end = map(int, value.split("-"))
        if 1 <= start <= end:
            return start, end
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("Use a one-based range such as 2-5.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    merge = commands.add_parser("merge", help="Combine PDFs in the order given")
    merge.add_argument("inputs", nargs="+", type=Path)
    extract = commands.add_parser("extract", help="Extract an inclusive page range")
    extract.add_argument("input", type=Path)
    extract.add_argument("pages", type=page_range)
    for command in (merge, extract):
        command.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)

    inputs = args.inputs if args.command == "merge" else [args.input]
    temporary = None
    try:
        with ExitStack() as stack:
            result = PdfDocument.new()
            stack.callback(result.close)
            for path in inputs:
                source = PdfDocument(path)
                stack.callback(source.close)
                pages = None
                if args.command == "extract":
                    start, end = args.pages
                    if end > len(source):
                        raise ValueError(f"Page {end} is outside this {len(source)}-page PDF.")
                    pages = list(range(start - 1, end))
                result.import_pages(source, pages=pages)
            with NamedTemporaryFile(dir=args.output.parent, suffix=".pdf", delete=False) as file:
                temporary = Path(file.name)
                result.save(file)
        # Link only after writing completes. An existing destination is never replaced.
        args.output.hardlink_to(temporary)
    except (OSError, PdfiumError, ValueError) as error:
        print(f"Could not write PDF: {error}", file=sys.stderr)
        return 1
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
