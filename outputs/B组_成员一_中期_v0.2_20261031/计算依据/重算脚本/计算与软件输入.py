from pathlib import Path
import math, json, shutil, subprocess

根目录 = Path.cwd()
归档 = 根目录 / 'outputs' / 'B组_成员一_中期_v0.2_20261031'
归档.mkdir(parents=True, exist_ok=True)
r = 33500 / (43517.7 - 8650)
k = r ** (1/3)

def 阻力(v):
    # 按课程给定的低傅汝德数公式逐项计算，保留模板环境参数与换算常数。
    rho, nu, g = 1025, 1.189e-6, 9.81
    L, B, T, vol, cp, cm, cb, cwp = 175.2, 28.8, 9.83, 40301.2, .8163, .9956, .8125, .9102
    S, Sa, At, Ab, hb, lr, ie = 7250, 34.498, 4.9458, 40.9186, 4.681, 74.6, 43.7439
    vel = v*.5144
    fn, rn = vel/math.sqrt(g*L), vel*L/nu
    cf = .075/(math.log10(rn)-2)**2
    rf = .5*rho*vel**2*cf*S
    f1 = .93+.487118*(1+.011*(-10))*(B/L)**1.06806*(T/L)**.46106*(L/lr)**.121563*(L**3/vol)**.36486*(1-cp)**(-.60247)
    rapp = .5*rho*vel**2*Sa*1.4*cf
    c7 = B/L
    c1 = 2223105*c7**3.78613*(T/B)**1.07961*(90-ie)**(-1.37565)
    c3 = .56*Ab**1.5/(B*T*(.31*math.sqrt(Ab)+T-hb))
    c2 = math.exp(-1.89*math.sqrt(c3))
    c5 = 1-.8*At/(B*T*cm)
    c16 = 1.73014-.7067*cp
    m1 = .0140407*L/T-1.75254*vol**(1/3)/L-4.79323*B/L-c16
    c15 = -1.69385
    m4 = .4*c15*math.exp(-.034*fn**(-3.29))
    lam = 1.446*cp-.03*L/B
    rw = rho*g*vol*c1*c2*c5*math.exp(m1*fn**(-.9)+m4*math.cos(lam/fn**2))
    pb = .56*math.sqrt(Ab)/(T-hb)
    fni = vel/math.sqrt(g*(T-hb-.25*math.sqrt(Ab))+.15*vel**2)
    rb = .11*math.exp(-3*pb**(-2))*fni**3*Ab**1.5*rho*g/(1+fni**2)
    fnt = vel/math.sqrt(2*g*At/(B+B*cwp))
    c6 = .2*(1-.2*fnt) if fnt < 5 else 0
    rtr = .5*rho*vel**2*At*c6
    ca = .006*(L+100)**(-.16)-.00205+.003*math.sqrt(L/7.5)*cb**4*c2*(.04-min(T/L,.04))
    ra = .5*rho*vel**2*(S+Sa)*ca
    rt = rf*f1+rapp+rw+rb+rtr+ra
    return dict(v=v,fn=fn,rn=rn,cf=cf,rf=rf,f1=f1,rapp=rapp,rw=rw,rb=rb,rtr=rtr,ra=ra,rt=rt,pe=rt*vel/1000)

def 生成工况(名称, 功率, 转速, 桨径, 吃水, 轴高, 新船=False):
    目录 = 归档 / '计算依据' / 'DMAU' / 名称
    目录.mkdir(parents=True, exist_ok=True)
    shutil.copy2(根目录/'0000DMAU软件2026/0000DMAU软件/DMAU.EXE', 目录/'DMAU.EXE')
    航速 = [11,12,13,14,15,16]
    有效功率 = [(阻力(v/math.sqrt(k))['pe']*r**(7/6) if 新船 else 阻力(v)['pe']) for v in 航速]
    # 软件采用公制马力，输出内部换算为 1 hp = 0.7355 kW。
    文本 = ['2026.10.31. MAU', 名称.encode('ascii',errors='ignore').decode() or 'B GROUP PROPULSION',
        ''.join(f'{x:5d}' for x in [6,4,1,2,15,0,6]),
        ''.join(f'{x:9.2f}' for x in [功率/.7355,转速,0,0]),
        ''.join(f'{x:9.4f}' for x in [1,.99,1,桨径,0,.1689,1.2,7.6]),
        ''.join(f'{x:9.4f}' for x in [104.63,吃水,轴高,.5*.8125-.05,.27*.8125]),
        ''.join(f'{x:9.2f}' for x in 航速),
        ''.join(f'{x/.7355:9.2f}' for x in 有效功率)]
    for n in [3,4,5,6,7]:
        assert len(文本[n]) % 9 == 0
    (目录/'DMAU.IPT').write_bytes(('\r\n'.join(文本)+'\r\n').encode('ascii'))
    运行 = subprocess.run([str(目录/'DMAU.EXE')], input=b'00341700\nn\ny\n', cwd=目录, capture_output=True, timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
    (目录/'运行日志.txt').write_text(运行.stdout.decode('gbk',errors='replace'),encoding='utf-8')
    原始 = (目录/'DMAU.OUT').read_text(encoding='gbk')
    (目录/'DMAU_中文结果.txt').write_text(原始,encoding='utf-8')
    print(名称, '\n', 原始[原始.find('(3)'):原始.find('(4)')])
    return {'名称':名称,'功率_kW':功率,'转速_rpm':转速,'桨径上限_m':桨径,'吃水_m':吃水,'有效功率_kW':有效功率}

if __name__ == '__main__':
    结果 = {'r':r,'k':k,'母型':[阻力(v) for v in [11,12,13,14,15,16]],'新船':[]}
    for v in [11,12,13,14,15,16]:
        原 = 阻力(v/math.sqrt(k))
        结果['新船'].append({'v':v,'母型对应航速':v/math.sqrt(k),'rt':原['rt']*r,'pe':原['pe']*r**(7/6)})
    print(json.dumps(结果,ensure_ascii=False,indent=2))
    结果['DMAU工况'] = [生成工况('01_parent_corrected',5832,131.4,5.3,9.83,3.2),生成工况('02_new_initial',5832*r**(7/6),131.4/math.sqrt(k),5.3*k,9.83*k,3.2*k,True)]
    (根目录/'tmp/计算结果.json').write_text(json.dumps(结果,ensure_ascii=False,indent=2),encoding='utf-8')
