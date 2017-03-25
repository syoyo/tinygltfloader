all:
	python gen.py buffer.schema.json 
	clang-format -i output.cc
	cat output.cc
	clang++ -std=c++11 -c output.cc
