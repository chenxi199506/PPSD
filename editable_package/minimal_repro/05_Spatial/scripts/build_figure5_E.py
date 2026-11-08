"""Requested 2x4 layout: former right-D/right-C bars on the far right;
three samples as spatial columns, NRFB region above PCDH9. Remove former bars A/B.
"""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,Normalize
from matplotlib.cm import ScalarMappable
P=Path(__file__).resolve().parent;S=P/'source';T=P/'tables';F=P/'figures'
BAR=pd.read_csv(S/'seven_section_summary.csv');VMAX=json.loads((S/'colour_limits.json').read_text())['PCDH9_limits'][1]
TEAL='#277F8E';PLUM='#8E2B83';CMAP=ListedColormap(plt.get_cmap('magma_r')(np.linspace(.06,.94,256)))
SAMPLES=[('Knee2','highPPSD'),('Knee3','low-PPSD'),('A4','control')]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(16.8,12.9));gs=fig.add_gridspec(3,4,left=.075,right=.935,top=.89,bottom=.13,wspace=.40,hspace=.50,width_ratios=[1,1,1,1.15])
summary=[];manifest=[];targets=[];overlaps=[]
def bars(ax,key,color,title,old_label):
 means=[];sds=[];vals=[]
 for group in ['Healthy','OA']:
  v=BAR.loc[BAR.group==group,key].to_numpy();means.append(float(v.mean()));sds.append(float(v.std(ddof=1)));vals.append(v)
  summary.append({'old_bar_panel':old_label,'metric':key,'group':group,'n_sections':len(v),'mean_percent':v.mean(),'SD_percent':v.std(ddof=1),'SEM_percent':v.std(ddof=1)/np.sqrt(len(v)),'error_bars_shown':'SD (not SEM or confidence interval)'})
 ax.bar([0,1],means,color=color,alpha=.82,width=.58,zorder=2)
 ax.errorbar([0,1],means,yerr=sds,fmt='none',ecolor='#263746',elinewidth=1.25,capsize=4,capthick=1.25,zorder=3)
 ymax=max(max(v.max(),mu+sd) for v,mu,sd in zip(vals,means,sds))
 for i,(v,mu,sd) in enumerate(zip(vals,means,sds)):
  ax.scatter(i+np.linspace(-.13,.13,len(v)),v,s=30,c='white',edgecolors='#263746',linewidths=.9,zorder=4)
  ax.text(i,max(v.max(),mu+sd)+ymax*.06,f'{mu:.2f}%',ha='center',fontsize=9)
 ax.set_ylim(0,ymax*1.26);ax.set_xlim(-.6,1.6);ax.set_xticks([0,1],['Control\n(n=5)','OA\n(n=2)']);ax.set_ylabel('Positive spots (%)',fontsize=10);ax.set_title(title,loc='left',fontsize=10,pad=11);ax.tick_params(axis='x',length=0)
 for edge in ['left','bottom']:ax.spines[edge].set_color('#aaa')
