all:
	python gen.py buffer.schema.json > gen.cc
	clang-format -i gen.cc
	cat gen.cc
