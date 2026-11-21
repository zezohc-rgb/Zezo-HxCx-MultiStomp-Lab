#!/usr/bin/env python3
"""Experimental, NOT hardware-validated CE-2 ZDL build."""
import json, os, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/'build'))
sys.path.insert(0,str(HERE.parent/'common'))
m=json.loads((HERE/'manifest.json').read_text())
if os.environ.get('ZEZO_FXID_REVIEWED') != str(m['fxid']):
    raise SystemExit('BLOCKED: independently review FXID collision before build')
TI_ROOT=Path(os.environ.get('TI_CGT_ROOT','/tmp/ti-cgt-c6000'))
cl6x=TI_ROOT/'bin'/'cl6x'
if not cl6x.is_file(): raise SystemExit('TI C6000 cl6x missing')
if not (ROOT/'build'/'linker.py').is_file(): raise SystemExit('Upstream linker missing')
stage=int(os.environ.get('ZEZO_STAGE','0'))
if stage not in (0,1,2): raise SystemExit('Invalid stage')
from linker import LinkerConfig, link, params_from_manifest
from custom_covers import make_cover
obj=HERE/'zezo_ce2.obj'
subprocess.run([str(cl6x),'--c99','--opt_level=2','-mv6740','--abi=eabi','--mem_model:data=far',f'--define=ZEZO_STAGE={stage}',f'--include_path={TI_ROOT}/include','-c',str(HERE/'zezo_ce2.c'),f'--output_file={obj}'],cwd=HERE,check=True)
out=ROOT/'dist'/f'ZZC2S{stage}.ZDL'
out.parent.mkdir(exist_ok=True)
link(LinkerConfig(effect_name=m['effect_name'],audio_func_name=m['audio_func_name'],gid=m['gid'],fxid=m['fxid'],params=params_from_manifest(m['params']),obj_path=obj,output_path=out,fxid_version=m['fxid_version'].encode('ascii'),flags_byte=m['flags_byte'],screen_image=make_cover(m['effect_name'],[p['name'] for p in m['params']]),knob_positions=[(2,26,46),(3,82,46)],audio_nop=m['audio_nop']))
if out.stat().st_size>32126:
    out.unlink()
    raise SystemExit('Oversize ZDL removed')
print('UNVALIDATED ZDL:',out, 'bytes:',out.stat().st_size)
