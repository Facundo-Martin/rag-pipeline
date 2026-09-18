# Include all modular makefiles
include make/*.mk

.PHONY: clean

# Clean up temp files and caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
