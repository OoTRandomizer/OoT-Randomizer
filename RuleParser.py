import ast
from collections import defaultdict
import logging
import re

from Item import MakeEventItem
from ItemList import item_table
from Location import Location
from State import State


escaped_items = {}
for item in item_table:
    escaped_items[re.sub(r'[\'()[\]]', '', item.replace(' ', '_'))] = item

event_name = re.compile(r'\w+')

def isliteral(expr):
    return isinstance(expr, (ast.Num, ast.Str, ast.Bytes, ast.NameConstant))


class Rule_AST_Transformer(ast.NodeTransformer):

    def __init__(self, world):
        self.world = world
        self.events = set()
        # map Region -> rule ast string -> item name
        self.replaced_rules = defaultdict(dict)
        # delayed rules need to keep: region name, ast node, event name
        self.delayed_rules = []


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
            # Settings are constant
            return ast.parse('%r' % self.world.__dict__[node.id], mode='eval').body
        elif node.id in State.__dict__:
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr=node.id,
                    ctx=ast.Load()),
                args=[],
                keywords=[])
        elif event_name.match(node.id):
            self.events.add(node.id.replace('_', ' '))
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr='has',
                    ctx=ast.Load()),
                args=[ast.Str(node.id.replace('_', ' '))],
                keywords=[])
        else:
            raise Exception('Parse Error: invalid node name %s' % node.id, self.current_spot.name, ast.parse(node, False))

    def visit_Str(self, node):
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='state', ctx=ast.Load()),
                attr='has',
                ctx=ast.Load()),
            args=[ast.Str(node.s)],
            keywords=[])

    # python 3.8 compatibility: ast walking now uses visit_Constant for Constant subclasses
    # this includes Num, Str, NameConstant, Bytes, and Ellipsis. We only handle Str.
    def visit_Constant(self, node):
        if isinstance(node, ast.Str):
            return self.visit_Str(node)
        return node


    def visit_Tuple(self, node):
        if len(node.elts) != 2:
            raise Exception('Parse Error: Tuple must have 2 values', self.current_spot.name, ast.parse(node, False))

        item, count = node.elts

        if not isinstance(item, (ast.Name, ast.Str)):
            raise Exception('Parse Error: first value must be an item. Got %s' % item.__class__.__name__, self.current_spot.name, ast.parse(node, False))
        iname = item.id if isinstance(item, ast.Name) else item.s

        if not (isinstance(count, ast.Name) or isinstance(count, ast.Num)):
            raise Exception('Parse Error: second value must be a number. Got %s' % item.__class__.__name__, self.current_spot.name, ast.parse(node, False))

        if isinstance(count, ast.Name):
            # Must be a settings constant
            count = ast.parse('%r' % self.world.__dict__[count.id], mode='eval').body

        if iname in escaped_items:
            iname = escaped_items[iname]

        if iname not in item_table:
            self.events.add(iname)

        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='state', ctx=ast.Load()),
                attr='has',
                ctx=ast.Load()),
            args=[ast.Str(iname), count],
            keywords=[])


    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            return node

        if node.func.id in dir(self):
            return getattr(self, node.func.id)(node)

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
            elif not isinstance(child, ast.Str):
                child = self.visit(child)
            new_args.append(child)

        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='state', ctx=ast.Load()),
                attr=node.func.id,
                ctx=ast.Load()),
            args=new_args,
            keywords=node.keywords)

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
        def escape_or_string(n):
            if isinstance(n, ast.Name) and n.id in escaped_items:
                return ast.Str(escaped_items[n.id])
            elif not isinstance(n, ast.Str):
                return self.visit(n)
            return n

        node.left = escape_or_string(node.left)
        node.comparators = list(map(escape_or_string, node.comparators))
        node.ops = list(map(self.visit, node.ops))

        # if all the children are literals now, we can evaluate
        if isliteral(node.left) and all(map(isliteral, node.comparators)):
            # either we turn the ops into operator functions to apply (lots of work),
            # or we compile, eval, and reparse the result
            res = eval(compile(ast.Expression(node), '<string>', 'eval'))
            return ast.parse('%r' % res, mode='eval').body
        return node


    def visit_UnaryOp(self, node):
        # visit the children first
        self.generic_visit(node)
        # if all the children are literals now, we can evaluate
        if isliteral(node.operand):
            res = eval(compile(ast.Expression(node), '<string>', 'eval'))
            return ast.parse('%r' % res, mode='eval').body
        return node


    def visit_BinOp(self, node):
        # visit the children first
        self.generic_visit(node)
        # if all the children are literals now, we can evaluate
        if isliteral(node.left) and isliteral(node.right):
            res = eval(compile(ast.Expression(node), '<string>', 'eval'))
            return ast.parse('%r' % res, mode='eval').body
        return node


    def visit_BoolOp(self, node):
        # Everything else must be visited, then can be removed/reduced to.
        # visit the children first
        self.generic_visit(node)

        early_return = isinstance(node.op, ast.Or)
        items = []
        new_values = []
        # if any elt is True(And)/False(Or), we can omit it
        # if any is False(And)/True(Or), the whole node can be replaced with it
        for elt in list(node.values):
            if isinstance(elt, ast.Str):
                items.append(elt.s)
            elif isinstance(elt, ast.Name) and elt.id in escaped_items:
                items.append(escaped_items[elt.id])
            else:
                # It's possible this returns a single item check,
                # but it's already wrapped in a Call.
                elt = self.visit(elt)
                if isinstance(elt, ast.NameConstant):
                    if elt.value == early_return:
                        return elt
                    # else omit it
                else:
                    new_values.append(elt)

        # package up the remaining items and values
        if not items and not new_values:
            # all values were True(And)/False(Or)
            return ast.NameConstant(not early_return)

        if items:
            node.values = [ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr='has_any_of' if early_return else 'has_all_of',
                    ctx=ast.Load()),
                args=[ast.Tuple(tuple(items))],
                keywords=[])] + new_values
        else:
            node.values = new_values
        if len(node.values) == 1:
            return node.values[0]
        return node


    def replace_subrule(self, target, node):
        rule = ast.dump(node, False)
        if rule in self.replaced_rules[target]:
            return self.replaced_rules[target][rule]

        subrule_name = target + ' Subrule %d' % (1 + len(self.replaced_rules[target]))
        # Save the info to be made into a rule later
        self.delayed_rules.append((target, node, subrule_name))
        # Replace the call with a reference to that item
        item_rule = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='state', ctx=ast.Load()),
                attr='has',
                ctx=ast.Load()),
            args=[ast.Str(subrule_name)],
            keywords=[])
        # Cache the subrule for any others in this region
        # (and reserve the item name in the process)
        self.replaced_rules[target][rule] = item_rule
        return item_rule


    # Requires the target regions have been defined in the world.
    def create_delayed_rules(self):
        for region_name, node, subrule_name in self.delayed_rules:
            region = self.world.get_region(region_name)
            event = Location(subrule_name, type='Event', parent=region)
            event.world = self.world

            self.current_spot = event
            # This could, in theory, create further subrules.
            event.access_rule = self.make_access_rule(self.visit(node))
            event.set_rule(event.access_rule)
            region.locations.append(event)

            MakeEventItem(subrule_name, event)
        # Safeguard in case this is called multiple times per world
        self.delayed_rules.clear()


    def make_access_rule(self, body):
        return eval(compile(
            ast.fix_missing_locations(
                ast.Expression(ast.Lambda(
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[ast.arg(arg='state')],
                        defaults=[],
                        kwonlyargs=[],
                        kw_defaults=[]),
                    body=body))),
            '<string>', 'eval'))


    ## Handlers for specific internal functions used in the json logic.

    # at(region_name, rule)
    # Creates an internal event at the remote region and depends on it.
    def at(self, node):
        # Cache this under the target (region) name
        if len(node.args) < 2 or not isinstance(node.args[0], ast.Str):
            raise Exception('Parse Error: invalid at() arguments', self.current_spot.name, ast.dump(node, False))
        return self.replace_subrule(node.args[0].s, node.args[1])


    # here(rule)
    # Creates an internal event in the same region and depends on it.
    def here(self, node):
        if not node.args:
            raise Exception('Parse Error: missing here() argument', self.current_spot.name, ast.parse(node, False))
        return self.replace_subrule(
                self.current_spot.parent_region.name,
                node.args[0])


    def parse_spot_rule(self, spot):
        rule = spot.rule_string.split('#', 1)[0].strip()

        self.current_spot = spot
        rule_ast = ast.parse(rule, mode='eval').body
        spot.access_rule = self.make_access_rule(self.visit(rule_ast))
        spot.set_rule(spot.access_rule)
