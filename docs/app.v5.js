/* ============================================================
   Colour Generator — web port of UI.py + Pallet_generator.py
   Faithful port of the CustomTkinter desktop app:
     - multiple palettes with prev/next navigation ("Shuffle palettes")
     - add / remove / edit colours, click-to-select
     - gradient interpolation (generate_gradient_colors port)
     - multi-palette interleave ("shuffel" port)
     - square nearest-neighbour preview image (create_color_image port)
     - save colourset as .txt (one hex per line)
   Extras: image import (median cut), dark/light/system appearance,
   autosave to localStorage, export-format options, JSON backup,
   random harmony palettes, clipboard copy, PNG export, share links.
   ============================================================ */

"use strict";

/* ---------------- state ---------------- */
let palettes = [[]];          // colour_parent_array equivalent
let currentPalette = 0;
let selectedIndex = null;     // selected swatch index in current palette
let gradientEnabled = false;
let gradientLen = 10;
let gradientStyle = "balanced";
let shuffleEnabled = false;
let loopEnabled = false;

const settings = {
  autosave: true,
  previewSize: 512,
  contrast: "auto",      // auto | black | white
  lineend: "crlf",       // crlf | lf
  hexcase: "upper",      // upper | lower
  hash: true,            // include "#" prefix in export
  accent: "blue",        // blue | toxic | pink | violet
};

const STORAGE_KEY = "colour-generator-state-v1";

/* ---------------- helpers ---------------- */
const $ = (id) => document.getElementById(id);

function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }

function normaliseHex(hex) {
  let h = String(hex).trim();
  if (h.startsWith("#")) h = h.slice(1);
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  if (!/^[0-9a-fA-F]{6}$/.test(h)) return null;
  return "#" + h.toUpperCase();
}

// Apply the export-format settings (Settings page) to a hex colour.
function formatHex(hex) {
  let h = normaliseHex(hex);
  if (!h) return hex;
  if (settings.hexcase === "lower") h = h.toLowerCase();
  if (!settings.hash) h = h.slice(1);
  return h;
}

function darkenColor(hexColor, factor = 0.7) {
  // Port of ColourFramePallet.darken_color
  const rgb = [1, 3, 5].map((i) => parseInt(hexColor.slice(i, i + 2), 16));
  const darkened = rgb.map((c) => clamp(Math.floor(c * factor), 0, 255));  // floor = Python int() semantics
  return "#" + darkened.map((c) => c.toString(16).padStart(2, "0")).join("").toUpperCase();
}

function luminance(hex) {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function showToast(msg) {
  const holder = $("toast-holder");
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = msg;
  holder.appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    setTimeout(() => el.remove(), 300);
  }, 2600);
}

/* ---------------- persistence & sharing ---------------- */

function persistState() {
  if (!settings.autosave) return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      palettes, currentPalette,
      gradientEnabled, gradientLen, gradientStyle, shuffleEnabled,
      loopEnabled,
      settings,
    }));
  } catch (e) { /* storage full / blocked — ignore */ }
}

function applyRestored(s) {
  if (Array.isArray(s.palettes) && s.palettes.length) palettes = s.palettes;
  currentPalette = clamp(s.currentPalette || 0, 0, palettes.length - 1);
  gradientEnabled = !!s.gradientEnabled;
  gradientLen = clamp(parseInt(s.gradientLen) || 10, 5, 4096);
  gradientStyle = ["balanced", "bright", "dark", "vivid"].includes(s.gradientStyle)
    ? s.gradientStyle : "balanced";
  shuffleEnabled = !!s.shuffleEnabled;
  loopEnabled = !!s.loopEnabled;
  Object.assign(settings, s.settings || {});
  settings.autosave = (s.settings && typeof s.settings.autosave === "boolean")
    ? s.settings.autosave : true;
  selectedIndex = null;
  return true;
}

function loadPersisted() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return false;
    return applyRestored(JSON.parse(raw));
  } catch (e) { return false; }
}

function encodeShareURL() {
  const data = {
    p: palettes, c: currentPalette,
    g: gradientEnabled ? 1 : 0, l: gradientLen, gs: gradientStyle,
    s: shuffleEnabled ? 1 : 0, loop: loopEnabled ? 1 : 0,
  };
  const b64 = btoa(unescape(encodeURIComponent(JSON.stringify(data))));
  return location.origin + location.pathname + "#d=" + b64;
}

function decodeShareURL() {
  if (!location.hash.startsWith("#d=")) return false;
  try {
    const data = JSON.parse(decodeURIComponent(escape(atob(location.hash.slice(3)))));
    applyRestored(data);
    gradientStyle = ["balanced", "bright", "dark", "vivid"].includes(data.gs)
      ? data.gs : "balanced";
    loopEnabled = !!data.loop;
    settings.autosave = true; // sharing shouldn't inherit weird autosave flags
    return "share";
  } catch (e) { return false; }
}

/* ---------------- colour generator ports ---------------- */

