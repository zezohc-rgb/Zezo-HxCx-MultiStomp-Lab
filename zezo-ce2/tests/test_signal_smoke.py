"""Host-side signal smoke tests of the CE-2 equations; NOT DSP emulation."""
import math
import unittest

def render(rate, depth, samples=8192):
    delay=[0.0]*1024
    phase=0.0
    write=0
    pre_shelf=pre1=pre2=pre3=post1=post2=post3=de_shelf=wet_lp=0.0
    output=[]
    for i in range(samples):
        x=0.15*math.sin(2*math.pi*440*i/44100)
        tri=(-1+4*phase) if phase<0.5 else (3-4*phase)
        phase+=(.30+3.20*rate)*.000022675737
        if phase>=1:phase-=1
        m=.21794872*depth*tri
        d=max(128.,min(256.,171.99*(1+m+m*m+m*m*m+m*m*m*m)))
        pre_shelf+=.05675*(x-pre_shelf)
        pre=5.7*x-4.7*pre_shelf
        pre1+=.6097*(pre-pre1)
        pre2+=.6097*(pre1-pre2)
        pre3+=.6254*(pre2-pre3)
        delay[write]=pre3
        whole=int(d)
        frac=d-whole
        a=(write+1024-whole)&1023
        b=(a+1023)&1023
        wet=delay[a]*(1-frac)+delay[b]*frac
        post1+=.6097*(wet-post1)
        post2+=.6097*(post1-post2)
        post3+=.6254*(post2-post3)
        de_shelf+=.2832*(post3-de_shelf)
        recovered=(post3+4.7*de_shelf)*.1754385965
        wet_lp+=.01415*(recovered-wet_lp)
        wet=recovered-wet_lp
        write=(write+1)&1023
        output.append(1.115*(.65*x+.35*wet))
    return output

class SignalSmokeTests(unittest.TestCase):
    def test_finite_and_reasonable_peak(self):
        for rate,depth in ((0,0),(0,1),(.5,.5),(1,1)):
            y=render(rate,depth)
            self.assertTrue(all(math.isfinite(v) for v in y))
            self.assertLess(max(map(abs,y)),1.0)
    def test_output_rms_and_rate_response(self):
        def rms(values):
            return math.sqrt(sum(v*v for v in values)/len(values))
        input_rms=.15/math.sqrt(2)
        for rate,depth in ((0,0),(.5,.5),(1,1)):
            y=render(rate,depth)[1024:]
            gain_db=20*math.log10(rms(y)/input_rms)
            self.assertTrue(math.isfinite(gain_db))
            self.assertGreater(gain_db,-12)
            self.assertLess(gain_db,6)
        slow=render(0,1)
        fast=render(1,1)
        self.assertGreater(sum(abs(a-b) for a,b in zip(slow,fast)),.01)
    def test_depth_changes_signal(self):
        dry=render(.5,0)
        mod=render(.5,1)
        self.assertGreater(sum(abs(a-b) for a,b in zip(dry,mod)),.01)

if __name__=='__main__':
    unittest.main()
