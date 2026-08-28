import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join, dirname, basename, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];
const warnings = [];

const rel = (p) => relative(ROOT, p).split(sep).join("/");
const isStr = (v) => typeof v === "string";
const isBool = (v) => typeof v === "boolean";
const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const isArr = (v) => Array.isArray(v);

function fail(file, msg) {
  errors.push(`${rel(file)}: ${msg}`);
}

function warnFile(file, msg) {
  warnings.push(`${rel(file)}: ${msg}`);
}

function loadJson(file) {
  try {
    return JSON.parse(readFileSync(file, "utf8"));
  } catch (e) {
    fail(file, `invalid JSON (${e.message})`);
    return null;
  }
}

function required(data, keys, file) {
  let ok = true;
  for (const key of keys) {
    if (!(key in data)) {
      fail(file, `missing required field "${key}"`);
      ok = false;
    }
  }
  return ok;
}

function strField(data, key, file, { minLength = 1 } = {}) {
  const value = data[key];
  if (!isStr(value) || value.length < minLength) {
    fail(file, `"${key}" must be a non-empty string`);
    return false;
  }
  return true;
}

function patternField(data, key, regex, file) {
  const value = data[key];
  if (!isStr(value) || !regex.test(value)) {
    fail(file, `"${key}" does not match required pattern ${regex}`);
    return false;
  }
  return true;
}

function enumField(data, key, allowed, file, { optional = false } = {}) {
  const value = data[key];
  if (value === undefined) {
    if (optional) return true;
    fail(file, `missing required field "${key}"`);
    return false;
  }
  if (!allowed.includes(value)) {
    fail(file, `"${key}" must be one of [${allowed.join(", ")}], got "${value}"`);
    return false;
  }
  return true;
}

const ASSET_ID = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const LESSON_ID = /^[a-z0-9]+(-[a-z0-9]+)*(\.[a-z0-9]+(-[a-z0-9]+)*)*$/;
const SEMVER = /^\d+\.\d+\.\d+$/;
const CATEGORIES = ["chemistry", "physics", "biology", "mathematics", "shared"];
const SUBJECTS = ["chemistry", "physics", "biology", "mathematics"];
const ASSET_TYPES = ["prop", "molecular", "diagram"];
const STATUSES = ["draft", "reviewed", "final"];
const LESSON_STATUSES = ["foundation", "draft", "reviewed", "final"];
const PROVENANCE_METHODS = [
  "procedural-blender-python",
  "ai-text-to-3d",
  "manual-authoring",
  "scanned-sourced",
];
const OUTPUT_KINDS = ["blender-scene", "glTF-binary", "preview-render"];
const SUPPORTED_PRIMITIVES = [
  "appear",
  "disappear",
  "cameraMove",
  "showLabel",
  "move",
  "heat",
  "showFlame",
  "burn",
  "collectAsh",
  "transform",
  "showMolecule",
  "showEquation",
];

function numberArray(value, length, file, label) {
  if (!isArr(value) || value.length !== length || !value.every((v) => typeof v === "number")) {
    fail(file, `"${label}" must be an array of ${length} numbers`);
    return false;
  }
  return true;
}

