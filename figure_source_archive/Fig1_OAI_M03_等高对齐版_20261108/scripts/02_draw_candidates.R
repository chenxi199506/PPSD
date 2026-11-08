suppressPackageStartupMessages({library(ggplot2);library(patchwork);library(grid);library(jsonlite)})
a<-commandArgs(FALSE);a<-gsub('~+~',' ',sub('^--file=','',a[grep('^--file=',a)][1]),fixed=TRUE);ROOT<-dirname(dirname(normalizePath(a)));source(file.path(ROOT,'scripts/config.R'));source(file.path(ROOT,'scripts/common.R'))
# Harmonise the new candidates with the supplied TKA figure's marine palette.
# Palette and row sizes are controlled in config.R.
for(f in c('01_panel_a_balance.R','02_panel_b_followup_pain.R','03_panel_c_function.R','05_panel_e_adjusted_association.R','06_panels_f_g_prediction.R'))source(file.path(ROOT,'scripts',f))
d<-read.csv(file.path(ROOT,'data/panel_definition_scatter.csv'));c<-read.csv(file.path(ROOT,'data/panel_dose_response.csv'));info<-fromJSON(file.path(ROOT,'reports/new_analysis.json'))
cols<-c('Lower decile'=CFG$teal,'Middle 80%'='#D7E1E8','Upper decile'=CFG$red);cuts<-c(info$P10,info$P90)
new_theme<-function(){base_theme()+theme(plot.margin=margin(1.5,2,1.5,2),axis.title=element_text(size=6.2),axis.text=element_text(size=6.0))}
make_distribution<-function(letter='d'){ggplot(d,aes(PPSD,fill=display_group))+geom_histogram(binwidth=.75,boundary=0,color='white',linewidth=.15)+scale_fill_manual(values=cols)+geom_vline(xintercept=cuts,linetype='dashed',linewidth=.3,color=CFG$ink)+labs(title=paste0(letter,'  PPSD distribution'),x='PPSD (pain points)',y='Knees')+scale_x_continuous(breaks=c(-5,0,5,10))+new_theme()}
make_definition<-function(letter='e'){ggplot(d,aes(baseline_expected_pain,mean_pain_0_24))+geom_abline(slope=1,intercept=0,color='#90A5B3',linewidth=.4,linetype='dashed')+geom_point(data=d[d$display_group=='Middle 80%',],color='#C8D5DF',alpha=.35,size=.55)+geom_point(data=d[d$display_group!='Middle 80%',],aes(color=display_group),alpha=.7,size=.8)+scale_color_manual(values=cols)+scale_x_continuous(breaks=c(0,2,4,6),limits=c(0,7.5))+scale_y_continuous(breaks=c(0,5,10,15),limits=c(0,17))+labs(title=paste0(letter,'  Observed vs expected pain'),x='Baseline expected pain',y='Mean pain, 0-24 mo')+new_theme()}
make_curve<-function(letter='f'){ggplot(c,aes(PPSD,100*probability))+geom_ribbon(aes(ymin=100*lower,ymax=100*upper),fill=CFG$red,alpha=.15)+geom_line(color=CFG$red,linewidth=.6)+geom_rug(data=d,aes(PPSD,y=NULL),inherit.aes=FALSE,sides='b',alpha=.1,linewidth=.15)+scale_y_continuous(limits=c(0,100),breaks=c(0,50,100),expand=expansion(mult=c(0,.03)))+scale_x_continuous(breaks=c(-5,0,5))+annotate('text',x=0,y=95,label=if(info$overall_p<.001)'Overall P <0.001'else sprintf('Overall P = %.3f',info$overall_p),size=mm_pt(6.0),family=CFG$family)+labs(title=paste0(letter,'  Later high-pain probability'),x='PPSD (pain points)',y='Probability (%)')+new_theme()}

# All row heights are equal; first six panels share one patchwork layout so
# corresponding y-axis lines and plotting widths align across the two rows.
A<-make_a();B<-make_distribution('b');C<-make_definition('c')
D<-make_b()+labs(title='d  Follow-up pain');E<-make_c()+labs(title='e  Function over follow-up');F<-make_curve('f')
L<-CFG$layout;gap<-L$top_mm[2]-(L$top_mm[1]+L$height_mm[1]);top_height<-L$top_mm[2]+L$height_mm[2]-L$top_mm[1]
TOP6<-wrap_plots(A,B,C,D,E,F,design="ABC\n###\nDEF")+plot_layout(widths=c(1,1,1),heights=c(L$height_mm[1],gap,L$height_mm[2]))
H<-make_prediction('pain_mean','h','pain');I<-make_prediction('function_mean','i','function');BOTTOM<-H+I+plot_layout(ncol=2,widths=c(1,1))
local_association<-function(){expr<-paste(deparse(body(draw_e)),collapse='\n');expr<-gsub('e  Adjusted association with sustained follow-up pain','g  Adjusted association with sustained follow-up pain',expr,fixed=TRUE);eval(parse(text=expr))}
place<-function(obj,top,height){print(obj,vp=viewport(x=0,y=1-top/CFG$height_mm,width=1,height=height/CFG$height_mm,just=c('left','top')),newpage=FALSE)}
paint<-function(){grid.newpage();grid.rect(gp=gpar(fill='white',col=NA));place(TOP6,L$top_mm[1],top_height);pushViewport(viewport(x=0,y=1-L$top_mm[3]/CFG$height_mm,width=1,height=L$height_mm[3]/CFG$height_mm,just=c('left','top')));local_association();popViewport();place(BOTTOM,L$top_mm[4],L$height_mm[4])}
prefix<-file.path(ROOT,'figures/M03_equal_rows_aligned')
svglite::svglite(paste0(prefix,'.svg'),width=CFG$width_mm/25.4,height=CFG$height_mm/25.4);paint();dev.off();open_pdf(paste0(prefix,'.pdf'),CFG$width_mm,CFG$height_mm);paint();dev.off();ragg::agg_png(paste0(prefix,'.png'),width=CFG$width_mm,height=CFG$height_mm,units='mm',res=600,background='white');paint();dev.off()
# Reusable single panels with the new lettering and final font sizes.
for(z in list(list(A,'a_balance'),list(B,'b_distribution'),list(C,'c_observed_expected'),list(D,'d_followup_pain'),list(E,'e_followup_function'),list(F,'f_adjusted_curve')))export_plot(z[[1]],z[[2]],61,40.5)
export_plot(H,'h_prediction_pain',91.5,40.5);export_plot(I,'i_prediction_function',91.5,40.5)
pp<-file.path(ROOT,'figures/panels/g_association');svglite::svglite(paste0(pp,'.svg'),width=183/25.4,height=40.5/25.4);grid.newpage();local_association();dev.off();open_pdf(paste0(pp,'.pdf'),183,40.5);grid.newpage();local_association();dev.off();ragg::agg_png(paste0(pp,'.png'),width=183,height=40.5,units='mm',res=600,background='white');grid.newpage();local_association();dev.off()
writeLines(capture.output(sessionInfo()),file.path(ROOT,'reports/R_sessionInfo.txt'));write.csv(L,file.path(ROOT,'reports/row_layout_mm.csv'),row.names=FALSE);cat('M03 and nine panels redrawn: four rows, each 40.5 mm.\n')
