import ast
from typing import Type, Optional
from app.models.documentation import CodeEntity
import esprima
import javalang
from javalang.tree import MethodDeclaration, ClassDeclaration, InterfaceDeclaration, ConstructorDeclaration
import re


def insert_docstring(language: str, content: str, entity: Type[CodeEntity], docstring: Optional[str]) -> str:
    lang = language.lower().strip()
    if lang == "python":
        return _insert_python_docstring(content, entity, docstring)
    elif lang == "javascript":
        return _insert_javascript_docstring(content, entity, docstring)
    elif lang == "java":
        return _insert_java_docstring(content, entity, docstring)
    return content


def _insert_python_docstring(content: str, entity: Type[CodeEntity],
                             docstring: Optional[str]) -> str:
    if docstring is None:
        return content

    lines = content.splitlines()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return content

    class DocstringRewriter(ast.NodeVisitor):
        def __init__(self, target_name):
            self.target_name = target_name
            self.result = None

        def visit_ClassDef(self, node):
            self._process_node(node)
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            self._process_node(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)

        @staticmethod
        def _get_full_name(node):
            parts = []
            while node:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef)):
                    parts.append(node.name)
                node = getattr(node, 'parent', None)
            return '.'.join(reversed(parts))

        def _process_node(self, node):
            full_name = self._get_full_name(node)
            if full_name != self.target_name:
                return

            if node.body:
                first_stmt = node.body[0]
                if (isinstance(first_stmt, ast.Expr) and
                        isinstance(first_stmt.value, ast.Str)):
                    self.result = ('replace', first_stmt.lineno - 1,
                                   first_stmt.end_lineno - 1)
                else:
                    self.result = ('insert', node.body[0].lineno - 1)
            else:
                self.result = ('insert', node.lineno)

    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    rewriter = DocstringRewriter(entity.name)
    rewriter.visit(tree)

    if rewriter.result is None:
        return content

    docstring_lines = (['"""'] + docstring.strip().replace('"""', '')
                       .split('\n') + ['"""'])

    if rewriter.result[0] == 'replace':
        start, end = rewriter.result[1], rewriter.result[2]
        indent = len(lines[start]) - len(lines[start].lstrip())
        formatted = [(' ' * indent) + line for line in docstring_lines]
        return '\n'.join(lines[:start] + formatted + lines[end + 1:])

    elif rewriter.result[0] == 'insert':
        insert_line = rewriter.result[1]
        indent = len(lines[insert_line]) - len(lines[insert_line].lstrip())
        formatted = [(' ' * indent) + line for line in docstring_lines]
        return '\n'.join(lines[:insert_line] + formatted +
                         lines[insert_line:])

    return content


