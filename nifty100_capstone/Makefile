.PHONY: load ratios test report dashboard api clean

PYTHON = python
PIP = pip
DB_PATH = data/db/nifty100.db

load:
	$(PYTHON) src/etl/loader.py

ratios:
	$(PYTHON) src/etl/ratios.py

test:
	pytest tests/ -v

report:
	$(PYTHON) src/etl/report_generator.py

dashboard:
	streamlit run dashboard/streamlit_app.py

api:
	$(PYTHON) src/api/app.py

clean:
	rm -rf __pycache__ src/etl/__pycache__ tests/__pycache__ tests/etl/__pycache__
	rm -f logs/*.log
	rm -f $(DB_PATH)
