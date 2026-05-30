from typing import List, Dict, Tuple, Type
from app.models.documentation import CodeEntity
from app.models.project import Project
from app.models.file import CodeFile
from app.services.sanitize_html import sanitize_html


def generate_html_documentation(db_project: Project, entities: List[Type[CodeEntity]]) -> str:
    title = f'Документация для проекта "{db_project.title}"'

    files_dict: Dict[int, Tuple[CodeFile, List[Type[CodeEntity]]]] = {}
    for entity in entities:
        if not entity.visibility:
            continue
        if entity.file.id not in files_dict:
            files_dict[entity.file.id] = (entity.file, [])
        files_dict[entity.file.id][1].append(entity)

    files_html = ""
    for file_id, (file, file_entities) in files_dict.items():
        file_src = f"/code-docs/projects/{db_project.id}/files/{file.id}"

        tree = build_entity_tree(file_entities)

        file_html = f"""
        <div class="file-entity">
            <div class="file-header">
                <span class="file-language">{file.language}</span>
                <a href="{file_src}" class="file-name">{file.filename}</a>
            </div>
            <div class="file-content">
        """

        file_html += generate_tree_html(tree)
        file_html += """
            </div>
        </div>
        """
        files_html += file_html

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
            body {{ 
                line-height: 1.6; 
                margin: 0; 
                padding: 0;
                color: #333;
            }}
            h1 {{ margin-bottom: 30px; }}
            .file-entity {{
                margin-bottom: 40px;
                border: 1px solid #e1e1e1;
                border-radius: 8px;
                overflow: hidden;
            }}
            .file-header {{
                background: #f5f5f5;
                padding: 15px;
                border-bottom: 1px solid #e1e1e1;
                display: flex;
                align-items: center;
            }}
            .file-language {{
                background: #e1e1e1;
                padding: 3px 10px;
                border-radius: 20px;
                font-size: 0.9em;
                margin-right: 15px;
            }}
            .file-name {{
                font-weight: bold;
                font-size: 1.2em;
                color: #2c3e50;
                text-decoration: none;
            }}
            .file-name:hover {{ text-decoration: underline; }}
            .file-content {{
                padding: 15px;
            }}
            .entity {{
                margin-top: 15px;
            }}
            .entity-header {{
                display: flex;
                align-items: center;
                margin-bottom: 5px;
            }}
            .entity-type {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.8em;
                margin-right: 10px;
                color: white;
            }}
            .entity-type.class {{ background: #3498db; }}
            .entity-type.function {{ background: #2ecc71; }}
            .entity-type.method {{ background: #e67e22; }}
            .entity-name {{
                font-weight: bold;
            }}
            .entity-docs {{
                background: #f9f9f9;
                padding: 10px 15px;
                border-radius: 4px;
                margin-top: 5px;
                border-left: 3px solid #ddd;
            }}
            .entity-children {{
                margin-left: 30px;
                border-left: 2px solid #eee;
                padding-left: 15px;
            }}
            pre {{
                white-space: pre-wrap;
                margin: 0;
                font-family: inherit;
            }}
            .no-docs {{
                color: #95a5a6;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
    """

    if not files_dict:
        html += "<div class='no-docs'>Нет доступной документации</div>"
    else:
        html += files_html

    html += """
    </body>
    </html>
    """

    return html


def build_entity_tree(entities: List[Type[CodeEntity]]) -> Dict:
    root = {"children": {}, "entities": []}

    for entity in entities:
        parts = entity.name.split('.')
        current_node = root

        for i, part in enumerate(parts):
            is_leaf = i == len(parts) - 1

            if part not in current_node["children"]:
                node_type = entity.type
                if not is_leaf:
                    node_type = "class"

                current_node["children"][part] = {
                    "name": part,
                    "type": node_type,
                    "children": {},
                    "entities": [],
                    "docs": None
                }

            if is_leaf:
                current_node["children"][part].update(
                    {"docs": entity.modified_docs or entity.original_docs or "Нет доступной документации"})
                current_node["children"][part].update({"type": entity.type})

            current_node = current_node["children"][part]
    return root


def generate_tree_html(node: Dict, level: int = 0) -> str:
    html = ""

    for child_name, child_node in node.get("children", {}).items():
        html += f"""
        <div class="entity" style="padding-left: {level * 20}px">
            <div class="entity-header">
                <span class="entity-type {child_node['type']}">{child_node['type']}</span>
                <span class="entity-name">{child_name}</span>
            </div>
        """

        if child_node["docs"]:
            html += f"""
            <div class="entity-docs">
                <pre>{sanitize_html(child_node['docs'])}</pre>
            </div>
            """

        if child_node["children"]:
            html += f"""
            <div class="entity-children">
                {generate_tree_html(child_node, level + 1)}
            </div>
            """

        html += """
        </div>
        """

    return html
