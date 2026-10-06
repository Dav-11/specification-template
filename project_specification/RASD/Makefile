PREPROCESSOR = ../../utils/preprocess.py
PDF_ENGINE ?= typst

all: rasd.pdf

rasd.pdf: main.md chapters/**/*.md $(PREPROCESSOR)
	python3 $(PREPROCESSOR) main.md --engine=$(PDF_ENGINE) > compiled.md
	pandoc compiled.md -o rasd.pdf --pdf-engine=$(PDF_ENGINE) --syntax-highlighting=espresso --number-sections
	rm compiled.md

clean:
	rm -f rasd.pdf compiled.md