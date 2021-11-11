.PHONY: all clean instantiate

all: clean gen_diag_with_stage_obs_set.yaml instantiate

clean:
	rm -rf gen_diag_with_stage_obs_set.yaml

gen_diag_with_stage_obs_set.yaml: gen_diag_with_stage_obs_set.py
	pipenv run python $<
	cat $@

instantiate: instantiate_diag_with_stage_obs_set.py
	pipenv run python $<
