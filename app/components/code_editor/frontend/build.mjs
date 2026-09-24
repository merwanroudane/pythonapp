// Bundle the editor into one ES module that Python passes to CCv2 as inline JS.
//   npm install && npm run build   ->   ../editor.bundle.js
import { build } from "esbuild"

await build({
  entryPoints: ["src/index.js"],
  bundle: true,
  format: "esm",
  minify: true,
  target: ["es2020"],
  legalComments: "eof",
  // CCv2 treats single-line strings that look like paths as file references; the
  // banner guarantees the bundle is multi-line so it is always read as inline code.
  banner: { js: "// Python Learning Lab code editor — CodeMirror 6 (MIT). Built by build.mjs.\n" },
  outfile: "../editor.bundle.js",
})
console.log("built ../editor.bundle.js")
