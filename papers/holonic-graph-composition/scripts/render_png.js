// Rasterise the generated SVG figures for visual review and for paper.yaml's
// raster fallback. Requires @resvg/resvg-js and Inter in ~/.fonts.
//   node render_png.js out.png in.svg [width]
const fs = require('fs');
const path = require('path');
const { Resvg } = require(process.env.RESVG_PATH || '@resvg/resvg-js');

const [out, input, width] = process.argv.slice(2);
const svg = fs.readFileSync(input);
const r = new Resvg(svg, {
  fitTo: { mode: 'width', value: Number(width) || 1600 },
  font: {
    fontDirs: [path.join(process.env.HOME, '.fonts')],
    defaultFontFamily: 'Inter',
    loadSystemFonts: true,
  },
});
fs.writeFileSync(out, r.render().asPng());
