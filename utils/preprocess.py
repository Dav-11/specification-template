import re
import sys
import os
import argparse
import datetime

def resolve_path(base_dir, rel_path):
    """
    Resolves a file path:
    1. Relative to base_dir
    2. Relative to current working directory
    3. Relative to repository root (searching up for .git)
    """
    rel_path = rel_path.strip()
    p1 = os.path.normpath(os.path.join(base_dir, rel_path))
    if os.path.exists(p1):
        return p1
    if os.path.exists(rel_path):
        return os.path.normpath(rel_path)
    cur = os.path.abspath(base_dir) if base_dir else os.getcwd()
    while cur != os.path.dirname(cur):
        if os.path.exists(os.path.join(cur, '.git')):
            candidate = os.path.normpath(os.path.join(cur, rel_path))
            if os.path.exists(candidate):
                return candidate
            break
        cur = os.path.dirname(cur)
    return None

def extract_section(filepath, section_title, level_offset=0):
    """
    Extracts a section by its heading title and adjusts heading levels
    relative to level_offset.
    """
    if not os.path.exists(filepath):
        return f"<!-- ERROR: File not found: {filepath} -->"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    target_level = None
    capturing = False
    extracted_lines = []
    target_title = section_title.strip()
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block

        if not in_code_block:
            heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                clean_title = re.sub(r'\{#.*?\}', '', title).strip()

                if not capturing:
                    if clean_title.lower() == target_title.lower():
                        target_level = level
                        capturing = True
                        new_lvl = (level_offset + 1) if level_offset > 0 else level
                        extracted_lines.append('#' * min(6, new_lvl) + ' ' + title + '\n')
                        continue
                else:
                    if level <= target_level:
                        break
                    sub_diff = level - target_level
                    new_lvl = (level_offset + 1 + sub_diff) if level_offset > 0 else level
                    extracted_lines.append('#' * min(6, new_lvl) + ' ' + title + '\n')
                    continue
        
        if capturing:
            extracted_lines.append(line)

    if not capturing:
        return f"<!-- ERROR: Section '{section_title}' not found in {filepath} -->"
    
    return "".join(extracted_lines)

def format_datetime(match):
    """
    Formats the current date/time based on tag and optional format string.
    <!-- @date --> -> YYYY-MM-DD
    <!-- @datetime --> -> YYYY-MM-DD HH:MM:SS
    <!-- @date %d/%m/%Y --> -> custom format
    """
    tag = match.group(1).lower()
    arg = match.group(2)
    now = datetime.datetime.now()
    if arg and arg.strip():
        fmt = arg.strip().strip('"').strip("'")
        try:
            return now.strftime(fmt)
        except Exception:
            pass
    if tag == 'date':
        return now.strftime('%Y-%m-%d')
    return now.strftime('%Y-%m-%d %H:%M:%S')

def format_toc(match, engine='typst'):
    """
    Generates a Table of Contents / Index directive for the specified engine.
    """
    arg = match.group(2)
    title = arg.strip().strip('"').strip("'") if arg and arg.strip() else None
    if engine == 'typst':
        if title:
            return f"```{{=typst}}\n#outline(title: \"{title}\", indent: auto)\n```\n"
        return "```{=typst}\n#outline(indent: auto)\n```\n"
    else:
        if title:
            return f"```{{=latex}}\n\\renewcommand{{\\contentsname}}{{{title}}}\n\\tableofcontents\n```\n"
        return "```{=latex}\n\\tableofcontents\n```\n"

def format_pagebreak(engine='typst'):
    """
    Generates a pagebreak directive for the specified engine.
    """
    if engine == 'typst':
        return "```{=typst}\n#pagebreak()\n```\n"
    return "```{=latex}\n\\newpage\n```\n"

