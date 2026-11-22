#include <stdint.h>
#define ZPTR(type,w) ((type)(uintptr_t)(w))
#define MAGIC 0x5A434533u
#define VERSION 8u
#define N 1024u
#define CLEAR_STEP 128u
#ifndef ZEZO_STAGE
#define ZEZO_STAGE 0
#endif
#pragma CODE_SECTION(Fx_DLY_ZezoCE2, ".audio")
typedef struct {
 uint32_t magic, version, clear_index, ready, write;
 float phase, rate, depth, lfo, pre_shelf, input_lp, pre1,pre2,pre3;
 float bbd_lp, post1,post2,post3,wet_lp,de_shelf;
} State;
static inline float clamp(float x) { if (!(x>=0.0f)) return 0.0f; if(x>1.0f)return 1.0f; return x; }
/* Own-runtime knobs are observed as normalized 0..1 on hardware in the upstream
 * StereoChorus port. 1..100 is retained only as a defensive fallback; do NOT
 * apply the legacy 0..0.14 GAIN-probe scaling here. CE-2 hardware test pending. */
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
 if(!base||end<=base||(base&3u)||(end&3u))return;
 if(end-base<sizeof(State)+N*sizeof(float)+8u||span<end-base||span>0x800000u||end-base>0x800000u)return;
 uintptr_t aligned=(base+3u)&~(uintptr_t)3u;
 uintptr_t delay_start=(aligned+sizeof(State)+3u)&~(uintptr_t)3u;
 if(delay_start>end || (end-delay_start)<N*sizeof(float))return;
 State *s=(State *)aligned;
 float *delay=(float *)delay_start;
 if(s->magic!=MAGIC||s->version!=VERSION||s->clear_index>N||s->ready>1u||s->write>=N){
   s->magic=MAGIC;s->version=VERSION;s->clear_index=0;s->ready=0;s->write=0;
   s->phase=0.0f;s->rate=norm(params[5]);s->depth=norm(params[6]);
   s->lfo=-1.0f;s->pre_shelf=0.0f;s->input_lp=0.0f;s->bbd_lp=0.0f;s->pre1=0.0f;s->pre2=0.0f;s->pre3=0.0f;
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
 /* Bilinear transforms of the complementary IC1 shelves.
  * C3/C15 = 6.8 nF, with 10 kΩ and (10+47) kΩ time constants. */
 const float fast=2.0f*44100.0f*10000.0f*6.8e-9f;
 const float slow=2.0f*44100.0f*57000.0f*6.8e-9f;
 const float aa=0.6097f, aa3=0.6254f;
 /* Matched RC poles at 44.1 kHz. See CE2-REFINEMENT.md. */
 const float input_hp=0.006848f, bbd_hp=0.002080f, mix_hp=0.015191f;
 const float lfo_lp=0.010254f;
 const float slew=0.001133f; /* 20 ms at 44.1 kHz */
 for(int i=0;i<8;i++){
   /* CE-2-style mono wet path: fold down stereo input so right-only
    * sources also feed modulation; preserve independent dry L/R paths. */
   float l=buf[i],r=buf[i+8],input=0.5f*(l+r);
   float phase=s->phase;
   if(!(phase>=0.0f && phase<1.0f)) { phase=0.0f; s->phase=0.0f; }
   s->rate+=slew*(rate-s->rate);
   s->depth+=slew*(depth-s->depth);
   /* A slow-end taper gives more travel to subtle chorus settings. */
   float hz=0.30f+3.20f*s->rate*(0.5f+0.5f*s->rate);
   float tri=phase<0.5f?(-1.0f+4.0f*phase):(3.0f-4.0f*phase);
   s->phase=phase+hz*0.000022675737f;
   if(s->phase>=1.0f)s->phase-=1.0f;
   /* BBD delay is inverse clock frequency. The product sums m^0..m^7
    * with no division or TI runtime helper in the sample loop. */
   s->lfo+=lfo_lp*(tri-s->lfo);
   float m=0.21794872f*s->depth*s->lfo;
   float m2=m*m;
   float d=171.99f*(1.0f+m)*(1.0f+m2)*(1.0f+m2*m2);
   if(!(d>=128.0f))d=128.0f;
   if(d>256.0f)d=256.0f;
   float pre=((1.0f+slow)/(1.0f+fast))*input+s->pre_shelf;
   s->pre_shelf=((1.0f-slow)/(1.0f+fast))*input-((1.0f-fast)/(1.0f+fast))*pre;
   s->input_lp+=input_hp*(pre-s->input_lp);
   pre-=s->input_lp;
   s->pre1+=aa*(pre-s->pre1);s->pre2+=aa*(s->pre1-s->pre2);
   s->pre3+=aa3*(s->pre2-s->pre3);
   /* Soft BBD headroom after pre-emphasis. Unity small-signal gain,
    * symmetric knee at 0.9 and continuous slope at both ends. */
   float drive=s->pre3;
   float magnitude=drive<0.0f?-drive:drive;
   if(magnitude>0.9f){
     float t=clamp((magnitude-0.9f)*0.55555556f);
     magnitude=0.9f+1.8f*t*(1.0f-0.5f*t);
     drive=drive<0.0f?-magnitude:magnitude;
   }
   delay[s->write]=drive;
   /* d is clamped to [128,256]: extract its positive IEEE-754 integer part without TI RTS __c6xabi_fixfu. */
   union { float f; uint32_t bits; } dbits;
   dbits.f=d;
   uint32_t exponent=(dbits.bits>>23)&255u;
   uint32_t whole=((dbits.bits&0x7fffffu)|0x800000u)>>(150u-exponent);
   float frac=d-(float)whole;
   uint32_t a=(s->write+N-whole)&(N-1u),b=(a+N-1u)&(N-1u);
   float wet=delay[a]*(1.0f-frac)+delay[b]*frac;
   s->bbd_lp+=bbd_hp*(wet-s->bbd_lp);
   wet-=s->bbd_lp;
   s->post1+=aa*(wet-s->post1);s->post2+=aa*(s->post1-s->post2);
   s->post3+=aa3*(s->post2-s->post3);
   s->wet_lp+=mix_hp*(s->post3-s->wet_lp);
   wet=s->post3-s->wet_lp;
   float recovered=((1.0f+fast)/(1.0f+slow))*wet+s->de_shelf;
   s->de_shelf=((1.0f-fast)/(1.0f+slow))*wet-((1.0f-slow)/(1.0f+slow))*recovered;
   s->write=(s->write+1u)&(N-1u);
   buf[i]=0.5f*(l+recovered);
   buf[i+8]=0.5f*(r+recovered);
 }
}
