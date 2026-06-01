.PHONY: quickstart full test clean

quickstart:
	python scripts/00_download_nbs_tables.py --skip-if-exists
	python scripts/03_build_features.py --mode quickstart
	python scripts/04_train_models.py --config configs/config.yaml
	python scripts/05_evaluate_and_explain.py --config configs/config.yaml

full:
	python scripts/00_download_nbs_tables.py --skip-if-exists
	python scripts/01_download_climate_nasa_power.py --config configs/config.yaml
	python scripts/02_download_sentinel2_planetary_computer.py --config configs/config.yaml --dry-run
	python scripts/03_build_features.py --mode full --climate-source nasa_power
	python scripts/04_train_models.py --config configs/config.yaml
	python scripts/05_evaluate_and_explain.py --config configs/config.yaml

test:
	pytest -q

clean:
	rm -f data/interim/*.csv data/processed/modeling_dataset*.csv reports/tables/*.csv reports/figures/*.png models/*.joblib
