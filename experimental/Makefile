all:
	python gen.py buffer.schema.json 
	clang-format -i output.cc
	cat output.cc
	clang++ -c output.cc
