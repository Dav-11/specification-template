.SUFFIXES:
.PHONY: all clean

PREPROCESSOR = ../../utils/preprocess.py

PDF_ENGINE ?= typst
TEMPLATE ?= ../../utils/templates/template.typst

TMP_PATH = .tmp
OUT_PATH = .out

all: $(OUT_PATH)/rasd.pdf

$(TMP_PATH):
	mkdir -p $(TMP_PATH)

$(OUT_PATH):
	mkdir -p $(OUT_PATH)

$(TMP_PATH)/compiled.md: main.md chapters/**/*.md $(PREPROCESSOR) | $(TMP_PATH)
	python3 $(PREPROCESSOR) main.md --engine=$(PDF_ENGINE) > $@

$(OUT_PATH)/rasd.pdf: $(TMP_PATH)/compiled.md | $(OUT_PATH)
	pandoc $< -o $@ --pdf-engine=$(PDF_ENGINE) --template=$(TEMPLATE) --syntax-highlighting=espresso --number-sections

clean:
	rm -rf $(OUT_PATH) $(TMP_PATH)