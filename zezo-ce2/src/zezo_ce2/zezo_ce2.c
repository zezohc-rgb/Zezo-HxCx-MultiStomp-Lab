#include <stdint.h>
#define ZPTR(type,w) ((type)(uintptr_t)(w))
#define MAGIC 0x5A434533u
#define VERSION 6u
#define N 1024u
#define CLEAR_STEP 128u
#ifndef ZEZO_STAGE
#define ZEZO_STAGE 0
#endif
#pragma CODE_SECTION(Fx_DLY_ZezoCE2, ".audio")
typedef struct {
 uint32_t magic, version, clear_index, ready, write;
 float phase, pre_shelf, pre1,pre2,pre3,post1,post2,post3,de_shelf,wet_lp;
} State;
static inline float clamp(float x) { if (!(x>=0.0f)) return 0.0f; if(x>1.0f)return 1.0f; return x; }
static inline float norm(float x) { if(!(x>=0.0f&&x<=100.0f))return 0.5f; return x<=1.0f?x:clamp(x*0.01f); }
void Fx_DLY_ZezoCE2(unsigned int *ctx) {
 float *params=ZPTR(float *,ctx[1]);
 float *buf=ZPTR(float *,ctx[5]);
 unsigned int *src=ZPTR(unsigned int *,ctx[12]);
 unsigned int *dst=ZPTR(unsigned int *,*(unsigned int *)ZPTR(unsigned int *,ctx[11]));
 *dst=*src;
 if(params[0]<0.5f)return;
 if(ZEZO_STAGE==0)return;
 volatile unsigned int *desc=ZPTR(volatile unsigned int *,ctx[3]);
 if(!desc)return;
 uintptr_t base=(uintptr_t)desc[0],end=(uintptr_t)desc[1];
 uint32_t span=desc[2];
 if(!base||end<=base||(base&3u)||(end&3u)||(span&3u))return;
 if(end-base<sizeof(State)+N*sizeof(float)+8u||span<end-base||span>0x800000u||end-base>0x800000u)return;
 uintptr_t aligned=(base+3u)&~(uintptr_t)3u;
 uintptr_t delay_start=(aligned+sizeof(State)+3u)&~(uintptr_t)3u;
 if(delay_start>end || (end-delay_start)<N*sizeof(float))return;
 State *s=(State *)aligned;
 float *delay=(float *)delay_start;
 if(s->magic!=MAGIC||s->version!=VERSION||s->clear_index>N||s->ready>1u||s->write>=N){
   s->magic=MAGIC;s->version=VERSION;s->clear_index=0;s->ready=0;s->write=0;
   s->phase=0.0f;s->pre_shelf=0.0f;s->pre1=0.0f;s->pre2=0.0f;s->pre3=0.0f;
   s->post1=0.0f;s->post2=0.0f;s->post3=0.0f;s->de_shelf=0.0f;s->wet_lp=0.0f;
 }
 if(!s->ready){
   uint32_t stop=s->clear_index+CLEAR_STEP;
   if(stop>N)stop=N;
   for(uint32_t j=s->clear_index;j<stop;j++)delay[j]=0.0f;
   s->clear_index=stop;if(stop==N)s->ready=1u;
   return;
 }
 if(ZEZO_STAGE==1)return;
 const float rate=norm(params[5]);
 const float depth=norm(params[6]);
 const float shelf=0.05675f, aa=0.6097f, aa3=0.6254f;
 const float de=0.2832f,hp=0.01415f;
 const float phase_step=(0.30f+3.20f*rate)*0.000022675737f;
 for(int i=0;i<8;i++){
   float l=buf[i],r=buf[i+8],input=l;
   float phase=s->phase;
   float tri=phase<0.5f?(-1.0f+4.0f*phase):(3.0f-4.0f*phase);
   s->phase=phase+phase_step;if(s->phase>=1.0f)s->phase-=1.0f;
   float m=0.21794872f*depth*tri;
   float inv=1.0f+m+m*m+m*m*m+m*m*m*m;
   float d=171.99f*inv;
   if(d<128.0f)d=128.0f;if(d>256.0f)d=256.0f;
   s->pre_shelf+=shelf*(input-s->pre_shelf);
   float pre=5.7f*input-4.7f*s->pre_shelf;
   s->pre1+=aa*(pre-s->pre1);s->pre2+=aa*(s->pre1-s->pre2);
   s->pre3+=aa3*(s->pre2-s->pre3);
   delay[s->write]=s->pre3;
   uint32_t whole=(uint32_t)d;
   float frac=d-(float)whole;
   uint32_t a=(s->write+N-whole)&(N-1u),b=(a+N-1u)&(N-1u);
   float wet=delay[a]*(1.0f-frac)+delay[b]*frac;
   s->post1+=aa*(wet-s->post1);s->post2+=aa*(s->post1-s->post2);
   s->post3+=aa3*(s->post2-s->post3);
   s->de_shelf+=de*(s->post3-s->de_shelf);
   float recovered=(s->post3+4.7f*s->de_shelf)*0.1754385965f;
   s->wet_lp+=hp*(recovered-s->wet_lp);
   wet=recovered-s->wet_lp;
   s->write=(s->write+1u)&(N-1u);
   buf[i]=1.115f*(0.65f*l+0.35f*wet);
   buf[i+8]=1.115f*(0.65f*r+0.35f*wet);
 }
}