bars(fig.add_subplot(gs[2,3]),'PCDH9_positive_within_region_percent','#277F8E','PCDH9+ within NRFB region','original right D')
bars(fig.add_subplot(gs[1,3]),'PCDH9_positive_percent','#8E2B83','PCDH9+ among all spots','original right C')
manifest.extend([{'row':3,'column':4,'content':'PCDH9+ within NRFB region','source':'original right D','colour':'#277F8E'},{'row':2,'column':4,'content':'PCDH9+ among all spots','source':'original right C','colour':'#8E2B83'}])
for col,(original,label) in enumerate(SAMPLES):
 d=pd.read_csv(S/(original+'_CD_units.csv.gz'));x=d.x.to_numpy();y=-d.y.to_numpy();axc=fig.add_subplot(gs[0,col]);axd=fig.add_subplot(gs[1,col])
 for ax in [axc,axd]:ax.axis('off');ax.set_aspect('auto');ax.margins(.025)
 axc.scatter(x,y,c=np.where(d.domain==1,TEAL,'#e5e5e5'),s=5,linewidths=0)
 bg=.55 if original.startswith('Knee') else 5;positive=3 if original.startswith('Knee') else 16
 axd.scatter(x,y,c='#eeeeee',s=bg,linewidths=0)
 ix=np.argsort(d.PCDH9_log1pCPM.to_numpy(),kind='stable');ix=ix[d.PCDH9_counts.to_numpy()[ix]>0]
 axd.scatter(x[ix],y[ix],c=d.PCDH9_log1pCPM.to_numpy()[ix],s=positive,cmap=CMAP,vmin=0,vmax=VMAX,linewidths=0)
 axc.text(0,-.045,f'Region: {int(d.domain.sum()):,}/{len(d):,} ({100*d.domain.mean():.1f}%)',transform=axc.transAxes,fontsize=8,color='#555')
 axd.text(0,-.045,f'PCDH9+: {(d.PCDH9_counts>0).sum():,}/{len(d):,} ({100*(d.PCDH9_counts>0).mean():.1f}%)',transform=axd.transAxes,fontsize=8,color='#555')
 axm=fig.add_subplot(gs[2,col]);axm.set_facecolor('#080B10');axm.set_frame_on(True);axm.tick_params(left=False,bottom=False,labelleft=False,labelbottom=False);[sp.set_visible(False) for sp in axm.spines.values()];axm.set_aspect('auto');axm.margins(.025)
 region=d.domain.to_numpy()==1;pos=d.PCDH9_counts.to_numpy()>0;category=region.astype(int)+2*pos.astype(int)
 colours=['#242A32', '#00DCE5', '#F34ACB', '#FFFFFF'];merge_collections=[]
 for k in range(4):
  mask=category==k
  coll=axm.scatter(x[mask],y[mask],c=colours[k],s=positive if k>=2 else 5,linewidths=0)
  if k<2:merge_collections.append(coll)
 targets.append((axm,d,original,merge_collections))
 both=int((category==3).sum())
 axm.text(0,-.045,f'Overlap: {both:,}/{len(d):,} ({100*both/len(d):.2f}%)',transform=axm.transAxes,fontsize=8,color='#555')
 out=d[['barcode','x','y']].copy();out['NRFB_region']=region;out['PCDH9_positive']=pos;out['merge_category']=category;out.to_csv(T/(original+'_merge_spots.csv.gz'),index=False)
 overlaps.append({'sample':original,'display_name':label,'total':len(d),'neither':int((category==0).sum()),'NRFB_only':int((category==1).sum()),'PCDH9_only':int((category==2).sum()),'both':both,'overlap_percent_all':100*both/len(d),'overlap_percent_region':100*both/region.sum()})
 manifest.append({'row':3,'column':col+1,'content':'NRFB / PCDH9 same-spot merge','source':original,'colour':'teal / plum / gold intersection'})
 box=gs[0,col].get_position(fig);fig.text((box.x0+box.x1)/2,.945,label,ha='center',fontsize=15,weight='bold')
 targets.append((axc,d,original,list(axc.collections)));manifest.extend([{'row':1,'column':col+1,'content':'NRFB region','source':original,'colour':TEAL},{'row':2,'column':col+1,'content':'PCDH9 expression','source':original,'colour':'palette A magma_r[.06:.94]'}])
box=gs[0,3].get_position(fig);fig.text((box.x0+box.x1)/2,.945,'Legend / OA vs Control',ha='center',fontsize=14,weight='bold')
for row,label in [(0,'NRFB region'),(1,'PCDH9'),(2,'Merge (spot overlap)')]:
 box=gs[row,:].get_position(fig);fig.text(.012,(box.y0+box.y1)/2,label,rotation=90,va='center',ha='center',fontsize=14,weight='bold')
control_box=gs[0,3].get_position(fig)
cax=fig.add_axes([control_box.x0+.015,control_box.y0+.015,control_box.width-.03,.007]);cb=fig.colorbar(ScalarMappable(norm=Normalize(0,VMAX),cmap=CMAP),cax=cax,orientation='horizontal');cb.set_label('PCDH9 log1p(CPM) (row 2)',fontsize=8,labelpad=1);cb.ax.tick_params(labelsize=7,pad=1)
fig.text(.075,.035,'Bars = section means +/- SD; dots = each section (5 Control, 2 OA). SD shows between-section dispersion, not a disease-effect confidence interval.\nSpatial display: OA region gates both top25%, control both top10%. Bar statistics: ALL seven sections use uniform top25% region gates.\nNRFB regions and PCDH9 positivity refer to mixed spots, not counted cells; comparisons are descriptive and confounded with source/platform. Display aspect stretched to equal frames.',fontsize=9,color='#555')
fig.canvas.draw();render=[]
for ax,d,original,collections in targets:
 xy=d[['x','y']].to_numpy();dist=cKDTree(xy).query(xy,k=2)[0][:,1];step=float(np.median(dist[dist>0]));pt=float(np.linalg.norm(ax.transData.transform((step,0))-ax.transData.transform((0,0)))*72/fig.dpi);area=float(np.clip((1.22*pt)**2,2,16))
 for c in collections:c.set_sizes([area])
 render.append({'sample':original,'C_marker_area_pt2':area})
