all: rasd.pdf

rasd.pdf: main.md chapters/**/*.md preprocess.py
	python3 preprocess.py main.md > compiled.md
	pandoc compiled.md -o rasd.pdf --pdf-engine=xelatex --highlight-style=espresso
	rm compiled.md

clean:
	rm -f rasd.pdf compiled.md