// Port of ColorGenerator.generate_gradient_colors(reference_colors, num_colors)
// Interpolates linearly in RGB between consecutive reference colours.
function generateGradientColors(referenceColors, numColors) {
  const numRefs = referenceColors.length;
  const colors = [];
  for (let i = 0; i < numColors; i++) {
    const hue = i / Math.max(1, numColors - 1);
    const refIndex = Math.floor(hue * (numRefs - 1));
    const remainder = hue * (numRefs - 1) - refIndex;
    const c1 = [1, 3, 5].map((j) => parseInt(referenceColors[refIndex].slice(j, j + 2), 16));
    let rgb;
    if (refIndex < numRefs - 1) {
      const c2 = [1, 3, 5].map((j) => parseInt(referenceColors[refIndex + 1].slice(j, j + 2), 16));
      rgb = c1.map((v, j) => Math.floor(v + remainder * (c2[j] - v)));  // floor = Python int() semantics
    } else {
      rgb = c1;
    }
    let color = "#" + rgb.map((v) => v.toString(16).padStart(2, "0")).join("").toUpperCase();
    const transitionAmount = Math.sin(Math.PI * remainder);
    if (gradientStyle !== "balanced" && transitionAmount > 0) {
      const hsv = hexToHsv(color);
      if (gradientStyle === "bright") hsv.v = clamp(hsv.v + 0.16 * transitionAmount, 0, 1);
      if (gradientStyle === "dark") hsv.v = clamp(hsv.v - hsv.v * 0.22 * transitionAmount, 0, 1);
      if (gradientStyle === "vivid") {
        hsv.s = clamp(hsv.s + 0.22 * transitionAmount, 0, 1);
        hsv.v = clamp(hsv.v + 0.04 * transitionAmount, 0, 1);
      }
      color = hsvToHex(hsv.h, hsv.s, hsv.v);
    }
    colors.push(color);
  }
  return colors;
}

// Port of ColorGenerator.shuffel(parent_array):
// interleaves the palettes column-wise (round-robin) into one array.
function shufflePalettes(parentArray) {
  const nonEmpty = parentArray.filter((arr) => arr.length > 0);
  if (nonEmpty.length === 0) return [];
  const maxLength = Math.max(...nonEmpty.map((arr) => arr.length));
  const flattened = nonEmpty.flat();
  const shuffled = [];
  for (let i = 0; i < maxLength; i++) {
    for (let j = i; j < flattened.length; j += maxLength) {
      shuffled.push(flattened[j]);
    }
  }
  return shuffled;
}

// Compute the effective output colour list given current settings
// (mirrors ColourFramePallet.update / save_pallet logic).
function computeOutputColors() {
  let output;
  if (shuffleEnabled) {
    const perPalette = palettes.map((pal) => {
      let arr = pal.slice();
      if (gradientEnabled && arr.length > 0) {
        const len = gradientLen > 5 ? gradientLen : 5;
        arr = generateGradientColors(arr, len);
      }
      return arr;
    });
    output = shufflePalettes(perPalette);
  } else {
    output = palettes[currentPalette].slice();
    if (gradientEnabled && output.length >= 2) {
      const len = gradientLen > 5 ? gradientLen : 5;
      output = generateGradientColors(output, len);
    }
  }
  if (loopEnabled && output.length > 1) output.push(...output.slice().reverse());
  return output;
}

/* ---------------- preview rendering ---------------- */

// Port of create_color_image: arrange colours in a near-square grid,
// scale up with nearest neighbour, center it on the preview canvas.
function updatePreview() {
  const colors = computeOutputColors();
  const canvas = $("preview-canvas");
  const size = settings.previewSize;
  if (canvas.width !== size) { canvas.width = size; canvas.height = size; }
  const ctx = canvas.getContext("2d");

  ctx.clearRect(0, 0, size, size);

  if (colors.length === 0) {
    ctx.fillStyle = getComputedStyle(document.body).getPropertyValue("--panel-2") || "#333";
    ctx.fillRect(0, 0, size, size);
    return;
  }

  let gridSize = Math.floor(Math.sqrt(colors.length));
  if (gridSize * gridSize < colors.length) gridSize++;

  const cell = size / gridSize;
  for (let i = 0; i < colors.length; i++) {
    const x = i % gridSize;
    const y = Math.floor(i / gridSize);
    ctx.fillStyle = colors[i];
    ctx.fillRect(Math.floor(x * cell), Math.floor(y * cell), Math.ceil(cell), Math.ceil(cell));
  }
}

/* ---------------- palette editor UI ---------------- */

function currentArray() { return palettes[currentPalette]; }

function updateNavButtons() {
  const showArrows = shuffleEnabled || palettes.length > 1;
  $("prev-pallet").classList.toggle("hidden", !(showArrows && palettes.length > 1));
  $("next-pallet").classList.toggle("hidden", !shuffleEnabled);
  $("add-palette").classList.toggle("hidden", !showArrows);
  $("palette-title").textContent = `Colour Pallet ${currentPalette + 1}`;
}

function swatchTextColor(hex) {
  if (settings.contrast === "black") return "#000";
  if (settings.contrast === "white") return "#fff";
  return luminance(hex) > 140 ? "#000" : "#fff";
}

