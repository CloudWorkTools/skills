"""Real grammar tests; FLOW_REQUIRE_TREE_SITTER=1 makes parser coverage mandatory."""
import importlib.util
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/flow-docs-sync/scripts'))
from flow_parsers import tree_sitter_hashes

AVAILABLE = importlib.util.find_spec('tree_sitter_language_pack') is not None
if os.environ.get('FLOW_REQUIRE_TREE_SITTER') == '1' and not AVAILABLE:
    raise RuntimeError('Install tree-sitter-language-pack==0.13.0 for required parser tests')

FIXTURES = {
    'javascript': ('function first(x=1){return x+1;} const second=(x)=>x+2;', 'first', 'second', 'x+1', 'x+9'),
    'typescript': ('function first(x:number){return x+1;} const second=(x:number)=>x+2;', 'first', 'second', 'x+1', 'x+9'),
    'tsx': ('const First=()=> <div>Hello world</div>; const Second=()=> <p>Bye</p>;', 'First', 'Second', 'Hello world', 'Hello earth'),
    'go': ('package demo\nfunc first(x int) int{return x+1}\nfunc second() {}', 'first', 'second', 'x+1', 'x+9'),
    'rust': ('fn first(x:i32)->i32{x+1} fn second() {}', 'first', 'second', 'x+1', 'x+9'),
    'java': ('class Demo { int first(int x){return x+1;} void second(){} }', 'Demo.first', 'Demo.second', 'x+1', 'x+9'),
    'csharp': ('class Demo { int First(int x){return x+1;} void Second(){} }', 'Demo.First', 'Demo.Second', 'x+1', 'x+9'),
    'c': ('int first(int x){return x+1;} void second(){}', 'first', 'second', 'x+1', 'x+9'),
    'cpp': ('int Demo::first(int x){return x+1;} void second(){}', 'Demo::first', 'second', 'x+1', 'x+9'),
    'gdscript': ('extends Node\nfunc first(x=1):\n return x+1\nfunc second():\n pass\n', 'first', 'second', 'x+1', 'x+9'),
    'sql': ('CREATE TABLE users (id INT); CREATE TABLE posts (id INT);', 'table.users', 'table.posts', 'id INT', 'id TEXT'),
    'prisma': ('model User {\n id Int @id\n}\nmodel Post {\n id Int @id\n}', 'model.User', 'model.Post', 'id Int', 'id String'),
    'json': ('{"a/b":{"x":1},"second":2}', '/a~1b', '/second', '"x":1', '"x":9'),
}

