import { defineConfig, Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'node:path'
import fs from 'node:fs'

import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

function getSharedAssetMap(): Map<string, string> {
  const assetsRoot = path.resolve(__dirname, '../../assets')
  const map = new Map<string, string>()
  if (!fs.existsSync(assetsRoot)) return map

  for (const cat of fs.readdirSync(assetsRoot)) {
    const catDir = path.join(assetsRoot, cat)
    if (fs.statSync(catDir).isDirectory()) {
      for (const item of fs.readdirSync(catDir)) {
        const outDir = path.join(catDir, item, 'out')
        if (fs.existsSync(outDir) && fs.statSync(outDir).isDirectory()) {
          for (const file of fs.readdirSync(outDir)) {
            if (file.endsWith('.glb')) {
              map.set(file, path.join(outDir, file))
            }
          }
        }
      }
    }
  }
  return map
}

function eduAssetsPlugin(): Plugin {
  return {
    name: 'edu-assets-plugin',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url && req.url.startsWith('/assets/') && req.url.endsWith('.glb')) {
          const filename = path.basename(req.url.split('?')[0])
          const assetMap = getSharedAssetMap()
          const filePath = assetMap.get(filename)
          if (filePath && fs.existsSync(filePath)) {
            res.setHeader('Content-Type', 'model/gltf-binary')
            return fs.createReadStream(filePath).pipe(res)
          }
        }
        next()
      })
    },
    closeBundle() {
      const distAssetsDir = path.resolve(__dirname, 'dist/assets')
      const assetMap = getSharedAssetMap()
      if (assetMap.size > 0) {
        fs.mkdirSync(distAssetsDir, { recursive: true })
        for (const [filename, sourcePath] of assetMap.entries()) {
          const target = path.join(distAssetsDir, filename)
          if (!fs.existsSync(target)) {
            fs.copyFileSync(sourcePath, target)
          }
        }
      }
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), eduAssetsPlugin()],
})
