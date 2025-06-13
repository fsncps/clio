import sys
from clio.ui.app import ClioApp
from clio.cli.main import run_cli  # your CLI entrypoint

def main():
    if len(sys.argv) == 1:
        ClioApp().run()
    else:
        run_cli()

if __name__ == "__main__":
    main()