def _insert_javascript_docstring(content: str, entity: Type[CodeEntity], docstring: Optional[str]) -> str:
    if docstring is None:
        return content

    lines = content.splitlines()

    try:
        tree = esprima.parseScript(content, loc=True, comment=True, tolerant=True)
    except Exception as e:
        print(f"Error parsing JavaScript: {e}")
        return content

    comments = tree.comments if hasattr(tree, 'comments') else []
    jsdoc_lines_map = {c.loc.end.line: c for c in comments
                       if c.type == 'Block' and c.value.strip().startswith('*')}

    class DocstringLocator:
        def __init__(self, target_name):
            self.target_name = target_name
            self.result = None

        def visit(self, node, current_name=None):
            if not hasattr(node, 'type'):
                return

            method_name = f'visit_{node.type}'
            if hasattr(self, method_name):
                getattr(self, method_name)(node, current_name)
            else:
                self.generic_visit(node, current_name)

        def generic_visit(self, node, current_name):
            for attr in ['body', 'declarations', 'expression', 'init', 'value']:
                child = getattr(node, attr, None)
                if isinstance(child, list):
                    for c in child:
                        self.visit(c, current_name)
                elif child is not None:
                    self.visit(child, current_name)

        def visit_FunctionDeclaration(self, node, current_name):
            if hasattr(node, 'id') and hasattr(node.id, 'name'):
                full_name = f"{current_name}.{node.id.name}" if current_name else node.id.name
                if full_name == self.target_name:
                    self._process_node(node)
                else:
                    self.visit(node.body, full_name)

        def visit_ClassDeclaration(self, node, current_name):
            if hasattr(node, 'id') and hasattr(node.id, 'name'):
                full_name = f"{current_name}.{node.id.name}" if current_name else node.id.name
                if full_name == self.target_name:
                    self._process_node(node)
                else:
                    if hasattr(node, 'body') and hasattr(node.body, 'body'):
                        for element in node.body.body:
                            self.visit(element, full_name)

        def visit_MethodDefinition(self, node, current_name):
            if hasattr(node, 'key') and hasattr(node.key, 'name'):
                full_name = f"{current_name}.{node.key.name}"
                if full_name == self.target_name:
                    self._process_node(node)
                else:
                    if hasattr(node, 'value'):
                        self.visit(node.value.body, full_name)

        def _process_node(self, node):
            node_start_line = node.loc.start.line
            for offset in range(0, 3):
                comment = jsdoc_lines_map.get(node_start_line - offset - 1)
                if comment:
                    self.result = ('replace', comment.loc.start.line - 1, comment.loc.end.line - 1)
                    return
            self.result = ('insert', node_start_line - 1)

    locator = DocstringLocator(entity.name)
    locator.visit(tree)

    if locator.result is None:
        return content

    docstring = docstring.replace("/**", "").replace("*/", "")
    docstring_lines = ['/**'] + [f' * {line}' for line in docstring.strip().split('\n')] + [' */']

    if locator.result[0] == 'replace':
        start, end = locator.result[1], locator.result[2]
        indent = len(lines[start]) - len(lines[start].lstrip())
        formatted = [(' ' * indent) + line for line in docstring_lines]
        return '\n'.join(lines[:start] + formatted + lines[end + 1:])
    elif locator.result[0] == 'insert':
        insert_line = locator.result[1]
        indent = len(lines[insert_line]) - len(lines[insert_line].lstrip())
        formatted = [(' ' * indent) + line for line in docstring_lines]
        return '\n'.join(lines[:insert_line] + formatted + lines[insert_line:])

    return content


def _insert_java_docstring(content: str, entity: Type[CodeEntity], docstring: Optional[str]) -> str:
    entity_name = entity.name
    try:
        tree = javalang.parse.parse(content)
    except javalang.parser.JavaSyntaxError:
        return content

    parts = entity_name.split('.')
    class_name = parts[0]
    method_name = parts[1] if len(parts) > 1 else None

    found_node = None
    for path, node in tree:
        if isinstance(node, (ClassDeclaration, InterfaceDeclaration, MethodDeclaration, ConstructorDeclaration)):
            current_name = node.name
            if isinstance(node, (MethodDeclaration, ConstructorDeclaration)):
                parent = path[-2] if len(path) > 1 else None
                if parent and isinstance(parent, (ClassDeclaration, InterfaceDeclaration)):
                    full_name = f"{parent.name}.{current_name}"
                    if full_name == entity_name:
                        found_node = node
                        break
            elif current_name == class_name and not method_name:
                found_node = node
                break

    if not found_node:
        return content

    if not hasattr(found_node, 'position') or not found_node.position:
        return content

    lines = content.splitlines()
    line_num = found_node.position.line - 1
    line = lines[line_num]

    indent = re.match(r'^\s*', line).group()

    javadoc_start = None
    javadoc_end = None
    current_search_line = line_num - 1

    while current_search_line >= 0:
        search_line = lines[current_search_line].strip()
        if search_line.endswith('*/'):
            javadoc_end = current_search_line
            while current_search_line >= 0:
                if lines[current_search_line].strip().startswith('/**'):
                    javadoc_start = current_search_line
                    break
                current_search_line -= 1
            break
        elif not search_line.startswith('*') and not search_line == '':
            break
        current_search_line -= 1

    new_javadoc = ""
    if docstring is not None:
        docstring = docstring.replace("/**", "").replace("*/", "")
        new_javadoc = f"{indent}/**\n"
        for line in docstring.split('\n'):
            new_javadoc += f"{indent} * {line}\n"
        new_javadoc += f"{indent} */\n"

    modified_lines = lines.copy()
    if javadoc_start is not None and javadoc_end is not None:
        del modified_lines[javadoc_start:javadoc_end + 1]
        modified_lines.insert(javadoc_start, new_javadoc.rstrip('\n'))
    else:
        modified_lines.insert(line_num, new_javadoc.rstrip('\n'))
    return '\n'.join(modified_lines)
