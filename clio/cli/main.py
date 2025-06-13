import argparse
import sys
from clio.cli.note import create_note_to_inbox

def run_cli():
    parser = argparse.ArgumentParser(prog="clio")
    subparsers = parser.add_subparsers(dest="command")

    note_parser = subparsers.add_parser("note", help="Create a note in _in genus")
    note_parser.add_argument("text", nargs="?", help="Note content (optional)")

    args = parser.parse_args()

    if args.command == "note":
        # Case 1: passed as argument → works
        if args.text:
            create_note_to_inbox(args.text)

        # Case 2: piped or redirected input
        elif not sys.stdin.isatty():
            note_text = sys.stdin.read().strip()
            if note_text:
                create_note_to_inbox(note_text)
            else:
                print("Aborted: empty stdin.")

        # Case 3: interactive prompt
        else:
            try:
                note_text = input("record note for _in folder: ")
                if note_text.strip():
                    create_note_to_inbox(note_text)
                else:
                    print("Aborted: empty note.")
            except KeyboardInterrupt:
                print("\nAborted.")

    else:
        parser.print_help()