function validateScenePlan(file, assetRegistry) {
  const data = loadJson(file);
  if (!data || !isObj(data)) return;

  if (!required(data, ["id", "lessonId", "fps", "duration", "instances", "timeline"], file)) return;

  patternField(data, "id", ASSET_ID, file);
  strField(data, "lessonId", file);

  if (!Number.isInteger(data.fps) || data.fps < 1) {
    fail(file, '"fps" must be a positive integer');
  }
  if (typeof data.duration !== "number" || data.duration <= 0) {
    fail(file, '"duration" must be a positive number (seconds)');
  }

  const instanceIds = new Set();
  if (!isArr(data.instances)) {
    fail(file, '"instances" must be an array');
  } else {
    for (const [index, instance] of data.instances.entries()) {
      const label = `instances[${index}]`;
      if (!isObj(instance)) {
        fail(file, `${label} must be an object`);
        continue;
      }
      if (!isStr(instance.asset) || !assetRegistry.has(instance.asset)) {
        fail(file, `${label} references unknown asset "${instance.asset}"`);
        continue;
      }
      if (instanceIds.has(instance.asset)) {
        fail(file, `duplicate instance of asset "${instance.asset}" (timeline targets use asset ids)`);
      }
      instanceIds.add(instance.asset);
      if (!("position" in instance)) {
        fail(file, `${label} missing required field "position"`);
      } else {
        numberArray(instance.position, 3, file, `${label}.position`);
      }
      if ("rotationZ" in instance && typeof instance.rotationZ !== "number") {
        fail(file, `${label}.rotationZ must be a number (degrees)`);
      }
    }
  }

  const shotNames = new Set();
  const shots = data.camera && data.camera.shots;
  if (shots !== undefined) {
    if (!isObj(shots)) {
      fail(file, '"camera.shots" must be an object of named shots');
    } else {
      for (const [name, shot] of Object.entries(shots)) {
        shotNames.add(name);
        const label = `camera.shots.${name}`;
        if (!isObj(shot)) {
          fail(file, `${label} must be an object`);
          continue;
        }
        numberArray(shot.position, 3, file, `${label}.position`);
        numberArray(shot.target, 3, file, `${label}.target`);
        if ("lens" in shot && typeof shot.lens !== "number") {
          fail(file, `${label}.lens must be a number (mm)`);
        }
      }
    }
  }

  if (!isArr(data.timeline) || data.timeline.length < 1) {
    fail(file, '"timeline" must be a non-empty array');
    return;
  }

  for (const [index, entry] of data.timeline.entries()) {
    const label = `timeline[${index}]`;
    if (!isObj(entry)) {
      fail(file, `${label} must be an object`);
      continue;
    }
    if (!isStr(entry.primitive) || !SUPPORTED_PRIMITIVES.includes(entry.primitive)) {
      fail(file, `${label}.primitive "${entry.primitive}" is not implemented (supported: ${SUPPORTED_PRIMITIVES.join(", ")})`);
      continue;
    }
    if (typeof entry.start !== "number" || entry.start < 0) {
      fail(file, `${label}.start must be a number >= 0 (seconds)`);
    }
    if ("duration" in entry && (typeof entry.duration !== "number" || entry.duration < 0)) {
      fail(file, `${label}.duration must be a number >= 0`);
    }
    if ("offset" in entry) {
      numberArray(entry.offset, 3, file, `${label}.offset`);
    }
    if ("color" in entry) {
      numberArray(entry.color, 3, file, `${label}.color`);
    }
    if ("strength" in entry && (typeof entry.strength !== "number" || entry.strength < 0)) {
      fail(file, `${label}.strength must be a number >= 0`);
    }

    if (entry.primitive === "showMolecule") {
      if (!isStr(entry.id) || !isStr(entry.model) || !('position' in entry)) {
        fail(file, `${label} (showMolecule) requires id, model, and position`);
      } else {
        instanceIds.add(entry.id);
        numberArray(entry.position, 3, file, `${label}.position`);
      }
    } else if (entry.primitive === "showEquation") {
      if (!isStr(entry.id) || !isStr(entry.text) || !('position' in entry) || typeof entry.end !== "number") {
        fail(file, `${label} (showEquation) requires id, text, position, and end`);
      } else {
        instanceIds.add(entry.id);
        numberArray(entry.position, 3, file, `${label}.position`);
      }
    } else if (entry.primitive === "appear" || entry.primitive === "disappear" || entry.primitive === "move" ||
        entry.primitive === "heat" || entry.primitive === "burn" || entry.primitive === "collectAsh") {
      if (!isStr(entry.target) || !instanceIds.has(entry.target)) {
        fail(file, `${label}.target "${entry.target}" is not an instance in this scene`);
      }
      if (entry.primitive === "move" && !("offset" in entry)) {
        fail(file, `${label} (move) requires "offset"`);
      }
      if (entry.primitive === "collectAsh" && entry.source && (!isStr(entry.source) || !instanceIds.has(entry.source))) {
        fail(file, `${label}.source "${entry.source}" is not an instance in this scene`);
      }
    } else if (entry.primitive === "showFlame") {
      if (!isStr(entry.target) || !instanceIds.has(entry.target)) {
        fail(file, `${label}.target "${entry.target}" is not an instance in this scene`);
      }
    } else if (entry.primitive === "transform") {
      if (!isStr(entry.target) || !instanceIds.has(entry.target)) {
        fail(file, `${label}.target "${entry.target}" is not an instance in this scene`);
      }
      if (!isStr(entry.look) || entry.look.length < 1) {
        fail(file, `${label} (transform) requires a "look" name`);
      }
    } else if (entry.primitive === "cameraMove") {
      if (!isStr(entry.shot) || !shotNames.has(entry.shot)) {
        fail(file, `${label}.shot "${entry.shot}" is not defined in camera.shots`);
      }
    } else if (entry.primitive === "showLabel") {
      if (!isStr(entry.text) || entry.text.length < 1) {
        fail(file, `${label}.text must be a non-empty string`);
      }
      if (!isStr(entry.target) || !instanceIds.has(entry.target)) {
        fail(file, `${label}.target "${entry.target}" is not an instance in this scene`);
      }
      if (typeof entry.end !== "number") {
        fail(file, `${label}.end must be a number (seconds)`);
      }
    }
  }
}

