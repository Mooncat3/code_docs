import ast
from typing import List, Dict
import esprima
import javalang
from javalang.tree import MethodDeclaration, ClassDeclaration, InterfaceDeclaration, ConstructorDeclaration
import re


def parse_code_entities(content: str, language: str) -> List[Dict]:
    lang = language.lower().strip()
    if lang == "python":
        return _parse_python_entities(content)
    elif lang == "javascript":
        return _parse_javascript_entities(content)
    elif lang == "java":
        return _parse_java_entities(content)
    return []


def _parse_python_entities(content: str) -> List[Dict]:
    def find_entity_end(node: ast.AST) -> int:
        if hasattr(node, 'body') and node.body:
            last_node = node.body[-1]
            if hasattr(last_node, 'end_lineno'):
                return last_node.end_lineno
            elif hasattr(last_node, 'lineno'):
                return last_node.lineno
        return node.lineno

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    entities = []

    class EntityVisitor(ast.NodeVisitor):
        def __init__(self, parent=None):
            self.parent = parent

        def visit_ClassDef(self, node):
            full_name = f"{self.parent}.{node.name}" if self.parent else node.name
            docstring = ast.get_docstring(node)
            entities.append({
                "name": full_name,
                "type": "class",
                "line_start": node.lineno,
                "line_end": find_entity_end(node),
                "parent": self.parent,
                "docstring": docstring
            })
            EntityVisitor(parent=full_name).visit_all(node.body)

        def visit_FunctionDef(self, node):
            full_name = f"{self.parent}.{node.name}" if self.parent else node.name
            docstring = ast.get_docstring(node)
            entities.append({
                "name": full_name,
                "type": "method" if self.parent else "function",
                "line_start": node.lineno,
                "line_end": find_entity_end(node),
                "parent": self.parent,
                "docstring": docstring
            })
            EntityVisitor(parent=full_name).visit_all(node.body)

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)

        def visit_all(self, body):
            for child in body:
                self.visit(child)

    visitor = EntityVisitor()
    visitor.visit(tree)
    return entities


def _parse_javascript_entities(content: str) -> List[Dict]:
    try:
        tree = esprima.parseScript(content, loc=True, comment=True, range=True,
                                   tolerant=True)
    except Exception as e:
        print(f"Error parsing JavaScript: {e}")
        return []

    entities = []
    comments = tree.comments if hasattr(tree, 'comments') else []

    jsdoc_map = {}
    for comment in comments:
        if comment.type == 'Block' and comment.value.strip().startswith('*'):
            end_line = comment.loc.end.line
            jsdoc_map[end_line + 1] = comment.value.strip()

    class EntityVisitor:
        def __init__(self, parent=None):
            self.parent = parent

        def visit(self, node, parent_name=None):
            if not hasattr(node, 'type'):
                return

            method_name = f'visit_{node.type}'
            if hasattr(self, method_name):
                getattr(self, method_name)(node, parent_name)
            else:
                self.generic_visit(node, parent_name)

        def generic_visit(self, node, parent_name):
            for attr in ['body', 'declarations', 'expression', 'init',
                         'value', 'consequent', 'alternate', 'argument', 'arguments']:
                child = getattr(node, attr, None)
                if child is not None:
                    if isinstance(child, list):
                        for c in child:
                            self.visit(c, parent_name)
                    else:
                        self.visit(child, parent_name)

        def visit_FunctionDeclaration(self, node, parent_name):
            if not hasattr(node, 'id') or not hasattr(node.id, 'name'):
                return

            full_name = f"{parent_name}.{node.id.name}" if parent_name else node.id.name
            docstring = self._get_jsdoc(node)

            entities.append({
                "name": full_name,
                "type": "method" if parent_name else "function",
                "line_start": node.loc.start.line,
                "line_end": node.loc.end.line,
                "parent": parent_name,
                "docstring": docstring
            })

            EntityVisitor(parent=full_name).visit(node.body, full_name)

        def visit_ClassDeclaration(self, node, parent_name):
            if not hasattr(node, 'id') or not hasattr(node.id, 'name'):
                return

            full_name = f"{parent_name}.{node.id.name}" if parent_name \
                else node.id.name
            docstring = self._get_jsdoc(node)

            entities.append({
                "name": full_name,
                "type": "class",
                "line_start": node.loc.start.line,
                "line_end": node.loc.end.line,
                "parent": parent_name,
                "docstring": docstring
            })

            if hasattr(node, 'body') and hasattr(node.body, 'body'):
                for element in node.body.body:
                    self.visit(element, full_name)

        def visit_MethodDefinition(self, node, parent_name):
            if not hasattr(node, 'key') or not hasattr(node.key, 'name'):
                return

            full_name = f"{parent_name}.{node.key.name}"
            docstring = self._get_jsdoc(node)

            entities.append({
                "name": full_name,
                "type": "method",
                "line_start": node.loc.start.line,
                "line_end": node.loc.end.line,
                "parent": parent_name,
                "docstring": docstring
            })

            if hasattr(node, 'value'):
                self.visit(node.value.body, full_name)

        @staticmethod
        def _get_jsdoc(node):
            """Ищет JSDoc комментарий непосредственно перед узлом"""
            node_line = node.loc.start.line
            for i in range(3):
                candidate = jsdoc_map.get(node_line - i)
                if candidate:
                    lines = [line.strip().lstrip('*').strip()
                             for line in candidate.split('\n')]
                    return '\n'.join(lines).strip()
            return None

    visitor = EntityVisitor()
    visitor.visit(tree)
    return entities


