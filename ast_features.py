import ast
import textwrap


class ASTNormalizer(ast.NodeTransformer):
    def visit_Name(self, node):
        # Replace variable names with generic token
        return ast.copy_location(ast.Name(id="VAR", ctx=node.ctx), node)

    def visit_arg(self, node):
        # Replace function argument names
        node.arg = "ARG"
        return node


def get_normalized_ast(code):
    try:
        # Fix indentation issues from textarea input
        code = textwrap.dedent(code).strip()

        tree = ast.parse(code)
        tree = ASTNormalizer().visit(tree)
        ast.fix_missing_locations(tree)

        return ast.dump(tree)
    except Exception as e:
        print("AST ERROR:", e)
        return ""