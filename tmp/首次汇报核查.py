from pathlib import Path
import sys, csv, json, hashlib, shutil
from collections import Counter, defaultdict
sys.path.insert(0,str(Path('tmp/analysislibs').resolve()))
import numpy as np
import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

根=Path.cwd(); 源=根/'outputs/33500DWT_图纸模型表格_20261101'
出=根/'outputs/B组_首次汇报综合材料_v0.3_20261101'; 出.mkdir(exist_ok=True)
图=出/'图像'; 图.mkdir(exist_ok=True)
数据=出/'核查数据'; 数据.mkdir(exist_ok=True)
plt.rcParams.update({'font.sans-serif':['Microsoft YaHei'],'axes.unicode_minus':False,'font.size':11})
行=list(csv.DictReader(next(源.rglob('*型值点.csv')).open(encoding='utf-8-sig')))
点=np.array([[float(r[k]) for k in ['x_m','y_halfbreadth_m','z_m']] for r in 行])
母点=np.array([[float(r[k]) for k in ['mother_x_m','mother_y_halfbreadth_m','mother_z_m']] for r in 行])
k=0.9867500766092098; r=k**3
剖=ezdxf.readfile(next(源.rglob('*三维剖面.dxf')))
剖点=np.array([list(e.dxf.location) for e in 剖.modelspace().query('POINT')])
标点=np.loadtxt(next(源.rglob('*Markers.txt')))[:,1:4]
def 排序(a):return a[np.lexsort((a[:,2],a[:,1],a[:,0]))]
误差剖=float(np.max(np.abs(排序(点)-排序(剖点))))
误差标=float(np.max(np.abs(点-标点)))
型=ezdxf.readfile(next(源.rglob('*型线图*.dxf')))
审=型.audit()
分组=defaultdict(list)
for rr,p in zip(行,点):分组[(rr['station'],rr['branch'])].append(p)
记录=[]
for (站,支),a in 分组.items():
    a=np.array(a);记录.append({'站位':站,'分支':支,'点数':len(a),'X_m':float(a[0,0]),'最大半宽_m':float(a[:,1].max()),'最低Z_m':float(a[:,2].min()),'最高Z_m':float(a[:,2].max())})