function renderSwatches() {
  const list = $("colour-list");
  list.innerHTML = "";
  const arr = currentArray();

  if (arr.length === 0) {
    const hint = document.createElement("div");
    hint.className = "empty-hint";
    hint.textContent = "No colours yet — press “Add” to pick one.";
    list.appendChild(hint);
  }

  arr.forEach((hex, idx) => {
    const row = document.createElement("div");
    row.className = "swatch-row";

    const btn = document.createElement("button");
    btn.className = "swatch" + (idx === selectedIndex ? " selected" : "");
    btn.style.backgroundColor = hex;
    btn.style.setProperty("--glow-color", hex);
    btn.style.color = swatchTextColor(hex);
    btn.textContent = formatHex(hex);
    btn.title = "Click: select · Drag: reorder";
    attachSwatchPointer(btn, row, idx);
    row.appendChild(btn);
    list.appendChild(row);
  });
}

/* ----- drag-to-reorder (LIVE: rows shift while dragging, before drop) ----- */

const DRAG_THRESHOLD = 6; // px before a press becomes a drag

let dragState = null; // { fromIdx, ghost }

function rowsList() {
  return Array.from($("colour-list").querySelectorAll(".swatch-row"));
}

function markDraggedRow() {
  rowsList().forEach((r, i) => r.classList.toggle("dragging", !!dragState && i === dragState.fromIdx));
}

// Other swatches react to the dragged colour: the more similar a
// swatch is, the stronger it glows in the dragged colour.
function applyReactions(dragHex) {
  if (!dragState) return;
  const dr = parseInt(dragHex.slice(1, 3), 16);
  const dg = parseInt(dragHex.slice(3, 5), 16);
  const db = parseInt(dragHex.slice(5, 7), 16);
  rowsList().forEach((r2, i2) => {
    if (dragState && i2 === dragState.fromIdx) return;
    const h2 = currentArray()[i2];
    if (!h2) return;
    const or2 = parseInt(h2.slice(1, 3), 16);
    const og = parseInt(h2.slice(3, 5), 16);
    const ob = parseInt(h2.slice(5, 7), 16);
    const dist = Math.hypot(dr - or2, dg - og, db - ob); // 0..441
    const sim = 1 - dist / 441;                          // 1 = identical
    const sw = r2.querySelector(".swatch");
    sw.classList.add("reacting");
    sw.style.setProperty("--react-color", dragHex);
    sw.style.setProperty("--react-strength", sim.toFixed(3));
  });
}

function clearReactions() {
  rowsList().forEach((r2) => {
    const sw = r2.querySelector(".swatch");
    if (!sw) return;
    sw.classList.remove("reacting");
    sw.style.removeProperty("--react-color");
    sw.style.removeProperty("--react-strength");
  });
}

// Move the dragged colour to toIdx RIGHT NOW and re-render the rows,
// so the others slide away live while you are still holding it.
function liveReorder(toIdx) {
  if (!dragState) return;
  const from = dragState.fromIdx;
  const arrRef = currentArray();
  if (toIdx === from || toIdx < 0 || toIdx >= arrRef.length) return;
  const [moved] = arrRef.splice(from, 1);
  arrRef.splice(toIdx, 0, moved);
  if (selectedIndex === from) selectedIndex = toIdx;
  else if (from < selectedIndex && toIdx >= selectedIndex) selectedIndex--;
  else if (from > selectedIndex && toIdx <= selectedIndex) selectedIndex++;
  dragState.fromIdx = toIdx;
  renderSwatches();          // rebuild rows in the new live order
  markDraggedRow();          // keep the dragged row faded
  applyReactions(moved);     // re-apply similarity glows (render wiped them)
}

function startSwatchDrag(idx, btn, ev) {
  const ghost = btn.cloneNode(true);
  // "selected" gives the ghost the same rounded ::before neon glow
  // (--glow-color is cloned inline). Never use box-shadow here — its
  // halo has square corners and paints over every row it crosses.
  ghost.classList.add("drag-ghost", "selected");
  ghost.style.width = `${btn.offsetWidth}px`;
  ghost.style.height = `${btn.offsetHeight}px`;
  ghost.style.transform = "scale(1.03)";
  document.body.appendChild(ghost);
  // grabbing a swatch selects it immediately → neon glow appears on grab
  selectedIndex = idx;
  dragState = { fromIdx: idx, ghost };
  document.body.classList.add("is-dragging");
  moveSwatchGhost(ev);
  markDraggedRow();
  renderSwatches(); // re-render so the grabbed swatch shows its glow in the list too
  markDraggedRow();
}

function moveSwatchGhost(ev) {
  if (!dragState || !dragState.ghost) return;
  dragState.ghost.style.left = `${ev.clientX - dragState.ghost.offsetWidth / 2}px`;
  dragState.ghost.style.top = `${ev.clientY - dragState.ghost.offsetHeight / 2}px`;
}

function endSwatchDrag() {
  if (!dragState) return;
  if (dragState.ghost) dragState.ghost.remove();
  dragState = null;
  document.body.classList.remove("is-dragging");
  clearReactions();
  refresh(); // final render + preview + persistence
}

