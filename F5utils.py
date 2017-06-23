#!/usr/bin/env python
__author__ = "agrebin"
from f5parse import F5confParser
import pycontrol.pycontrol as pc

class LoadBalancer(object):
    def __init__(self, lbfile="", audit=False, vip_filter="", print_members=False):
        try:
            fp = open(lbfile)
        except (IOError, OSError):
            print "can't open file: ", lbfile
            raise IOError

        text = fp.read()
        parser = F5confParser()
        self.print_members = print_members
        ast = parser.parse(text, rule_name='file', semantics=Semantics())
        self.vip_filter = vip_filter
        self.audit = audit
        self.vips = []
        self.pools = self.load_pools(ast)
        self.oneconnects = self.load_oneconnects(ast)

        for command in ast:
            if command.vip_name is not None:
                if vip_filter:
                    if vip_filter in command.vip_name:
                        self.vips.append(self.vip_parse(command,self.pools,self.oneconnects))
                else:
                    self.vips.append(self.vip_parse(command,self.pools,self.oneconnects))

    def load_oneconnects(self,ast):
        oneconnects=[]
        for command in ast:
            if command.oneconnect_name is not None:
                oneconnects.append(self.oneconnect_parse(command))
        return oneconnects

    def load_pools(self,ast):
        pools = []
        for command in ast:
            if command.pool_name is not None:
                pools.append(self.pool_parse(command))
        return pools

    def pool_parse(self,command):
        members = []
        name = ""
        if command.pool_name is not None:
            name = command.pool_name
        if command.pool_def is not None:
            for cmd in command.pool_def:
                if cmd is not None:
                    members.append((cmd.ip, cmd.port))
        return Pool(name,members)

    def find_pool(self,pool_name,pools=[]):
        ret = Pool()
        for pool in pools:
            if pool_name.strip() == pool.name.strip():
                ret = pool
        return ret

    def find_oneconnect(self,oc_name, oneconnects):
        ret = Oneconnect()
        for oc in oneconnects:
            if oc_name.strip() in oc.name.strip():
                ret = oc
        return ret

    def vip_parse(self,command, pools=[], oneconnects=[]):
        name = ""
        pool = Pool()
        dest = ('',0)
        oneconnect = Oneconnect()
        profiles = []
        if command.vip_name is not None:
            name = command.vip_name
            if command.vip_block is not None:
                for subcmd in command.vip_block:
                    if subcmd.pool_call is not None:
                        pool = self.find_pool(subcmd.pool_call,pools)
                    elif subcmd.dest is not None:
                        dest = (subcmd.dest.ip, subcmd.dest.port)
                    elif subcmd.profiles is not None:
                        for profile in subcmd.profiles[2]:
                            if "ONECONNECT" in profile:
                               oneconnect = self.find_oneconnect(profile,oneconnects)
                            else:
                             profiles.append(profile)
        return(Vip(name,dest,pool,oneconnect,profiles))

    def oneconnect_parse(self,command):
        name = command.oneconnect_name
        maxsize = 0
        for subcmd in command.profiledef:
            if subcmd.maxsize is not None:
                maxsize = int(subcmd.maxsize.size)
                if subcmd.maxsize.q:
                    if subcmd.maxsize.q in 'kK':
                        maxsize *= 1000
                    if subcmd.maxsize.q in 'mM':
                        maxsize *= 1000000
                    if subcmd.maxsize.q in 'Gg':
                        maxsize *= 1000000000
        return Oneconnect(name, maxsize)

    def find_member(self, ip="", print_members=False):
        ret = []
        for vip in self.vips:
            if vip.pool.name:
                if ip in [ tup[0] for tup in vip.pool.members ]:
                    if print_members:
                        ret.append((vip, str(vip.pool)))
                    else:
                        ret.append((vip, ''))
        return ret

    def __str__(self):
        ret = ""
        for vip in self.vips:
            if self.audit:
                if vip.warning:
                    ret+=str(vip)
            else:
                if self.print_members:
                    ret+= str(vip.pool)
                ret += str(vip)
        return ret

class Oneconnect(object):
    def __init__(self, name="", maxsize=0):
        self.name = name
        self.maxsize = int(maxsize)

    def __str__(self):
        ret = ""
        if self.name:
            ret =  "Oneconnect name: %s\n" % self.name
            ret += "Max Size       : %d (%d members)\n" % (int(self.maxsize), int(self.maxsize) / 3900 )
        return ret

class Pool(object):
    def __init__(self, name='', members=[]):
        self.members = members
        self.name = name

    def __str__(self):
        ret = "Pool Name : %s\n" % self.name
        ret += "Members  (%d): \n" % len(self.members)
        for (ip, port) in self.members:
            ret += "IP: %s:%s\n" % (ip, port)
        ret += "==============================\n"
        return ret

