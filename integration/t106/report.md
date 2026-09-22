# T106: scoped Fly the Colours graphics candidate

September 22, 2026 — Essex. Implemented in the isolated local checkout
`C:/Users/Calvin/03_Personal_Files/07_Projects/fly-the-colours-t106`, branch
`fix/t106-graphics-compat`. This commit is the review candidate, not a deployment.
Runtime acceptance is **NOT RUN**. The reported motorized-HQ symptom is not claimed fixed.

## Source and preservation

- Diagnostic entry point: T99 `d5f4bc85b8844d72ac5dacd555decd1362fcc738`.
- Live FTC HEAD: `e84640834bb0b6f71ef2f1a73673c4c45a16f02b`.
- Separate inherited-edit commit: `b2539b2b081b958e85fe67b59358fad819c074af`.
  It contains only Calvin's existing `mapicons.gui` active-ability relocation
  (14 additions, 9 deletions). It is not a T106 fix.
- `evidence.json` retains the exact original GUI bytes as a JSON string, SHA-256
  `d1bee5ec19a931bbd50add5c99061b507fa37422572f1a92ccef54bdd2a44d88`.
  The normal Git text conversion records an LF blob with SHA-256
  `7424af32b6a288c023ac0a7edaa42260282b9c94dc438ca884e44b03fa9fc178`.
  This distinction is explicit; the original bytes are recoverable without guessing line endings.
- The user-owned untracked `interface/mapicons.gui.bak-pre-1.19.2-fix` remains in
  the live tree, SHA-256 `15377424d4886d343c97e5c6da56744a8076ef212d725ea13eb813ae4667120a`.
  It is not added to the candidate's interface directory.
- The clone has independent Git objects and no remote. The live repository was
  never cleaned, reset, stashed, staged, committed, or edited.

`live-before.json` inventories all 2,889 live files with hashes, sizes, creation and
modification timestamps, and Windows attributes. `preservation.json` records the
final equality check, including Git HEAD, status, index bytes and dirty diff.
This is a source-preservation check, not a runtime isolation trace. No HOI4 process
was launched; launcher/playsets, saves, Workshop, installed game, NVIDIA and
security settings were not changed.

## Implementation

Only four interface files change after the inherited baseline: 51 additions and
3 deletions. `implementation.patch` is the exact fix-only diff;
`inherited-mapicons.patch` separates Calvin's earlier edit. `manifest.json`
records each changed source file's original and candidate hashes, Git blob IDs,
artifact hashes, and validator provenance.

| File | Scoped change and evidence |
| --- | --- |
| `interface/subuniticons.gfx` | Add exactly `GFX_unit_hq_armored_car_icon_medium` and `GFX_unit_hq_armored_car_icon_medium_white`, both with two frames. Large icon uses the existing vanilla `unit_armored_car_icon.dds` (152×40, 76×40 per tile), matching the ordinary armored-car large mapping. Map icon uses FTC's existing `mpu.unit.Mobile.Cavalry.Armoured.Bn.map.dds` (112×31, 56×31 per tile), consistent with the existing MPU armored-car mapping and eight June HQ remaps. |
| `interface/mapicons.gui` | Add `unit_counter/active_abilities` and `construction_info_mapicon/construction_info_window/dam_icon` under the exact vanilla parents, with vanilla node properties. Preserve the inherited top-level `active_ability_item` and every existing counter position/scale. |
| `interface/unitview.gui` | Add `army_badge_view/pending_leader_icon`, `leader_coming`, `pending_leader_shown_offset`, and the nested HQ deploy button's `deploy_button_no_commander_message`, with their exact current vanilla properties and parents. |
| `interface/mapicons.gfx` | Set `GFX_mapicon_naval_base_large` and `GFX_mapicon_naval_base` to 11 frames, matching their current vanilla declarations and vanilla-owned textures. Set `GFX_onmap_unit_counter_ideology` to 3 frames, matching the existing FTC 123×39 atlas's three 41×39 tiles, as explicitly scoped in T106. |

The full deploy-message path is
`army_division_list_view/content_window/hq_window/empty_slot/deploy_dropdown/deploy_button_container_window/deploy_button_no_commander_message`.
The newly referenced dam, unknown-leader and arrow sprites and their textures
resolve to explicit pinned vanilla files in the recorded FTC II provider stack.
No asset bytes, gameplay files, duplicate-sprite mappings or load-order settings change.

### Geometry findings and limits

The added armored-car HQ map sprite reuses artwork already supplied by FTC.
Its two alpha≥128 ink bounds are `(14,10)..(37,24)` and `(10,8)..(46,28)` within
56×31 frames. At the unchanged ordinary type anchor (-7,-5), these become
`(7,5)..(30,19)` and `(3,3)..(39,23)`. This proves the atlas dimensions and padding
agree with existing MPU conventions; actual HQ positioning remains an engine check.

