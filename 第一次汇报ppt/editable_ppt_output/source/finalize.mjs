// 执行技能提供的文件完整性、页面几何与重新导入验证。
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const SKILL='C:/Users/董昱彤/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const PY='C:/Users/董昱彤/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES='C:/Users/董昱彤/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const scenes=JSON.parse(await fs.readFile(path.join(root,'source/scenes.json'),'utf8'));
const jobs=[['combined',9],...scenes.map(s=>[path.parse(s.source).name,1])];
const finalDir=path.join(root,process.argv[2]||'pptx');
await fs.mkdir(finalDir,{recursive:true});
const receiptDir=path.join(root,'.build','receipts_'+path.basename(finalDir));
await fs.mkdir(receiptDir,{recursive:true});
for(const [stem,n] of jobs){
 const result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(root,'.build',stem+'_candidate.pptx'),finalPath:path.join(finalDir,stem+'_editable.pptx'),pythonExecutable:PY,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:n,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],layoutArgs:['--expected-slide-size-emu','12192000,6861646','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Microsoft YaHei','Arial','Microsoft YaHei UI','宋体','Calibri','Aptos','Times New Roman','黑体','微软雅黑'],scriptFonts:{ea:'Microsoft YaHei'}},verifyArtifactToolImport:true,receiptPath:path.join(receiptDir,stem+'.validation.json')});
 console.log('验证并交付',stem,result.finalPath||'');
}


