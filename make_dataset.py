import os
import random
import re
import csv

random.seed(42)

# -----------------------------
# Base code pool (different tasks)
# -----------------------------
BASE_SNIPPETS = [
    # 1) factorial (recursion)
    """def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
""",
    # 2) factorial (loop)
    """def factorial(n):
    res = 1
    for i in range(2, n+1):
        res *= i
    return res
""",
    # 3) fibonacci
    """def fibonacci(n):
    a, b = 0, 1
    out = []
    for _ in range(n):
        out.append(a)
        a, b = b, a + b
    return out
""",
    # 4) is_prime
    """def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True
""",
    # 5) gcd
    """def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
""",
    # 6) reverse string
    """def reverse_string(s):
    return s[::-1]
""",
    # 7) palindrome check
    """def is_palindrome(s):
    s = ''.join(ch.lower() for ch in s if ch.isalnum())
    return s == s[::-1]
""",
    # 8) bubble sort
    """def bubble_sort(arr):
    a = arr[:]
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
    return a
""",
    # 9) linear search
    """def linear_search(arr, target):
    for i, x in enumerate(arr):
        if x == target:
            return i
    return -1
""",
    # 10) binary search
    """def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
""",
    # 11) merge two sorted lists
    """def merge_sorted(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out
""",
    # 12) count frequency
    """def freq_map(items):
    m = {}
    for x in items:
        m[x] = m.get(x, 0) + 1
    return m
""",
    # 13) sum of squares
    """def sum_squares(n):
    total = 0
    for i in range(1, n+1):
        total += i*i
    return total
""",
    # 14) max in list
    """def max_in_list(nums):
    if not nums:
        return None
    m = nums[0]
    for x in nums[1:]:
        if x > m:
            m = x
    return m
""",
    # 15) unique elements preserving order
    """def unique_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
""",
]

# -----------------------------
# Plagiarism-style transformations
# -----------------------------
VAR_NAMES = ["x", "y", "z", "i", "j", "k", "n", "m", "a", "b", "res", "ans", "out", "data", "val"]
FUNC_NAMES = ["solve", "compute", "process", "calc", "run", "helper", "do_work", "task"]

def rename_identifiers(code: str) -> str:
    # Rename function name
    m = re.search(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", code)
    if m:
        old = m.group(1)
        new = random.choice(FUNC_NAMES)
        if new != old:
            code = re.sub(rf"\b{re.escape(old)}\b", new, code)

    # Rename some common identifiers (very lightweight)
    tokens = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", code))
    # Avoid keywords / builtins-ish
    blocked = {
        "def","return","for","while","if","else","elif","in","range","len","True","False",
        "None","set","list","dict","append","extend","enumerate","lower","isalnum","get"
    }
    candidates = [t for t in tokens if t not in blocked and not t.isupper()]
    random.shuffle(candidates)
    for t in candidates[: min(3, len(candidates))]:
        new = random.choice(VAR_NAMES)
        if new != t:
            code = re.sub(rf"\b{re.escape(t)}\b", new, code)
    return code

def add_dead_code(code: str) -> str:
    # Adds harmless statements inside function body
    lines = code.splitlines()
    insert = [
        "    _tmp = 0",
        "    _tmp += 1",
        "    _tmp -= 1",
    ]
    # Insert after def line if possible
    for idx, line in enumerate(lines):
        if line.strip().startswith("def "):
            pos = idx + 1
            lines[pos:pos] = random.sample(insert, k=1)
            break
    return "\n".join(lines) + ("\n" if not code.endswith("\n") else "")

def change_loop_style(code: str) -> str:
    # Small loop rewrite (range(2, n+1) -> range(1, n+1) with guard)
    code2 = code
    code2 = code2.replace("for i in range(2, n+1):", "for i in range(1, n+1):")
    return code2

def reorder_independent_lines(code: str) -> str:
    # Only reorder simple consecutive assignment lines (safe-ish)
    lines = code.splitlines()
    # Find block of simple assigns after def
    start = None
    block = []
    for i, line in enumerate(lines):
        if line.strip().startswith("def "):
            start = i + 1
            continue
        if start is not None and line.startswith("    ") and "=" in line and "==" not in line and "for " not in line and "while " not in line:
            block.append(i)
        elif block:
            break
    if len(block) >= 2:
        # shuffle those lines
        seg = [lines[i] for i in block]
        random.shuffle(seg)
        for idx, li in zip(block, seg):
            lines[idx] = li
    return "\n".join(lines) + ("\n" if not code.endswith("\n") else "")

def add_format_noise(code: str) -> str:
    # Extra blank lines / spacing noise
    code = re.sub(r"\n{2,}", "\n", code)
    if random.random() < 0.5:
        code = code.replace(":", ":  ")
    if random.random() < 0.5:
        code = "\n" + code
    if random.random() < 0.5:
        code = code + "\n"
    return code

TRANSFORMS = [
    rename_identifiers,
    add_dead_code,
    change_loop_style,
    reorder_independent_lines,
    add_format_noise
]

def make_similar_pair(base: str) -> tuple[str, str]:
    a = base
    b = base
    # Apply 2–4 transforms to b
    for _ in range(random.randint(2, 4)):
        b = random.choice(TRANSFORMS)(b)
    # sometimes apply 1 transform to a too (to avoid identical pairs)
    if random.random() < 0.35:
        a = random.choice(TRANSFORMS)(a)
    return a.strip() + "\n", b.strip() + "\n"

def make_different_pair() -> tuple[str, str]:
    a, b = random.sample(BASE_SNIPPETS, 2)
    # lightly transform each so "different" isn't too easy
    if random.random() < 0.5:
        a = rename_identifiers(a)
    if random.random() < 0.5:
        b = rename_identifiers(b)
    return a.strip() + "\n", b.strip() + "\n"


def main(out_path="data/pairs_100.csv", n_total=100):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    n_pos = n_total // 2
    n_neg = n_total - n_pos

    rows = []
    idx = 1

    # Positive (similar/plagiarized)
    for _ in range(n_pos):
        base = random.choice(BASE_SNIPPETS)
        c1, c2 = make_similar_pair(base)
        rows.append((idx, c1, c2, 1))
        idx += 1

    # Negative (different)
    for _ in range(n_neg):
        c1, c2 = make_different_pair()
        rows.append((idx, c1, c2, 0))
        idx += 1

    random.shuffle(rows)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "code1", "code2", "label"])
        w.writerows(rows)

    print(f"✅ Saved dataset: {out_path}")
    print(f"   Total: {n_total} | Similar(1): {n_pos} | Different(0): {n_neg}")


if __name__ == "__main__":
    main()