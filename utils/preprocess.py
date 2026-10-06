import re
import sys
import os

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    base_dir = os.path.dirname(filepath)

    # 1. Handle file includes: <!-- @include path/to/file.md -->
    def replace_include(match):
        inc_path = os.path.normpath(os.path.join(base_dir, match.group(1)))
        if not os.path.exists(inc_path):
            return f"<!-- ERROR: File not found: {match.group(1)} -->"
        return process_file(inc_path)

    content = re.sub(r'<!--\s*@include\s+(.*?)\s*-->', replace_include, content)

    # 2. Handle mermaid merging: <!-- @merge file1.mermaid file2.mermaid -->
    def replace_merge(match):
        files = match.group(1).split()
        merged_body = ""
        for f_rel in files:
            f_path = os.path.normpath(os.path.join(base_dir, f_rel))
            if os.path.exists(f_path):
                with open(f_path, 'r', encoding='utf-8') as mf:
                    # Strip outer ```mermaid wrapper if present in source
                    body = re.sub(r'```(?:mermaid)?\n(.*?)\n```', r'\1', mf.read(), flags=re.DOTALL)
                    merged_body += f"\n    %% From {f_rel}\n" + body + "\n"
        return f"```mermaid\nsequenceDiagram\n{merged_body}\n```"

    content = re.sub(r'<!--\s*@merge\s+(.*?)\s*-->', replace_merge, content)
    return content

if __name__ == '__main__':
    main_file = sys.argv[1]
    print(process_file(main_file))