Re-reading the original motorized, generic-HQ and vanilla motorized DDS data
reproduces T99's alpha bounds exactly. Explicit motorized HQ already uses two
56×31 MPU frames; generic HQ uses two 30×12 frames. The type anchor remains
(-7,-5), and named HQ offset remains (-13,+8). Engine sprite selection, duplicate
precedence and whether offsets combine are still unknown for Calvin's affected
unit. No motorized/HQ resizing, shifting or speculative mapping change is made.

The ideology change follows T106's three-tile declaration requirement. Vanilla
declares four states, and T99 proposed a future four-state atlas. This candidate
does not manufacture a fourth tile or prove how an engine request for a fourth
state behaves. That state is an explicit runtime acceptance item.

The small naval-base texture is 301×29, not evenly divisible by 11; the large is
374×36 (11×34). Both declarations now exactly match vanilla. No texture is cropped
or padded on an unsupported divisibility assumption.

## Static evidence

Run from this checkout:

```powershell
python -B tools/test_t106_graphics.py
python -B tools/test_t106_graphics.py --source-ref b2539b2b081b958e85fe67b59358fad819c074af
```

The first command passes **16 tests**. The second intentionally exits 1 with
**22 failed assertions/subtests** across the expected missing symbols/nodes and
wrong frame declarations. Logs are `tests-after.log` and `tests-before.log`
(line endings and trailing whitespace normalized for storage).
Preservation checks pass on the old source as well.

Tests check exact sprite names/mappings, typed GUI nodes and parents, frame
contracts, DDS geometry and decoded alpha bounds, provider-qualified sprite and
texture hashes, all 662 effective loose interface inputs across vanilla plus
13 enabled mod providers, uniqueness of the new/referenced symbols, all 12
overridden GUI named-path sets, and unchanged existing GFX assets and mappings.
Removing only the intended additions and reverting only the three frame fields
reconstructs the inherited syntax trees exactly. Duplicate ordering is retained.
Missing providers or provider inventory/hash drift fails validation.

The test runner uses Python's standard library; it requires the pinned local
provider contents. `--provider-roots roots.json` can relocate those providers
using an `{ "provider-id": "path" }` map. These tests describe the recorded loose
interface stack, not an exhaustive engine/DLC virtual filesystem or future mod versions.

Existing validators also pass:

- T99 checkout's `integration/validate_mod.py interface --json`: 19 script files,
  zero errors, warnings or informational findings (`validator-interface.json`).
- Existing `_test_gui_parity.ps1`: 258 vanilla names covered in `mapicons.gui`
  and 330 in `unitview.gui` (`gui-parity.log`). Only its hard-coded mod root was
  substituted in a temporary copy; the original script and live mod were untouched.
- `git diff --check` for the source changes and staged candidate: pass.

There is no compile/build target in this GFX/GUI asset repository. Static syntax,
reference and regression checks are complete; they do not substitute for engine validation.

## Later runtime acceptance matrix — all NOT RUN

Requires separately authorized runtime work after the isolation prerequisite is
resolved. Use disposable copied data and record exact candidate/provider pins,
version/checksum, DLC, mod order, display resolution, UI scale and map zoom.

| Case | Required observation | Status |
| --- | --- | --- |
| Baseline, FTC, three-mod stack, full FTC II | Compare each stack separately; identify actual sprite/provider and attributable new GUI/GFX log warnings. | NOT RUN |
| Armored-car HQ | Large template icon and map symbol visible; both symbol modes; automatic/custom template, selected/unselected, stacked/unstacked and representative zooms. No blank/fallback or clipped intended ink. | NOT RUN |
| Original motorized-HQ symptom | Native screenshot plus template/battalion/HQ identity and selected icon; ordinary motorized, infantry HQ and generic HQ controls; establish engine-selected sprite and offset behavior before any geometry fix. | NOT RUN |
| Active abilities | No badge when inactive; one and multiple active badges toggle and fit without unintended collisions; inherited ability-item behavior preserved. | NOT RUN |
| Dam and pending/HQ commander UI | Dam construction icon, pending portrait/arrow and vertically displaced en-route marker appear correctly; missing-commander deploy message fits its container. | NOT RUN |
| Naval bases | All eleven engine-selected states render the intended small and large symbols without wrong slicing. | NOT RUN |
| Ideology | Exercise every requested engine state, including the vanilla fourth state; no out-of-range, wrong-tile or blank behavior. Three correct tile slices alone are insufficient for runtime acceptance. | NOT RUN |
| Protected state | Recheck live dirty files, active playset/settings and saves through the independently approved isolation procedure. | NOT RUN |

Known mip warnings, unrelated sprite duplicates/path quirks, general gameplay,
campaign/save compatibility and the September crash remain outside this patch.