function validateAsset(file, registry) {
  const data = loadJson(file);
  if (!data || !isObj(data)) return;

  if (
    !required(
      data,
      ["id", "name", "category", "version", "semanticDescription", "scaleConvention", "provenance", "rendererCompatibility"],
      file
    )
  )
    return;

  patternField(data, "id", ASSET_ID, file);
  strField(data, "name", file);
  strField(data, "semanticDescription", file);
  enumField(data, "category", CATEGORIES, file);
  enumField(data, "type", ASSET_TYPES, file, { optional: true });
  enumField(data, "status", STATUSES, file, { optional: true });
  patternField(data, "version", SEMVER, file);

  const dirName = basename(dirname(file));
  if (isStr(data.id) && data.id !== dirName) {
    fail(file, `asset id "${data.id}" must match its directory name "${dirName}"`);
  }

  if (registry.has(data.id)) {
    fail(file, `duplicate asset id "${data.id}" (also defined in ${registry.get(data.id)})`);
  } else if (isStr(data.id)) {
    registry.set(data.id, rel(file));
  }

  const scale = data.scaleConvention;
  if (!isObj(scale)) {
    fail(file, '"scaleConvention" must be an object');
  } else {
    strField(scale, "unit", file);
    enumField(scale, "basis", ["real-world-scale", "visualization-scale"], file);
  }

  if ("simplifications" in data && !isArr(data.simplifications)) {
    fail(file, '"simplifications" must be an array of strings');
  }

  const prov = data.provenance;
  if (!isObj(prov)) {
    fail(file, '"provenance" must be an object');
  } else {
    strField(prov, "generator", file);
    enumField(prov, "method", PROVENANCE_METHODS, file);
    const method = prov.method;
    if ((method === "ai-text-to-3d" || method === "scanned-sourced") && !prov.source) {
      fail(file, `"provenance.source" is mandatory for method "${method}"`);
    }
    if ((method === "ai-text-to-3d" || method === "scanned-sourced") && !prov.license) {
      fail(file, `"provenance.license" is mandatory for method "${method}"`);
    }
  }

  const compat = data.rendererCompatibility;
  if (!isObj(compat)) {
    fail(file, '"rendererCompatibility" must be an object');
  } else if (!isBool(compat.blender)) {
    fail(file, '"rendererCompatibility.blender" must be a boolean');
  }

  if ("outputs" in data) {
    if (!isArr(data.outputs)) {
      fail(file, '"outputs" must be an array');
    } else {
      for (const out of data.outputs) {
        if (!isObj(out) || !isStr(out.file) || !out.kind) {
          fail(file, "each outputs[] entry needs \"file\" and \"kind\"");
          continue;
        }
        if (!OUTPUT_KINDS.includes(out.kind)) {
          fail(file, `outputs kind "${out.kind}" must be one of [${OUTPUT_KINDS.join(", ")}]`);
        }
        if (!existsSync(join(dirname(file), out.file))) {
          warnFile(file, `declared output "${out.file}" not found yet (run the build script)`);
        }
      }
    }
  }
}

function validateLesson(file, assetRegistry) {
  const data = loadJson(file);
  if (!data || !isObj(data)) return;

  if (
    !required(
      data,
      ["id", "title", "subject", "grade", "curriculum", "learningObjectives", "scenes"],
      file
    )
  )
    return;

  patternField(data, "id", LESSON_ID, file);
  strField(data, "title", file);
  strField(data, "curriculum", file);
  enumField(data, "subject", SUBJECTS, file);
  enumField(data, "status", LESSON_STATUSES, file, { optional: true });

  if (!Number.isInteger(data.grade) || data.grade < 1 || data.grade > 12) {
    fail(file, '"grade" must be an integer between 1 and 12');
  }

  if (!isArr(data.learningObjectives) || data.learningObjectives.length < 1) {
    fail(file, '"learningObjectives" must be a non-empty array');
  }

  if (!isArr(data.scenes) || data.scenes.length < 1) {
    fail(file, '"scenes" must be a non-empty array');
    return;
  }

  const seenSceneIds = new Set();
  data.scenes.forEach((scene, index) => {
    const label = `scenes[${index}]`;
    if (!isObj(scene)) {
      fail(file, `${label} must be an object`);
      return;
    }
    if (!("id" in scene)) {
      fail(file, `${label} missing required field "id"`);
      return;
    }
    if (!isStr(scene.id) || !ASSET_ID.test(scene.id)) {
      fail(file, `${label}.id must match ${ASSET_ID}`);
      return;
    }
    if (seenSceneIds.has(scene.id)) {
      fail(file, `duplicate scene id "${scene.id}"`);
    }
    seenSceneIds.add(scene.id);

    if (!("purpose" in scene)) {
      fail(file, `${label} ("${scene.id}") missing required field "purpose"`);
    } else if (!isStr(scene.purpose) || scene.purpose.length < 1) {
      fail(file, `${label}.purpose must be a non-empty string`);
    }

    if ("assets" in scene) {
      if (!isArr(scene.assets)) {
        fail(file, `${label}.assets must be an array`);
      } else {
        for (const assetId of scene.assets) {
          if (!assetRegistry.has(assetId)) {
            fail(file, `${label} references unknown asset "${assetId}"`);
          }
        }
      }
    }
  });
}