with (数据/'逐站型值统计.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=记录[0]);w.writeheader();w.writerows(记录)
iges=next(源.rglob('*.igs')).read_text().splitlines()
目录=[a for a in iges if len(a)>72 and a[72]=='D']
曲面=[{'类型':int(目录[i][:8]),'名称':目录[i+1][56:64].strip()} for i in range(0,len(目录),2)]
结论={'点数':len(行),'站位数':len(set(rr['station'] for rr in 行)),'分支组数':len(分组),'分支点数':dict(Counter(rr['branch'] for rr in 行)),
    '坐标范围_m':{'min':点.min(axis=0).tolist(),'max':点.max(axis=0).tolist()},'缩尺最大绝对差_m':float(np.max(np.abs(点-母点*k))),
    'CSV与三维DXF点集最大绝对差_m':误差剖,'CSV与Markers最大绝对差_m':误差标,'三维DXF实体':dict(Counter(e.dxftype() for e in 剖.modelspace())),
    '二维DXF实体':dict(Counter(e.dxftype() for e in 型.modelspace())),'二维DXF单位编码':型.header.get('$INSUNITS'),'二维DXF审查错误数':len(审.errors),'二维DXF修复项数':len(审.fixes),'IGES目录':曲面,
    '满载口径修正量推导_t':(43517.7-42323*1.025)*r,'未核验':['MSD原生曲面与IGES及型值点的拟合偏差','MSD静水力软件输出','二维型线与MSD重新切剖的一致性','两份DWG实体一致性']}
(数据/'一致性核查结果.json').write_text(json.dumps(结论,ensure_ascii=False,indent=2),encoding='utf-8')
assert 误差剖<1e-8 and 误差标<1e-8
# 绘制真实型值点和分支折线，不作曲面插值，也不称作模型切剖。
fig,ax=plt.subplots(figsize=(13,4.5))
for key,a in 分组.items():
    a=np.array(a)
    for sign in [-1,1]:ax.plot(.9396926*a[:,0]-.3420201*sign*a[:,1],.0885213*a[:,0]+.2432103*sign*a[:,1]+.9659258*a[:,2],lw=.75,color='#276889' if key[1]=='HULL_SECTIONS' else '#c35b20')
ax.set(title='型值分支的三维空间复核  左右舷镜像显示');ax.set_aspect('equal');ax.axis('off')
ax.text(0,-3,'艉  AP附近',fontsize=10);ax.text(150,32,'艏  FP附近',fontsize=10)
fig.text(.04,.02,'来自751个提交型值点；折线连接仅辅助核查。不是MSD曲面重建或软件截图。',fontsize=10)
fig.savefig(图/'03_型值三维核查.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(12,6),sharey=True)
for ax,选,标题 in [(axs[0],['0','1','2','3','4','6','10'],'艉部至舯部'),(axs[1],['10','16','18','19','19.5','20','20.25'],'舯部至艏部')]:
    for 站 in 选:
        for (s,支),a in 分组.items():
            if s==站:
                a=np.array(a);ax.plot(a[:,1],a[:,2],lw=1,label='ST '+站+(' 球鼻艏' if 支=='BULB_SECTIONS' else ' 上艏' if 支=='UPPER_BOW' else ''))
    ax.axhline(9.699753,color='gray',ls='--',lw=.8);ax.axhline(10.133923,color='#ba342a',ls=':',lw=.8)
    ax.set(title=标题,xlabel='半宽 Y / m',ylabel='高度 Z / m',xlim=(-.3,15),ylim=(-.3,15.5));ax.set_aspect('equal');ax.grid(alpha=.2);ax.legend(fontsize=8,loc='lower right')
fig.suptitle('典型横剖面型值折线复核');fig.text(.08,.01,'灰虚线为性能参考吃水9.699753 m；红点线为满载参考吃水10.133923 m。分支分别连接，不跨缺口拟合。',fontsize=9)
fig.savefig(图/'04_典型横剖面.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(12,4.5))
for (s,支),a in 分组.items():
    a=np.array(a);ax.scatter(a[:,0],a[:,2],s=4,color='#236b8e' if 支=='HULL_SECTIONS' else '#c35b20')
for h,c,n in [(14.406551,'#555555','型深14.406551 m'),(10.133923,'#ba342a','原满载参考10.133923 m'),(9.699753,'#26874b','性能参考9.699753 m')]:ax.axhline(h,color=c,lw=.9,ls='--',label=n)
ax.set(xlabel='距AP纵坐标 X / m',ylabel='距基线高度 Z / m',title='型值站位分布及吃水基准');ax.legend(loc='lower center',ncol=3,fontsize=9);ax.grid(alpha=.2)
fig.savefig(图/'05_站位与吃水基准.png',dpi=180,bbox_inches='tight');plt.close(fig)
shutil.copy2(next(源.rglob('*三维预览.png')),图/'01_组员三维曲面预览.png')
shutil.copy2(next(源.rglob('*型线图*预览.png')),图/'02_组员型线图全图.png')
# 保留交付原件与旧版计算依据，便于按图索引回溯。
for 名 in ['01图纸_组内当前','02模型_组内当前','03表格_组内当前']:
    shutil.copytree(源/名,出/'原始成果'/名,dirs_exist_ok=True)
shutil.copy2(源/'先读我_文件说明.md',出/'原始成果/组员原说明.md')
旧=根/'outputs/B组_成员一_中期_v0.2_20261031'
for 名 in ['01_成员一中期设计计算报告.docx','02_阻力快速性与总体校核.xlsx','03_重量重心与浮态待补.xlsx','04_统一参数与结果快照.json']:
    (出/'前期计算').mkdir(exist_ok=True);shutil.copy2(旧/名,出/'前期计算'/名)
print(json.dumps(结论,ensure_ascii=False,indent=2))
