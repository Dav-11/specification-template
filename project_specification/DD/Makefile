all: dd.pdf

dd.pdf: main.md chapters/**/*.md preprocess.py
	python3 preprocess.py main.md > compiled.md
	pandoc compiled.md -o dd.pdf --pdf-engine=xelatex --highlight-style=espresso
	rm compiled.md

clean:
	rm -f dd.pdf compiled.md