function attachSwatchPointer(btn, row, idx) {
  btn.style.touchAction = "none";

  btn.addEventListener("pointerdown", (e) => {
    if (e.button !== 0 || dragState) return;
    e.preventDefault();

    const startX = e.clientX;
    const startY = e.clientY;
    let started = false;

    const onMove = (ev) => {
      if (!started) {
        if (Math.hypot(ev.clientX - startX, ev.clientY - startY) < DRAG_THRESHOLD) return;
        started = true;
        startSwatchDrag(idx, btn, ev);
      }
      moveSwatchGhost(ev);
      applyReactions(currentArray()[dragState.fromIdx]);
      // which row is the pointer over? → reorder live
      const el = document.elementFromPoint(ev.clientX, ev.clientY);
      const targetRow = el ? el.closest(".swatch-row") : null;
      if (!targetRow || !dragState) return;
      const rows = rowsList();
      const j = rows.indexOf(targetRow);
      if (j === -1 || j === dragState.fromIdx) return;
      const rect = targetRow.getBoundingClientRect();
      const below = ev.clientY > rect.top + rect.height / 2;
      const toIdx = (below ? j + 1 : j) - (dragState.fromIdx < j ? 1 : 0);
      liveReorder(toIdx);
    };

    const onUp = () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      window.removeEventListener("pointercancel", onCancel);
      if (!started) {
        // simple click → toggle selection
        selectedIndex = (selectedIndex === idx) ? null : idx;
        refresh();
        return;
      }
      endSwatchDrag();
    };

    const onCancel = () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      window.removeEventListener("pointercancel", onCancel);
      if (started) endSwatchDrag();
    };

    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    window.addEventListener("pointercancel", onCancel);
  });
}

function moveSelected(delta) {
  if (selectedIndex === null) { showToast("Select a colour first (click it)."); return; }
  const arrRef = currentArray();
  const to = selectedIndex + delta;
  if (to < 0 || to >= arrRef.length) return;
  const [c] = arrRef.splice(selectedIndex, 1);
  arrRef.splice(to, 0, c);
  selectedIndex = to;
  refresh();
}

function refresh() {
  updateNavButtons();
  renderSwatches();
  updatePreview();
  persistState();
}

function goPalette(delta) {
  if (delta > 0) {
    // Desktop behaviour: only create a new palette when moving right
    // from the last one and the current one has colours.
    if (currentPalette === palettes.length - 1) {
      if (currentArray().length === 0) return;
      palettes.push([]);
    }
    currentPalette++;
  } else if (delta < 0) {
    if (currentPalette === 0) return;
    // Desktop behaviour: leaving an empty trailing palette removes it.
    if (
      currentPalette === palettes.length - 1 &&
      currentArray().length === 0 &&
      palettes.length > 1
    ) {
      palettes.pop();
    }
    currentPalette--;
  }
  selectedIndex = null;
  refresh();
}

function addNewPaletteSlot() {
  palettes.push([]);
  currentPalette = palettes.length - 1;
  selectedIndex = null;
  refresh();
}

/* ---------------- colour picker dialog (custom) ---------------- */

const picker = {
  h: 0, s: 1, v: 1,
  open: false,
  resolve: null,
  recent: JSON.parse(localStorage.getItem("cg-recent-colours") || "[]"),
};

function hsvToHex(h, s, v) {
  const f = (n) => {
    const k = (n + h / 60) % 6;
    const val = v - v * s * Math.max(0, Math.min(k, 4 - k, 1));
    return Math.round(255 * val);
  };
  return "#" + [f(5), f(3), f(1)].map((x) => x.toString(16).padStart(2, "0")).join("").toUpperCase();
}

function hexToHsv(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
  let h = 0;
  if (d !== 0) {
    if (max === r) h = 60 * (((g - b) / d) % 6);
    else if (max === g) h = 60 * ((b - r) / d + 2);
    else h = 60 * ((r - g) / d + 4);
  }
  if (h < 0) h += 360;
  return { h, s: max === 0 ? 0 : d / max, v: max };
}

function pushRecent(hex) {
  picker.recent = [hex, ...picker.recent.filter((c) => c !== hex)].slice(0, 12);
  localStorage.setItem("cg-recent-colours", JSON.stringify(picker.recent));
}

function renderRecent() {
  const holder = $("presets-recent");
  holder.innerHTML = "";
  picker.recent.forEach((hex) => {
    const chip = document.createElement("button");
    chip.className = "preset-chip";
    chip.style.background = hex;
    chip.title = hex;
    chip.addEventListener("click", () => setPickerFromHex(hex));
    holder.appendChild(chip);
  });
}

function renderPicker() {
  const hex = hsvToHex(picker.h, picker.s, picker.v);
  const area = $("sv-area");
  const thumb = $("sv-thumb");
  const hueThumb = $("hue-thumb");

  area.style.setProperty("--hue-bg", hsvToHex(picker.h, 1, 1));
  thumb.style.left = `${picker.s * 100}%`;
  thumb.style.top = `${(1 - picker.v) * 100}%`;
  thumb.style.background = hex;
  hueThumb.style.left = `${(picker.h / 360) * 100}%`;
  hueThumb.style.background = hsvToHex(picker.h, 1, 1);

  $("picker-preview").style.background = hex;
  if (document.activeElement !== $("picker-hex")) $("picker-hex").value = hex;
  const f = (n) => {
    const k = (n + picker.h / 60) % 6;
    const val = picker.v - picker.v * picker.s * Math.max(0, Math.min(k, 4 - k, 1));
    return Math.round(255 * val);
  };
  if (document.activeElement !== $("picker-r")) $("picker-r").value = f(5);
  if (document.activeElement !== $("picker-g")) $("picker-g").value = f(3);
  if (document.activeElement !== $("picker-b")) $("picker-b").value = f(1);
}