def _parse_java_entities(content: str) -> List[Dict]:
    def _find_end_line(node, lines) -> int:
        if not hasattr(node, 'position') or not node.position:
            return 0

        start_line = node.position.line - 1
        start_pos = node.position.column if hasattr(node.position, 'column') else 0

        brace_stack = 0
        current_line = start_line

        while current_line < len(lines):
            line = lines[current_line]
            search_start = start_pos if current_line == start_line else 0
            for i in range(search_start, len(line)):
                char = line[i]
                if char == '{':
                    brace_stack += 1
                elif char == '}':
                    brace_stack -= 1
                    if brace_stack == 0:
                        return current_line + 1
                    elif brace_stack < 0:
                        return current_line + 1
            current_line += 1
        return current_line

    def _clean_docstring(docstring: str) -> str:
        if not docstring:
            return docstring
        docstring = docstring.strip()
        docstring = re.sub(r'^\s*/\*\*?\s*', '', docstring)
        docstring = re.sub(r'\s*\*/\s*$', '', docstring)
        lines = docstring.splitlines()
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            line = re.sub(r'^\*\s?', '', line)
            if line:
                cleaned_lines.append(line.strip())
        result = '\n'.join(cleaned_lines)
        return result.strip()

    def _process_method_or_constructor(node, parent_path, entities, lines):
        method_type = 'constructor' if isinstance(node, ConstructorDeclaration) else 'method'
        full_name = f"{parent_path}.{node.name}"
        line_end = _find_end_line(node, lines)
        entities.append({
            "name": full_name,
            "type": method_type,
            "line_start": node.position.line if node.position else None,
            "line_end": line_end,
            "parent": parent_path.split('.')[-1],
            "docstring": _clean_docstring(node.documentation) if hasattr(node, 'documentation') else None
        })

    def _process_class_or_interface(node, parent_path, entities, lines):
        class_type = 'class' if isinstance(node, ClassDeclaration) else 'interface'
        full_name = f"{parent_path}.{node.name}" if parent_path else node.name

        line_end = _find_end_line(node, lines)

        entities.append({
            "name": full_name,
            "type": class_type,
            "line_start": node.position.line if node.position else None,
            "line_end": line_end,
            "parent": parent_path.split('.')[-1] if parent_path else None,
            "docstring": _clean_docstring(node.documentation) if hasattr(node, 'documentation') else None
        })

        for member in node.body:
            if isinstance(member, (MethodDeclaration, ConstructorDeclaration)):
                _process_method_or_constructor(member, full_name, entities, lines)
            elif isinstance(member, (ClassDeclaration, InterfaceDeclaration)):
                _process_class_or_interface(member, full_name, entities, lines)

    try:
        tree = javalang.parse.parse(content)
    except javalang.parser.JavaSyntaxError as e:
        return []

    entities = []

    tree_filtered = list(tree.filter(ClassDeclaration)) + list(tree.filter(InterfaceDeclaration))
    for path, node in tree_filtered:
        _process_class_or_interface(node, "", entities, content.splitlines())

    return entities
