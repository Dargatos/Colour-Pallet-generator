/* ============================================================
   Colour Generator — web port of UI.py + Pallet_generator.py
   Faithful port of the CustomTkinter desktop app:
     - multiple palettes with prev/next navigation ("Shuffle palettes")
     - add / remove / edit colours, click-to-select
     - gradient interpolation (generate_gradient_colors port)
     - multi-palette interleave ("shuffel" port)
     - square nearest-neighbour preview image (create_color_image port)
     - save colourset as .txt (one hex per line)
   Extras that make sense on the web: image import (median cut),
   dark/light/system appearance, download or save into a picked folder.
   ============================================================ */

"use strict";

/* ---------------- state ---------------- */
let palettes = [[]];          // colour_parent_array equivalent
let currentPalette = 0;
let selectedIndex = null;     // selected swatch index in current palette
let gradientEnabled = false;
let gradientLen = 10;
let shuffleEnabled = false;

const PREVIEW_SIZE = 512;

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
    colors.push("#" + rgb.map((v) => v.toString(16).padStart(2, "0")).join("").toUpperCase());
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
  if (shuffleEnabled) {
    const perPalette = palettes.map((pal) => {
      let arr = pal.slice();
      if (gradientEnabled && arr.length > 0) {
        const len = gradientLen > 5 ? gradientLen : 5;
        arr = generateGradientColors(arr, len);
      }
      return arr;
    });
    return shufflePalettes(perPalette);
  }
  let arr = palettes[currentPalette].slice();
  if (gradientEnabled && arr.length >= 2) {
    const len = gradientLen > 5 ? gradientLen : 5;
    arr = generateGradientColors(arr, len);
  }
  return arr;
}

/* ---------------- preview rendering ---------------- */

// Port of create_color_image: arrange colours in a near-square grid,
// scale up with nearest neighbour, center it on the preview canvas.
function updatePreview() {
  const colors = computeOutputColors();
  const canvas = $("preview-canvas");
  const ctx = canvas.getContext("2d");

  ctx.clearRect(0, 0, PREVIEW_SIZE, PREVIEW_SIZE);

  if (colors.length === 0) {
    ctx.fillStyle = getComputedStyle(document.body).getPropertyValue("--panel-2") || "#333";
    ctx.fillRect(0, 0, PREVIEW_SIZE, PREVIEW_SIZE);
    return;
  }

  let gridSize = Math.floor(Math.sqrt(colors.length));
  if (gridSize * gridSize < colors.length) gridSize++;

  const cell = PREVIEW_SIZE / gridSize;
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
    btn.style.color = luminance(hex) > 140 ? "#000" : "#fff";
    btn.textContent = hex;
    btn.addEventListener("click", () => {
      selectedIndex = (selectedIndex === idx) ? null : idx;
      renderSwatches();
    });

    row.appendChild(btn);
    list.appendChild(row);
  });
}

