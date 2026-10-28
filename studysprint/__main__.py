"""Entry point so ``python -m studysprint ...`` works."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
