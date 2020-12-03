#!/usr/bin/python
import sys
import os
from lxml import etree

def writeShape(f, link):
    elem = link.find("origin")
    if elem is not None:
        att = elem.attrib.get('rpy')
        if att is not None:
           f.write('rel:<T t(%s) E(%s)>\n' % (elem.attrib['xyz'],att))
        else:
           f.write('rel:<T t(%s)>\n' % elem.attrib['xyz'])

    elem = link.find("geometry/box")
    if elem is not None:
        f.write('type:box size:[%s 0]\n' % elem.attrib['size'])

    elem = link.find("geometry/sphere")
    if elem is not None:
        f.write('type:sphere size:[0 0 0 %s]\n' % elem.attrib['radius'])

    elem = link.find("geometry/cylinder")
    if elem is not None:
        f.write('type:cylinder size:[0 0 %s %s]\n' % (elem.attrib['length'], elem.attrib['radius']))

    elem = link.find("geometry/mesh")
    if elem is not None:
        f.write('type:mesh mesh:\'%s\'' % elem.attrib['filename'])
        att = elem.attrib.get('scale')
        if att is not None:
            f.write('meshscale:[%s]\n' % elem.attrib['scale'])

    elem = link.find("material/color")
    if elem is not None:
        f.write('color:[%s]\n' % elem.attrib['rgba'])

    elem = link.find("material")
    if elem is not None:
        if elem.attrib['name'] is not None:
            f.write('colorName:%s\n' % elem.attrib['name'])


def urdf2rai(inFile):
  filename, extension = os.path.splitext(os.path.basename(inFile))
  dirname = os.path.dirname(inFile)
  outFile = dirname + "/" + filename + ".g"

  xmlData = etree.parse(inFile)
  links = xmlData.findall("/link")

  with open(outFile, 'w') as f:

    for link in links:
        name = link.attrib['name']
        f.write('body %s {' % name)

        elem = link.find("inertial/mass")
        if elem is not None:
            f.write('mass:%s' % elem.attrib['value'])

        elem = link.find("inertial/inertia")
        if elem is not None:
            f.write('inertiaTensor:[%s %s %s %s %s %s]' % (
                elem.attrib['ixx'],
                elem.attrib['ixy'],
                elem.attrib['ixz'],
                elem.attrib['iyy'],
                elem.attrib['iyz'],
                elem.attrib['izz']))

        f.write('}\n') # end of body

        # visual shape
        for visual in link.findall("visual"):
            f.write('shape visual %s_1 (%s) {\n  ' % (name, name))
            writeShape(f, visual)
            f.write(' visual }\n') # end of shape

        # collision shape
        for collision in link.findall("collision"):
            f.write('shape collision %s_0 (%s) {\n  ' % (name, name))
            f.write(' color:[.8 .2 .2 .5])\n')
            writeShape(f, collision)
            f.write(' contact:-2 }\n') # end of shape


    joints = xmlData.findall("/joint")
    for joint in joints:
        name = joint.attrib['name']
        if joint.find("child") is not None:
            f.write('joint %s (%s %s) {\n  ' % (name,
                                          joint.find("parent").attrib['link'],
                                          joint.find("child").attrib['link']))

            # figure out joint type
            att = joint.attrib.get('type')
            if att in ["revolute", "continuous"]:
                f.write('type:hingeX\n')
            if att == "prismatic":
                f.write('type:transX\n')
            if att == "fixed":
                f.write('type:rigid\n')

            elem = joint.find("mimic")
            if elem is not None:
                f.write('mimic:(%s)\n' % elem.attrib['joint'])

            elem = joint.find("axis")
            if elem is not None:
                f.write('axis:[%s]\n' % elem.attrib['xyz'])

            elem = joint.find("origin")
            if elem is not None:
                att = elem.attrib.get('rpy')
                if att is not None:
                    f.write('A:<T t(%s) E(%s)>\n' % (elem.attrib['xyz'], att))
                else:
                    f.write('A:<T t(%s)>\n' % (elem.attrib['xyz']))

            elem = joint.find("safety_controller")
            if elem is not None:
                lo = elem.attrib.get('soft_lower_limit')
                up = elem.attrib.get('soft_upper_limit')
                if lo is not None:
                    f.write('limits:[%s %s]\n' % (lo, up))

            elem = joint.find("limit")
            if elem is not None:
                lo = elem.attrib.get('lower')
                up = elem.attrib.get('upper')
                eff = elem.attrib.get('effort')
                vel = elem.attrib.get('velocity')
                if lo is not None:
                    f.write('limits:[%s %s]\n' % (lo, up))
                if vel is not None:
                    f.write('ctrl_limits:[%s %s 1]\n' % (vel, eff)) #the 3rd value is an acceleration limit

            f.write('}\n')

    print('Exported %s to %s'%(inFile,outFile))

if __name__ == '__main__':
  inFile = sys.argv[1]
  urdf2rai(inFile)
