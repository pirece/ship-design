import fs from 'node:fs/promises';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
for (const [file,sheet,range] of [['0003_阻力估算模板.xlsx','HoltropMennen','A1:I20'],['重量重心和浮态调整.xlsx','Weight','A1:J16']]) {
  const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  const png = await wb.render({sheetName:sheet, range, scale:1.5});
  await fs.writeFile(`tmp/${sheet}_原模板.png`,new Uint8Array(await png.arrayBuffer()));
  console.log(file, (await wb.inspect({kind:'sheet',include:'id,name',maxChars:1000})).ndjson);
}