@unittest.skipUnless(AVAILABLE, 'optional tree-sitter-language-pack is not installed')
class ParserTests(unittest.TestCase):
    def hashes(self, data, language):
        return tree_sitter_hashes(data.encode(), language, 'fixture.' + language)

    def test_all_grammars_isolate_symbol_changes(self):
        for language, (source, first, second, old, new) in FIXTURES.items():
            with self.subTest(language=language):
                context, symbols = self.hashes(source, language)
                changed_context, changed = self.hashes(source.replace(old, new, 1), language)
                self.assertEqual(set(symbols), {first, second})
                self.assertEqual(context, changed_context)
                self.assertNotEqual(symbols[first], changed[first])
                self.assertEqual(symbols[second], changed[second])

    def test_headers_and_globals_change_context(self):
        for source, changed in [
            ('function f(x=1){return x;}', 'function f(x=2){return x;}'),
            ('const global=1; function f(){}', 'const global=2; function f(){}'),
            ('class C extends A { f(){} }', 'class C extends B { f(){} }'),
        ]:
            self.assertNotEqual(self.hashes(source, 'javascript')[0], self.hashes(changed, 'javascript')[0])

    def test_layout_comments_and_literal_content(self):
        original = self.hashes('function f(){return "a b";}', 'javascript')
        self.assertEqual(original, self.hashes('function f ( ) { /* ordinary */ return "a b" ; }', 'javascript'))
        self.assertNotEqual(original, self.hashes('function f(){return "ab";}', 'javascript'))
        self.assertNotEqual(self.hashes('const f=()=>`a b`;', 'javascript'), self.hashes('const f=()=>`ab`;', 'javascript'))

    def test_schema_identity_changes_context(self):
        for language, source, renamed in [
            ('sql', 'CREATE TABLE users (id INT);', 'CREATE TABLE accounts (id INT);'),
            ('prisma', 'model User {\n id Int @id\n}', 'model Account {\n id Int @id\n}'),
            ('json', '{"first":1}', '{"renamed":1}'),
        ]:
            with self.subTest(language=language):
                self.assertNotEqual(self.hashes(source, language)[0], self.hashes(renamed, language)[0])

    def test_sql_comment_statement_is_semantic_context(self):
        source = "CREATE TABLE users (id INT); COMMENT ON TABLE users IS 'first';"
        changed = source.replace("'first'", "'second'")
        self.assertNotEqual(self.hashes(source, 'sql')[0], self.hashes(changed, 'sql')[0])

    def test_ordinary_comments_in_each_grammar(self):
        for language, (source, *_) in FIXTURES.items():
            if language == 'json':
                continue
            comment = '# ordinary prose\n' if language == 'gdscript' else '-- ordinary prose\n' if language == 'sql' else '// ordinary prose\n'
            with self.subTest(language=language):
                self.assertEqual(self.hashes(source, language), self.hashes(comment + source, language))

    def test_directive_comments_retained(self):
        self.assertNotEqual(self.hashes('//go:embed a\npackage p\nfunc f(){}', 'go')[0], self.hashes('//go:embed b\npackage p\nfunc f(){}', 'go')[0])
        self.assertNotEqual(self.hashes('// @ts-ignore\nfunction f(){}', 'typescript')[0], self.hashes('function f(){}', 'typescript')[0])

    def test_qualified_symbols(self):
        cases = [
            ('javascript', 'class C { f(){} }', {'C.f'}),
            ('go', 'package p\nfunc (r *R) F(){}', {'*R.F'}),
            ('rust', 'impl X { fn f(&self) {} } impl T for X { fn f(&self) {} } trait T { fn f(&self); }', {'X::f', 'T for X::f', 'T::f'}),
            ('cpp', 'namespace N { class C { int f(){return 1;} }; }', {'N::C::f'}),
            ('c', 'int (*factory(void))(int) { return 0; }', {'factory'}),
        ]
        for language, source, expected in cases:
            with self.subTest(language=language):
                self.assertEqual(set(self.hashes(source, language)[1]), expected)

    def test_failures_are_actionable(self):
        for language, source, expected in [
            ('unknown', 'x', 'language'),
            ('typescript', 'function f( {', 'parse'),
            ('javascript', 'function f(){} function f(){}', 'duplicate'),
            ('java', 'class C { void f(){} void f(int x){} }', 'duplicate'),
            ('json', '{"x":1,"x":2}', 'duplicate'),
            ('typescript', 'const x=1;', 'kind:file'),
        ]:
            with self.subTest(language=language, source=source):
                with self.assertRaisesRegex(ValueError, expected):
                    self.hashes(source, language)

class DependencyTests(unittest.TestCase):
    def test_missing_optional_dependency_has_install_command(self):
        with patch.dict(sys.modules, {'tree_sitter_language_pack': None}):
            with self.assertRaisesRegex(ValueError, 'tree-sitter-language-pack==0.13.0'):
                tree_sitter_hashes(b'function f(){}', 'javascript', 'fixture.js')

    @unittest.skipUnless(AVAILABLE, 'optional parser is not installed')
    def test_dependency_version_is_pinned(self):
        with patch('flow_parsers.version', return_value='99.0'):
            with self.assertRaisesRegex(ValueError, 'found 99.0'):
                tree_sitter_hashes(b'function f(){}', 'javascript', 'fixture.js')


if __name__ == '__main__':
    unittest.main()
