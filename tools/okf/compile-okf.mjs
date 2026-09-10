import { readdirSync, readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname, basename, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseOkfDocument } from './parser.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '../..');
const KNOWLEDGE_DIR = join(ROOT, 'knowledge');
const MANIFEST_PATH = join(KNOWLEDGE_DIR, 'manifest.json');
const VIEWER_TS_OUT_DIR = join(ROOT, 'apps/interactive-viewer/src/data/generated');
const VIEWER_TS_OUT_FILE = join(VIEWER_TS_OUT_DIR, 'okfKnowledge.ts');
const VIDEO_TS_OUT_DIR = join(ROOT, 'apps/video-composer/src/data/generated');
const VIDEO_TS_OUT_FILE = join(VIDEO_TS_OUT_DIR, 'okfKnowledge.ts');

function walk(dir, acc = []) {
  if (!existsSync(dir)) return acc;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, acc);
    } else if (entry.name.endsWith('.md')) {
      acc.push(full);
    }
  }
  return acc;
}

export function compileOkf() {
  console.log('--- Compiling Open Knowledge Format (OKF v0.2) ---');
  const files = walk(KNOWLEDGE_DIR);
  const concepts = {};
  const edges = [];
  const byType = {};
  const byCategory = {};

  for (const file of files) {
    const raw = readFileSync(file, 'utf8');
    const { frontmatter, body } = parseOkfDocument(raw);
    const id = frontmatter.id || basename(file, '.md');
    const relPath = relative(ROOT, file).replace(/\\/g, '/');

    // Categorize by parent directory under knowledge/
    const pathParts = relPath.split('/');
    const category = pathParts.length > 2 ? pathParts[1] : 'general';

    const concept = {
      id,
      filePath: relPath,
      category,
      type: frontmatter.type || 'concept',
      title: frontmatter.title || id,
      description: frontmatter.description || '',
      status: frontmatter.status || 'active',
      verified: frontmatter.verified || 'unverified',
      timestamp: frontmatter.timestamp || new Date().toISOString(),
      stale_after: frontmatter.stale_after,
      resource: frontmatter.resource,
      tags: frontmatter.tags || [],
      sources: frontmatter.sources || [],
      cbse_mapping: frontmatter.cbse_mapping,
      equations: frontmatter.equations || [],
      misconceptions: frontmatter.misconceptions || [],
      safety: frontmatter.safety || [],
      related_assets: frontmatter.related_assets || [],
      related_lessons: frontmatter.related_lessons || [],
      related_concepts: frontmatter.related_concepts || [],
      body
    };

    concepts[id] = concept;

    // Build Graph Edges
    if (concept.related_concepts) {
      for (const target of concept.related_concepts) {
        edges.push({ source: id, target, kind: 'concept-to-concept' });
      }
    }
    if (concept.related_assets) {
      for (const assetId of concept.related_assets) {
        edges.push({ source: id, target: assetId, kind: 'concept-to-asset' });
      }
    }
    if (concept.related_lessons) {
      for (const lessonId of concept.related_lessons) {
        edges.push({ source: id, target: lessonId, kind: 'concept-to-lesson' });
      }
    }

    // Indexes
    if (!byType[concept.type]) byType[concept.type] = [];
    byType[concept.type].push(id);

    if (!byCategory[category]) byCategory[category] = [];
    byCategory[category].push(id);
  }

  const manifest = {
    schemaVersion: '0.2.0',
    spec: 'https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md',
    generatedAt: new Date().toISOString(),
    totalConcepts: Object.keys(concepts).length,
    totalEdges: edges.length,
    byType,
    byCategory,
    concepts,
    edges
  };

  // 1. Write knowledge/manifest.json
  writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2), 'utf8');
  console.log(`✓ Wrote ${MANIFEST_PATH} (${Object.keys(concepts).length} concepts, ${edges.length} edges)`);

  // 2. Generate TypeScript bindings for interactive-viewer and video-composer
  const tsContent = `/**
 * AUTO-GENERATED FILE by tools/okf/compile-okf.mjs
 * DO NOT EDIT MANUALLY.
 * Generated on: ${manifest.generatedAt}
 */

export type OkfConceptType =
  | 'concept'
  | 'experiment'
  | 'apparatus'
  | 'reaction'
  | 'phenomenon'
  | 'anatomy'
  | 'law'
  | 'curriculum';

export type OkfTrustTier = 'human-reviewed' | 'machine-confirmed' | 'unverified';
export type OkfLifecycleStatus = 'active' | 'draft' | 'reviewed' | 'deprecated';

export interface OkfSourceCitation {
  name: string;
  chapter?: string;
  activity?: string;
  section?: string;
  url?: string;
}

export interface OkfCbseMapping {
  class?: number;
  subject?: 'chemistry' | 'physics' | 'biology' | 'mathematics';
  chapter?: string;
  ncert_activity?: string;
  key_takeaways?: string[];
}

export interface OkfEquation {
  latex: string;
  meaning: string;
  type?: 'chemical' | 'physical' | 'mathematical' | 'biological';
}

export interface OkfMisconception {
  claim: string;
  correction: string;
}

export interface OkfConcept {
  id: string;
  filePath: string;
  category: string;
  type: OkfConceptType;
  title: string;
  description: string;
  status: OkfLifecycleStatus;
  verified: OkfTrustTier;
  timestamp: string;
  stale_after?: string;
  resource?: string;
  tags: string[];
  sources: OkfSourceCitation[];
  cbse_mapping?: OkfCbseMapping;
  equations: OkfEquation[];
  misconceptions: OkfMisconception[];
  safety: string[];
  related_assets: string[];
  related_lessons: string[];
  related_concepts: string[];
  body: string;
}

export interface OkfEdge {
  source: string;
  target: string;
  kind: 'concept-to-concept' | 'concept-to-asset' | 'concept-to-lesson';
}

export interface OkfManifest {
  schemaVersion: string;
  spec: string;
  generatedAt: string;
  totalConcepts: number;
  totalEdges: number;
  byType: Record<string, string[]>;
  byCategory: Record<string, string[]>;
  concepts: Record<string, OkfConcept>;
  edges: OkfEdge[];
}

export const OKF_MANIFEST: OkfManifest = ${JSON.stringify(manifest, null, 2)};

export const OKF_CONCEPTS: Record<string, OkfConcept> = OKF_MANIFEST.concepts;

export function getOkfConcept(id: string): OkfConcept | undefined {
  return OKF_CONCEPTS[id];
}

export function getOkfConceptsByCategory(category: string): OkfConcept[] {
  const ids = OKF_MANIFEST.byCategory[category] || [];
  return ids.map((id) => OKF_CONCEPTS[id]).filter(Boolean);
}

export function getOkfConceptsByType(type: OkfConceptType): OkfConcept[] {
  const ids = OKF_MANIFEST.byType[type] || [];
  return ids.map((id) => OKF_CONCEPTS[id]).filter(Boolean);
}

export function getOkfConceptsForAsset(assetId: string): OkfConcept[] {
  return Object.values(OKF_CONCEPTS).filter(
    (c) => c.related_assets && c.related_assets.includes(assetId)
  );
}

export function getOkfConceptsForLesson(lessonId: string): OkfConcept[] {
  return Object.values(OKF_CONCEPTS).filter(
    (c) => c.related_lessons && c.related_lessons.includes(lessonId)
  );
}
`;

  if (!existsSync(VIEWER_TS_OUT_DIR)) {
    mkdirSync(VIEWER_TS_OUT_DIR, { recursive: true });
  }
  writeFileSync(VIEWER_TS_OUT_FILE, tsContent, 'utf8');
  console.log(`✓ Wrote ${VIEWER_TS_OUT_FILE}`);

  // 3. Generate TypeScript bindings for video-composer
  if (!existsSync(VIDEO_TS_OUT_DIR)) {
    mkdirSync(VIDEO_TS_OUT_DIR, { recursive: true });
  }
  writeFileSync(VIDEO_TS_OUT_FILE, tsContent, 'utf8');
  console.log(`✓ Wrote ${VIDEO_TS_OUT_FILE}`);

  console.log('--- OKF Compilation Complete ---\n');
  return manifest;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  compileOkf();
}
