#!/usr/bin/python

import sys
from lxml import etree

inFile = sys.argv[1]
xmlData = etree.parse(inFile)

def writeShape(link):
    elem = link.find("origin")
    if elem is not None:
        att = elem.attrib.get('rpy')
        if att is not None:
           print 'rel:<T t(%s) E(%s)>' % (elem.attrib['xyz'], att),
        else:
           print 'rel:<T t(%s)>' % elem.attrib['xyz'],

    elem = link.find("geometry/box")
    if elem is not None:
        print 'type:box size:[%s 0]' % elem.attrib['size'],

    elem = link.find("geometry/sphere")
    if elem is not None:
        print 'type:sphere size:[0 0 0 %s]' % elem.attrib['radius'],

    elem = link.find("geometry/cylinder")
    if elem is not None:
        print 'type:cylinder size:[0 0 %s %s]' % (elem.attrib['length'], elem.attrib['radius']),

    elem = link.find("geometry/mesh")
    if elem is not None:
        print 'type:mesh mesh:\'%s\'' % elem.attrib['filename'],
        att = elem.attrib.get('scale')
        if att is not None:
            print 'meshscale:[%s]' % elem.attrib['scale'],

    elem = link.find("material/color")
    if elem is not None:
        print 'color:[%s]' % elem.attrib['rgba'],

    elem = link.find("material")
    if elem is not None:
        if elem.attrib['name'] is not None:
            print 'colorName:%s' % elem.attrib['name'],


links = xmlData.findall("/link")
for link in links:
    name = link.attrib['name']
    print 'body %s {' % name,

    elem = link.find("inertial/mass")
    if elem is not None:
        print 'mass:%s' % elem.attrib['value'],

    elem = link.find("inertial/inertia")
    if elem is not None:
        print 'inertiaTensor:[%s %s %s %s %s %s]' % (
            elem.attrib['ixx'],
            elem.attrib['ixy'],
            elem.attrib['ixz'],
            elem.attrib['iyy'],
            elem.attrib['iyz'],
            elem.attrib['izz']),

    print '}\n', # end of body

    # visual shape
    for visual in link.findall("visual"):
        print 'shape visual %s_1 (%s) {\n  ' % (name, name),
        writeShape(visual)
        print ' visual }\n', # end of shape

    # collision shape
    for collision in link.findall("collision"):
        print 'shape collision %s_0 (%s) {\n  ' % (name, name),
        print ' color:[.8 .2 .2 .5],',
        writeShape(collision)
        print ' contact:-2 }\n', # end of shape


joints = xmlData.findall("/joint")
for joint in joints:
    name = joint.attrib['name']
    if joint.find("child") is not None:
        print 'joint %s (%s %s) {\n  ' % (name,
                                      joint.find("parent").attrib['link'],
                                      joint.find("child").attrib['link']),

        # figure out joint type
        att = joint.attrib.get('type')
        if att in ["revolute", "continuous"]:
            print 'type:hingeX',
        if att == "prismatic":
            print 'type:transX',
        if att == "fixed":
            print 'type:rigid',

        elem = joint.find("mimic")
        if elem is not None:
            print 'mimic:(%s)' % elem.attrib['joint'],

        elem = joint.find("axis")
        if elem is not None:
            print 'axis:[%s]' % elem.attrib['xyz'],

        elem = joint.find("origin")
        if elem is not None:
            att = elem.attrib.get('rpy')
            if att is not None:
                print 'A:<T t(%s) E(%s)>' % (elem.attrib['xyz'], att),
            else:
                print 'A:<T t(%s)>' % (elem.attrib['xyz']),

        elem = joint.find("safety_controller")
        if elem is not None:
            lo = elem.attrib.get('soft_lower_limit')
            up = elem.attrib.get('soft_upper_limit')
            if lo is not None:
                print 'limits:[%s %s]' % (lo, up),

        elem = joint.find("limit")
        if elem is not None:
            lo = elem.attrib.get('lower')
            up = elem.attrib.get('upper')
            eff = elem.attrib.get('effort')
            vel = elem.attrib.get('velocity')
            if lo is not None:
                print 'limits:[%s %s]' % (lo, up),
            if vel is not None:
                print 'ctrl_limits:[%s %s 1]' % (vel, eff), #the 3rd value is an acceleration limit

        print '}\n',

#print(etree.tostring(links[22]))
#print(etree.tostring(joints[0]))