class Vip(object):
    def __init__(self, name="",dest=('',0),pool=Pool(),oneconnect=Oneconnect(),profiles=[]):
        self.name = name
        self.dest = dest
        self.pool = pool
        self.oneconnect = oneconnect
        self.profiles = profiles
        self.warning = False

        if len(self.pool.members) != self.oneconnect.maxsize / 3900:
            self.warning = True



    def __str__(self):
        ret = "Vip Name     : %s\n" % self.name
        ret += "Vip Pool     : %s (%d member[s])\n" % (self.pool.name, len(self.pool.members) )
        ret += "Vip Dest     : %s:%s\n" % (self.dest[0], self.dest[1])
        if self.profiles:
            ret += "Vip Profiles : %s\n" % [str(x) for x in self.profiles if x]
        if self.oneconnect is not Oneconnect():
           ret += "%s\n" % str(self.oneconnect)

        if (len(self.pool.members) != (self.oneconnect.maxsize / 3900) ):
            ret += "===WARNING ONECONNECT PROFILE WRONG ===\n"
            ret += "Pool %s has %d members " % (self.pool.name, len(self.pool.members))
            ret += "Oneconect %s maxsize is %d (for %d members)\n" % \
                  (self.oneconnect.name, self.oneconnect.maxsize, self.oneconnect.maxsize / 3900 )
        ret += "-------------------------------------------------------------------------------\n"
        return str(ret)

class LoadBalancerPycontrol(LoadBalancer):
    def __init__(self, lbhost = "", lbuser = "", lbpass="", audit=False, vip_filter="" ):

        self.LoadBalancer=pc.BIGIP(self.lbhost,lbuser,lbpass,fromurl=True, \
                                   wsdls=['LocalLB.VirtualServer', 'LocalLB.Pool',  'LocalLB.ProfileOneConnect'])
        self.lbhost = lbip
        self.lbuser = lbuser
        self.lbpass = lbpass
        self.vip_filter = vip_filter
        self.audit = audit
        self.vips = self.load_vips()
        self.pools = self.load_pools()
        self.oneconnects = self.load_oneconnects()


    def load_vips(self):
        vips=self.LoadBalancer.VirtualServer.get_list()

class Semantics(object):
    @staticmethod
    def commands(ast):
        if ast.pool is not None:
            return ast.pool
        elif ast.vip is not None:
            return ast.vip
        elif ast.oneconnect is not None:
            return ast.oneconnect

    @staticmethod
    def pblock(ast):
        for cmds in ast[1]:
            if cmds.cmd is not None:
                if cmds.cmd.members is not None:
                    return cmds.cmd.members

    @staticmethod
    def mblock(ast):
        return ast.member

    @staticmethod
    def member(ast):
        if ast.member_data[0] is not None:
            return ast.member_data[0]

    @staticmethod
    def pool_call(ast):
        if ast.pool is not None:
            return ast.pool

    @staticmethod
    def vip_block(ast):
        ret = []
        for cmd in ast[1]:
            if cmd.pool_call is None and \
                            cmd.dest is None and \
                            cmd.profiles is None:
                continue
            ret.append(cmd)
        return ret

    @staticmethod
    def profiledef(ast):
        return ast[1]

    @staticmethod
    def dest(ast):
        if ast is not None:
            return ast.ipport

    @staticmethod
    def profile_call(ast):
        if ast.profile != '':
            return ast.profile


#### MAIN ###########
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Simple parser for F5 exported config files Author: Adrian Grebin")
    parser.add_argument('file', help="the input file to parse")
    parser.add_argument('--ip', help="Find VIPs and Pool names on which an IP is referenced as member")
    parser.add_argument('-m', help="Show Pool Members", action="store_true")
    parser.add_argument('--audit', help="Audit VIPS for Oneconnect issues", action="store_true")
    parser.add_argument('--vip', help ="Search for Vip names containg vip")
    args = parser.parse_args()

    print "Parsing file %s\n" % args.file
    LB = LoadBalancer(lbfile=args.file,audit=args.audit,vip_filter=args.vip, print_members=args.m)

    if args.ip:
        print "Finding: %s" % args.ip
        found = LB.find_member(ip=args.ip, print_members=args.m)
        if found:
            for (vip, members) in found:
                print vip
                if members:
                    print members
            exit(0)
        else:
            print "IP: ", args.ip, " Is not referenced by any VIPs on:", args.file
            exit(1)
    else:
        print LB
        exit(0)


