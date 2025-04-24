# ========================
# Templates
# ========================
.PHONY: feature

feature:
	cookiecutter templates/FeatureTemplate -o ./src

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