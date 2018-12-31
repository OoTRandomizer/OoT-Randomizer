import ast
from ItemList import item_table
from State import State
import re


escaped_items = {}
for item in item_table:
    escaped_items[re.sub(r'[\'()[\]]', '', item.replace(' ', '_'))] = item


class Rule_AST_Transformer(ast.NodeTransformer):

    def __init__(self, world):
        self.world = world


    def visit_Name(self, node):
        if node.id in escaped_items:
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr='has',
                    ctx=ast.Load()),
                args=[ast.Str(escaped_items[node.id])],
                keywords=[])
        elif node.id in self.world.__dict__:
            return ast.Attribute(
                value=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr='world',
                    ctx=ast.Load()),
                attr=node.id,
                ctx=ast.Load())
        elif node.id in State.__dict__:
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr=node.id,
                    ctx=ast.Load()),
                args=[],
                keywords=[])
        else:
            return ast.Str(node.id.replace('_', ' '))


    def visit_Tuple(self, node):
        if len(node.elts) != 2:
            raise Exception('Parse Error: Tuple must has 2 values')

        item, count = node.elts

        if isinstance(item, ast.Str):
            item = ast.Name(id=item.s, ctx=ast.Load())

        if not isinstance(item, ast.Name):
            raise Exception('Parse Error: first value must be an item. Got %s' % item.__class__.__name__)

        if not (isinstance(count, ast.Name) or isinstance(count, ast.Num)):
            raise Exception('Parse Error: second value must be a number. Got %s' % item.__class__.__name__)

        if isinstance(count, ast.Name):
            count = ast.Attribute(
                value=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr='world',
                    ctx=ast.Load()),
                attr=count.id,
                ctx=ast.Load())

        if item.id in escaped_items:
            item.id = escaped_items[item.id]

        if not item.id in item_table:
            raise Exception('Parse Error: invalid item name')

        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='state', ctx=ast.Load()),
                attr='has',
                ctx=ast.Load()),
            args=[ast.Str(item.id), count],
            keywords=[])


    def visit_Call(self, node):
        new_args = []
        for child in node.args:
            if isinstance(child, ast.Name):
                if child.id in self.world.__dict__:
                    child = ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id='state', ctx=ast.Load()),
                            attr='world',
                            ctx=ast.Load()),
                        attr=child.id,
                        ctx=ast.Load())
                elif child.id in escaped_items:
                    child = ast.Str(escaped_items[child.id])
                else:
                    child = ast.Str(child.id.replace('_', ' '))
            new_args.append(child)

        if isinstance(node.func, ast.Name):
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr=node.func.id,
                    ctx=ast.Load()),
                args=new_args,
                keywords=node.keywords)
        else:
            return node


    def visit_Subscript(self, node):
        if isinstance(node.value, ast.Name):
            return ast.Subscript(
                value=ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id='state', ctx=ast.Load()),
                        attr='world',
                        ctx=ast.Load()),
                    attr=node.value.id,
                    ctx=ast.Load()),
                slice=ast.Index(value=ast.Str(node.slice.value.id.replace('_', ' '))),
                ctx=node.ctx)
        else:
            return node


    def visit_Compare(self, node):
        if isinstance(node.left, ast.Name):
            if node.left.id in escaped_items:
                node.left = ast.Str(escaped_items[node.left.id])

        if isinstance(node.comparators[0], ast.Name):
            if node.comparators[0].id in escaped_items:
                node.comparators[0] = ast.Str(escaped_items[node.comparators[0].id])

        self.generic_visit(node)
        return node


def parse_rule_string(rule, world):
    if rule is None:
        return lambda state: True
    else:
        rule = 'lambda state: ' + rule
    rule = rule.split('#')[0]

    rule_ast = ast.parse(rule, mode='eval')
    rule_ast = ast.fix_missing_locations(Rule_AST_Transformer(world).visit(rule_ast))
    rule_lambda = eval(compile(rule_ast, '<string>', 'eval'))
    return rule_lambda

