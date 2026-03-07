# Python Writing Style for LLMs

Write Python in a simple, tidy, human way.

- If the change adds a new concern, make a new file for it.
- Keep `main` files, route files, and entrypoints thin.
- Prefer small module-level functions over classes.
- Use `@dataclass` for simple structured data.
- Split logic into small helpers near where they are used.
- Prefer simple Python over clever Python or obscure library APIs.
- Do the minimum that solves the task cleanly. Do not over-abstract.
- Use clear snake_case names. Avoid vague names like `data`, `util`, `manager`, or `handler`.
- Use type hints, but keep them simple.
- Use comprehensions only when they are immediately readable.
- Prefer `pathlib` for filesystem code.

Avoid:

- putting core logic into `main.py` or route files
- growing one file into a dumping ground
- utility modules full of unrelated helpers
- utility classes with only static methods
- generic solutions for non-generic problems
- dense one-liners when a plain loop is clearer