function setPickerFromHex(hex) {
  const norm = normaliseHex(hex);
  if (!norm) return;
  const hsv = hexToHsv(norm);
  picker.h = hsv.h; picker.s = hsv.s; picker.v = hsv.v;
  renderPicker();
}

function bindDrag(el, onMove) {
  const handler = (ev) => {
    const rect = el.getBoundingClientRect();
    const pt = ev.touches ? ev.touches[0] : ev;
    onMove(
      clamp((pt.clientX - rect.left) / rect.width, 0, 1),
      clamp((pt.clientY - rect.top) / rect.height, 0, 1)
    );
  };
  el.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    handler(e);
    const move = (e2) => handler(e2);
    const up = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  });
}

function wirePicker() {
  bindDrag($("sv-area"), (nx, ny) => {
    picker.s = nx;
    picker.v = 1 - ny;
    renderPicker();
  });
  bindDrag($("hue-track"), (nx) => {
    picker.h = nx * 360;
    renderPicker();
  });

  $("picker-hex").addEventListener("input", (e) => {
    const norm = normaliseHex(e.target.value);
    if (norm) setPickerFromHex(norm);
  });
  const rgbInput = (id, idx) => {
    $(id).addEventListener("input", (e) => {
      const v = clamp(parseInt(e.target.value) || 0, 0, 255);
      const rgb = [parseInt($("picker-r").value) || 0, parseInt($("picker-g").value) || 0, parseInt($("picker-b").value) || 0];
      rgb[idx] = v;
      const hex = "#" + rgb.map((c) => clamp(c, 0, 255).toString(16).padStart(2, "0")).join("");
      setPickerFromHex(hex);
    });
  };
  rgbInput("picker-r", 0);
  rgbInput("picker-g", 1);
  rgbInput("picker-b", 2);

  $("picker-cancel").addEventListener("click", closePicker);
  $("picker-ok").addEventListener("click", confirmPicker);
  $("picker-backdrop").addEventListener("click", (e) => {
    if (e.target === $("picker-backdrop")) closePicker();
  });
}

function openPicker(initialHex) {
  setPickerFromHex(initialHex || "#ffffff");
  renderRecent();
  $("picker-backdrop").classList.add("open");
  picker.open = true;
}

function closePicker() {
  $("picker-backdrop").classList.remove("open");
  picker.open = false;
  if (picker.resolve) { picker.resolve(null); picker.resolve = null; }
}

function confirmPicker() {
  const hex = hsvToHex(picker.h, picker.s, picker.v);
  pushRecent(hex);
  $("picker-backdrop").classList.remove("open");
  picker.open = false;
  if (picker.resolve) { picker.resolve(hex); picker.resolve = null; }
}

function pickColor(initial = "#ffffff") {
  return new Promise((resolve) => {
    picker.resolve = resolve;
    openPicker(initial);
  });
}

async function onAddColour() {
  const color = await pickColor(currentArray()[currentArray().length - 1] || "#ffffff");
  if (!color) return;
  currentArray().push(color);
  selectedIndex = currentArray().length - 1;
  refresh();
}

async function onEditColour() {
  if (selectedIndex === null) { showToast("Select a colour first (click it)."); return; }
  const color = await pickColor(currentArray()[selectedIndex]);
  if (!color) return;
  currentArray()[selectedIndex] = color;
  refresh();
}

function onRemoveColour() {
  const arr = currentArray();
  if (arr.length === 0) return;
  if (selectedIndex !== null) arr.splice(selectedIndex, 1);
  else arr.pop(); // desktop behaviour: no selection → remove last
  selectedIndex = null;
  refresh();
}

/* ---------------- random palette generator ---------------- */

const HARMONIES = ["analogous", "complementary", "triadic", "split", "monochrome", "tetradic"];
const HARMONY_OFFSETS = {
  analogous:    [-45, -22, 0, 22, 45],
  complementary:[0, 15, 180, 195, -15],
  triadic:      [0, 120, 240, 10, 130],
  split:        [0, 150, 210, 15, 195],
  monochrome:   [0, 0, 0, 0, 0, 0, 0],
  tetradic:     [0, 90, 180, 270, 45, 315],
};

function hslToHex(h, s, l) {
  h = ((h % 360) + 360) % 360;
  const f = (n) => {
    const k = (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const v = l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1));
    return Math.round(255 * v);
  };
  return "#" + [f(0), f(8), f(4)].map((v) => v.toString(16).padStart(2, "0")).join("").toUpperCase();
}

