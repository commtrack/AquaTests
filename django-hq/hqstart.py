#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import sys, os
filedir = os.path.dirname(__file__)
sys.path.append('..')
sys.path.append(os.path.join(filedir))
sys.path.append(os.path.join(filedir,'apps'))
sys.path.append(os.path.join(filedir,'..','rapidsms'))
sys.path.append(os.path.join(filedir,'..','rapidsms','apps'))

#rapidsms lib stuff
sys.path.append(os.path.join(filedir,'..','rapidsms','lib'))
sys.path.append(os.path.join(filedir,'..','rapidsms','lib','rapidsms'))
sys.path.append(os.path.join(filedir,'..','rapidsms','lib','rapidsms','webui'))
  

import rapidsms

if __name__ == "__main__":
    #print "rapidsms'ing"
    #print sys.argv
    #os.environ["RAPIDSMS_INI"] = 'hqsetup.ini'
    os.environ["RAPIDSMS_HOME"] = os.path.abspath(os.path.dirname(__file__))
    rapidsms.manager.start(sys.argv)
#some test comment