// 验证八页 PPT、原生图表数据及内嵌工作簿，并写入新的交付文件。
import path from 'node:path';
import fs from 'node:fs/promises';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const skill='C:/Users/董昱彤/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const py='C:/Users/董昱彤/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES='C:/Users/董昱彤/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
await fs.mkdir(path.join(root,'.build/final'),{recursive:true});
const result=await finalizePresentation({workspaceDir:path.dirname(root),candidatePath:path.join(root,'.build/normalized.pptx'),finalPath:path.join(root,'.build/final/validated_v2.pptx'),pythonExecutable:py,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:8,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[5],materializeLiteralChartWorkbooks:true,layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Microsoft YaHei','Arial','Microsoft YaHei UI','宋体','Calibri','Aptos','Times New Roman','黑体','微软雅黑'],scriptFonts:{ea:'Microsoft YaHei'}},verifyArtifactToolImport:true,receiptPath:path.join(root,'.build/final_validation_v2.json')});
console.log(result.finalPath||'已通过最终验证');
