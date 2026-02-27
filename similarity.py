from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity(vec1, vec2):
    return cosine_similarity([vec1], [vec2])[0][0]


def structural_similarity(ast_str1, ast_str2):
    if not ast_str1 or not ast_str2:
        return 0

    tokens1 = ast_str1.split()
    tokens2 = ast_str2.split()

    set1 = set(tokens1)
    set2 = set(tokens2)

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    if union == 0:
        return 0

    return intersection / union