# Specification Template

This repository should serve as a specification template for projects

## Requirements
- Python 3
- GNU make
- pandoc
- typst

## How to use

### Global Docs
the [global-docs](global-docs/) folder contains the general documentation of all your code.

- Place general apps documentation in `global-docs/apps/<app-name>`
- Place general flows documentation in `global-docs/flows/<flow-name>`

You can also point these folders to other git repositories using git submodules (also to aspecifc tag):
```shell
git submodule add [--tag <tag>] <url> global-docs/apps/<app-name>
```

```shell
git submodule add [--tag <tag>] <url> global-docs/flows/<flow-name>
```

### Project specification
The `project_specification/<document-name>/main.md` is your main docuemnt. It will be the one that will be rendered.

You should embed other documents into it (see []() to see how)


## Special commands
This project uses pandoc and a custom preprocessor to generate the pdf.

### Embedding
You can embed other files by using these preprocessors commands inside the markdown:

To embed the full content of another file use: 
```md
<!-- @include ../../apps/mistral/modules/cart/class_diagram.md -->
```

TO embed only a section of a md file:
```md
<!-- @include-section path/to/file.md#Section Title -->
```

### Auto-numbering
The chapter headers will be auto-numbered, so do not number them.

### Labels and references
To create a label add a `{#label}` tag, ES:
```md
### Sequence diagram {#sec:seq_diag}
```

To reference the label use the `\ref{sec:seq_diag}` tag, ES:
```md
See Section \ref{sec:seq_diag} for more details.
```

### Merge mermaid (testing required)

To merge multiple sequence mermaid diagrams into one:
```md
<!-- @merge-mermaid apps/mistral/modules/cart/sequence_diagrams/01_new_cart-item.mermaid apps/mistral/modules/customer/... -->
```
This will concatenate their sequence definitions inside a single ```mermaid code block.

### Table of Contents / Index
To embed an auto-generated Table of Contents:
```md
<!-- @toc -->
```
You can also use `<!-- @index -->` or specify an optional title like `<!-- @toc "Table of Contents" -->`.

### Date and Time
To automatically insert the compile date or timestamp:
```md
Release Date: <!-- @date -->
```
- `<!-- @date -->`: Outputs `YYYY-MM-DD` (e.g. `2026-10-06`)
- `<!-- @datetime -->` or `<!-- @now -->`: Outputs `YYYY-MM-DD HH:MM:SS`
- Custom formatting is supported using standard tokens: `<!-- @date %d/%m/%Y -->`

### Page Break
To force a page break between sections or after the Table of Contents:
```md
<!-- @pagebreak -->
```