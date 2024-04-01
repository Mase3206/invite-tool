import yaml


with open('phone.yml', 'r') as f1:
	# explicit typing for type hints, because pyyaml can't do that automatically
	formats: list[dict[str, str|list]]
	formats = yaml.safe_load(f1)


for f in formats:
	print(f)