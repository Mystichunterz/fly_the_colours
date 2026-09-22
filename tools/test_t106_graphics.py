"""Read-only T106 regressions. Needs the pinned local providers in evidence.json.

Run: python -B tools/test_t106_graphics.py
Old-source control: python -B tools/test_t106_graphics.py --source-ref b2539b2
Provider roots can be relocated with --provider-roots roots.json ({id: path}).
This checks static contracts only; no game is started and no files are written.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
FTC = 'mod/fly_the_colours.mod'
FILES = ('interface/subuniticons.gfx', 'interface/mapicons.gfx',
         'interface/mapicons.gui', 'interface/unitview.gui')
NEW_SPRITES = ('GFX_unit_hq_armored_car_icon_medium',
               'GFX_unit_hq_armored_car_icon_medium_white')
NEW_PATHS = {
    'interface/mapicons.gui': (
        'unit_counter/active_abilities',
        'construction_info_mapicon/construction_info_window/dam_icon'),
    'interface/unitview.gui': (
        'army_badge_view/pending_leader_icon',
        'army_badge_view/leader_coming',
        'army_badge_view/pending_leader_shown_offset',
        'army_division_list_view/content_window/hq_window/empty_slot/deploy_dropdown/'
        'deploy_button_container_window/deploy_button_no_commander_message'),
}
FRAMES = {'GFX_mapicon_naval_base_large': '11', 'GFX_mapicon_naval_base': '11',
          'GFX_onmap_unit_counter_ideology': '3'}
TOKEN = re.compile(r'\s+|\#[^\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}=#"]+')


@dataclass
class Node:
    key: str
    value: str | list[Node]
    start: int = field(compare=False)
    end: int = field(compare=False)


def parse(text):
    """Parse GUI/GFX blocks and scalar lists; preserve duplicate nodes."""
    tokens = []
    offset = 0
    for match in TOKEN.finditer(text):
        if match.start() != offset:
            raise ValueError(f'Unrecognized syntax at {offset}')
        offset = match.end()
        token = match.group()
        if not token.isspace() and not token.startswith('#'):
            tokens.append((token, match.start(), match.end()))
    if offset != len(text):
        raise ValueError(f'Unrecognized syntax at {offset}')
    cursor = 0

    def sequence(nested=False):
        nonlocal cursor
        nodes = []
        while cursor < len(tokens):
            key, start, _ = tokens[cursor]
            if key == '}':
                if not nested:
                    raise ValueError('Unexpected closing brace')
                cursor += 1
                return nodes
            cursor += 1
            if cursor >= len(tokens) or tokens[cursor][0] != '=':
                if key in ('{', '='):
                    raise ValueError(f'Unexpected token {key}')
                nodes.append(Node('', key.strip('"'), start, tokens[cursor - 1][2]))
                continue
            cursor += 1
            if cursor >= len(tokens):
                raise ValueError(f'Missing value for {key}')
            value = tokens[cursor][0]
            cursor += 1
            if value == '{':
                value = sequence(True)
            elif value in ('}', '='):
                raise ValueError(f'Invalid value for {key}')
            else:
                value = value.strip('"')
            nodes.append(Node(key, value, start, tokens[cursor - 1][2]))
        if nested:
            raise ValueError('Unclosed block')
        return nodes
    return sequence()


def props(node):
    return {child.key.lower(): child.value for child in node.value
            if isinstance(child.value, str)}


def named(nodes, parent=''):
    result = {}
    for node in nodes:
        if isinstance(node.value, list):
            name = props(node).get('name')
            path = '/'.join(filter(None, (parent, name)))
            if name:
                result.setdefault(path, []).append(node)
            for child_path, items in named(node.value, path).items():
                result.setdefault(child_path, []).extend(items)
    return result


def one(tree, path):
    matches = named(tree).get(path, [])
    if len(matches) != 1:
        raise AssertionError(f'{path}: expected one node, got {len(matches)}')
    return matches[0]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_bytes(ref, path):
    return subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{ref}:{path}'])


def read_script(raw):
    return raw.decode('utf-8-sig').replace('\r\n', '\n')


def alpha_boxes(raw, frames):
    """Inclusive ink bounds at alpha >=128 for the pinned legacy BGRA32 atlases."""
    if raw[:4] != b'DDS ' or raw[84:88] != bytes(4):
        raise ValueError('Expected legacy DDS')
    if struct.unpack_from('<5I', raw, 88) != (32, 0xff0000, 0xff00, 0xff, 0xff000000):
        raise ValueError('Expected BGRA32 masks')
    height, width = struct.unpack_from('<II', raw, 12)
    if width % frames or len(raw) != 128 + width * height * 4:
        raise ValueError('Expected an integral single-mip atlas')
    tile = width // frames
    result = []
    for frame in range(frames):
        pixels = [(x, y) for y in range(height) for x in range(tile)
                  if raw[128 + 4 * (y * width + frame * tile + x) + 3] >= 128]
        result.append([min(x for x, y in pixels), min(y for x, y in pixels),
                       max(x for x, y in pixels), max(y for x, y in pixels)] if pixels else None)
    return result


def without_paths(nodes, excluded, parent=''):
    result = []
    for node in nodes:
        value = node.value
        if isinstance(value, list):
            path = '/'.join(filter(None, (parent, props(node).get('name'))))
            if path in excluded:
                continue
            value = without_paths(value, excluded, path)
        result.append(Node(node.key, value, 0, 0))
    return result


class GraphicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads((ROOT / 'integration/t106/evidence.json').read_text())
        cls.roots = {p['id']: Path(p['root']) for p in cls.evidence['providers']}
        if OPTIONS.provider_roots:
            cls.roots.update({k: Path(v) for k, v in
                              json.loads(OPTIONS.provider_roots.read_text()).items()})
        # Validate input coverage explicitly. Missing providers must never mean PASS.
        for provider, root in cls.roots.items():
            if not root.is_dir():
                raise AssertionError(f'Missing provider {provider}: {root}')
        cls.base = cls.evidence['inherited_baseline_commit']
        cls.original = {p: parse(read_script(git_bytes(cls.base, p))) for p in FILES}
        cls.current = {p: parse(read_script(git_bytes(OPTIONS.source_ref, p)
                       if OPTIONS.source_ref else (ROOT / p).read_bytes())) for p in FILES}
        cls.vanilla = {p: parse(read_script((cls.roots['vanilla'] / p).read_bytes()))
                       for p in FILES}

    def resolve(self, relative):
        matches = []
        for provider in self.evidence['providers']:
            root = ROOT if provider['id'] == FTC else self.roots[provider['id']]
            path = root / relative
            if path.is_file():
                matches.append((provider['id'], path))
        self.assertTrue(matches, f'Unresolved texture: {relative}')
        return matches[-1]

    def assert_nodes(self, path):
        for name in NEW_PATHS[path]:
            with self.subTest(node=name):
                self.assertEqual(one(self.current[path], name), one(self.vanilla[path], name))

    def test_01_armored_hq_exact_sprites(self):
        expected = self.evidence['armored_car_hq']
        for name in NEW_SPRITES:
            with self.subTest(sprite=name):
                node = one(self.current[FILES[0]], name)
                self.assertEqual(node.key, 'spriteType')
                self.assertEqual(props(node), {'name': name, 'texturefile': expected[name]['texture'],
                                               'noofframes': '2'})

    def test_02_armored_hq_atlas_geometry(self):
        for name, expected in self.evidence['armored_car_hq'].items():
            with self.subTest(sprite=name):
                sprite = props(one(self.current[FILES[0]], name))
                provider, path = self.resolve(sprite['texturefile'])
                self.assertEqual(provider, expected['provider'])
                raw = path.read_bytes()
                self.assertEqual(raw[:4], b'DDS ')
                height, width = struct.unpack_from('<II', raw, 12)
                self.assertEqual([width, height], expected['dimensions'])
                self.assertEqual([width // int(sprite['noofframes']), height], expected['tile'])
                self.assertEqual(width % int(sprite['noofframes']), 0)
                self.assertEqual(sha(raw), expected['sha256'])

    def test_03_map_gui_nodes(self):
        self.assert_nodes('interface/mapicons.gui')

    def test_04_unit_gui_nodes(self):
        self.assert_nodes('interface/unitview.gui')

    def test_05_naval_frames_match_vanilla(self):
        for name in ('GFX_mapicon_naval_base', 'GFX_mapicon_naval_base_large'):
            with self.subTest(sprite=name):
                current = props(one(self.current[FILES[1]], name))
                base = props(one(self.vanilla[FILES[1]], name))
                self.assertEqual(current['noofframes'], '11')
                self.assertEqual(current, base)
                provider, path = self.resolve(current['texturefile'])
                self.assertEqual(provider, 'vanilla')
                expected = self.evidence['textures'][current['texturefile']]
                self.assertEqual(sha(path.read_bytes()), expected['sha256'])

    def test_06_ideology_three_tile_atlas(self):
        sprite = props(one(self.current[FILES[1]], 'GFX_onmap_unit_counter_ideology'))
        self.assertEqual(sprite['noofframes'], '3')
        provider, path = self.resolve(sprite['texturefile'])
        self.assertEqual(provider, FTC)
        raw = path.read_bytes()
        self.assertEqual(struct.unpack_from('<II', raw, 12), (39, 123))
        self.assertEqual(123 // int(sprite['noofframes']), 41)
        self.assertEqual(sha(raw), self.evidence['textures'][sprite['texturefile']]['sha256'])

    def test_07_unrelated_sprite_mappings_preserved(self):
        for path in FILES[:2]:
            current = without_paths(self.current[path], set(NEW_SPRITES))
            for name in FRAMES:
                matches = named(current).get(name)
                if matches:
                    old = props(one(self.original[path], name))['noofframes']
                    for field_node in matches[0].value:
                        if field_node.key.lower() == 'noofframes':
                            field_node.value = old
            self.assertEqual(current, self.original[path], path)

    def test_08_unrelated_gui_layout_preserved(self):
        for path in FILES[2:]:
            self.assertEqual(without_paths(self.current[path], set(NEW_PATHS[path])),
                             self.original[path], path)

    def test_09_inherited_active_ability_edit(self):
        snapshot = self.evidence['inherited_gui_bytes'].encode('utf-8')
        self.assertEqual(sha(snapshot), self.evidence['live_critical_sha256'][FILES[2]])
        self.assertEqual(parse(read_script(snapshot)), self.original[FILES[2]])
        self.assertEqual(one(self.current[FILES[2]], 'active_ability_item'),
                         one(self.original[FILES[2]], 'active_ability_item'))
        self.assertNotIn('unit_counter/active_ability', named(self.current[FILES[2]]))

    def test_10_motorized_hq_mapping_and_offsets_preserved(self):
        for name in ('GFX_unit_hq_motorized_icon_medium_white', 'GFX_unit_hq_icon_medium_white',
                     'GFX_unit_hq_support_company_icon_medium_white'):
            self.assertEqual(one(self.current[FILES[0]], name), one(self.original[FILES[0]], name))
        for name in ('unit_counter/type', 'unit_counter/unit_counter_hq_x_offset'):
            # Offset location is asserted by its exact observed named path in evidence.
            if name.endswith('unit_counter_hq_x_offset'):
                name = self.evidence['hq_offset_path']
            self.assertEqual(one(self.current[FILES[2]], name), one(self.original[FILES[2]], name))
        for texture in self.evidence['motorized_hq_textures']:
            provider, path = self.resolve(texture['path'])
            self.assertEqual(provider, texture['provider'])
            self.assertEqual(sha(path.read_bytes()), texture['sha256'])

    def test_11_provider_inputs_still_pinned(self):
        sources = self.evidence['t99_source_hashes']
        self.assertEqual(len(sources), 662)
        self.assertEqual(len(self.roots), 14)
        for item in sources:
            with self.subTest(provider=item['provider'], path=item['path']):
                self.assertEqual(sha((self.roots[item['provider']] / item['path']).read_bytes()),
                                 item['sha256'])

    def test_12_new_gui_gfx_references_resolve(self):
        for ref, expected in self.evidence['gui_gfx_references'].items():
            with self.subTest(reference=ref):
                path = self.roots[expected['provider']] / expected['path']
                self.assertEqual(sha(path.read_bytes()), expected['source_sha256'])
                node = one(parse(read_script(path.read_bytes())), ref)
                self.assertEqual(props(node)['texturefile'], expected['texture'])
                provider, texture_path = self.resolve(expected['texture'])
                self.assertEqual(provider, expected['texture_provider'])
                self.assertEqual(sha(texture_path.read_bytes()), expected['texture_sha256'])
        for path, paths in NEW_PATHS.items():
            for name in paths:
                with self.subTest(node=name):
                    node = one(self.current[path], name)
                    for key in ('spritetype', 'quadtexturesprite'):
                        ref = props(node).get(key)
                        if ref:
                            self.assertIn(ref, self.evidence['gui_gfx_references'])

    def test_13_existing_textures_unchanged(self):
        manifest = json.loads((ROOT / 'integration/t106/live-before.json').read_text())
        count = 0
        for path, item in manifest['files'].items():
            if path.startswith('gfx/'):
                self.assertEqual(sha((ROOT / path).read_bytes()), item['sha256'], path)
                count += 1
        self.assertGreater(count, 2800)

    def test_14_all_vanilla_named_gui_paths_covered(self):
        paths = sorted(ROOT.glob('interface/*.gui'))
        compared = 0
        for path in paths:
            rel = path.relative_to(ROOT).as_posix()
            vanilla = self.roots['vanilla'] / rel
            if vanilla.is_file():
                current = self.current.get(rel)
                if current is None:
                    current = parse(read_script(path.read_bytes()))
                missing = set(named(parse(read_script(vanilla.read_bytes())))) - set(named(current))
                self.assertFalse(missing, f'{rel}: {sorted(missing)}')
                compared += 1
        self.assertEqual(compared, 12)

    def test_15_effective_provider_inventory_and_unique_new_sprites(self):
        effective = {}
        for provider in self.evidence['providers']:
            root = ROOT if provider['id'] == FTC else self.roots[provider['id']]
            for path in (root / 'interface').rglob('*'):
                if path.suffix.lower() in ('.gui', '.gfx') and path.is_file():
                    effective[path.relative_to(root).as_posix()] = (provider['id'], path)
        self.assertEqual({p: entry[0] for p, entry in effective.items()},
                         {item['path']: item['provider'] for item in self.evidence['t99_source_hashes']})
        refs = set(NEW_SPRITES) | set(self.evidence['gui_gfx_references'])
        found = {ref: [] for ref in refs}
        for rel, (provider, path) in effective.items():
            if not rel.endswith('.gfx'):
                continue
            text = read_script(git_bytes(OPTIONS.source_ref, rel)
                               if OPTIONS.source_ref and provider == FTC and rel in FILES
                               else path.read_bytes())
            relevant = [ref for ref in refs if ref in text]
            if relevant:
                names = named(parse(text))
                for ref in relevant:
                    found[ref].extend((provider, rel) for _ in names.get(ref, []))
        for ref in NEW_SPRITES:
            with self.subTest(sprite=ref):
                self.assertEqual(found[ref], [(FTC, FILES[0])])
        for ref, expected in self.evidence['gui_gfx_references'].items():
            self.assertEqual(found[ref], [(expected['provider'], expected['path'])])

    def test_16_decoded_alpha_geometry(self):
        for item in self.evidence['motorized_hq_textures']:
            _, path = self.resolve(item['path'])
            original = next(box for box in self.evidence['t99_geometry']
                            if item['path'].endswith('/' + box['name']))
            self.assertEqual(alpha_boxes(path.read_bytes(), 2),
                             [[f['x0'], f['y0'], f['x1'], f['y1']] for f in original['frames']])
        for item in self.evidence['atlas_pixel_checks']:
            _, path = self.resolve(item['path'])
            self.assertEqual(alpha_boxes(path.read_bytes(), item['frames']), item['alpha_boxes'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-ref', help='Read the four changed files from this Git revision')
    parser.add_argument('--provider-roots', type=Path)
    OPTIONS = parser.parse_args()
    unittest.main(argv=[__file__], verbosity=2)
