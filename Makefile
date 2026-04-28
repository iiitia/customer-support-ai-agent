.PHONY: run eval install lint

install:
	pip install -r requirements.txt

run:
	streamlit run app/main.py

eval:
	python -m evals.evaluator

lint:
	python -m py_compile app/config.py app/main.py models/llm_handler.py models/prompts.py models/language.py services/pipeline.py schemas/response_schema.py evals/evaluator.py && echo "All files OK"
