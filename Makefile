.PHONY: all clean instantiate

all: clean gen_diag_with_stage_obs_set.yaml instantiate

clean:
	rm -rf gen_diag_with_stage_obs_set.yaml
	rm -rf Pipfile.lock
	pipenv --rm
	pipenv install
	pipenv run pip list

gen_diag_with_stage_obs_set.yaml: gen_diag_with_stage_obs_set.py
	pipenv run python $<
	cat $@

instantiate: instantiate_diag_with_stage_obs_set.py
	pipenv run python $<