def process_file_content(filepath, level_offset=0, engine='typst'):
    """
    Recursively processes a file, resolving includes, scaling headings,
    handling TOC, date/time, and merging sequence mermaid diagrams.
    """
    if not os.path.exists(filepath):
        return f"<!-- ERROR: File not found: {filepath} -->"

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    base_dir = os.path.dirname(filepath)
    out_lines = []
    current_heading_level = level_offset
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            out_lines.append(line)
            continue

        if in_code_block:
            out_lines.append(line)
            continue

        # Check for @date, @datetime, @now (inline replacement)
        if '<!--' in line and '@' in line:
            line = re.sub(r'<!--\s*@(date|datetime|now)(?:\s+(.*?))?\s*-->', format_datetime, line)

        # Check for @toc or @index
        toc_match = re.match(r'^\s*<!--\s*@(toc|index)(?:\s+(.*?))?\s*-->\s*$', line)
        if toc_match:
            out_lines.append(format_toc(toc_match, engine=engine))
            continue

        # Check for @pagebreak or @newpage
        pb_match = re.match(r'^\s*<!--\s*@(pagebreak|newpage)\s*-->\s*$', line)
        if pb_match:
            out_lines.append(format_pagebreak(engine=engine))
            continue

        # Check for heading
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            base_level = len(heading_match.group(1))
            new_level = min(6, base_level + level_offset)
            title_rest = heading_match.group(2)
            current_heading_level = new_level
            out_lines.append('#' * new_level + ' ' + title_rest + '\n')
            continue

        # Check for @include-section: <!-- @include-section path/to/file.md#Heading -->
        inc_sec_match = re.match(r'^\s*<!--\s*@include-section\s+(.*?)\s*-->\s*$', line)
        if inc_sec_match:
            raw_target = inc_sec_match.group(1).strip()
            if '#' in raw_target:
                f_rel, sec_title = raw_target.rsplit('#', 1)
                resolved = resolve_path(base_dir, f_rel.strip())
                if not resolved:
                    out_lines.append(f"<!-- ERROR: File not found: {f_rel.strip()} -->\n")
                else:
                    sec_content = extract_section(resolved, sec_title.strip(), level_offset=current_heading_level)
                    out_lines.append(sec_content + "\n")
            else:
                out_lines.append("<!-- ERROR: Invalid @include-section syntax. Use path.md#Heading Name -->\n")
            continue

        # Check for @include: <!-- @include path/to/file.md -->
        inc_match = re.match(r'^\s*<!--\s*@include\s+(?!-section)(.*?)\s*-->\s*$', line)
        if inc_match:
            f_rel = inc_match.group(1).strip()
            resolved = resolve_path(base_dir, f_rel)
            if not resolved:
                out_lines.append(f"<!-- ERROR: File not found: {f_rel} -->\n")
            else:
                sub_content = process_file_content(resolved, level_offset=current_heading_level, engine=engine)
                out_lines.append(sub_content + "\n")
            continue

        # Check for @merge or @merge-mermaid
        merge_match = re.match(r'^\s*<!--\s*@(merge|merge-mermaid)\s+(.*?)\s*-->\s*$', line)
        if merge_match:
            files = merge_match.group(2).split()
            merged_body = ""
            for f_rel in files:
                f_path = resolve_path(base_dir, f_rel)
                if f_path and os.path.exists(f_path):
                    with open(f_path, 'r', encoding='utf-8') as mf:
                        body = re.sub(r'```(?:mermaid)?\n(.*?)\n```', r'\1', mf.read(), flags=re.DOTALL)
                        merged_body += f"\n    %% From {f_rel}\n" + body + "\n"
                else:
                    merged_body += f"\n    %% ERROR: File not found: {f_rel}\n"
            out_lines.append(f"```mermaid\nsequenceDiagram\n{merged_body}\n```\n")
            continue

        out_lines.append(line)

    return "".join(out_lines)

def apply_labels_and_refs(content, engine='typst'):
    r"""
    Translates \label, \ref, and \autoref into engine-compatible syntax
    while preserving code blocks and backtick spans.
    """
    lines = content.splitlines(keepends=True)
    out_lines = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            out_lines.append(line)
            continue

        if in_code_block:
            out_lines.append(line)
            continue

        # 1. Replace \label{key} on headings: ## Title \label{key} -> ## Title {#key}
        line = re.sub(r'^(#{1,6}\s+.*?)\s*\\label\{([^}]+)\}', r'\1 {#\2}', line)

        # 2. Standalone \label{key} -> {#key}
        line = re.sub(r'^\s*\\label\{([^}]+)\}\s*$', r'{#\1}\n', line)

        # 3. Replace \autoref{key} and \ref{key} outside inline code backticks
        parts = re.split(r'(`+[^`]+`+)', line)
        for i in range(0, len(parts), 2):
            if engine == 'typst':
                parts[i] = re.sub(r'\\autoref\{([^}]+)\}', r'`@\1`{=typst}', parts[i])
                parts[i] = re.sub(r'\\ref\{([^}]+)\}', r'`#ref(<\1>, supplement: none)`{=typst}', parts[i])
            else:
                parts[i] = re.sub(r'\\autoref\{([^}]+)\}', r'`\\autoref{\1}`{=latex}', parts[i])
                parts[i] = re.sub(r'\\ref\{([^}]+)\}', r'`\\ref{\1}`{=latex}', parts[i])

        out_lines.append("".join(parts))

    return "".join(out_lines)

def process_file(filepath, engine='typst'):
    content = process_file_content(filepath, level_offset=0, engine=engine)
    return apply_labels_and_refs(content, engine=engine)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Markdown preprocessor for Pandoc documents")
    parser.add_argument("main_file", help="Path to main markdown file")
    parser.add_argument("--engine", default="typst", choices=["typst", "xelatex", "latex", "pdflatex"],
                        help="Target PDF engine (default: typst)")
    args = parser.parse_args()
    print(process_file(args.main_file, engine=args.engine))