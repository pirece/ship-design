import fs from 'node:fs/promises';
import {Presentation,PresentationFile,FileBlob} from '@oai/artifact-tool';
const root = 'C:/Users/董昱彤/Desktop/船舶设计/第一次汇报ppt';
const p=await PresentationFile.importPptx(await FileBlob.load(root+'/ppt模板.pptx'));
console.log((await p.inspect({kind:'slide,textbox,shape,image,layout',maxChars:14000})).ndjson);
console.log('slides',p.slides.items.map(s=>s.id));
await (await PresentationFile.exportPptx(p)).save(root+'/editable_ppt_output/.build/template_import.pptx');