function validateNarration(file) {
  const data = loadJson(file);
  if (!data) return;

  if (!required(data, ["lessonId", "fps", "totalDurationSeconds", "scenes"], file)) return;
  patternField(data, "lessonId", LESSON_ID, file);

  if (!Number.isInteger(data.fps) || data.fps <= 0) {
    fail(file, '"fps" must be a positive integer');
  }

  if (typeof data.totalDurationSeconds !== "number" || data.totalDurationSeconds <= 0) {
    fail(file, '"totalDurationSeconds" must be a positive number');
  }

  if (!isArr(data.scenes) || data.scenes.length === 0) {
    fail(file, '"scenes" must be a non-empty array');
    return;
  }

  data.scenes.forEach((scene, index) => {
    const label = `scenes[${index}]`;
    if (!isObj(scene)) {
      fail(file, `${label} must be an object`);
      return;
    }
    if (!required(scene, ["id", "startFrame", "endFrame", "cues"], file)) return;
    if (!isArr(scene.cues)) {
      fail(file, `${label}.cues must be an array`);
      return;
    }
    scene.cues.forEach((cue, cueIdx) => {
      const cueLabel = `${label}.cues[${cueIdx}]`;
      if (!required(cue, ["start", "end", "speaker", "text"], file)) return;
      if (typeof cue.start !== "number" || typeof cue.end !== "number" || cue.start >= cue.end) {
        fail(file, `${cueLabel} invalid start/end timestamps`);
      }
      strField(cue, "speaker", file);
      strField(cue, "text", file);
    });
  });
}

function walk(dir, predicate, acc = []) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name === "out") continue;
    const full = join(dir, entry.name);
    if (entry.isDirectory()) walk(full, predicate, acc);
    else if (predicate(entry.name)) acc.push(full);
  }
  return acc;
}

const assetRegistry = new Map();

const assetFiles = walk(join(ROOT, "assets"), (name) => name === "asset.json");
for (const file of assetFiles) validateAsset(file, assetRegistry);

const lessonFiles = walk(join(ROOT, "lessons"), (name) => name === "lesson.json");
for (const file of lessonFiles) validateLesson(file, assetRegistry);

const narrationFiles = walk(join(ROOT, "lessons"), (name) => name === "narration.json");
for (const file of narrationFiles) validateNarration(file);

const sceneFiles = walk(join(ROOT, "lessons"), (name) => name.endsWith(".json") && name !== "lesson.json" && name !== "narration.json");
for (const file of sceneFiles) validateScenePlan(file, assetRegistry);

if (lessonFiles.length === 0) warnFile(ROOT, "no lesson.json files found under lessons/");
if (assetFiles.length === 0) warnFile(ROOT, "no asset.json files found under assets/");

console.log(`Lessons checked   : ${lessonFiles.length}`);
console.log(`Assets checked    : ${assetFiles.length}`);
console.log(`Scene plans       : ${sceneFiles.length}`);
console.log(`Narration scripts : ${narrationFiles.length}`);
console.log(`Asset registry    : ${[...assetRegistry.keys()].join(", ") || "(empty)"}`);

if (warnings.length > 0) {
  console.log(`\nWarnings (${warnings.length}):`);
  for (const w of warnings) console.log(`  ! ${w}`);
}

if (errors.length > 0) {
  console.error(`\nErrors (${errors.length}):`);
  for (const e of errors) console.error(`  x ${e}`);
  process.exit(1);
}

console.log("\nValidation passed.");