legend=fig.add_subplot(gs[0,3]);legend.axis('off')
for k,(label,color) in enumerate(zip(['Neither','NRFB region only','PCDH9+ only','Both (same spot)'],['#242A32', '#00DCE5', '#F34ACB', '#FFFFFF'])):
 legend.scatter(.08,.92-k*.13,s=85,c=color,edgecolors='#637080',linewidths=.8,transform=legend.transAxes)
 legend.text(.20,.92-k*.13,label,va='center',fontsize=10,transform=legend.transAxes)
legend.text(.04,.30,'Same-spot overlap; not single-cell.',fontsize=8,color='#555',transform=legend.transAxes)
pd.DataFrame(overlaps).to_csv(T/'merge_overlap_summary.csv',index=False)
assert [r['both'] for r in overlaps]==[528,527,1]
assert all(sum(r[k] for k in ['neither','NRFB_only','PCDH9_only','both'])==r['total'] for r in overlaps)

stem='Rearranged_3x4_spatial_merge_PCDH9_bars_SD'
for ext in ['png','pdf','svg']:fig.savefig(F/(stem+'.'+ext),dpi=300,facecolor='white')
plt.close(fig)
pd.DataFrame(summary).to_csv(T/'bar_mean_SD.csv',index=False);pd.DataFrame(manifest).to_csv(T/'panel_manifest.csv',index=False);pd.DataFrame(render).to_csv(T/'spatial_rendering.csv',index=False)
(T/'source_sha256.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in S.iterdir() if f.is_file()},indent=2))
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>重排：左侧D/C柱状图＋横排三样本空间图</title><style>body{font:16px system-ui;max-width:1750px;margin:25px auto;padding:0 24px;background:#f3f5f8;color:#1b2b38}header,section{background:white;border-radius:12px;padding:25px;margin:22px 0}img{width:100%;height:auto}p{line-height:1.85}a{color:#09689b;margin-right:14px}table{border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #ddd}</style><header><h1>三行空间图与右侧柱状图：新增 NRFB / PCDH9 merge</h1><p>最左列：上方为原右侧D（NRFB区域内PCDH9阳性率），改为原A/B相同青绿；下方为原右侧C（总体PCDH9阳性率），保留紫红。原右侧A、B两张柱状图已移除。</p><p>右侧三列依次highPPSD、low-PPSD、control；第一排NRFB region，第二排PCDH9，第三排为空间叠加图。青绿表示仅NRFB区域，紫红表示仅PCDH9阳性，金色表示同一barcode同时满足两者，浅灰表示均不满足。交集按原始点位计算，不由放大的图形重叠判断；混合spot/bin的交集不等于单细胞共定位。两张保留的柱状图均加均值±SD误差线，散点保留每张切片。SD为切片间离散度，不是SEM、疾病效应置信区间或显著性检验。</p><img src="figures/'''+stem+'.png"><p>'+''.join(f'<a download href="figures/{stem}.{ext}">{ext.upper()}</a>' for ext in ['pdf','svg','png'])+'''<a href="tables/bar_mean_SD.csv">误差线原始统计</a><a href="tables/panel_manifest.csv">新旧面板映射</a><a href="build.py">重绘代码</a></p><p>配色A、原始数据、坐标和归一化范围保留。空间展示control双前10%、OA双前25%；柱状统计仍对七片统一双前25%，图内同时注明。不同物理面积与来源差异未消除，不将区域比例或检出率当成真实细胞比例。</p></header><section><h2>误差线数据：各片等权均值±SD</h2>'''+pd.DataFrame(summary).round(4).to_html(index=False,border=0)+'</section><section><h2>空间交集统计</h2>'+pd.DataFrame(overlaps).round(4).to_html(index=False,border=0)+'</section></html>'
html=html.replace('重排：左侧D/C柱状图＋横排三样本空间图','重排：横排三样本空间图＋右侧D/C柱状图').replace('最左列：','最右列：').replace('右侧三列依次highPPSD','左侧三列依次highPPSD')
(P/'index.html').write_text(html)
print(pd.DataFrame(summary).to_string(index=False),flush=True)

(T/'validation.json').write_text(json.dumps({'layout':'3 rows x 4 columns; bottom right legend','data_panels':11,'intersection_counts':[r['both'] for r in overlaps],'same_barcode_intersection':True,'single_cell_colocalization_claimed':False,'bar_error':'sample SD ddof=1','source_unchanged':True},indent=2))
