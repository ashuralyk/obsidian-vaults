#!/usr/bin/env python3
"""核对针孔相机中指定三维点的画框位置；不检查遮挡、碰撞或真实镜头。"""
import argparse
import json
import math
from pathlib import Path
import sys


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def cross(a,b):
    return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]


def vector(value):
    if not isinstance(value,(list,tuple)) or len(value)!=3:
        raise ValueError('坐标和朝向必须是三个有限数值。')
    result=[float(x) for x in value]
    if not all(math.isfinite(x) for x in result):
        raise ValueError('坐标必须是有限数值。')
    return result


def unit(value):
    length=math.sqrt(dot(value,value))
    if length<1e-12:
        raise ValueError('相机与目标不能重合，up 也不能与视轴平行。')
    return [x/length for x in value]


def check_camera(config):
    position=vector(config['position']);target=vector(config['target'])
    focal=float(config['focal_mm'])
    width=float(config.get('sensor_width_mm',36))
    height=float(config.get('sensor_height_mm',20.25))
    if not all(math.isfinite(x) and x>0 for x in [focal,width,height]):
        raise ValueError('焦距和有效传感器宽高必须为正的有限数值。')
    forward=unit([t-p for t,p in zip(target,position)])
    right=unit(cross(forward,vector(config.get('up',[0,0,1]))))
    up=cross(right,forward)
    rows=[]
    for point in config['points']:
        location=vector(point['position'])
        offset=[v-p for v,p in zip(location,position)]
        depth=dot(offset,forward)
        if depth<=0:
            rows.append({'name':point['name'],'depth_m':depth,'ndc':None,'in_frame':False})
            continue
        x=dot(offset,right);y=dot(offset,up)
        ndc=[2*focal*x/(width*depth),2*focal*y/(height*depth)]
        rows.append({'name':point['name'],'depth_m':depth,'ndc':ndc,'h_angle_deg':math.degrees(math.atan2(x,depth)),'v_angle_deg':math.degrees(math.atan2(y,depth)),'in_frame':all(abs(v)<=1+1e-9 for v in ndc)})
    return {'horizontal_fov_deg':math.degrees(2*math.atan(width/(2*focal))),'vertical_fov_deg':math.degrees(2*math.atan(height/(2*focal))),'points':rows,'all_in_frame':all(p['in_frame'] for p in rows),'limits':'只核验所给点的理想针孔投影；头部中心在框内不等于整张脸可见。请给头脸或身体边界点，另查遮挡、墙体、门扇、运动扫掠、真实镜头畸变及安全余量。空点集不代表任何事件已验证。'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_json',type=Path)
    args=parser.parse_args()
    try:
        result=check_camera(json.loads(args.input_json.read_text()))
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(str(error),file=sys.stderr)
        return 2
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['all_in_frame'] else 1


if __name__=='__main__':
    raise SystemExit(main())
