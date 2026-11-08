suppressPackageStartupMessages({library(ggplot2);library(jsonlite);library(svglite);library(ragg)})
a<-commandArgs(FALSE);h<-dirname(normalizePath(sub('^--file=','',a[grep('^--file=',a)][1])))
e<-head(read.csv(file.path(h,'source/endpoints.csv')),2);p<-read.csv(file.path(h,'source/performance.csv'));g<-read.csv(file.path(h,'source/increments.csv'));n<-read.csv(file.path(h,'source/endpoint_samples.csv'));sig<-read.csv(file.path(h,'source/significance_tests.csv'),stringsAsFactors=FALSE,na.strings='NA');sig$stars[is.na(sig$stars)]<-''
blue<-'#3B4992';red<-'#EE1B12';ink<-'#213648';muted<-'#64707D';grey<-'#9BA4AE';teal<-'#008280';purple<-'#631879'
mods<-c('Structure','Reference','ReferenceStructure','PPSD','ReferencePPSD','Full');cols<-c(Structure=blue,Reference=grey,ReferenceStructure=teal,PPSD=red,ReferencePPSD='#B45F06',Full=purple)
th<-theme_classic(base_family='Arial',base_size=8)+theme(plot.title=element_text(size=10,face='bold',color=ink,margin=margin(b=6)),plot.subtitle=element_text(size=6.5,color=muted,margin=margin(b=8)),axis.title=element_text(size=8,face='bold',color=ink),axis.text=element_text(size=6.7,color=ink),axis.line=element_line(linewidth=.3),axis.ticks=element_line(linewidth=.3),legend.title=element_blank(),legend.position='bottom',legend.text=element_text(size=7.5),plot.caption=element_text(size=6,color=muted,hjust=0,margin=margin(t=7)),plot.margin=margin(9,12,8,9),plot.title.position='plot',plot.caption.position='plot')
pdfdev<-if(capabilities('aqua'))function(filename,width,height,...)quartz(type='pdf',file=filename,width=width,height=height,...)else grDevices::cairo_pdf
save3<-function(x,stem,w=135,hg=108){ggsave(file.path(h,'figures',paste0(stem,'.svg')),x,width=w,height=hg,units='mm',device=svglite::svglite,bg='white');ggsave(file.path(h,'figures',paste0(stem,'.pdf')),x,width=w,height=hg,units='mm',device=pdfdev,bg='white');ggsave(file.path(h,'figures',paste0(stem,'.png')),x,width=w,height=hg,units='mm',device=ragg::agg_png,dpi=600,bg='white')}
manifest<-list()
for(i in seq_len(nrow(e))){
 sp<-e[i,];q<-p[p$endpoint==sp$id&p$model%in%mods,];q<-q[match(mods,q$model),];ischange<-grepl('change',sp$window)
 ref<-paste(if(ischange)'24-month'else'Baseline',sp$domain)
 labels<-c('Structure',ref,paste0(ref,' + structure'),'PPSD',paste0(ref,' + PPSD'),paste0(ref,' + structure\n+ clinical + PPSD'));q$label<-factor(labels,levels=rev(labels));q$model<-factor(q$model,levels=mods)
 tests<-sig[sig$endpoint==sp$id,];q$stars<-'';q$stars[q$model=='ReferencePPSD']<-tests$stars[tests$comparison=='PPSD_added_to_reference'];q$stars[q$model=='Full']<-tests$stars[tests$comparison=='StructureClinical_added_to_reference_PPSD']
 gain<-g[g$endpoint==sp$id&g$comparison=='PPSD_added_to_full_reference',]
 for(metric in c('r2','rmse')){
  q$val<-q[[metric]];q$lo<-q[[paste0(metric,'_lo')]];q$hi<-q[[paste0(metric,'_hi')]]
  limits<-if(metric=='r2')c(min(-.04,min(q$lo)-.025),max(.65,max(q$hi)+.13)) else c(0,max(q$hi)*1.24)
  offset<-diff(limits)*.02
  caption<-'* q<0.05; ** q<0.01; *** q<0.001 (BH).\nStars: +PPSD vs reference; full vs reference + PPSD.\nPaired tests of fixed out-of-fold squared errors.'
  plot<-ggplot(q,aes(val,label,fill=model))+geom_col(width=.55,alpha=.9)+geom_errorbar(aes(xmin=lo,xmax=hi),orientation='y',width=.13,linewidth=.5,color=ink)+geom_text(aes(x=hi+offset,label=paste0(sprintf('%.3f',val),stars)),hjust=0,size=2.3,family='Arial',color=ink)+geom_vline(xintercept=0,color='#A1AAB5',linewidth=.3)+scale_fill_manual(values=cols,guide='none')+scale_x_continuous(limits=limits,expand=expansion(mult=0))+labs(title=if(i==1)'E  Prediction of follow-up pain'else'F  Prediction of follow-up function',subtitle=sprintf('Mean 36/48-month score; n=%d; participant-level CV',q$n[1]),x=if(metric=='r2')'Held-out R-squared (95% CI); higher is better'else'Held-out RMSE (95% CI); lower is better',y=NULL,caption=caption)+th
  stem<-sprintf('W%02d_%s_%s',i,sp$id,metric);save3(plot,stem)
 }
 manifest[[i]]<-data.frame(figure=sprintf('W%02d',i),stem=sprintf('W%02d_%s_r2',i,sp$id),endpoint=sp$id,purpose=sp$label,method='Same-participant five-fold OOF linear prediction; 2000 paired fixed-prediction bootstrap intervals',source='source/performance.csv; source/out_of_fold_predictions.csv; endpoint-specific analysis CSV',verdict='Exploratory predictive association; not external validation or causal effect',priority=if(i<=2)'Main/Supp'else'Exploratory')
}