function generateRandomPalette() {
  const count = 5 + Math.floor(Math.random() * 4); // 5–8 colours
  const baseH = Math.random() * 360;
  const harmony = HARMONIES[Math.floor(Math.random() * HARMONIES.length)];
  const offsets = HARMONY_OFFSETS[harmony];
  const colors = [];
  for (let i = 0; i < count; i++) {
    const h = baseH + offsets[i % offsets.length] + (Math.random() * 16 - 8);
    const s = 0.45 + Math.random() * 0.45;
    const l = harmony === "monochrome"
      ? 0.18 + (i / Math.max(1, count - 1)) * 0.62   // lightness ramp for monochrome
      : 0.28 + Math.random() * 0.5;
    colors.push(hslToHex(h, s, l));
  }
  return colors;
}

function onRandomPalette() {
  const colors = generateRandomPalette();
  palettes[currentPalette] = colors;
  selectedIndex = null;
  refresh();
  showToast("🎲 Random palette generated.");
}

/* ---------------- clipboard / PNG / share ---------------- */

async function onCopyHex() {
  const colors = palettes[currentPalette];
  if (!colors.length) { showToast("Palette is empty."); return; }
  const sep = settings.lineend === "lf" ? "\n" : "\r\n";
  const text = colors.map(formatHex).join(sep);
  try {
    await navigator.clipboard.writeText(text);
    showToast(`📋 Copied ${colors.length} hex codes.`);
  } catch (e) {
    showToast("Clipboard blocked by browser.");
  }
}

function onPngExport() {
  const canvas = $("preview-canvas");
  if (!computeOutputColors().length) { showToast("Nothing to export — add some colours."); return; }
  canvas.toBlob((blob) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `colour-pallet-${currentPalette + 1}-${Date.now()}.png`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast("🖼️ PNG downloaded.");
  });
}

async function onShareLink() {
  const url = encodeShareURL();
  try {
    await navigator.clipboard.writeText(url);
    showToast("🔗 Shareable link copied to clipboard.");
  } catch (e) {
    showToast("Clipboard blocked — link is in the address bar.");
    history.replaceState(null, "", "#" + url.split("#")[1]);
  }
}

/* ---------------- saving ---------------- */

