from __future__ import annotations
import ast
import logging
import re
from collections import defaultdict
from typing import TYPE_CHECKING, Optional, Any

from Entrance import Entrance
from Item import ItemInfo, Item, make_event_item
from Location import Location
from Region import TimeOfDay
from RulesCommon import AccessRule, allowed_globals, escape_name
from State import State
from Utils import data_path, read_logic_file

if TYPE_CHECKING:
    from World import World

escaped_items: dict[str, str] = {}
for item in ItemInfo.items:
    escaped_items[escape_name(item)] = item

event_name: re.Pattern[str] = re.compile(r'[A-Z]\w+')
# All generated lambdas must accept these keyword args!
# For evaluation at a certain age (required as all rules are evaluated at a specific age)
# or at a certain spot (can be omitted in many cases)
# or at a specific time of day (often unused)
kwarg_defaults: dict[str, Any] = {
    'age': None,
    'spot': None,
    'tod': TimeOfDay.NONE,
}

special_globals: dict[str, Any] = {'TimeOfDay': TimeOfDay}
allowed_globals.update(special_globals)

rule_aliases: dict[str, tuple[list[re.Pattern[str]], str]] = {}
nonaliases: set[str] = set()


def load_aliases() -> None:
    j = read_logic_file(data_path('LogicHelpers.json'))
    for s, repl in j.items():
        if '(' in s:
            rule, args = s[:-1].split('(', 1)
            args = [re.compile(fr'\b{a.strip()}\b') for a in args.split(',')]
        else:
            rule = s
            args = []
        rule_aliases[rule] = (args, repl)
    nonaliases.update(escaped_items.keys())
    nonaliases.difference_update(rule_aliases.keys())


def isliteral(expr: ast.expr) -> bool:
    return isinstance(expr, ast.Constant)


