#!/usr/bin/env node

/**
 * tools/sync-web-assets.mjs
 * Synchronizes production 3D asset outputs (out/*.glb) into the web interactive viewer public directory.
 * Source: assets/<discipline>/<asset-id>/out/<asset-id>.glb
 * Target: apps/interactive-viewer/public/assets/<asset-id>.glb
 */

import { existsSync, mkdirSync, copyFileSync, statSync, readFileSync, readdirSync } from 'node:fs';
import { resolve, join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT_DIR = resolve(__dirname, '..');

const ASSETS_DIR = join(ROOT_DIR, 'assets');
const TARGET_DIR = join(ROOT_DIR, 'apps', 'interactive-viewer', 'public', 'assets');

const args = process.argv.slice(2);
const isCheckOnly = args.includes('--check');
const isVerbose = args.includes('--verbose');
const isForce = args.includes('--force');

// glTF Binary header magic: 0x46546C67 ('glTF')
const GLTF_MAGIC = 0x46546C67;

function isValidGlb(filePath) {
  try {
    const buffer = readFileSync(filePath);
    if (buffer.length < 12) return false;
    const magic = buffer.readUInt32LE(0);
    return magic === GLTF_MAGIC;
  } catch {
    return false;
  }
}

function findAssetGlbFiles(dir) {
  const glbFiles = [];
  const disciplines = ['biology', 'chemistry', 'physics'];

  for (const disc of disciplines) {
    const discDir = join(dir, disc);
    if (!existsSync(discDir)) continue;

    const assetDirs = readdirSync(discDir, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name);

    for (const assetId of assetDirs) {
      const outDir = join(discDir, assetId, 'out');
      if (!existsSync(outDir)) continue;

      const glbPath = join(outDir, `${assetId}.glb`);
      if (existsSync(glbPath)) {
        glbFiles.push({
          assetId,
          discipline: disc,
          srcPath: glbPath,
          destPath: join(TARGET_DIR, `${assetId}.glb`),
        });
      }
    }
  }

  return glbFiles;
}

function syncAssets() {
  console.log('Synchronizing GLB models to apps/interactive-viewer/public/assets/...');
  if (isForce) {
    console.log('Force mode enabled: all assets will be synchronized unconditionally.');
  }

  if (!existsSync(TARGET_DIR)) {
    if (!isCheckOnly) {
      mkdirSync(TARGET_DIR, { recursive: true });
    } else {
      console.error(`Target directory does not exist: ${TARGET_DIR}`);
      process.exit(1);
    }
  }

  const assets = findAssetGlbFiles(ASSETS_DIR);
  let copied = 0;
  let upToDate = 0;
  let invalid = 0;
  let errors = 0;

  for (const { assetId, srcPath, destPath } of assets) {
    if (!isValidGlb(srcPath)) {
      console.warn(`[WARN] Invalid GLB binary header: ${srcPath}`);
      invalid++;
      continue;
    }

    let needsCopy = true;
    if (!isForce && existsSync(destPath)) {
      const srcStat = statSync(srcPath);
      const destStat = statSync(destPath);
      if (srcStat.size === destStat.size) {
        // When byte counts match, verify modification time and buffer content equality
        if (srcStat.mtimeMs > destStat.mtimeMs) {
          needsCopy = true;
        } else {
          const srcBuf = readFileSync(srcPath);
          const destBuf = readFileSync(destPath);
          if (srcBuf.equals(destBuf)) {
            needsCopy = false;
            upToDate++;
            if (isVerbose) {
              console.log(`  [OK] ${assetId}.glb (up to date, ${srcStat.size} bytes)`);
            }
          } else {
            needsCopy = true;
          }
        }
      } else {
        needsCopy = true;
      }
    }

    if (needsCopy) {
      if (!isCheckOnly) {
        try {
          copyFileSync(srcPath, destPath);
          copied++;
          if (isVerbose) {
            console.log(`  [SYNC] Copied ${assetId}.glb to target`);
          }
        } catch (err) {
          console.error(`  [ERROR] Failed to copy ${assetId}.glb: ${err.message}`);
          errors++;
        }
      } else {
        copied++;
        if (isVerbose) {
          console.log(`  [DRIFT] ${assetId}.glb differs in target`);
        }
      }
    }
  }

  console.log('------------------------------------------------------------');
  console.log(`Summary: Total found: ${assets.length} | Synced: ${copied} | Up-to-date: ${upToDate} | Invalid: ${invalid} | Errors: ${errors}`);
  console.log('------------------------------------------------------------');

  if (errors > 0 || invalid > 0) {
    process.exit(1);
  }
}

syncAssets();