async function saveColorset(colors, name) {
  const sep = settings.lineend === "lf" ? "\n" : "\r\n";
  const text = colors.map(formatHex).join(sep) + sep;

  const blob = new Blob([text], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${name}.txt`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  showToast(`Downloaded ${name}.txt (${colors.length} colours)`);
}

function openCreateModal() {
  const colors = computeOutputColors();
  if (colors.length === 0) { showToast("Nothing to save — add some colours first."); return; }
  $("modal-backdrop").classList.add("open");
  $("modal-name").value = "";
  $("modal-name").focus();
}

async function confirmCreate() {
  const name = ($("modal-name").value || "").trim() || "colorset";
  const colors = computeOutputColors();
  $("modal-backdrop").classList.remove("open");
  await saveColorset(colors, name);
}

/* ---------------- JSON backup ---------------- */

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function exportJSON() {
  const payload = {
    app: "colour-pallet-generator",
    version: 1,
    palettes, currentPalette,
    gradientEnabled, gradientLen, gradientStyle, shuffleEnabled, loopEnabled,
  };
  downloadBlob(
    new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }),
    `colour-palettes-backup-${new Date().toISOString().slice(0, 10)}.json`
  );
  showToast("⬇️ JSON backup downloaded.");
}

function importJSONFile(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result);
      if (!Array.isArray(data.palettes)) throw new Error("no palettes array");
      palettes = data.palettes.map((pal) =>
        Array.isArray(pal)
          ? pal.map((h) => normaliseHex(h) || h).filter(Boolean)
          : []
      );
      if (!palettes.length) palettes = [[]];
      currentPalette = clamp(parseInt(data.currentPalette) || 0, 0, palettes.length - 1);
      gradientEnabled = !!data.gradientEnabled;
      gradientLen = clamp(parseInt(data.gradientLen) || 10, 5, 4096);
      gradientStyle = ["balanced", "bright", "dark", "vivid"].includes(data.gradientStyle)
        ? data.gradientStyle : "balanced";
      shuffleEnabled = !!data.shuffleEnabled;
      loopEnabled = !!data.loopEnabled;
      $("opt-gradient").checked = gradientEnabled;
      $("opt-shuffle").checked = shuffleEnabled;
      $("opt-loop").checked = loopEnabled;
      $("set-loop").checked = loopEnabled;
      $("gradient-style").value = gradientStyle;
      $("set-gradient-style").value = gradientStyle;
      $("grad-len-row").classList.toggle("disabled", !gradientEnabled);
      $("grad-style-row").classList.toggle("disabled", !gradientEnabled);
      selectedIndex = null;
      refresh();
      showToast(`⬆️ Imported ${palettes.length} palettes from JSON.`);
    } catch (e) {
      showToast("Invalid JSON backup file.");
    }
  };
  reader.readAsText(file);
}

/* ---------------- hotkeys modal ---------------- */

function showHotkeys() {
  $("hotkeys-backdrop").classList.add("open");
}
function hideHotkeys() {
  $("hotkeys-backdrop").classList.remove("open");
}

/* ---------------- hotkeys modal wiring (inside wire()) ---------------- */
function debugPrintArray() {
  console.log("palettes:", JSON.stringify(palettes));
  console.log("settings:", JSON.stringify(settings));
  showToast("Printed palettes to browser console (F12)");
}

/* ---------------- appearance mode ---------------- */

const mql = window.matchMedia("(prefers-color-scheme: dark)");

function applyAppearance(mode) {
  let theme = mode;
  if (mode === "system") theme = mql.matches ? "dark" : "light";
  document.body.dataset.theme = theme;
  document.querySelectorAll(".appearance-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.mode === mode);
  });
  localStorage.setItem("cg-appearance", mode);
  updatePreview(); // re-render empty-state fill in new theme
}

mql.addEventListener("change", () => {
  if ((localStorage.getItem("cg-appearance") || "system") === "system") applyAppearance("system");
});

/* ---------------- settings page sync ---------------- */

function syncSettingsUI() {
  $("set-autosave").checked = settings.autosave;
  $("set-preview-size").value = String(settings.previewSize);
  $("set-contrast").value = settings.contrast;
  $("set-accent").value = settings.accent;
  $("set-lineend").value = settings.lineend;
  $("set-hexcase").value = settings.hexcase;
  $("set-hash").checked = settings.hash;
  applyAccent();
}

function applyAccent() {
  if (settings.accent && settings.accent !== "blue") {
    document.body.dataset.accent = settings.accent;
  } else {
    delete document.body.dataset.accent;
  }
}

function applySettingsChange() {
  settings.previewSize = parseInt($("set-preview-size").value) || 512;
  settings.contrast = $("set-contrast").value;
  settings.accent = $("set-accent").value;
  settings.lineend = $("set-lineend").value;
  settings.hexcase = $("set-hexcase").value;
  settings.hash = $("set-hash").checked;
  applyAccent();
  refresh();
}

/* ---------------- wiring ---------------- */

function wire() {
  // navigation
  const frames = { home: $("frame-home"), colours: $("frame-colours"), settings: $("frame-settings") };
  const navBtns = { home: $("btn-home"), colours: $("btn-colours"), settings: $("btn-settings") };
  Object.keys(frames).forEach((name) => {
    navBtns[name].addEventListener("click", () => {
      Object.values(frames).forEach((f) => f.classList.remove("active"));
      Object.values(navBtns).forEach((b) => b.classList.remove("active"));
      frames[name].classList.add("active");
      navBtns[name].classList.add("active");
    });
  });

  // appearance buttons
  document.querySelectorAll(".appearance-btn").forEach((b) => {
    b.addEventListener("click", () => applyAppearance(b.dataset.mode));
  });

  // home extras
  $("clear-all").addEventListener("click", () => {
    palettes = [[]];
    currentPalette = 0;
    selectedIndex = null;
    shuffleEnabled = false;
    gradientEnabled = false;
    $("opt-gradient").checked = false;
    $("opt-shuffle").checked = false;
    gradientStyle = "balanced";
    $("gradient-style").value = gradientStyle;
    $("set-gradient-style").value = gradientStyle;
    loopEnabled = false;
    $("opt-loop").checked = false;
    $("set-loop").checked = false;
    $("grad-len-row").classList.add("disabled");
    refresh();
    showToast("Reset.");
  });

  // palette actions
  $("add-colour").addEventListener("click", onAddColour);
  $("remove-colour").addEventListener("click", onRemoveColour);
  $("edit-colour").addEventListener("click", onEditColour);
  $("prev-pallet").addEventListener("click", () => goPalette(-1));
  $("next-pallet").addEventListener("click", () => goPalette(+1));
  $("add-palette").addEventListener("click", addNewPaletteSlot);

  // palette toolbar extras
  $("random-btn").addEventListener("click", onRandomPalette);
  $("copy-btn").addEventListener("click", onCopyHex);
  $("png-btn").addEventListener("click", onPngExport);
  $("share-btn").addEventListener("click", onShareLink);

  // settings panel (colours frame)
  $("opt-gradient").addEventListener("change", (e) => {
    gradientEnabled = e.target.checked;
    $("grad-len-row").classList.toggle("disabled", !gradientEnabled);
    $("grad-style-row").classList.toggle("disabled", !gradientEnabled);
    refresh();
  });
  $("grad-len").addEventListener("input", (e) => {
    gradientLen = clamp(parseInt(e.target.value) || 10, 5, 4096);
    refresh();
  });
  $("gradient-style").addEventListener("change", (e) => {
    gradientStyle = e.target.value;
    $("set-gradient-style").value = gradientStyle;
    refresh();
  });
  $("opt-shuffle").addEventListener("change", (e) => {
    shuffleEnabled = e.target.checked;
    refresh();
  });
  $("opt-loop").addEventListener("change", (e) => {
    loopEnabled = e.target.checked;
    $("set-loop").checked = loopEnabled;
    refresh();
  });
  // settings page
  $("set-autosave").addEventListener("change", (e) => {
    settings.autosave = e.target.checked;
    if (settings.autosave) persistState();
    else localStorage.removeItem(STORAGE_KEY);
    showToast(settings.autosave ? "Autosave enabled." : "Autosave disabled — data cleared.");
  });
  ["set-preview-size", "set-contrast", "set-accent", "set-lineend", "set-hexcase", "set-hash"].forEach((id) => {
    $(id).addEventListener("change", applySettingsChange);
  });
  $("set-loop").addEventListener("change", (e) => {
    loopEnabled = e.target.checked;
    $("opt-loop").checked = loopEnabled;
    refresh();
  });
  $("set-gradient-style").addEventListener("change", (e) => {
    gradientStyle = e.target.value;
    $("gradient-style").value = gradientStyle;
    refresh();
  });
  $("export-json").addEventListener("click", exportJSON);
  $("import-json").addEventListener("click", () => $("json-file").click());
  $("json-file").addEventListener("change", (e) => {
    const file = e.target.files && e.target.files[0];
    e.target.value = "";
    if (file) importJSONFile(file);
  });
  $("clear-storage").addEventListener("click", () => {
    localStorage.removeItem(STORAGE_KEY);
    palettes = [[]];
    currentPalette = 0;
    selectedIndex = null;
    gradientEnabled = false;
    shuffleEnabled = false;
    gradientLen = 10;
    gradientStyle = "balanced";
    $("opt-gradient").checked = false;
    $("opt-shuffle").checked = false;
    $("gradient-style").value = gradientStyle;
    $("set-gradient-style").value = gradientStyle;
    loopEnabled = false;
    $("opt-loop").checked = false;
    $("set-loop").checked = false;
    $("grad-len-row").classList.add("disabled");
    refresh();
    showToast("Saved data deleted.");
  });

  // create modal
  $("create-btn").addEventListener("click", openCreateModal);
  $("modal-cancel").addEventListener("click", () => $("modal-backdrop").classList.remove("open"));
  $("modal-save").addEventListener("click", confirmCreate);
  $("modal-name").addEventListener("keydown", (e) => {
    if (e.key === "Enter") confirmCreate();
    if (e.key === "Escape") $("modal-backdrop").classList.remove("open");
  });
  $("modal-backdrop").addEventListener("click", (e) => {
    if (e.target === $("modal-backdrop")) $("modal-backdrop").classList.remove("open");
  });

  wirePicker();

  // hotkeys modal
  $("hotkeys-close").addEventListener("click", hideHotkeys);
  $("hotkeys-backdrop").addEventListener("click", (e) => {
    if (e.target === $("hotkeys-backdrop")) hideHotkeys();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && $("hotkeys-backdrop").classList.contains("open")) hideHotkeys();
  });

  // keyboard shortcuts / hotkeys
  document.addEventListener("keydown", (e) => {
    if ($("picker-backdrop").classList.contains("open")) {
      if (e.key === "Escape") closePicker();
      if (e.key === "Enter") confirmPicker();
      return;
    }
    if ($("modal-backdrop").classList.contains("open")) {
      if (e.key === "Escape") $("modal-backdrop").classList.remove("open");
      return;
    }
    const typing = /^(input|textarea|select)$/i.test(document.activeElement.tagName);
    if (typing) return;
    if (e.key === "ArrowLeft" && !$("prev-pallet").classList.contains("hidden")) goPalette(-1);
    if (e.key === "ArrowRight" && shuffleEnabled) goPalette(+1);
    if (e.altKey && e.key === "ArrowUp") { e.preventDefault(); moveSelected(-1); }
    if (e.altKey && e.key === "ArrowDown") { e.preventDefault(); moveSelected(+1); }
    switch (e.key.toLowerCase()) {
      case "a": onAddColour(); break;
      case "e": onEditColour(); break;
      case "d": case "delete": case "backspace": onRemoveColour(); break;
      case "r": onRandomPalette(); break;
      case "c": onCopyHex(); break;
      case "p": onPngExport(); break;
      case "s": openCreateModal(); break;
      case "g":
        gradientEnabled = !gradientEnabled;
        $("opt-gradient").checked = gradientEnabled;
        $("grad-len-row").classList.toggle("disabled", !gradientEnabled);
        $("grad-style-row").classList.toggle("disabled", !gradientEnabled);
        refresh();
        showToast(`Gradient ${gradientEnabled ? "on" : "off"}`);
        break;
      case "m":
        shuffleEnabled = !shuffleEnabled;
        $("opt-shuffle").checked = shuffleEnabled;
        refresh();
        showToast(`Shuffle ${shuffleEnabled ? "on" : "off"}`);
        break;
      case "?": showHotkeys(); break;
      case "escape": break;
      default: return;
    }
    if (e.key !== "Escape" && !e.altKey && !e.ctrlKey && !e.metaKey) e.preventDefault();
  });

  // expose debug helper
  window.debugPrintArray = debugPrintArray;
}

/* ---------------- init ---------------- */
wire();
const restored = decodeShareURL() || loadPersisted();
applyAppearance(localStorage.getItem("cg-appearance") || "system");
$("opt-gradient").checked = gradientEnabled;
$("opt-shuffle").checked = shuffleEnabled;
$("opt-loop").checked = loopEnabled;
$("set-loop").checked = loopEnabled;
$("grad-len-row").classList.toggle("disabled", !gradientEnabled);
$("grad-style-row").classList.toggle("disabled", !gradientEnabled);
$("gradient-style").value = gradientStyle;
$("set-gradient-style").value = gradientStyle;
$("grad-len").value = gradientLen;
syncSettingsUI();
refresh();
if (restored === "share") showToast("Loaded shared palette from link.");