class Rule_AST_Transformer(ast.NodeTransformer):
    def __init__(self, world: World) -> None:
        self.world: World = world
        self.current_spot: Optional[Location | Entrance] = None
        self.events: set[str] = set()
        # map Region -> rule ast string -> item name
        self.replaced_rules: dict[str, dict[str, ast.Call]] = defaultdict(dict)
        # delayed rules need to keep: region name, ast node, event name
        self.delayed_rules: list[tuple[str, ast.AST, str]] = []
        # lazy load aliases
        if not rule_aliases:
            load_aliases()
        # final rule cache
        self.rule_cache: dict[str, AccessRule] = {}

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id in dir(self):
            return getattr(self, node.id)(node)
        elif node.id in rule_aliases:
            args, repl = rule_aliases[node.id]
            if args:
                raise Exception(f'Parse Error: expected {len(args):d} args for {node.id}, not 0',
                                self.current_spot, ast.dump(node, False))
            return self.visit(ast.parse(repl, mode='eval').body)
        elif node.id in escaped_items:
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr='has',
                    ctx=ast.Load()),
                args=[node],
                keywords=[])
        elif node.id in self.world.__dict__:
            return ast.parse('%r' % self.world.__dict__[node.id], mode='eval').body
        elif node.id in self.world.settings.settings_dict:
            # Settings are constant
            return ast.parse('%r' % self.world.settings.settings_dict[node.id], mode='eval').body
        elif node.id in State.__dict__:
            return self.make_call(node, node.id, [], [])
        elif node.id in kwarg_defaults or node.id in special_globals:
            return node
        elif event_name.match(node.id):
            self.events.add(node.id.replace('_', ' '))
            # Ensure the item info is updated properly
            Item(node.id, event=True)
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr='has',
                    ctx=ast.Load()),
                args=[node],
                keywords=[])
        else:
            raise Exception('Parse Error: invalid node name %s' % node.id, self.current_spot, ast.dump(node, False))

    def visit_Str(self, node: ast.Constant) -> Any:
        esc = escape_name(node.value)
        if esc not in ItemInfo.solver_ids:
            self.events.add(esc.replace('_', ' '))
            Item(esc, event=True)
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='state', ctx=ast.Load()),
                attr='has',
                ctx=ast.Load()),
            args=[ast.Name(id=escape_name(node.value), ctx=ast.Load())],
            keywords=[])

    # python 3.8 compatibility: ast walking now uses visit_Constant for Constant subclasses
    # this includes Num, Str, NameConstant, Bytes, and Ellipsis. We only handle Str.
    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, str):
            return self.visit_Str(node)
        return node

    def visit_Tuple(self, node: ast.Tuple) -> Any:
        if len(node.elts) != 2:
            raise Exception('Parse Error: Tuple must have 2 values', self.current_spot, ast.dump(node, False))

        item, count = node.elts

        if not isinstance(item, ast.Name) and not (isinstance(item, ast.Constant) and isinstance(item.value, str)):
            raise Exception('Parse Error: first value must be an item. Got %s' % item.__class__.__name__, self.current_spot.name, ast.dump(node, False))
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            item = ast.Name(id=escape_name(item.value), ctx=ast.Load())

        if not (isinstance(count, ast.Name) or (isinstance(count, ast.Constant) and isinstance(count.value, int))):
            raise Exception('Parse Error: second value must be a number. Got %s' % item.__class__.__name__, self.current_spot.name, ast.dump(node, False))

        if isinstance(count, ast.Name):
            # Must be a settings constant
            count = ast.parse('%r' % self.world.settings.settings_dict[count.id], mode='eval').body

        if item.id not in ItemInfo.solver_ids:
            self.events.add(item.id.replace('_', ' '))

        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='state', ctx=ast.Load()),
                attr='has',
                ctx=ast.Load()),
            args=[item, count],
            keywords=[])

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            return node

        if node.func.id in dir(self):
            return getattr(self, node.func.id)(node)
        elif node.func.id in rule_aliases:
            args, repl = rule_aliases[node.func.id]
            if len(args) != len(node.args):
                raise Exception(f'Parse Error: expected {len(args):d} args for {node.func.id}, not {len(node.args):d}',
                                self.current_spot, ast.dump(node, False))
            # straightforward string manip
            for arg_re, arg_val in zip(args, node.args):
                if isinstance(arg_val, ast.Name):
                    val = arg_val.id
                elif isinstance(arg_val, ast.Constant):
                    val = repr(arg_val.value)
                else:
                    raise Exception('Parse Error: invalid argument %s' % ast.dump(arg_val, False),
                            self.current_spot, ast.dump(node, False))
                repl = arg_re.sub(val, repl)
            return self.visit(ast.parse(repl, mode='eval').body)

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
                elif child.id in self.world.settings.settings_dict:
                    child = ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Name(id='state', ctx=ast.Load()),
                                attr='world',
                                ctx=ast.Load()),
                            attr='settings',
                            ctx=ast.Load()),
                        attr=child.id,
                        ctx=ast.Load())
                elif child.id in rule_aliases:
                    child = self.visit(child)
                elif child.id in escaped_items:
                    logging.getLogger('').debug(f'Call? {node.func.id} with {child.id}')
                    child = ast.Constant(escaped_items[child.id])
                else:
                    logging.getLogger('').debug(f'Call? {node.func.id} with {child.id}')
                    child = ast.Constant(child.id.replace('_', ' '))
            elif not (isinstance(child, ast.Constant) and isinstance(child.value, str)):
                child = self.visit(child)
            new_args.append(child)

        return self.make_call(node, node.func.id, new_args, node.keywords)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        if isinstance(node.value, ast.Name):
            s = node.slice if isinstance(node.slice, ast.Name) else node.slice.value
            return ast.Subscript(
                value=ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id='state', ctx=ast.Load()),
                        attr='world',
                        ctx=ast.Load()),
                    attr=node.value.id,
                    ctx=ast.Load()),
                slice=ast.Index(value=ast.Constant(s.id.replace('_', ' '))),
                ctx=node.ctx)
        else:
            return node

    def visit_Compare(self, node: ast.Compare) -> Any:
        def escape_or_string(n: ast.AST) -> Any:
            if isinstance(n, ast.Name) and n.id in escaped_items:
                return ast.Constant(escaped_items[n.id])
            elif not (isinstance(n, ast.Constant) and isinstance(n.value, str)):
                return self.visit(n)
            return n

        # Fast check for json can_use
        if (len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq)
                and isinstance(node.left, ast.Name) and isinstance(node.comparators[0], ast.Name)
                and node.left.id not in self.world.__dict__ and node.comparators[0].id not in self.world.__dict__
                and node.left.id not in self.world.settings.settings_dict and node.comparators[0].id not in self.world.settings.settings_dict):
            return ast.Constant(node.left.id == node.comparators[0].id)

        node.left = escape_or_string(node.left)
        node.comparators = list(map(escape_or_string, node.comparators))
        node.ops = list(map(self.visit, node.ops))

        # if all the children are literals now, we can evaluate
        if isliteral(node.left) and all(map(isliteral, node.comparators)):
            # either we turn the ops into operator functions to apply (lots of work),
            # or we compile, eval, and reparse the result
            try:
                res = eval(compile(ast.fix_missing_locations(ast.Expression(node)), '<string>', 'eval'))
            except TypeError as e:
                raise Exception('Parse Error: %s' % e, self.current_spot.name, ast.dump(node, False))
            return self.visit(ast.parse('%r' % res, mode='eval').body)
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        # visit the children first
        self.generic_visit(node)
        # if all the children are literals now, we can evaluate
        if isliteral(node.operand):
            res = eval(compile(ast.Expression(node), '<string>', 'eval'))
            return ast.parse('%r' % res, mode='eval').body
        return node

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        # visit the children first
        self.generic_visit(node)
        # if all the children are literals now, we can evaluate
        if isliteral(node.left) and isliteral(node.right):
            res = eval(compile(ast.Expression(node), '<string>', 'eval'))
            return ast.parse('%r' % res, mode='eval').body
        return node

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        # Everything else must be visited, then can be removed/reduced to.
        early_return = isinstance(node.op, ast.Or)
        groupable = 'has_any_of' if early_return else 'has_all_of'
        items = set()
        new_values = []
        # if any elt is True(And)/False(Or), we can omit it
        # if any is False(And)/True(Or), the whole node can be replaced with it
        for elt in list(node.values):
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                items.add(escape_name(elt.value))
            elif (isinstance(elt, ast.Name) and elt.id not in rule_aliases
                    and elt.id not in self.world.__dict__
                    and elt.id not in self.world.settings.settings_dict
                    and elt.id not in dir(self)
                    and elt.id not in State.__dict__):
                items.add(elt.id)
            else:
                # It's possible this returns a single item check,
                # but it's already wrapped in a Call.
                elt = self.visit(elt)
                if isinstance(elt, ast.Constant) and isinstance(elt.value, bool):
                    if elt.value == early_return:
                        return elt
                    # else omit it
                elif (isinstance(elt, ast.Call) and isinstance(elt.func, ast.Attribute)
                        and elt.func.attr in ('has', groupable) and len(elt.args) == 1):
                    args = elt.args[0]
                    if isinstance(args, ast.Constant) and isinstance(args.value, str):
                        items.add(escape_name(args.value))
                    elif isinstance(args, ast.Name):
                        items.add(args.id)
                    else:
                        items.update(it.id for it in args.elts)
                elif isinstance(elt, ast.BoolOp) and node.op.__class__ == elt.op.__class__:
                    new_values.extend(elt.values)
                else:
                    new_values.append(elt)

        # package up the remaining items and values
        if not items and not new_values:
            # all values were True(And)/False(Or)
            return ast.Constant(not early_return)

        if items:
            node.values = [ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='state', ctx=ast.Load()),
                    attr='has_any_of' if early_return else 'has_all_of',
                    ctx=ast.Load()),
                args=[ast.Tuple(elts=[ast.Name(id=i, ctx=ast.Load()) for i in items],
                                ctx=ast.Load())],
                keywords=[])] + new_values
        else:
            node.values = new_values
        if len(node.values) == 1:
            return node.values[0]
        return node

    # Generates an ast.Call invoking the given State function 'name',
    # providing given args and keywords, and adding in additional
    # keyword args from kwarg_defaults (age, etc.)
    def make_call(self, node: ast.AST, name: str, args: list[Any], keywords: list[ast.keyword]) -> ast.Call:
        if not hasattr(State, name):
            raise Exception('Parse Error: No such function State.%s' % name, self.current_spot.name, ast.dump(node, False))

        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='state', ctx=ast.Load()),
                attr=name,
                ctx=ast.Load()),
            args=args,
            keywords=keywords)

    def replace_subrule(self, target: str, node: ast.AST) -> ast.Call:
        rule = ast.dump(node, False)
        if rule in self.replaced_rules[target]:
            return self.replaced_rules[target][rule]

        subrule_name = target + ' Subrule %d' % (1 + len(self.replaced_rules[target]))
        # Ensure the item info is created
        Item(subrule_name, event=True)
        # Save the info to be made into a rule later
        self.delayed_rules.append((target, node, subrule_name))
        # Replace the call with a reference to that item
        item_rule = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='state', ctx=ast.Load()),
                attr='has',
                ctx=ast.Load()),
            args=[ast.Name(id=escape_name(subrule_name), ctx=ast.Load())],
            keywords=[])
        # Cache the subrule for any others in this region
        # (and reserve the item name in the process)
        self.replaced_rules[target][rule] = item_rule
        return item_rule

    # Requires the target regions have been defined in the world.
    def create_delayed_rules(self) -> None:
        for region_name, node, subrule_name in self.delayed_rules:
            region = self.world.get_region(region_name)
            event = Location(subrule_name, location_type='Event', parent=region, internal=True)
            event.world = self.world

            self.current_spot = event
            # This could, in theory, create further subrules.
            access_rule = self.make_access_rule(self.visit(node))
            if access_rule is self.rule_cache.get('NameConstant(False)') or access_rule is self.rule_cache.get('Constant(False)'):
                event.access_rule = None
                event.never = True
                logging.getLogger('').debug('Dropping unreachable delayed event: %s', event.name)
            else:
                if access_rule is self.rule_cache.get('NameConstant(True)') or access_rule is self.rule_cache.get('Constant(True)'):
                    event.always = True
                event.set_rule(access_rule)
                region.locations.append(event)

                make_event_item(subrule_name, event)
        # Safeguard in case this is called multiple times per world
        self.delayed_rules.clear()

    def make_access_rule(self, body: ast.AST) -> AccessRule:
        rule_str = ast.dump(body, False)
        if rule_str not in self.rule_cache:
            # requires consistent iteration on dicts
            kwargs = [ast.arg(arg=k) for k in kwarg_defaults.keys()]
            kwd = list(map(ast.Constant, kwarg_defaults.values()))
            name = f'<{self.current_spot and self.current_spot.name}: {rule_str}>'
            try:
                self.rule_cache[rule_str] = eval(compile(
                    ast.fix_missing_locations(
                        ast.Expression(ast.Lambda(
                            args=ast.arguments(
                                posonlyargs=[],
                                args=[ast.arg(arg='state')],
                                defaults=[],
                                kwonlyargs=kwargs,
                                kw_defaults=kwd),
                            body=body))),
                    name, 'eval'),
                    # globals/locals. if undefined, everything in the namespace *now* would be allowed
                    # Intentionally modifiable so we can add the ItemInfo solver ids as we go
                    allowed_globals)
            except TypeError as e:
                raise Exception('Parse Error: %s' % e, self.current_spot.name, ast.dump(body, False))
        return self.rule_cache[rule_str]

    ## Handlers for specific internal functions used in the json logic.

    # at(region_name, rule)
    # Creates an internal event at the remote region and depends on it.
    def at(self, node: ast.Call) -> ast.Call:
        # Cache this under the target (region) name
        if len(node.args) < 2 or not (isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
            raise Exception('Parse Error: invalid at() arguments', self.current_spot.name, ast.dump(node, False))
        return self.replace_subrule(node.args[0].value, node.args[1])

    # here(rule)
    # Creates an internal event in the same region and depends on it.
    def here(self, node: ast.Call) -> ast.Call:
        if not node.args:
            raise Exception('Parse Error: missing here() argument', self.current_spot.name, ast.dump(node, False))
        return self.replace_subrule(self.current_spot.parent_region.name, node.args[0])

    ## Handlers for compile-time optimizations (former State functions)

    def at_day(self, node: ast.Call) -> ast.expr:
        if self.world.ensure_tod_access:
            # tod has DAY or (tod == NONE and (ss or find a path from a provider))
            # parsing is better than constructing this expression by hand
            return ast.parse("(tod & TimeOfDay.DAY) if tod else ((state.has_all_of((Ocarina, Suns_Song)) and state.has_all_notes_for_song('Suns Song')) or state.search.can_reach(spot.parent_region, age=age, tod=TimeOfDay.DAY))", mode='eval').body
        return ast.Constant(True)

    def at_dampe_time(self, node: ast.Call) -> ast.expr:
        if self.world.ensure_tod_access:
            # tod has DAMPE or (tod == NONE and (find a path from a provider))
            # parsing is better than constructing this expression by hand
            return ast.parse("(tod & TimeOfDay.DAMPE) if tod else state.search.can_reach(spot.parent_region, age=age, tod=TimeOfDay.DAMPE)", mode='eval').body
        return ast.Constant(True)

    def at_night(self, node: ast.Call) -> ast.expr:
        if self.current_spot.type == 'GS Token' and self.world.settings.logic_no_night_tokens_without_suns_song:
            # Using visit here to resolve 'can_play' rule
            return self.visit(ast.parse('can_play(Suns_Song)', mode='eval').body)
        if self.world.ensure_tod_access:
            # tod has DAMPE or (tod == NONE and (ss or find a path from a provider))
            # parsing is better than constructing this expression by hand
            return ast.parse("(tod & TimeOfDay.DAMPE) if tod else ((state.has_all_of((Ocarina, Suns_Song)) and state.has_all_notes_for_song('Suns Song')) or state.search.can_reach(spot.parent_region, age=age, tod=TimeOfDay.DAMPE))", mode='eval').body
        return ast.Constant(True)

    # Parse entry point
    # If spot is None, here() rules won't work.
    def parse_rule(self, rule_string: str, spot: Optional[Location | Entrance] = None) -> AccessRule:
        self.current_spot = spot
        return self.make_access_rule(self.visit(ast.parse(rule_string, mode='eval').body))

    def parse_spot_rule(self, spot: Location | Entrance) -> None:
        rule = spot.rule_string.split('#', 1)[0].strip()

        access_rule = self.parse_rule(rule, spot)
        spot.set_rule(access_rule)
        if access_rule is self.rule_cache.get('NameConstant(False)') or access_rule is self.rule_cache.get('Constant(False)'):
            spot.never = True
        elif access_rule is self.rule_cache.get('NameConstant(True)') or access_rule is self.rule_cache.get('Constant(True)'):
            spot.always = True
