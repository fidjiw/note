#@author:九世
#@time:2020/4/6
#@file:Permission_enhancement.py

import os
from colorama import Fore,init
import subprocess
import optparse
import chardet
import psutil
import winreg
import re
import datetime

init(wrap=True)

class Permission_enhancement(object):
    def __init__(self):
        parser=optparse.OptionParser()
        parser.add_option('--info',dest='info',action='store_true',help='Get current user information')
        parser.add_option('--service',dest='service',action='store_true',help='Enumerate non-default services')
        parser.add_option('--sysinfo',dest='sysinfo',action='store_true',help='Get system information')
        parser.add_option('--registry',dest='registry',action='store_true',help='Get registry information')
        parser.add_option('--vuln',dest='vuln',action='store_true',help='Patch vulnerability query')
        parser.add_option('--avquery',dest='avquery',action='store_true',help='Antivirus query')
        parser.add_option('--other',dest='other',action='store_true',help='other information')
        parser.add_option('--all',dest='all',action='store_true',help='Get all')
        note=Fore.GREEN+'绿色代表高权限\n'+Fore.YELLOW+'黄色代表当前用户拥有的\n'+Fore.RED+'红色代表可能提升权限'
        option,args=parser.parse_args()
        if option.info:
            self.getuserinfo()
        elif option.service:
            self.getservice()
        elif option.sysinfo:
            self.systeminfo()
        elif option.registry:
            self.registry()
        elif option.vuln:
            self.getvuln()
        elif option.avquery:
            self.avquery()
        elif option.other:
            self.getorher()
        elif option.all:
            self.getuserinfo()
            self.getservice()
            self.systeminfo()
            self.registry()
            self.getvuln()
            self.avquery()
            self.getorher()
        else:
            print(note)
            parser.print_help()

    def runcmd(self,command):
        runcmd = subprocess.run(command, True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = runcmd.stdout
        enc = chardet.detect(data)
        if enc['encoding']==None:
            encode="utf-8"
        else:
            encode=enc['encoding']
        jg = bytes.decode(data, encoding=encode)
        return jg

    def getuserinfo(self):
        currentuser=""
        administrators=[]
        command={"Currentusername:":"wmic computersystem get username","Userid:":"wmic useraccount get name,sid"}
        for c in command:
            jg=self.runcmd(command[c])
            print(Fore.BLUE+'[+] '+Fore.WHITE+c)
            if c=="Currentusername:":
                currentuser+=str(jg).split('\\')[-1].rstrip().lstrip()
                print(jg.replace('\r\n',''))
                print('')
            elif c=="Userid:":
                zz=re.findall('.*'.format(currentuser),jg)
                for z in zz:
                    if z!='':
                        if len(re.findall('.* S-.*-500',str(z)))>0:
                            print(Fore.GREEN+z+Fore.WHITE)
                        elif currentuser in str(z):
                            print(Fore.YELLOW+str(z).replace('\r\r','')+Fore.WHITE)
                        else:
                            print(str(z).replace('\r\r',''))


        print(Fore.BLUE+'[+] '+Fore.WHITE+'Admin group')
        data=os.popen("wmic group get name | findstr Admin")
        group=str(data.read()).rstrip().lstrip().split('\n')
        for g in group:
            print(g)
            administrators.append(g)
        print('')

        print(Fore.BLUE+'[+] '+Fore.WHITE+'current username info')
        jg=self.runcmd('net1 user {}'.format(currentuser))
        print(jg)

        print(Fore.BLUE+'[+] '+Fore.WHITE+'session token query')
        tokenlist = []
        ids = psutil.pids()
        for id in ids:
            try:
                username = psutil.Process(id).username()
                if username not in tokenlist and id != 0 and id != 4:
                    tokenlist.append(username)
            except:
                pass

        for t in tokenlist:
            print(t)
        print('')

    def getservice(self):
        print(Fore.BLUE+'[+] '+Fore.WHITE+' status Runing service')
        data="".join(self.runcmd('wmic service where (state="running") get name,startmode,caption,StartName').split('\n'))
        print(data)

        print(Fore.BLUE+'[+] '+Fore.WHITE+' Services that the current user can modify through the control manager')
        services=[]
        sucess=[]
        keys=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,'SYSTEM\\CurrentControlSet\\services')
        calc=0
        try:
            while True:
                r_keys=winreg.EnumKey(keys,calc)
                try:
                    path='SYSTEM\\CurrentControlSet\\services\\{}'.format(r_keys)
                    keys2=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,path)
                    winreg.QueryValueEx(keys2,'ImagePath')
                    services.append('SYSTEM\\CurrentControlSet\\services\\{}'.format(r_keys))
                except:
                    pass
                calc+=1
        except:
            pass

        for s in services:
            try:
                keys3=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,s)
                winreg.SetValue(keys3,"test",winreg.REG_SZ,"test")
                asscess=winreg.QueryValueEx(keys3,'ObjectName')
                sucess.append({'Servicename':str(s).split('\\')[-1],'StartName':asscess[0]})
            except:
                pass

        print(Fore.BLUE+'[!] '+Fore.WHITE+' Modifiable service path,'+Fore.YELLOW+'If you cannot modify ImagePath, there may be antivirus'+Fore.WHITE)
        for s in sucess:
            for k in s:
                print('{}:{} '.format(k,s[k]),end='')
            print('')
        print('')

        print(Fore.BLUE+'[+] '+Fore.WHITE+'All services with modifiable binaries')
        mkdirs=[]
        data2=self.runcmd('wmic.exe service where (state="running") get Name,PathName').split('\r\n')
        for d in data2:
            path=re.findall('[A-z-a-z]{1}:.*',str(d))
            if len(path)>0:
                paths=str(path[0]).rstrip().replace('\r','').replace('"','').split('\\')
                del paths[-1]
                paths="\\".join(paths).lower()
                if not 'c:\\windows\\system32' in paths and not 'c:\\windows\\syswow64' in paths:
                    try:
                        dk=open('{}\\errorxxxxxxxxx.txt'.format(paths),'w')
                        dk.close()
                        if os.path.exists('{}\\errorxxxxxxxxx.txt'.format(paths)):
                            mkdirs.append(paths)
                            os.remove('{}\\errorxxxxxxxxx.txt'.format(paths))
                    except:
                        pass

        print(Fore.BLUE+'[+] '+Fore.WHITE+'Controllable service binary folder path')
        for c in data2:
            for m in mkdirs:
                if str(m) in str(c).rstrip().replace('\r','').lower():
                    print('{}'.format(str(c).rstrip().replace('\r','').lower()))
        print('')

        print(Fore.BLUE + '[+] ' + Fore.WHITE + 'Missing "service path')
        mkdirss=[]
        for d in data2:
            path=re.findall('[A-z-a-z]{1}:.*',str(d))
            if len(path)>0:
                if not '"' in str(path[0]):
                    paths=str(path[0]).rstrip().replace('\r','').split('\\')
                    y_paths = "\\".join(paths).lower()
                    del paths[-1]
                    paths = "\\".join(paths).lower()
                    if not 'c:\\windows\\system32' in paths and not 'c:\\windows\\syswow64' in paths:
                        paths = str(paths).split('\\')
                        calc = len(paths)
                        while True:
                            calc = calc
                            path = ""
                            for r in range(0, calc):
                                path += paths[r]
                                path += "\\"
                            try:
                                dk = open('{}\\errorxxxxxxxxx.txt'.format(path), 'w')
                                dk.close()
                                if os.path.exists('{}\\errorxxxxxxxxx.txt'.format(path)):
                                    if y_paths not in mkdirss:
                                        mkdirss.append(y_paths)
                                    os.remove('{}\\errorxxxxxxxxx.txt'.format(path))
                            except:
                                pass
                            calc -= 1
                            if calc == 0:
                                break

        for c in data2:
            for m in mkdirss:
                if str(m) in str(c).rstrip().replace('\r','').lower():
                    print('{}'.format(str(c).rstrip().replace('\r','').lower()))
        print('')

    def systeminfo(self):
        data={"Locate system files":"wmic environment get Description, VariableValue","Get a list of installed applications":"wmic product get name,version",
              "Get system driver details":"wmic sysdriver get Caption, Name, PathName, ServiceType, State, Status /format:list",
              "bios":"wmic bios get serialNumber","Get memory cache data":"wmic memcache get Name, BlockSize, Purpose, MaxCacheSize, Status",
              "Get memory chip information":"wmic memorychip get PartNumber, SerialNumber","Determine whether the target system is a virtual machine":"wmic onboarddevice get Caption,CreationClassName,Description",
              "Get anti-virus product details":r"wmic /namespace:\\root\securitycenter2 path antivirusproduct GET displayName,productState, pathToSignedProductExe"}
        for d in data:
            print(Fore.BLUE+'[+]'+Fore.WHITE+'{}'.format(d))
            datas="".join(self.runcmd(data[d]).split('\s'))
            print(datas)
            print('')
        print('')

    def registry(self):
        uacstatus={}
        level=""
        data='''ConsentPromptBehaviorAdmin: level\nEnableLUA: Whether to turn off UAC\nPromptOnSecureDesktop: Does the desktop turn black'''
        print(Fore.BLUE+'[+] '+Fore.WHITE+'UAC detection')
        keys = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System')
        ConsentPromptBehaviorAdmin=winreg.QueryValueEx(keys, 'ConsentPromptBehaviorAdmin')
        EnableLUA=winreg.QueryValueEx(keys,'EnableLUA')
        PromptOnSecureDesktop=winreg.QueryValueEx(keys,'PromptOnSecureDesktop')
        uacstatus['ConsentPromptBehaviorAdmin']=ConsentPromptBehaviorAdmin[0]
        uacstatus['EnableLUA']=EnableLUA[0]
        uacstatus['PromptOnSecureDesktop']=PromptOnSecureDesktop[0]

        if uacstatus['ConsentPromptBehaviorAdmin']==0 and uacstatus['EnableLUA']==0 and uacstatus['PromptOnSecureDesktop']==0:
            level="off"
        elif uacstatus['ConsentPromptBehaviorAdmin']==5 and uacstatus['EnableLUA']==1 and uacstatus['PromptOnSecureDesktop']==0:
            level='low'
        elif uacstatus['ConsentPromptBehaviorAdmin'] == 5 and uacstatus['EnableLUA'] == 1 and uacstatus['PromptOnSecureDesktop'] == 1:
            level='intermediate'
        elif uacstatus['ConsentPromptBehaviorAdmin'] == 2 and uacstatus['EnableLUA'] == 1 and uacstatus['PromptOnSecureDesktop'] == 1:
            level='hight'

        print(data)
        print('')
        print('uac level={}'.format(level))
        for u in uacstatus:
            print('{}:{}'.format(u,uacstatus[u]))

        print('')
        print(Fore.BLUE+'[+] '+Fore.WHITE+'Lsa status')
        try:
            keys = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,'SYSTEM\\CurrentControlSet\\Control\\LSA')
            lsa = winreg.QueryValueEx(keys, 'RunAsPPL')
            if lsa[1]==1:
                print('LSA protection:ON')
            else:
                print('LSA protection:OFF')
        except:
            print('LSA protection:OFF')

        print('')
        print(Fore.BLUE + '[+] ' + Fore.WHITE + 'AlwaysInstallElevated status')
        try:
            keys = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Policies\\Microsoft\\Windows\\Installer')
            AlwaysInstallElevated = winreg.QueryValueEx(keys, 'AlwaysInstallElevated')
            if AlwaysInstallElevated[0] == 1:
                print('AlwaysInstallElevated protection:ON')
            else:
                print('AlwaysInstallElevated protection:OFF')
        except:
            print('AlwaysInstallElevated protection:OFF')

        print('')
    def getvuln(self):
        print(Fore.BLUE+'[+] '+Fore.WHITE+'Patch vulnerability query')
        datas = '''MS17-010 　[KB4013389]　　[Windows Kernel Mode Drivers]　　(windows 7/2008/2003/XP)
        MS16-135 　[KB3199135]　　[Windows Kernel Mode Drivers]　　(2016)
        MS16-111 　[KB3186973]　　[kernel api]　　(Windows 10 10586 (32/64)/8.1)
        MS16-098 　[KB3178466]　　[Kernel Driver]　　(Win 8.1)
        MS16-075 　[KB3164038]　　[Hot Potato]　　(2003/2008/7/8/2012)
        MS16-034 　[KB3143145]　　[Kernel Driver]　　(2008/7/8/10/2012)
        MS16-032 　[KB3143141]　　[Secondary Logon Handle]　　(2008/7/8/10/2012)
        MS16-016 　[KB3136041]　　[WebDAV]　　(2008/Vista/7)
        MS16-014 　[K3134228]　　[remote code execution]　　(2008/Vista/7)
        MS15-097 　[KB3089656]　　[remote code execution]　　(win8.1/2012)
        MS15-076 　[KB3067505]　　[RPC]　　(2003/2008/7/8/2012)
        MS15-077 　[KB3077657]　　[ATM]　　(XP/Vista/Win7/Win8/2000/2003/2008/2012)
        MS15-061 　[KB3057839]　　[Kernel Driver]　　(2003/2008/7/8/2012)
        MS15-051 　[KB3057191]　　[Windows Kernel Mode Drivers]　　(2003/2008/7/8/2012)
        MS15-015 　[KB3031432]　　[Kernel Driver]　　(Win7/8/8.1/2012/RT/2012 R2/2008 R2)
        MS15-010 　[KB3036220]　　[Kernel Driver]　　(2003/2008/7/8)
        MS15-001 　[KB3023266]　　[Kernel Driver]　　(2008/2012/7/8)
        MS14-070 　[KB2989935]　　[Kernel Driver]　　(2003)
        MS14-068 　[KB3011780]　　[Domain Privilege Escalation]　　(2003/2008/2012/7/8)
        MS14-058 　[KB3000061]　　[Win32k.sys]　　(2003/2008/2012/7/8)
        MS14-066 　[KB2992611]　　[Windows Schannel Allowing remote code execution] (VistaSP2/7 SP1/8/Windows 8.1/2003 SP2/2008 SP2/2008 R2 SP1/2012/2012 R2/Windows RT/Windows RT 8.1)
        MS14-040 　[KB2975684]　　[AFD Driver]　　(2003/2008/2012/7/8)
        MS14-002 　[KB2914368]　　[NDProxy]　　(2003/XP)
        MS13-053 　[KB2850851]　　[win32k.sys]　　(XP/Vista/2003/2008/win 7)
        MS13-046 　[KB2840221]　　[dxgkrnl.sys]　　(Vista/2003/2008/2012/7)
        MS13-005 　[KB2778930]　　[Kernel Mode Driver]　　(2003/2008/2012/win7/8)
        MS12-042 　[KB2972621]　　[Service Bus]　　(2008/2012/win7)
        MS12-020 　[KB2671387]　　[RDP]　　(2003/2008/7/XP)
        MS11-080 　[KB2592799]　　[AFD.sys]　　(2003/XP)
        MS11-062 　[KB2566454]　　[NDISTAPI]　　(2003/XP)
        MS11-046 　[KB2503665]　　[AFD.sys]　　(2003/2008/7/XP)
        MS11-011 　[KB2393802]　　[kernel Driver]　　(2003/2008/7/XP/Vista)
        MS10-092 　[KB2305420]　　[Task Scheduler]　　(2008/7)
        MS10-065 　[KB2267960]　　[FastCGI]　　(IIS 5.1, 6.0, 7.0, and 7.5)
        MS10-059 　[KB982799]　　 [ACL-Churraskito]　　(2008/7/Vista)
        MS10-048 　[KB2160329]　　[win32k.sys]　　(XP SP2 & SP3/2003 SP2/Vista SP1 & SP2/2008 Gold & SP2 & R2/Win7)
        MS10-015 　[KB977165]　　 [KiTrap0D]　　(2003/2008/7/XP)
        MS10-012 　[KB971468]　　[SMB Client Trans2 stack overflow]　　(Windows 7/2008R2)
        MS09-050 　[KB975517]　　 [Remote Code Execution]　　(2008/Vista)
        MS09-020 　[KB970483]　　 [IIS 6.0]　　(IIS 5.1 and 6.0)
        MS09-012 　[KB959454]　　 [Chimichurri]　　(Vista/win7/2008/Vista)
        MS08-068 　[KB957097]　　 [Remote Code Execution]　　(2000/XP)
        MS08-067 　[KB958644]　　 [Remote Code Execution]　　(Windows 2000/XP/Server 2003/Vista/Server 2008)
        MS08-066 　[KB956803]　　 [AFD.sys]　　(Windows 2000/XP/Server 2003)
        MS08-025 　[KB941693]　　 [Win32.sys]　　(XP/2003/2008/Vista)
        MS06-040 　[KB921883]　　 [Remote Code Execution]　　(2003/xp/2000)
        MS05-039 　[KB899588]　　 [PnP Service]　　(Win 9X/ME/NT/2000/XP/2003)
        MS03-026 　[KB823980]　　 [Buffer Overrun In RPC Interface]　　(/NT/2000/XP/2003)'''.split('\n')

        data = str(self.runcmd('wmic qfe GET hotfixid')).split('\n')
        for j in data:
            if j != '':
                jc = str(j).rstrip().replace(' ', '')
                if jc != 'HotFixID':
                    for k in datas:
                        if jc not in str(k).rstrip(''):
                            print(k)

        print('explist:https://github.com/SecWiki/windows-kernel-exploits')

    def avquery(self):
        print(Fore.BLUE+'[+] '+Fore.WHITE+'Antivirus query')
        avlist = {
            "360tray": "360安全卫士-实时保护",
            "360safe": "360安全卫士-主程序",
            "ZhuDongFangYu": "360安全卫士-主动防御",
            "360sd": "360杀毒",
            "a2guard": "a-squared杀毒",
            "ad-watch": "Lavasoft杀毒",
            "cleaner8": "The Cleaner杀毒",
            "vba32lder": "vb32杀毒",
            "MongoosaGUI": "Mongoosa杀毒",
            "CorantiControlCenter32": "Coranti2012杀毒",
            "F-PROT": "F-Prot AntiVirus",
            "CMCTrayIcon": "CMC杀毒",
            "K7TSecurity": "K7杀毒",
            "UnThreat": "UnThreat杀毒",
            "CKSoftShiedAntivirus4": "Shield Antivirus杀毒",
            "AVWatchService": "VIRUSfighter杀毒",
            "ArcaTasksService": "ArcaVir杀毒",
            "iptray": "Immunet杀毒",
            "PSafeSysTray": "PSafe杀毒",
            "nspupsvc": "nProtect杀毒",
            "SpywareTerminatorShield": "SpywareTerminator杀毒",
            "BKavService": "Bkav杀毒",
            "MsMpEng": "Microsoft Security Essentials",
            "SBAMSvc": "VIPRE",
            "ccSvcHst": "Norton杀毒",
            "f-secure": "冰岛",
            "avp": "Kaspersky",
            "KvMonXP": "江民杀毒",
            "RavMonD": "瑞星杀毒",
            "Mcshield": "Mcafee",
            "Tbmon": "Mcafee",
            "Frameworkservice": "Mcafee",
            "egui": "ESET NOD32",
            "ekrn": "ESET NOD32",
            "eguiProxy": "ESET NOD32",
            "kxetray": "金山毒霸",
            "knsdtray": "可牛杀毒",
            "TMBMSRV": "趋势杀毒",
            "avcenter": "Avira(小红伞)",
            "avguard": "Avira(小红伞)",
            "avgnt": "Avira(小红伞)",
            "sched": "Avira(小红伞)",
            "ashDisp": "Avast网络安全",
            "rtvscan": "诺顿杀毒",
            "ccapp": "Symantec Norton",
            "NPFMntor": "Norton杀毒软件相关进程",
            "ccSetMgr": "赛门铁克",
            "ccRegVfy": "Norton杀毒软件自身完整性检查程序",
            "vptray": "Norton病毒防火墙-盾牌图标程序",
            "ksafe": "金山卫士",
            "QQPCRTP": "QQ电脑管家",
            "Miner": "流量矿石",
            "AYAgent": "韩国胶囊",
            "patray": "安博士",
            "V3Svc": "安博士V3",
            "avgwdsvc": "AVG杀毒",
            "QUHLPSVC": "QUICK HEAL杀毒",
            "mssecess": "微软杀毒",
            "SavProgress": "Sophos杀毒",
            "SophosUI": "Sophos杀毒",
            "SophosFS": "Sophos杀毒",
            "SophosHealth": "Sophos杀毒",
            "SophosSafestore64": "Sophos杀毒",
            "SophosCleanM": "Sophos杀毒",
            "fsavgui": "F-Secure杀毒",
            "vsserv": "比特梵德",
            "remupd": "熊猫卫士",
            "FortiTray": "飞塔",
            "safedog": "安全狗",
            "parmor": "木马克星",
            "Iparmor": "木马克星",
            "beikesan": "贝壳云安全",
            "KSWebShield": "金山网盾",
            "TrojanHunter": "木马猎手",
            "GG": "巨盾网游安全盾",
            "adam": "绿鹰安全精灵",
            "AST": "超级巡警",
            "ananwidget": "墨者安全专家",
            "AVK": "GData",
            "avg": "AVG Anti-Virus",
            "spidernt": "Dr.web",
            "avgaurd": "Avira Antivir",
            "vsmon": "ZoneAlarm",
            "cpf": "Comodo",
            "outpost": "Outpost Firewall",
            "rfwmain": "瑞星防火墙",
            "kpfwtray": "金山网镖",
            "FYFireWall": "风云防火墙",
            "MPMon": "微点主动防御",
            "pfw": "天网防火墙",
            "S": "在抓鸡",
            "1433": "在扫1433",
            "DUB": "在爆破",
            "ServUDaemon": "发现S-U",
            "BaiduSdSvc": "百度杀毒-服务进程",
            "BaiduSdTray": "百度杀毒-托盘进程",
            "BaiduSd": "百度杀毒-主程序",
            "SafeDogGuardCenter": "安全狗",
            "safedogupdatecenter": "安全狗",
            "safedogguardcenter": "安全狗",
            "SafeDogSiteIIS": "安全狗",
            "SafeDogTray": "安全狗",
            "SafeDogServerUI": "安全狗",
            "D_Safe_Manage": "D盾",
            "d_manage": "D盾",
            "yunsuo_agent_service": "云锁",
            "yunsuo_agent_daemon": "云锁",
            "HwsPanel": "护卫神",
            "hws_ui": "护卫神",
            "hws": "护卫神",
            "hwsd": "护卫神",
            "hipstray": "火绒",
            "wsctrl": "火绒",
            "usysdiag": "火绒",
            "WEBSCANX": "网络病毒克星",
            "SPHINX": "SPHINX防火墙",
            "bddownloader": "百度卫士",
            "baiduansvx": "百度卫士-主进程",
            "AvastUI": "Avast!5主程序",
            "emet_agent": "EMET",
            "emet_service": "EMET",
            "firesvc": "McAfee",
            "firetray": "McAfee",
            "hipsvc": "McAfee",
            "mfevtps": "McAfee",
            "mcafeefire": "McAfee",
            "scan32": "McAfee",
            "shstat": "McAfee",
            "vstskmgr": "McAfee",
            "engineserver": "McAfee",
            "mfeann": "McAfee",
            "mcscript": "McAfee",
            "updaterui": "McAfee",
            "udaterui": "McAfee",
            "naprdmgr": "McAfee",
            "cleanup": "McAfee",
            "cmdagent": "McAfee",
            "frminst": "McAfee",
            "mcscript_inuse": "McAfee",
            "mctray": "McAfee",
            "AAWTray": "已知杀软进程,名称暂未收录",
            "Ad-Aware": "已知杀软进程,名称暂未收录",
            "MSASCui": "已知杀软进程,名称暂未收录",
            "_avp32": "卡巴斯基",
            "_avpcc": "卡巴斯基",
            "_avpm": "卡巴斯基",
            "aAvgApi": "AVG",
            "ackwin32": "已知杀软进程,名称暂未收录",
            "adaware": "已知杀软进程,名称暂未收录",
            "advxdwin": "已知杀软进程,名称暂未收录",
            "agentsvr": "已知杀软进程,名称暂未收录",
            "agentw": "已知杀软进程,名称暂未收录",
            "alertsvc": "Norton AntiVirus",
            "alevir": "已知杀软进程,名称暂未收录",
            "alogserv": "McAfee VirusScan",
            "amon9x": "已知杀软进程,名称暂未收录",
            "anti-trojan": "Anti-Trojan Elite",
            "antivirus": "已知杀软进程,名称暂未收录",
            "ants": "已知杀软进程,名称暂未收录",
            "apimonitor": "已知杀软进程,名称暂未收录",
            "aplica32": "已知杀软进程,名称暂未收录",
            "apvxdwin": "已知杀软进程,名称暂未收录",
            "arr": "Application Request Route",
            "atcon": "已知杀软进程,名称暂未收录",
            "atguard": "AntiVir",
            "atro55en": "已知杀软进程,名称暂未收录",
            "atupdater": "已知杀软进程,名称暂未收录",
            "atwatch": "Mustek",
            "au": "NSIS",
            "aupdate": "Symantec",
            "auto-protect.nav80try": "已知杀软进程,名称暂未收录",
            "autodown": "AntiVirus AutoUpdater",
            "autotrace": "已知杀软进程,名称暂未收录",
            "autoupdate": "已知杀软进程,名称暂未收录",
            "avconsol": "McAfee",
            "ave32": "已知杀软进程,名称暂未收录",
            "avgcc32": "AVG",
            "avgctrl": "AVG",
            "avgemc": "AVG",
            "avgrsx": "AVG",
            "avgserv": "AVG",
            "avgserv9": "AVG",
            "avgw": "AVG",
            "avkpop": "G DATA SOFTWARE AG",
            "avkserv": "G DATA SOFTWARE AG",
            "avkservice": "G DATA SOFTWARE AG",
            "avkwctl9": "G DATA SOFTWARE AG",
            "avltmain": "Panda Software Aplication",
            "avnt": "H+BEDV Datentechnik GmbH",
            "avp32": "Kaspersky Anti-Virus",
            "avpcc": " Kaspersky AntiVirus",
            "avpdos32": " Kaspersky AntiVirus",
            "avpm": " Kaspersky AntiVirus",
            "avptc32": " Kaspersky AntiVirus",
            "avpupd": " Kaspersky AntiVirus",
            "avsched32": "已知杀软进程,名称暂未收录",
            "avsynmgr": "McAfee",
            "avwin": " H+BEDV",
            "avwin95": "已知杀软进程,名称暂未收录",
            "avwinnt": "已知杀软进程,名称暂未收录",
            "avwupd": "已知杀软进程,名称暂未收录",
            "avwupd32": "已知杀软进程,名称暂未收录",
            "avwupsrv": "已知杀软进程,名称暂未收录",
            "avxmonitor9x": "已知杀软进程,名称暂未收录",
            "avxmonitornt": "已知杀软进程,名称暂未收录",
            "avxquar": "已知杀软进程,名称暂未收录",
            "backweb": "已知杀软进程,名称暂未收录",
            "bargains": "Exact Advertising SpyWare",
            "bd_professional": "已知杀软进程,名称暂未收录",
            "beagle": "Avast",
            "belt": "已知杀软进程,名称暂未收录",
            "bidef": "已知杀软进程,名称暂未收录",
            "bidserver": "已知杀软进程,名称暂未收录",
            "bipcp": "已知杀软进程,名称暂未收录",
            "bipcpevalsetup": "已知杀软进程,名称暂未收录",
            "bisp": "已知杀软进程,名称暂未收录",
            "blackd": "BlackICE",
            "blackice": "BlackICE",
            "blink": "micromedia",
            "blss": "CBlaster",
            "bootconf": "已知杀软进程,名称暂未收录",
            "bootwarn": "Symantec",
            "borg2": "已知杀软进程,名称暂未收录",
            "bpc": "Grokster",
            "brasil": "Exact Advertising",
            "bs120": "已知杀软进程,名称暂未收录",
            "bundle": "已知杀软进程,名称暂未收录",
            "bvt": "已知杀软进程,名称暂未收录",
            "ccevtmgr": "Norton Internet Security",
            "ccpxysvc": "已知杀软进程,名称暂未收录",
            "cdp": "CyberLink Corp.",
            "cfd": "Motive Communications",
            "cfgwiz": " Norton AntiVirus",
            "cfiadmin": "已知杀软进程,名称暂未收录",
            "cfiaudit": "已知杀软进程,名称暂未收录",
            "cfinet": "已知杀软进程,名称暂未收录",
            "cfinet32": "已知杀软进程,名称暂未收录",
            "claw95": "已知杀软进程,名称暂未收录",
            "claw95cf": "已知杀软进程,名称暂未收录",
            "clean": "windows流氓软件清理大师",
            "cleaner": "windows流氓软件清理大师",
            "cleaner3": "windows流氓软件清理大师",
            "cleanpc": "windows流氓软件清理大师",
            "click": "已知杀软进程,名称暂未收录",
            "cmesys": "已知杀软进程,名称暂未收录",
            "cmgrdian": "已知杀软进程,名称暂未收录",
            "cmon016": "已知杀软进程,名称暂未收录",
            "connectionmonitor": "已知杀软进程,名称暂未收录",
            "cpd": "McAfee",
            "cpf9x206": "已知杀软进程,名称暂未收录",
            "cpfnt206": "已知杀软进程,名称暂未收录",
            "ctrl": "已知杀软进程,名称暂未收录",
            "cv": "已知杀软进程,名称暂未收录",
            "cwnb181": "已知杀软进程,名称暂未收录",
            "cwntdwmo": "已知杀软进程,名称暂未收录",
            "datemanager": "已知杀软进程,名称暂未收录",
            "dcomx": "已知杀软进程,名称暂未收录",
            "defalert": "Symantec",
            "defscangui": "Symantec",
            "defwatch": "Norton Antivirus",
            "deputy": "已知杀软进程,名称暂未收录",
            "divx": "已知杀软进程,名称暂未收录",
            "dllcache": "已知杀软进程,名称暂未收录",
            "dllreg": "已知杀软进程,名称暂未收录",
            "doors": "已知杀软进程,名称暂未收录",
            "dpf": "已知杀软进程,名称暂未收录",
            "dpfsetup": "已知杀软进程,名称暂未收录",
            "dpps2": "PanicWare",
            "drwatson": "已知杀软进程,名称暂未收录",
            "drweb32": "已知杀软进程,名称暂未收录",
            "drwebupw": "已知杀软进程,名称暂未收录",
            "dssagent": "Broderbund",
            "dvp95": "已知杀软进程,名称暂未收录",
            "dvp95_0": "已知杀软进程,名称暂未收录",
            "ecengine": "已知杀软进程,名称暂未收录",
            "efpeadm": "已知杀软进程,名称暂未收录",
            "emsw": "Alset Inc",
            "ent": "已知杀软进程,名称暂未收录",
            "esafe": "已知杀软进程,名称暂未收录",
            "escanhnt": "已知杀软进程,名称暂未收录",
            "escanv95": "已知杀软进程,名称暂未收录",
            "espwatch": "已知杀软进程,名称暂未收录",
            "ethereal": "RationalClearCase",
            "etrustcipe": "已知杀软进程,名称暂未收录",
            "evpn": "已知杀软进程,名称暂未收录",
            "exantivirus-cnet": "已知杀软进程,名称暂未收录",
            "exe.avxw": "已知杀软进程,名称暂未收录",
            "expert": "已知杀软进程,名称暂未收录",
            "explore": "已知杀软进程,名称暂未收录",
            "f-agnt95": "已知杀软进程,名称暂未收录",
            "f-prot95": "已知杀软进程,名称暂未收录",
            "f-stopw": "已知杀软进程,名称暂未收录",
            "fameh32": "F-Secure",
            "fast": " FastUsr",
            "fch32": "F-Secure",
            "fih32": "F-Secure",
            "findviru": "F-Secure",
            "firewall": "AshampooSoftware",
            "fnrb32": "F-Secure",
            "fp-win": " F-Prot Antivirus OnDemand",
            "fp-win_trial": "已知杀软进程,名称暂未收录",
            "fprot": "已知杀软进程,名称暂未收录",
            "frw": "已知杀软进程,名称暂未收录",
            "fsaa": "F-Secure",
            "fsav": "F-Secure",
            "fsav32": "F-Secure",
            "fsav530stbyb": "F-Secure",
            "fsav530wtbyb": "F-Secure",
            "fsav95": "F-Secure",
            "fsgk32": "F-Secure",
            "fsm32": "F-Secure",
            "fsma32": "F-Secure",
            "fsmb32": "F-Secure",
            "gator": "已知杀软进程,名称暂未收录",
            "gbmenu": "已知杀软进程,名称暂未收录",
            "gbpoll": "已知杀软进程,名称暂未收录",
            "generics": "已知杀软进程,名称暂未收录",
            "gmt": "已知杀软进程,名称暂未收录",
            "guard": "ewido",
            "guarddog": "ewido",
            "hacktracersetup": "已知杀软进程,名称暂未收录",
            "hbinst": "已知杀软进程,名称暂未收录",
            "hbsrv": "已知杀软进程,名称暂未收录",
            "hotactio": "已知杀软进程,名称暂未收录",
            "hotpatch": "已知杀软进程,名称暂未收录",
            "htlog": "已知杀软进程,名称暂未收录",
            "htpatch": "Silicon Integrated Systems Corporation",
            "hwpe": "已知杀软进程,名称暂未收录",
            "hxdl": "已知杀软进程,名称暂未收录",
            "hxiul": "已知杀软进程,名称暂未收录",
            "iamapp": "Symantec",
            "iamserv": "Symantec",
            "iamstats": "Symantec",
            "ibmasn": "已知杀软进程,名称暂未收录",
            "ibmavsp": "已知杀软进程,名称暂未收录",
            "icload95": "已知杀软进程,名称暂未收录",
            "icloadnt": "已知杀软进程,名称暂未收录",
            "icmon": "已知杀软进程,名称暂未收录",
            "icsupp95": "已知杀软进程,名称暂未收录",
            "icsuppnt": "已知杀软进程,名称暂未收录",
            "idle": "已知杀软进程,名称暂未收录",
            "iedll": "已知杀软进程,名称暂未收录",
            "iedriver": " Urlblaze.com",
            "iface": "Panda Antivirus Module",
            "ifw2000": "已知杀软进程,名称暂未收录",
            "inetlnfo": "已知杀软进程,名称暂未收录",
            "infus": "Infus Dialer",
            "infwin": "Msviewparasite",
            "init": "已知杀软进程,名称暂未收录",
            "intdel": "Inet Delivery",
            "intren": "已知杀软进程,名称暂未收录",
            "iomon98": "已知杀软进程,名称暂未收录",
            "istsvc": "已知杀软进程,名称暂未收录",
            "jammer": "已知杀软进程,名称暂未收录",
            "jdbgmrg": "已知杀软进程,名称暂未收录",
            "jedi": "已知杀软进程,名称暂未收录",
            "kavlite40eng": "已知杀软进程,名称暂未收录",
            "kavpers40eng": "已知杀软进程,名称暂未收录",
            "kavpf": "Kapersky",
            "kazza": "Kapersky",
            "keenvalue": "EUNIVERSE INC",
            "kerio-pf-213-en-win": "已知杀软进程,名称暂未收录",
            "kerio-wrl-421-en-win": "已知杀软进程,名称暂未收录",
            "kerio-wrp-421-en-win": "已知杀软进程,名称暂未收录",
            "kernel32": "已知杀软进程,名称暂未收录",
            "killprocesssetup161": "已知杀软进程,名称暂未收录",
            "launcher": "Intercort Systems",
            "ldnetmon": "已知杀软进程,名称暂未收录",
            "ldpro": "已知杀软进程,名称暂未收录",
            "ldpromenu": "已知杀软进程,名称暂未收录",
            "ldscan": "Windows Trojans Inspector",
            "lnetinfo": "已知杀软进程,名称暂未收录",
            "loader": "已知杀软进程,名称暂未收录",
            "localnet": "已知杀软进程,名称暂未收录",
            "lockdown": "已知杀软进程,名称暂未收录",
            "lockdown2000": "已知杀软进程,名称暂未收录",
            "lookout": "已知杀软进程,名称暂未收录",
            "lordpe": "已知杀软进程,名称暂未收录",
            "lsetup": "已知杀软进程,名称暂未收录",
            "luall": "Symantec",
            "luau": "Symantec",
            "lucomserver": "Norton",
            "luinit": "已知杀软进程,名称暂未收录",
            "luspt": "已知杀软进程,名称暂未收录",
            "mapisvc32": "已知杀软进程,名称暂未收录",
            "mcagent": "McAfee",
            "mcmnhdlr": "McAfee",
            "mctool": "McAfee",
            "mcupdate": "McAfee",
            "mcvsrte": "McAfee",
            "mcvsshld": "McAfee",
            "md": "已知杀软进程,名称暂未收录",
            "mfin32": "MyFreeInternetUpdate",
            "mfw2en": "MyFreeInternetUpdate",
            "mfweng3.02d30": "MyFreeInternetUpdate",
            "mgavrtcl": "McAfee",
            "mgavrte": "McAfee",
            "mghtml": "McAfee",
            "mgui": "BullGuard",
            "minilog": "Zone Labs Inc",
            "mmod": "EzulaInc",
            "monitor": "已知杀软进程,名称暂未收录",
            "moolive": "已知杀软进程,名称暂未收录",
            "mostat": "WurldMediaInc",
            "mpfagent": "McAfee",
            "mpfservice": "McAfee",
            "mpftray": "McAfee",
            "mrflux": "已知杀软进程,名称暂未收录",
            "msapp": "已知杀软进程,名称暂未收录",
            "msbb": "已知杀软进程,名称暂未收录",
            "msblast": "已知杀软进程,名称暂未收录",
            "mscache": "Integrated Search Technologies Spyware",
            "msccn32": "已知杀软进程,名称暂未收录",
            "mscman": "OdysseusMarketingInc",
            "msconfig": "已知杀软进程,名称暂未收录",
            "msdm": "已知杀软进程,名称暂未收录",
            "msdos": "已知杀软进程,名称暂未收录",
            "msiexec16": "已知杀软进程,名称暂未收录",
            "msinfo32": "已知杀软进程,名称暂未收录",
            "mslaugh": "已知杀软进程,名称暂未收录",
            "msmgt": "Total Velocity Spyware",
            "msmsgri32": "已知杀软进程,名称暂未收录",
            "mssmmc32": "已知杀软进程,名称暂未收录",
            "mssys": "已知杀软进程,名称暂未收录",
            "msvxd": "W32/Datom-A",
            "mu0311ad": "已知杀软进程,名称暂未收录",
            "mwatch": "已知杀软进程,名称暂未收录",
            "n32scanw": "已知杀软进程,名称暂未收录",
            "nav": "Reuters Limited",
            "navap.navapsvc": "已知杀软进程,名称暂未收录",
            "navapsvc": "Norton AntiVirus",
            "navapw32": "Norton AntiVirus",
            "navdx": "已知杀软进程,名称暂未收录",
            "navlu32": "已知杀软进程,名称暂未收录",
            "navnt": "已知杀软进程,名称暂未收录",
            "navstub": "已知杀软进程,名称暂未收录",
            "navw32": "Norton Antivirus",
            "navwnt": "已知杀软进程,名称暂未收录",
            "nc2000": "已知杀软进程,名称暂未收录",
            "ncinst4": "已知杀软进程,名称暂未收录",
            "ndd32": "诺顿磁盘医生",
            "neomonitor": "已知杀软进程,名称暂未收录",
            "neowatchlog": "已知杀软进程,名称暂未收录",
            "netarmor": "已知杀软进程,名称暂未收录",
            "netd32": "已知杀软进程,名称暂未收录",
            "netinfo": "已知杀软进程,名称暂未收录",
            "netmon": "已知杀软进程,名称暂未收录",
            "netscanpro": "已知杀软进程,名称暂未收录",
            "netspyhunter-1.2": "已知杀软进程,名称暂未收录",
            "netstat": "已知杀软进程,名称暂未收录",
            "netutils": "已知杀软进程,名称暂未收录",
            "nisserv": "Norton",
            "nisum": "Norton",
            "nmain": "Norton",
            "nod32": "ESET Smart Security",
            "normist": "已知杀软进程,名称暂未收录",
            "norton_internet_secu_3.0_407": "已知杀软进程,名称暂未收录",
            "notstart": "已知杀软进程,名称暂未收录",
            "npf40_tw_98_nt_me_2k": "已知杀软进程,名称暂未收录",
            "npfmessenger": "已知杀软进程,名称暂未收录",
            "nprotect": "Symantec",
            "npscheck": "Norton",
            "npssvc": "Norton",
            "nsched32": "已知杀软进程,名称暂未收录",
            "nssys32": "已知杀软进程,名称暂未收录",
            "nstask32": "已知杀软进程,名称暂未收录",
            "nsupdate": "已知杀软进程,名称暂未收录",
            "nt": "已知杀软进程,名称暂未收录",
            "ntrtscan": "趋势反病毒应用程序",
            "ntvdm": "已知杀软进程,名称暂未收录",
            "ntxconfig": "已知杀软进程,名称暂未收录",
            "nui": "已知杀软进程,名称暂未收录",
            "nupgrade": "已知杀软进程,名称暂未收录",
            "nvarch16": "已知杀软进程,名称暂未收录",
            "nvc95": "已知杀软进程,名称暂未收录",
            "nvsvc32": "已知杀软进程,名称暂未收录",
            "nwinst4": "已知杀软进程,名称暂未收录",
            "nwservice": "已知杀软进程,名称暂未收录",
            "nwtool16": "已知杀软进程,名称暂未收录",
            "ollydbg": "已知杀软进程,名称暂未收录",
            "onsrvr": "已知杀软进程,名称暂未收录",
            "optimize": "已知杀软进程,名称暂未收录",
            "ostronet": "已知杀软进程,名称暂未收录",
            "otfix": "已知杀软进程,名称暂未收录",
            "outpostinstall": "Outpost",
            "outpostproinstall": "已知杀软进程,名称暂未收录",
            "padmin": "已知杀软进程,名称暂未收录",
            "panixk": "已知杀软进程,名称暂未收录",
            "patch": "趋势科技",
            "pavcl": "已知杀软进程,名称暂未收录",
            "pavproxy": "已知杀软进程,名称暂未收录",
            "pavsched": "已知杀软进程,名称暂未收录",
            "pavw": "已知杀软进程,名称暂未收录",
            "pccwin98": "已知杀软进程,名称暂未收录",
            "pcfwallicon": "已知杀软进程,名称暂未收录",
            "pcip10117_0": "已知杀软进程,名称暂未收录",
            "pcscan": "趋势科技",
            "pdsetup": "已知杀软进程,名称暂未收录",
            "periscope": "已知杀软进程,名称暂未收录",
            "persfw": "Tiny Personal Firewall",
            "perswf": "已知杀软进程,名称暂未收录",
            "pf2": "已知杀软进程,名称暂未收录",
            "pfwadmin": "已知杀软进程,名称暂未收录",
            "pgmonitr": "PromulGate SpyWare",
            "pingscan": "已知杀软进程,名称暂未收录",
            "platin": "已知杀软进程,名称暂未收录",
            "pop3trap": "PC-cillin",
            "poproxy": "NortonAntiVirus",
            "popscan": "已知杀软进程,名称暂未收录",
            "portdetective": "已知杀软进程,名称暂未收录",
            "portmonitor": "已知杀软进程,名称暂未收录",
            "powerscan": "Integrated Search Technologies",
            "ppinupdt": "已知杀软进程,名称暂未收录",
            "pptbc": "已知杀软进程,名称暂未收录",
            "ppvstop": "已知杀软进程,名称暂未收录",
            "prizesurfer": "Prizesurfer",
            "prmt": "OpiStat",
            "prmvr": "Adtomi",
            "procdump": "已知杀软进程,名称暂未收录",
            "processmonitor": "Sysinternals",
            "procexplorerv1.0": "已知杀软进程,名称暂未收录",
            "programauditor": "已知杀软进程,名称暂未收录",
            "proport": "已知杀软进程,名称暂未收录",
            "protectx": "ProtectX",
            "pspf": "已知杀软进程,名称暂未收录",
            "purge": "已知杀软进程,名称暂未收录",
            "qconsole": "Norton AntiVirus Quarantine Console",
            "qserver": "Norton Internet Security",
            "rapapp": "BlackICE",
            "rav7": "已知杀软进程,名称暂未收录",
            "rav7win": "已知杀软进程,名称暂未收录",
            "rav8win32eng": "已知杀软进程,名称暂未收录",
            "ray": "已知杀软进程,名称暂未收录",
            "rb32": "RapidBlaster",
            "rcsync": "PrizeSurfer",
            "realmon": "Realmon ",
            "reged": "已知杀软进程,名称暂未收录",
            "regedit": "已知杀软进程,名称暂未收录",
            "regedt32": "已知杀软进程,名称暂未收录",
            "rescue": "已知杀软进程,名称暂未收录",
            "rescue32": "卡巴斯基互联网安全套装",
            "rrguard": "已知杀软进程,名称暂未收录",
            "rshell": "已知杀软进程,名称暂未收录",
            "rtvscn95": "Real-time virus scanner ",
            "rulaunch": "McAfee User Interface",
            "run32dll": "PAL PC Spy",
            "rundll": "已知杀软进程,名称暂未收录",
            "rundll16": "已知杀软进程,名称暂未收录",
            "ruxdll32": "已知杀软进程,名称暂未收录",
            "safeweb": "PSafe Tecnologia",
            "sahagentscan32": "已知杀软进程,名称暂未收录",
            "save": "已知杀软进程,名称暂未收录",
            "savenow": "已知杀软进程,名称暂未收录",
            "sbserv": "Norton Antivirus",
            "sc": "已知杀软进程,名称暂未收录",
            "scam32": "已知杀软进程,名称暂未收录",
            "scan95": "已知杀软进程,名称暂未收录",
            "scanpm": "已知杀软进程,名称暂未收录",
            "scrscan": "360杀毒",
            "serv95": "已知杀软进程,名称暂未收录",
            "setup_flowprotector_us": "已知杀软进程,名称暂未收录",
            "setupvameeval": "已知杀软进程,名称暂未收录",
            "sfc": "System file checker",
            "sgssfw32": "已知杀软进程,名称暂未收录",
            "sh": "MKS Toolkit for Win3",
            "shellspyinstall": "已知杀软进程,名称暂未收录",
            "shn": "已知杀软进程,名称暂未收录",
            "showbehind": "MicroSmarts Enterprise Component ",
            "smc": "已知杀软进程,名称暂未收录",
            "sms": "已知杀软进程,名称暂未收录",
            "smss32": "已知杀软进程,名称暂未收录",
            "soap": "System Soap Pro",
            "sofi": "已知杀软进程,名称暂未收录",
            "sperm": "已知杀软进程,名称暂未收录",
            "spf": "已知杀软进程,名称暂未收录",
            "spoler": "已知杀软进程,名称暂未收录",
            "spoolcv": "已知杀软进程,名称暂未收录",
            "spoolsv32": "已知杀软进程,名称暂未收录",
            "spyxx": "已知杀软进程,名称暂未收录",
            "srexe": "已知杀软进程,名称暂未收录",
            "srng": "已知杀软进程,名称暂未收录",
            "ss3edit": "已知杀软进程,名称暂未收录",
            "ssg_4104": "已知杀软进程,名称暂未收录",
            "ssgrate": "已知杀软进程,名称暂未收录",
            "st2": "已知杀软进程,名称暂未收录",
            "start": "已知杀软进程,名称暂未收录",
            "stcloader": "已知杀软进程,名称暂未收录",
            "supftrl": "已知杀软进程,名称暂未收录",
            "support": "已知杀软进程,名称暂未收录",
            "supporter5": "eScorcher反病毒",
            "svchostc": "已知杀软进程,名称暂未收录",
            "svchosts": "已知杀软进程,名称暂未收录",
            "sweep95": "已知杀软进程,名称暂未收录",
            "sweepnet.sweepsrv.sys.swnetsup": "已知杀软进程,名称暂未收录",
            "symproxysvc": "Symantec",
            "symtray": "Symantec",
            "sysedit": "已知杀软进程,名称暂未收录",
            "sysupd": "已知杀软进程,名称暂未收录",
            "taskmg": "已知杀软进程,名称暂未收录",
            "taskmo": "已知杀软进程,名称暂未收录",
            "taumon": "已知杀软进程,名称暂未收录",
            "tbscan": "ThunderBYTE",
            "tc": "TimeCalende",
            "tca": "已知杀软进程,名称暂未收录",
            "tcm": "已知杀软进程,名称暂未收录",
            "tds-3": "已知杀软进程,名称暂未收录",
            "tds2-98": "已知杀软进程,名称暂未收录",
            "tds2-nt": "已知杀软进程,名称暂未收录",
            "teekids": "已知杀软进程,名称暂未收录",
            "tfak": "已知杀软进程,名称暂未收录",
            "tfak5": "已知杀软进程,名称暂未收录",
            "tgbob": "已知杀软进程,名称暂未收录",
            "titanin": "TitanHide",
            "titaninxp": "已知杀软进程,名称暂未收录",
            "tracert": "已知杀软进程,名称暂未收录",
            "trickler": "已知杀软进程,名称暂未收录",
            "trjscan": "已知杀软进程,名称暂未收录",
            "trjsetup": "已知杀软进程,名称暂未收录",
            "trojantrap3": "已知杀软进程,名称暂未收录",
            "tsadbot": "已知杀软进程,名称暂未收录",
            "tvmd": "Total Velocity",
            "tvtmd": " Total Velocity",
            "undoboot": "已知杀软进程,名称暂未收录",
            "updat": "已知杀软进程,名称暂未收录",
            "update": "已知杀软进程,名称暂未收录",
            "upgrad": "已知杀软进程,名称暂未收录",
            "utpost": "已知杀软进程,名称暂未收录",
            "vbcmserv": "已知杀软进程,名称暂未收录",
            "vbcons": "已知杀软进程,名称暂未收录",
            "vbust": "已知杀软进程,名称暂未收录",
            "vbwin9x": "已知杀软进程,名称暂未收录",
            "vbwinntw": "已知杀软进程,名称暂未收录",
            "vcsetup": "已知杀软进程,名称暂未收录",
            "vet32": "已知杀软进程,名称暂未收录",
            "vet95": "已知杀软进程,名称暂未收录",
            "vettray": "eTrust",
            "vfsetup": "已知杀软进程,名称暂未收录",
            "vir-help": "已知杀软进程,名称暂未收录",
            "virusmdpersonalfirewall": "已知杀软进程,名称暂未收录",
            "vnlan300": "已知杀软进程,名称暂未收录",
            "vnpc3000": "已知杀软进程,名称暂未收录",
            "vpc32": "Symantec",
            "vpc42": "Symantec",
            "vpfw30s": "已知杀软进程,名称暂未收录",
            "vscan40": "已知杀软进程,名称暂未收录",
            "vscenu6.02d30": "已知杀软进程,名称暂未收录",
            "vsched": "已知杀软进程,名称暂未收录",
            "vsecomr": "已知杀软进程,名称暂未收录",
            "vshwin32": "McAfee",
            "vsisetup": "已知杀软进程,名称暂未收录",
            "vsmain": "McAfee",
            "vsstat": "McAfee",
            "vswin9xe": "已知杀软进程,名称暂未收录",
            "vswinntse": "已知杀软进程,名称暂未收录",
            "vswinperse": "已知杀软进程,名称暂未收录",
            "w32dsm89": "已知杀软进程,名称暂未收录",
            "w9x": "已知杀软进程,名称暂未收录",
            "watchdog": "已知杀软进程,名称暂未收录",
            "webdav": "已知杀软进程,名称暂未收录",
            "webtrap": "已知杀软进程,名称暂未收录",
            "wfindv32": "已知杀软进程,名称暂未收录",
            "whoswatchingme": "已知杀软进程,名称暂未收录",
            "wimmun32": "已知杀软进程,名称暂未收录",
            "win-bugsfix": "已知杀软进程,名称暂未收录",
            "win32": "已知杀软进程,名称暂未收录",
            "win32us": "已知杀软进程,名称暂未收录",
            "winactive": "已知杀软进程,名称暂未收录",
            "window": "已知杀软进程,名称暂未收录",
            "windows": "已知杀软进程,名称暂未收录",
            "wininetd": "已知杀软进程,名称暂未收录",
            "wininitx": "已知杀软进程,名称暂未收录",
            "winlogin": "已知杀软进程,名称暂未收录",
            "winmain": "已知杀软进程,名称暂未收录",
            "winnet": "已知杀软进程,名称暂未收录",
            "winppr32": "已知杀软进程,名称暂未收录",
            "winrecon": "已知杀软进程,名称暂未收录",
            "winservn": "已知杀软进程,名称暂未收录",
            "winssk32": "已知杀软进程,名称暂未收录",
            "winstart": "已知杀软进程,名称暂未收录",
            "winstart001": "已知杀软进程,名称暂未收录",
            "wintsk32": "已知杀软进程,名称暂未收录",
            "winupdate": "已知杀软进程,名称暂未收录",
            "wkufind": "已知杀软进程,名称暂未收录",
            "wnad": "已知杀软进程,名称暂未收录",
            "wnt": "已知杀软进程,名称暂未收录",
            "wradmin": "已知杀软进程,名称暂未收录",
            "wrctrl": "已知杀软进程,名称暂未收录",
            "wsbgate": "已知杀软进程,名称暂未收录",
            "wupdater": "已知杀软进程,名称暂未收录",
            "wupdt": "已知杀软进程,名称暂未收录",
            "wyvernworksfirewall": "已知杀软进程,名称暂未收录",
            "xpf202en": "已知杀软进程,名称暂未收录",
            "zapro": "Zone Alarm",
            "zapsetup3001": "已知杀软进程,名称暂未收录",
            "zatutor": "已知杀软进程,名称暂未收录",
            "zonalm2601": "已知杀软进程,名称暂未收录",
            "zonealarm": "Zone Alarm",
            "AVPM": "Kaspersky",
            "A2CMD": "Emsisoft Anti-Malware",
            "A2SERVICE": "a-squared free",
            "A2FREE": "a-squared Free",
            "ADVCHK": "Norton AntiVirus",
            "AGB": "安天防线",
            "AKRNL": "已知杀软进程,名称暂未收录",
            "AHPROCMONSERVER": "安天防线",
            "AIRDEFENSE": "AirDefense",
            "ALERTSVC": "Norton AntiVirus",
            "AVIRA": "小红伞杀毒",
            "AMON": "Tiny Personal Firewall",
            "TROJAN": "已知杀软进程,名称暂未收录",
            "AVZ": "AVZ",
            "ANTIVIR": "已知杀软进程,名称暂未收录",
            "APVXDWIN": "熊猫卫士",
            "ARMOR2NET": "已知杀软进程,名称暂未收录",
            "ASHexe": "已知杀软进程,名称暂未收录",
            "ASHENHCD": "已知杀软进程,名称暂未收录",
            "ASHMAISV": "Alwil",
            "ASHPOPWZ": "已知杀软进程,名称暂未收录",
            "ASHSERV": "Avast Anti-virus",
            "ASHSIMPL": "AVAST!VirusCleaner",
            "ASHSKPCK": "已知杀软进程,名称暂未收录",
            "ASHWEBSV": "Avast",
            "ASWUPDSV": "Avast",
            "ASWSCAN": "Avast",
            "AVCIMAN": "熊猫卫士",
            "AVCONSOL": "McAfee",
            "AVENGINE": "熊猫卫士",
            "AVESVC": "Avira AntiVir Security Service",
            "AVEVAL": "已知杀软进程,名称暂未收录",
            "AVEVL32": "已知杀软进程,名称暂未收录",
            "AVGAM": "AVG",
            "AVGCC": "AVG",
            "AVGCHSVX": "AVG",
            "AVGCSRVX": "已知杀软进程,名称暂未收录",
            "AVGNSX": "AVG",
            "AVGCC32": "AVG",
            "AVGCTRL": "AVG",
            "AVGEMC": "AVG",
            "AVGFWSRV": "AVG",
            "AVGNTMGR": "AVG",
            "AVGSERV": "AVG",
            "AVGTRAY": "AVG",
            "AVGUPSVC": "AVG",
            "AVINITNT": "Command AntiVirus for NT Server",
            "AVKSERV": "已知杀软进程,名称暂未收录",
            "AVKSERVICE": "已知杀软进程,名称暂未收录",
            "AVKWCTL": "已知杀软进程,名称暂未收录",
            "AVP32": "已知杀软进程,名称暂未收录",
            "AVPCC": "Kaspersky",
            "AVSERVER": "Kerio MailServer",
            "AVSCHED32": "H+BEDV",
            "AVSYNMGR": "McAfee",
            "AVWUPD32": "已知杀软进程,名称暂未收录",
            "AVWUPSRV": "H+BEDV",
            "AVXMONITOR": "已知杀软进程,名称暂未收录",
            "AVXQUAR": "已知杀软进程,名称暂未收录",
            "BDSWITCH": "BitDefender Module",
            "BLACKD": "BlackICE",
            "BLACKICE": "已知杀软进程,名称暂未收录",
            "CAFIX": "已知杀软进程,名称暂未收录",
            "BITDEFENDER": "已知杀软进程,名称暂未收录",
            "CCEVTMGR": "Symantec",
            "CFP": "COMODO",
            "CFPCONFIG": "已知杀软进程,名称暂未收录",
            "CFIAUDIT": "已知杀软进程,名称暂未收录",
            "CLAMTRAY": "已知杀软进程,名称暂未收录",
            "CLAMWIN": "ClamWin Portable",
            "CUREIT": "DrWeb CureIT",
            "DEFWATCH": "Norton Antivirus",
            "DRVIRUS": "已知杀软进程,名称暂未收录",
            "DRWADINS": "Dr.Web",
            "DRWEB": "Dr.Web",
            "DEFENDERDAEMON": "ShadowDefender",
            "DWEBLLIO": "已知杀软进程,名称暂未收录",
            "DWEBIO": "已知杀软进程,名称暂未收录",
            "ESCANH95": "已知杀软进程,名称暂未收录",
            "ESCANHNT": "已知杀软进程,名称暂未收录",
            "EWIDOCTRL": "Ewido Security Suite",
            "EZANTIVIRUSREGISTRATIONCHECK": "e-Trust Antivirus",
            "F-AGNT95": "已知杀软进程,名称暂未收录",
            "FAMEH32": "已知杀软进程,名称暂未收录",
            "FILEMON": "已知杀软进程,名称暂未收录",
            "FIREWALL": "AshampooSoftware",
            "FORTICLIENT": "已知杀软进程,名称暂未收录",
            "FORTISCAN": "已知杀软进程,名称暂未收录",
            "FPAVSERVER": "已知杀软进程,名称暂未收录",
            "FPROTTRAY": "F-PROT Antivirus",
            "FPWIN": "Verizon",
            "FRESHCLAM": "ClamAV",
            "FSAV32": "F-Secure",
            "FSBWSYS": "F-secure",
            "F-SCHED": "已知杀软进程,名称暂未收录",
            "FSDFWD": "F-Secure",
            "FSGK32": "F-Secure",
            "FSGK32ST": "F-Secure",
            "FSGUIEXE": "已知杀软进程,名称暂未收录",
            "FSMA32": "F-Secure",
            "FSMB32": "F-Secure",
            "FSPEX": "已知杀软进程,名称暂未收录",
            "FSSM32": "F-Secure",
            "F-STOPW": "已知杀软进程,名称暂未收录",
            "GCASDTSERV": "已知杀软进程,名称暂未收录",
            "GCASSERV": "已知杀软进程,名称暂未收录",
            "GIANTANTISPYWARE": "已知杀软进程,名称暂未收录",
            "GUARDGUI": "网游保镖",
            "GUARDNT": "IKARUS",
            "GUARDXSERVICE": "已知杀软进程,名称暂未收录",
            "GUARDXKICKOFF": "已知杀软进程,名称暂未收录",
            "HREGMON": "已知杀软进程,名称暂未收录",
            "HRRES": "已知杀软进程,名称暂未收录",
            "HSOCKPE": "已知杀软进程,名称暂未收录",
            "HUPDATE": "已知杀软进程,名称暂未收录",
            "IAMAPP": "Symantec",
            "IAMSERV": "已知杀软进程,名称暂未收录",
            "ICLOAD95": "已知杀软进程,名称暂未收录",
            "ICLOADNT": "已知杀软进程,名称暂未收录",
            "ICMON": "已知杀软进程,名称暂未收录",
            "ICSSUPPNT": "已知杀软进程,名称暂未收录",
            "ICSUPP95": "已知杀软进程,名称暂未收录",
            "ICSUPPNT": "已知杀软进程,名称暂未收录",
            "INETUPD": "已知杀软进程,名称暂未收录",
            "INOCIT": "eTrust",
            "INORPC": "eTrust",
            "INORT": "eTrust",
            "INOTASK": "eTrust",
            "INOUPTNG": "eTrust",
            "IOMON98": "已知杀软进程,名称暂未收录",
            "ISAFE": "eTrust",
            "ISATRAY": "已知杀软进程,名称暂未收录",
            "KAV": "Kaspersky",
            "KAVMM": "Kaspersky",
            "KAVPF": "Kaspersky",
            "KAVPFW": "Kaspersky",
            "KAVSTART": "Kaspersky",
            "KAVSVC": "Kaspersky",
            "KAVSVCUI": "Kaspersky",
            "KMAILMON": "金山毒霸",
            "MAMUTU": "已知杀软进程,名称暂未收录",
            "MCAGENT": "McAfee",
            "MCMNHDLR": "McAfee",
            "MCREGWIZ": "McAfee",
            "MCUPDATE": "McAfee",
            "MCVSSHLD": "McAfee",
            "MINILOG": "Zone Alarm",
            "MYAGTSVC": "McAfee",
            "MYAGTTRY": "McAfee",
            "NAVAPSVC": "Norton",
            "NAVAPW32": "Norton",
            "NAVLU32": "Norton",
            "NAVW32": "Norton Antivirus",
            "NEOWATCHLOG": "NeoWatch",
            "NEOWATCHTRAY": "NeoWatch",
            "NISSERV": "Norton",
            "NISUM": "Norton",
            "NMAIN": "Norton",
            "NOD32": "ESET NOD32",
            "NORMIST": "已知杀软进程,名称暂未收录",
            "NOTSTART": "已知杀软进程,名称暂未收录",
            "NPAVTRAY": "已知杀软进程,名称暂未收录",
            "NPFMSG": "Norman个人防火墙",
            "NPROTECT": "Symantec",
            "NSCHED32": "已知杀软进程,名称暂未收录",
            "NSMDTR": "Norton",
            "NSSSERV": "已知杀软进程,名称暂未收录",
            "NSSTRAY": "已知杀软进程,名称暂未收录",
            "NTRTSCAN": "趋势科技",
            "NTOS": "已知杀软进程,名称暂未收录",
            "NTXCONFIG": "已知杀软进程,名称暂未收录",
            "NUPGRADE": "已知杀软进程,名称暂未收录",
            "NVCOD": "已知杀软进程,名称暂未收录",
            "NVCTE": "已知杀软进程,名称暂未收录",
            "NVCUT": "已知杀软进程,名称暂未收录",
            "NWSERVICE": "已知杀软进程,名称暂未收录",
            "OFCPFWSVC": "OfficeScanNT",
            "ONLINENT": "已知杀软进程,名称暂未收录",
            "OPSSVC": "已知杀软进程,名称暂未收录",
            "OP_MON": " OutpostFirewall",
            "PAVFIRES": "熊猫卫士",
            "PAVFNSVR": "熊猫卫士",
            "PAVKRE": "熊猫卫士",
            "PAVPROT": "熊猫卫士",
            "PAVPROXY": "熊猫卫士",
            "PAVPRSRV": "熊猫卫士",
            "PAVSRV51": "熊猫卫士",
            "PAVSS": "熊猫卫士",
            "PCCGUIDE": "PC-cillin",
            "PCCIOMON": "PC-cillin",
            "PCCNTMON": "PC-cillin",
            "PCCPFW": "趋势科技",
            "PCCTLCOM": "趋势科技",
            "PCTAV": "PC Tools AntiVirus",
            "PERSFW": "Tiny Personal Firewall",
            "PERTSK": "已知杀软进程,名称暂未收录",
            "PERVAC": "已知杀软进程,名称暂未收录",
            "PESTPATROL": "Ikarus",
            "PNMSRV": "已知杀软进程,名称暂未收录",
            "PREVSRV": "熊猫卫士",
            "PREVX": "已知杀软进程,名称暂未收录",
            "PSIMSVC": "已知杀软进程,名称暂未收录",
            "QHONLINE": "已知杀软进程,名称暂未收录",
            "QHONSVC": "已知杀软进程,名称暂未收录",
            "QHWSCSVC": "已知杀软进程,名称暂未收录",
            "QHSET": "已知杀软进程,名称暂未收录",
            "RTVSCN95": "Real-time Virus Scanner",
            "SALITY": "已知杀软进程,名称暂未收录",
            "SAPISSVC": "已知杀软进程,名称暂未收录",
            "SCANWSCS": "已知杀软进程,名称暂未收录",
            "SAVADMINSERVICE": "SAV",
            "SAVMAIN": "SAV",
            "SAVSCAN": "SAV",
            "SCANNINGPROCESS": "已知杀软进程,名称暂未收录",
            "SDRA64": "已知杀软进程,名称暂未收录",
            "SDHELP": "Spyware Doctor",
            "SHSTAT": "McAfee",
            "SITECLI": "已知杀软进程,名称暂未收录",
            "SPBBCSVC": "Symantec",
            "SPIDERCPL": "Dr.Web",
            "SPIDERML": "Dr.Web",
            "SPIDERUI": "Dr.Web",
            "SPYBOTSD": "Spybot ",
            "SPYXX": "已知杀软进程,名称暂未收录",
            "SS3EDIT": "已知杀软进程,名称暂未收录",
            "STOPSIGNAV": "已知杀软进程,名称暂未收录",
            "SWAGENT": "SonicWALL",
            "SWDOCTOR": "SonicWALL",
            "SWNETSUP": "Sophos",
            "SYMLCSVC": "Symantec",
            "SYMPROXYSVC": "Symantec",
            "SYMSPORT": "Sysmantec",
            "SYMWSC": "Sysmantec",
            "SYNMGR": "Sysmantec",
            "TAUMON": "已知杀软进程,名称暂未收录",
            "TMLISTEN": "趋势科技",
            "TMNTSRV": "趋势科技",
            "TMPROXY": "趋势科技",
            "TNBUTIL": "Anti-Virus",
            "TRJSCAN": "已知杀软进程,名称暂未收录",
            "VBA32ECM": "已知杀软进程,名称暂未收录",
            "VBA32IFS": "已知杀软进程,名称暂未收录",
            "VBA32LDR": "已知杀软进程,名称暂未收录",
            "VBA32PP3": "已知杀软进程,名称暂未收录",
            "VBSNTW": "已知杀软进程,名称暂未收录",
            "VCRMON": "VirusChaser",
            "VRFWSVC": "已知杀软进程,名称暂未收录",
            "VRMONNT": "HAURI",
            "VRMONSVC": "HAURI",
            "VRRW32": "已知杀软进程,名称暂未收录",
            "VSECOMR": "已知杀软进程,名称暂未收录",
            "VSHWIN32": "McAfee",
            "VSSTAT": "McAfee",
            "WATCHDOG": "已知杀软进程,名称暂未收录",
            "WINSSNOTIFY": "已知杀软进程,名称暂未收录",
            "WRCTRL": "已知杀软进程,名称暂未收录",
            "XCOMMSVR": "BitDefender",
            "ZLCLIENT": "已知杀软进程,名称暂未收录",
            "ZONEALARM": "Zone Alarm",
            "360rp": "360杀毒",
            "afwServ": " Avast Antivirus ",
            "safeboxTray": "360杀毒",
            "360safebox": "360杀毒",
            "QQPCTray": "QQ电脑管家",
            "KSafeTray": "金山毒霸",
            "KSafeSvc": "金山毒霸",
            "KWatch": "金山毒霸",
            "AVGCSRVX": "AVG",
            "gov_defence_service": "云锁",
            "gov_defence_daemon": "云锁"
        }
        processlist=[]
        pids=psutil.pids()
        for pid in pids:
            processlist.append({'pid':pid,'name':psutil.Process(pid).name().lower()})

        for p in processlist:
            for u in avlist:
                if '{}.exe'.format(u.lower())==p['name'].lower():
                    print('processname:{} pid:{} av:{}'.format(p['name'],p['pid'],avlist[u]))
        print('')

    def getorher(self):
        print(Fore.BLUE+'[+] '+Fore.WHITE+'other information')
        commands={"Architecture information":"wmic OS get Caption,CSDVersion,OSArchitecture,Version","Internet Information":"ipconfig /all",
                  "arp routing":"arp -a","All group information":"wmic group get name,sid,description"}
        for c in commands:
            print(Fore.BLUE + '[+] ' + Fore.WHITE + c)
            print(self.runcmd(commands[c]))

        print(Fore.BLUE+'[+] '+Fore.WHITE+'boot time')
        boot_time = psutil.boot_time()  # 返回一个时间戳
        boot_time_obj = datetime.datetime.fromtimestamp(boot_time)
        # print(boot_time_obj)
        # 当前时间
        now_time = datetime.datetime.now()

        delta_time = datetime.datetime.now()
        delta_time1 = now_time - boot_time_obj

        print('boot_time:', boot_time_obj)

        print('current time:', str(now_time).split('.')[0])
        print('Boot time:', str(delta_time1).split('.')[0])

if __name__ == '__main__':
    obj=Permission_enhancement()