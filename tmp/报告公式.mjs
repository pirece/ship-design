import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {mathjax}=require('mathjax-full/js/mathjax.js');
const {TeX}=require('mathjax-full/js/input/tex.js');
const {SVG}=require('mathjax-full/js/output/svg.js');
const {liteAdaptor}=require('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=require('mathjax-full/js/handlers/html.js');
const {AllPackages}=require('mathjax-full/js/input/tex/AllPackages.js');
const sharp=require('sharp');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const document=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'none'})});
const eq={
 scale:String.raw`r=\frac{33500}{43517.7-8650}=0.9607745851,\quad k=r^{1/3}=0.9867500766`,
 weight:String.raw`W=\sum_i W_i,\quad x_G=\frac{\sum_iW_i x_i}{W},\quad z_G=\frac{\sum_iW_i z_i}{W}`,
 resistance:String.raw`R_T=(1+k_1)R_F+R_{APP}+R_W+R_B+R_{TR}+R_A,\quad P_E=R_TV`,
 cf:String.raw`C_F=\frac{0.075}{(\log_{10}Re-2)^2},\quad Re=\frac{VL_{WL}}{\nu},\quad Fn=\frac{V}{\sqrt{gL_{WL}}}`,
 similarity:String.raw`\frac{V_2}{V_1}=r^{1/6}=\sqrt{k},\quad\frac{R_2}{R_1}=r,\quad\frac{P_{E2}}{P_{E1}}=r^{7/6}`,
 speed:String.raw`J=\frac{V(1-w)}{nD},\quad\frac{n_2}{n_1}=\frac{V_2/V_1}{D_2/D_1}=r^{-1/6}`,
 propulsion:String.raw`w=0.5C_B-0.05,\quad t=0.27C_B,\quad\eta_D=\eta_O\eta_R\eta_S\frac{1-t}{1-w}`,
 eedi:String.raw`EEDI_{ref}=961.79\,DWT^{-0.477},\quad EEDI_{req}=(1-X)EEDI_{ref}`,
 attained:String.raw`EEDI=\frac{P_{ME}C_{F,ME}SFC_{ME}+P_{AE}C_{F,AE}SFC_{AE}}{DWT\,V_{ref}}`,
 fuel:String.raw`t=\frac{16000}{14}=1142.857\ \mathrm{h},\quad W_F=\frac{P_{CSR}\,SFC_{CSR}\,t}{10^6}`,
 trim:String.raw`\tau=d_F-d_A=\frac{\Delta(x_G-x_B)}{100MTC},\quad GM=KM-KG-\frac{\sum FSM}{\Delta}`
};
await fs.mkdir('tmp/报告公式',{recursive:true});
for(const[name,latex]of Object.entries(eq)){
 let svg=adaptor.outerHTML(document.convert(latex,{display:true}));svg=svg.slice(svg.indexOf('<svg'),svg.indexOf('</svg>')+6).replace(/currentColor/g,'#000000');
 svg=svg.replace(/(width|height)="([0-9.]+)(ex|em)"/g,(_,a,n)=>`${a}="${Number(n)*8.5}px"`);
 await sharp(Buffer.from(svg),{density:300}).png().toFile(`tmp/报告公式/${name}.png`);
}
