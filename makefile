# ========================
# Templates
# ========================
.PHONY: module

module:
	cookiecutter templates/ModuleTemplate -o ./src

# ========================
# Dev Commands
# ========================
.PHONY: run test clean

run:
	uvicorn src.main:app --reload

test:
	pytest

clean:
	rm -rf ./tmp