function refresh() {
  updateNavButtons();
  renderSwatches();
  updatePreview();
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

/* ---------------- colour picker dialog ---------------- */
// Uses the native <input type="color">. If the user cancels, no change
// event fires and the promise resolves with null.

let pickerResolve = null;
const colorInput = $("native-color-input");

colorInput.addEventListener("change", () => {
  if (pickerResolve) { pickerResolve(colorInput.value.toUpperCase()); pickerResolve = null; }
});
window.addEventListener("focus", () => {
  // Cancel path: when window regains focus without a change event.
  setTimeout(() => {
    if (pickerResolve) { pickerResolve(null); pickerResolve = null; }
  }, 250);
}, true);

function pickColor(initial = "#ffffff") {
  return new Promise((resolve) => {
    pickerResolve = resolve;
    colorInput.value = normaliseHex(initial) ? normaliseHex(initial).toLowerCase() : "#ffffff";
    colorInput.click();
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

/* ---------------- image import (extra) ---------------- */

// Extract k dominant colours from an image using median cut + a few
// k-means refinement passes. Returns array of hex strings.
function extractPaletteFromImage(img, k) {
  const S = 128;
  const canvas = document.createElement("canvas");
  canvas.width = S; canvas.height = S;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  ctx.drawImage(img, 0, 0, S, S);
  const data = ctx.getImageData(0, 0, S, S).data;

  const px = [];
  for (let i = 0; i < data.length; i += 4) {
    px.push([data[i], data[i + 1], data[i + 2]]);
  }

  // median cut
  let boxes = [px];
  while (boxes.length < k) {
    boxes.sort((a, b) => boxRange(b) - boxRange(a));
    const box = boxes.shift();
    if (!box || box.length < 2) { if (box) boxes.push(box); break; }
    const ch = largestChannel(box);
    box.sort((a, b) => a[ch] - b[ch]);
    const mid = Math.floor(box.length / 2);
    boxes.push(box.slice(0, mid), box.slice(mid));
  }

  // k-means refinement
  let centroids = boxes.map((b) => avgColor(b)).filter(Boolean);
  for (let iter = 0; iter < 6; iter++) {
    const assign = px.map((p) => {
      let best = 0, bd = Infinity;
      for (let c = 0; c < centroids.length; c++) {
        const d = dist2(p, centroids[c]);
        if (d < bd) { bd = d; best = c; }
      }
      return best;
    });
    const sums = centroids.map(() => [0, 0, 0, 0]);
    for (let i = 0; i < px.length; i++) {
      const s = sums[assign[i]];
      s[0] += px[i][0]; s[1] += px[i][1]; s[2] += px[i][2]; s[3]++;
    }
    centroids = sums.map((s, ci) =>
      s[3] > 0 ? [s[0] / s[3], s[1] / s[3], s[2] / s[3]] : centroids[ci]
    );
  }

  return centroids.map((c) => rgbToHex(c.map(Math.round)));
}

function boxRange(box) {
  const ranges = [0, 1, 2].map((ch) => {
    let min = 255, max = 0;
    for (const p of box) { if (p[ch] < min) min = p[ch]; if (p[ch] > max) max = p[ch]; }
    return max - min;
  });
  return Math.max(...ranges) * box.length;
}
function largestChannel(box) {
  let bestCh = 0, bestR = -1;
  for (const ch of [0, 1, 2]) {
    let min = 255, max = 0;
    for (const p of box) { if (p[ch] < min) min = p[ch]; if (p[ch] > max) max = p[ch]; }
    if (max - min > bestR) { bestR = max - min; bestCh = ch; }
  }
  return bestCh;
}
function avgColor(box) {
  if (!box.length) return null;
  const s = [0, 0, 0];
  for (const p of box) { s[0] += p[0]; s[1] += p[1]; s[2] += p[2]; }
  return s.map((v) => v / box.length);
}
function dist2(a, b) { return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2; }
function rgbToHex(rgb) {
  return "#" + rgb.map((v) => clamp(v, 0, 255).toString(16).padStart(2, "0")).join("").toUpperCase();
}

function onImportImage() {
  $("img-import").onchange = (e) => {
    const file = e.target.files && e.target.files[0];
    e.target.value = "";
    if (!file) return;
    const img = new Image();
    img.onload = () => {
      const k = clamp(parseInt($("k-value").value) || 16, 2, 256);
      const cols = extractPaletteFromImage(img, k);
      palettes.push(cols);
      currentPalette = palettes.length - 1;
      selectedIndex = null;
      refresh();
      showToast(`Imported ${cols.length} colours from image.`);
      URL.revokeObjectURL(img.src);
    };
    img.src = URL.createObjectURL(file);
  };
  $("img-import").click();
}

/* ---------------- saving ---------------- */

let sspDirHandle = null;

$("pick-ssp-dir").addEventListener("click", async () => {
  if (!window.showDirectoryPicker) {
    showToast("Folder access not supported in this browser — use downloads instead.");
    return;
  }
  try {
    sspDirHandle = await window.showDirectoryPicker({ id: "ssp-colorsets" });
    $("ssp-dir-status").textContent = `→ ${sspDirHandle.name}`;
    $("modal-dest").textContent = `${sspDirHandle.name}/ (SoundSpacePlus colorsets)`;
    showToast(`Saving into "${sspDirHandle.name}" until page reloads.`);
  } catch (err) {
    /* user cancelled */
  }
});

async function saveColorset(colors, name) {
  const text = colors.join("\r\n") + "\r\n";

  if (sspDirHandle) {
    const fileName = `${name}.txt`;
    const fh = await sspDirHandle.getFileHandle(fileName, { create: true });
    const w = await fh.createWritable();
    await w.write(text);
    await w.close();
    showToast(`Saved ${fileName} → ${sspDirHandle.name} (${colors.length} colours)`);
    return;
  }

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

/* ---------------- debug (port of Extra/Debug button) ---------------- */
function debugPrintArray() {
  console.log("palettes:", JSON.stringify(palettes));
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

  // settings panel
  $("opt-gradient").addEventListener("change", (e) => {
    gradientEnabled = e.target.checked;
    $("grad-len-row").classList.toggle("disabled", !gradientEnabled);
    refresh();
  });
  $("grad-len").addEventListener("input", (e) => {
    gradientLen = clamp(parseInt(e.target.value) || 10, 5, 4096);
    refresh();
  });
  $("opt-shuffle").addEventListener("change", (e) => {
    shuffleEnabled = e.target.checked;
    refresh();
  });
  $("import-img-btn").addEventListener("click", onImportImage);

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

  // keyboard shortcuts
  document.addEventListener("keydown", (e) => {
    if ($("modal-backdrop").classList.contains("open")) return;
    if (e.key === "ArrowLeft" && !$("prev-pallet").classList.contains("hidden")) goPalette(-1);
    if (e.key === "ArrowRight" && shuffleEnabled) goPalette(+1);
  });

  // expose debug helper
  window.debugPrintArray = debugPrintArray;
}

/* ---------------- init ---------------- */
wire();
applyAppearance(localStorage.getItem("cg-appearance") || "system");
refresh();
