import re

def remove_comments(code):
    code = re.sub(r"#.*", "", code)
    code = re.sub(r'"""[\s\S]*?"""', "", code)
    code = re.sub(r"'''[\s\S]*?'''", "", code)
    return code

def normalize_whitespace(code):
    return "\n".join(line.strip() for line in code.splitlines() if line.strip())

def normalize_code(code):
    code = remove_comments(code)
    code = normalize_whitespace(code)
    return code