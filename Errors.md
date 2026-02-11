# Error Triage Checklist (from game log)

## ✅ Checklist
- [ ] **DDS mipmap data mismatch** (`gfx_dds_loader.cpp:325`) — textures likely truncated/cis-exported
- [ ] **Missing GUI element** (`containerwindow.cpp:1020`) — `frame_btn` not found in `naval_combat_mapicon`
- [ ] **Undefined GUI_TYPE** (`gui.cpp:931`) — `naval_headquarter_mapicon` missing (warning says this will likely crash)
- [ ] **Failed to create window type** (`gui.cpp:409`) — cannot create `naval_headquarter_mapicon` container window type

---

## Error Summary (grouped)

### 1) DDS mipmap data mismatch (most frequent)
**Type:** `gfx_dds_loader.cpp:325`  
**Message (canonical):** Expected more data in the texture mipmaps than was actually present  
**Files affected (49):**
- [ ] `gfx/interface/army_insignia_selection_bg.dds`
- [ ] `gfx/interface/efficiency_progressbar_bg_max.dds`
- [ ] `gfx/interface/special_project/mapicon_facility_specialization_land.dds`
- [ ] `gfx//interface//division_designer_popup_bg.dds`
- [ ] `gfx//interface//inf_softness_icon.dds`
- [ ] `gfx//interface//equipmentdesigner//ship_designer_popup_bg.dds`
- [ ] `gfx/interface/equipmentdesigner/tanks/tank_designer_popup_bg.dds`
- [ ] `gfx/interface/equipmentdesigner/planes/plane_designer_popup_bg.dds`
- [ ] `gfx/interface/group_name_bg.dds`
- [ ] `gfx/interface/parch_bg.dds`
- [ ] `gfx/interface/naviesview/btn_training.dds`
- [ ] `gfx/interface/naviesview/btn_patrol.dds`
- [ ] `gfx/interface/naviesview/btn_strike_force.dds`
- [ ] `gfx/interface/naviesview/btn_convoy_raid.dds`
- [ ] `gfx/interface/naviesview/btn_convoy_escort.dds`
- [ ] `gfx/interface/naviesview/btn_mines_planting.dds`
- [ ] `gfx/interface/naviesview/btn_mines_sweeping.dds`
- [ ] `gfx/interface/naviesview/btn_invasion.dds`
- [ ] `gfx/interface/naviesview/btn_hold_small.dds`
- [ ] `gfx/interface/mapmode/find_screen_button.dds`
- [ ] `gfx/interface/mapmode/mapmode_main_bg.dds`
- [ ] `gfx//interface//mapmode//mapmode_buttons_deselected_small.dds`
- [ ] `gfx//interface//mapmode//mapmode_buttons_selected_small.dds`
- [ ] `gfx//interface/mapmode/mapmode_button_bg.dds`
- [ ] `gfx/interface/topbar/armyoverview_button.dds`
- [ ] `gfx/interface/topbar/navyoverview_button.dds`
- [ ] `gfx/interface/topbar/airoverview_button.dds`
- [ ] `gfx/interface/topbar/toolbar/topbar_decisionview_button.dds`
- [ ] `gfx/interface/topbar/toolbar/intelligence_button.dds`
- [ ] `gfx/interface/topbar/toolbar/science_button.dds`
- [ ] `gfx/interface/topbar/toolbar/diplomacy_button.dds`
- [ ] `gfx/interface/topbar/toolbar/trade_button.dds`
- [ ] `gfx/interface/topbar/toolbar/construction_button.dds`
- [ ] `gfx/interface/topbar/toolbar/production_button.dds`
- [ ] `gfx/interface/topbar/toolbar/deployment_button.dds`
- [ ] `gfx/interface/topbar/toolbar/ledger_button.dds`
- [ ] `gfx/interface/topbar/toolbar/staff_office_button.dds`
- [ ] `gfx/interface/topbar/toolbar/international_market_button.dds`
- [ ] `gfx/interface/intel_ledger/economy_tab_icon.dds`
- [ ] `gfx/interface/intel_ledger/army_tab_icon.dds`
- [ ] `gfx/interface/intel_ledger/navy_tab_icon.dds`
- [ ] `gfx/interface/intel_ledger/air_tab_icon.dds`
- [ ] `gfx/interface/onmap_unit_counter_land.dds`
- [ ] `gfx/interface/onmap_unit_counter_land_overlay.dds`
- [ ] `gfx/interface/onmap_unit_counter_land_selected.dds`
- [ ] `gfx/interface/special_project/mapicon_facility_specialization_naval.dds`
- [ ] `gfx/interface/naviesview/all_missions.dds`
- [ ] `gfx/interface/naviesview/btn_repair_now.dds`
- [ ] `gfx/interface/naviesview/btn_refit_ship.dds`

**Original full message (one example line):**
- `[07:25:35][no_game_date][gfx_dds_loader.cpp:325]: Expected more data in the texture mipmaps than was actually present in file "gfx/interface/army_insignia_selection_bg.dds"`

---

### 2) Could not find "frame_btn" in window naval_combat_mapicon
**Type:** `containerwindow.cpp:1020`  
**Location reference:** `interface/mapicons.gui (line 1065)`  

**Files / definitions implicated:**
- [ ] `interface/mapicons.gui (line 1065)`

**Original full message (canonical):**
- `[07:27:12][1936.01.01.12][containerwindow.cpp:1020]: interface/mapicons.gui (line 1065 ): Could not find "frame_btn" in window naval_combat_mapicon`

---

### 3) Undefined GUI_TYPE: naval_headquarter_mapicon (likely crash)
**Type:** `gui.cpp:931`  

**GUI type implicated:**
- [ ] `naval_headquarter_mapicon`

**Original full message (canonical):**
- `[07:27:12][1936.01.01.12][gui.cpp:931]: Undefined GUI_TYPE: naval_headquarter_mapicon - This will most likely crash the game`

---

### 4) Failed to create containerWindowType "naval_headquarter_mapicon"
**Type:** `gui.cpp:409`  

**GUI type implicated:**
- [ ] `naval_headquarter_mapicon`

**Original full message (canonical):**
- `[07:27:12][1936.01.01.12][gui.cpp:409]: Error: Failed to create containerWindowType "naval_headquarter_mapicon".`
