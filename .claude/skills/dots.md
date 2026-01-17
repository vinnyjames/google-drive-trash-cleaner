# Dots Progress Indicator

Use the `Dots` class from `dots.py` when displaying progress for iterative operations.

```python
from dots import Dots

# Basic usage (no ETA)
dots = Dots()
for item in items:
    process(item)
    dots.dot()
dots.done()

# With ETA (when total is known)
dots = Dots(total=len(items))
for item in items:
    process(item)
    dots.dot()
dots.done()
```

## Constructor Parameters
- `total` (optional): Expected number of dots. Enables ETA display.
- `width` (default=80): Number of columns before auto-wrapping to a new line.
- `msg` (optional): Initial message to print before dots (e.g., "Deleting..."). Its length counts toward the column width.

## Methods
- `dot(char='.')`: Print a progress character. Shows ETA if total is set.
- `done(message='done')`: Clear ETA and print completion message.
- `average_time()`: Returns average seconds between dots.
