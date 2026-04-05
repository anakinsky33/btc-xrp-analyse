#!/usr/bin/env python3
"""
BTC & XRP Elliott Wave Analyse – täglich per E-Mail
Datenquelle: CoinGecko (funktioniert auf PythonAnywhere)
"""

import os, json, datetime, urllib.request, urllib.error, smtplib, html, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ══════════════════════════════════════════════════════════════
#!/usr/bin/env python3
"""
BTC & XRP Elliott Wave Analyse - taeglich per E-Mail
Datenquelle: Kraken (kein API-Key noetig)
"""

import os, json, datetime, urllib.request, smtplib, html, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# =====================================================
#  KONFIGURATION
# =====================================================

ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
GMAIL_ABSENDER     = os.environ["GMAIL_ABSENDER"]
GMAIL_APP_PASSWORT = os.environ["GMAIL_APP_PASSWORT"]
EMPFAENGER         = os.environ["EMPFAENGER"]

COINS = [
        {"name": "BTC", "pair": "XBTUSD",  "kraken": "XXBTZUSD"},
        {"name": "XRP", "pair": "XRPUSD",  "kraken": "XXRPZUSD"},
]

# =====================================================

def fetch_kraken(pair, kraken_key, limit=720):
        since = int((datetime.datetime.utcnow() - datetime.timedelta(days=limit)).ti#m!e/sutsarm/pb(i)n)/
                    e n v   puyrtlh o=n 3f
    ""h"t"t
pBsT:C/ /&a pXiR.Pk rEalkleino.tcto mW/a0v/ep uAbnlailcy/sOeH L-C ?tpaaeigrl=i{cpha ipre}r& iEn-tMearivla
lD=a1t4e4n0q&useilnlcee:= {Ksriankceen} "(
k e i n  rAePqI -=K euyr lnloiebt.irge)q
u"e"s"t
.
    Riemqpuoerstt (ousr,l ,j shoena,d edrast=e{t"iUmsee,r -uArglelnitb".:r e"qMuoezsitl,l as/m5t.p0l"i}b),
  h t m lw,i tthi muer
lflriobm. reemqauiels.tm.iumrel.ompuelnt(irpeaqr,t  tiimmpeoorutt =M2I0M)E Mausl tri:p
a r t 
 f r o m  deamtaai l=. mjismoen..tleoxatd si(mrp.orreta dM(I)M)E
T e x t 
i
f#  d=a=t=a=.=g=e=t=(="=e=r=r=o=r="=)=:=
= = = = = = = = =r=a=i=s=e= =E=x=c=e=p=t=i=o=n=(=f="=K=r=a=k=e=n=-=F=e
h#l e rK:O N{FdIaGtUaR[A'TeIrOrNo
r#' ]=}="=)=
= = = = =c=a=n=d=l=e=s= === =d=a=t=a=[="=r=e=s=u=l=t="=]=[=k=r=a=k=e=n=_=k=e=y=]=
= = = = =r=e=t=u
r
nA N[T
H R O P I C _ A P{I"_dKaEtYe " :=   odsa.teentviimreo.nd[a"tAeN.TfHrRoOmPtIiCm_eAsPtIa_mKpE(Yi"n]t
(GcM[A0I]L)_)A.BiSsEoNfDoErRm a t ( ) ,=
  o s . e n v i r o"nc[l"oGsMeA"I:L _fAlBoSaEtN(DcE[R4"]])
  }G
  M A I L _ A P P _fPoArS ScW OiRnT  c=a nodsl.eesn viifr ofnl[o"aGtM(AcI[L4_]A)P P>_ P0A
  S S W O R]T
  "
  ]d
  eEfM PeFmAaE(NpGrEiRc e s ,   p e r i o=d )o:s
  . e n v ikr o=n [2"/E(MpPeFrAiEoNdG+E1R)";] 
  o
  uCtO=I[N]S;  =p r[e
  v = N o n{e"
  n a m e "f:o r" BiT,Cp" ,i n" peaniurm"e:r a"tXeB(TpUrSiDc"e,s ) :"
  k r a k e n " :  i"fX XiB T<Z UpSeDr"i}o,d
  - 1 :   o{u"tn.aampep"e:n d"(XNRoPn"e,) ;" pcaoinrt"i:n u"eX
  R P U S D " ,    i"fk rparkeevn "i:s  "NXoXnReP:Z UpSrDe"v} ,=
   ]s
   u
   m#( p=r=i=c=e=s=[=:=p=e=r=i=o=d=]=)=/=p=e=r=i=o=d=
   = = = = = = = = =e=l=s=e=:= =p=r=e=v= === =p=*=k= =+= =p=r=e
   v
   *d(e1f- kf)e
   t c h _ k r a k eonu(tp.aaiprp,e nkdr(arkoeunn_dk(epyr,e vl,i m6i)t)=
   7 2 0 ) :r
   e t u r ns ionucte
    
    =d eifn tr(s(id(aptreitciemse,. dpaetreitoidm=e1.4u)t:c
    n o w ( )o u-t =d[aNtoentei]m*ep.etriimoedd;e latga=(adla=y0s.=0l
    i m i t )f)o.rt iim eisnt armapn(g)e)(
    1 ,   p eurrilo d=+ 1f)":h
    t t p s : / / a pdi=.pkrriackeesn[.ic]o-mp/r0i/cpeusb[lii-c1/]O
    H L C ? p a i r =i{fp adi>r0}:& iangt+e=rdv
    a l = 1 4 4 0 & seilnscee:= {asli-n=cde
    } " 
        a g /r=epqe r=i oudr;l lailb/.=rpeeqruieosdt
        . R e q uoeustt.(auprple,n dh(eraoduenrds(=1{0"0U siefr -aAlg=e=n0t "e:l s"eM o1z0i0l-l1a0/05/.(01"+}a)g
        / a l ) ,w i2t)h) 
        u r l l ifbo.rr eiq uiens tr.aunrgleo(ppeenr(iroedq+,1 ,t ilmeeno(uptr=i2c0e)s )a)s: 
        r : 
                    d = pdraitcae s=[ ij]s-opnr.ilcoeasd[si(-r1.]r
                    e a d ( ) ) 
                        a g =i(fa gd*a(tpae.rgieotd(-"1e)r+rmoarx"()d:,
                        0 ) ) / p e r i orda
                        i s e   E x c e patli=o(na(lf*"(Kprearkieond--F1e)h+lmearx:( -{dd,a0t)a)[/'peerrrioord'
                        ] } " ) 
                                ocuatn.dalpepse n=d (draotuan[d"(r1e0s0u litf" ]a[lk=r=a0k eenl_skee y1]0
                                0 - 1 0 0r/e(t1u+rang /[a
                                l ) ,   2 ) ) 
                                  { " d arteet"u:r n  doautte
                                  t
                                  idmeef. dmaatced.(fprroimcteism)e:s
                                  t a m p (ei1n2t=(ecm[a0(]p)r)i.ciesso,f1o2r)m;a te(2)6,=
                                  e m a ( p r i c e s",c2l6o)s
                                  e " :   fmllo=a[tr(ocu[n4d]()e}1
                                  2 [ i ] - e 2 6 [fio]r, 6c)  iinf  cea1n2d[lie]s  ainfd  fel2o6a[ti(]c [e4l]s)e  >N o0n
                                  e   f o r] 
                                  i
                                   dienf  reamnag(ep(rliecne(sp,r ipceersi)o)d])
                                   : 
                                         s tk= n=e x2t/((ip efroiro di+,1v) ;i no uetn=u[m]e;r aptree(vm=lN)o nief
                                           v   i sf onro ti ,Npo nien) 
                                           e n u m esrra=teem(ap(r[ivc efso)r: 
                                           v   i n   m l   iiff  vi  i<s  pneorti oNdo-n1e:] ,o9u)t
                                           . a p p esnidg(=N[oNnoen)e;  icfo nmtli[niu]e 
                                           i s   N o n e   eilfs ep rserv[ ii-ss tN]o nfeo:r  pir eivn  =r asnugme((plreinc(epsr[i:cpeesr)i)o]d
                                           ] ) / p ehriisotd=
                                           [ r o u n d ( m le[lis]e-:s ipgr[eiv] ,=6 )p *ikf  +m lp[rie]v *i(s1 -nko)t
                                             N o n e   a n do usti.ga[pip]e nids( rnooutn dN(opnree ve,l s6e) )N
                                             o n e   froert uir ni no urta
                                             n
                                             gdee(fl erns(ip(rpirciecse)s),] 
                                             p e r i orde=t1u4r)n: 
                                             m l ,   soiugt,= [hNiosnte
                                             ]
                                             *dpeefr iboudi;l da(gr=aawl)=:0
                                             . 0 
                                                 p r ifcoers =i[ ri[n" crlaonsgee"(]1 ,f opre rri oidn+ 1r)a:w
                                                 ] 
                                                          e 5 0d==epmrai(cpersi[cie]s-,p5r0i)c;e se[2i0-01=]e
                                                          m a ( p r i c e si,f2 0d0>)0
                                                          :   a g +r=1d4
                                                          = r s i ( p r i ceelss)e;:  mall,-s=idg
                                                          , h i s ta=gm/a=cpde(rpiroidc;e sa)l
                                                          / = p e rrieotdu
                                                          r n   [ {o"udta.taep"p:ernadw([rio]u[n"dd(a1t0e0" ]i,f" parli=c=e0" :erlaswe[ i1]0[0"-c1l0o0s/e("1]+,a
                                                          g / a l ) ,   2 ) ) 
                                                                " efmoar5 0i" :ien5 0r[ain]g,e"(epmear2i0o0d"+:1e,2 0l0e[ni(]p,r
                                                                i c e s ) ) : 
                                                                            " r sdi="p:rri1c4e[si[]i,]"-mparcidc"e:sm[li[-i1]],
                                                                            " s i g n a l " :asgi=g([aig]*,("pheirsito"d:-h1i)s+tm[aix](}d
                                                                            , 0 ) ) / p e r i o d 
                                                                              f o r   i   i na lr=a(nagle*((lpeenr(iroadw-)1))]+
                                                                              m
                                                                              adxe(f- dc,l0a)u)d/ep_earniaoldy
                                                                              s e ( c o i n ,  oduatt.aa)p:p
                                                                              e n d ( rloausntd=(d1a0t0a [i-f1 ]a
                                                                              l = = 0  deelfs ep x1(0v0)-:1 0r0e/t(u1r+na gf/"a$l{)v,: ,2.)2)f
                                                                              } "   i fr evt uarnnd  ovu>t=
                                                                              1
                                                                               deelfs em a(cfd"($p{rvi:c.e5sf)}:"
                                                                                 i f   ve 1e2l=seem a"(-p"r)i
                                                                                 c e s , 1c2t)x;   e=2 6f="eCmoai(np:r i{cceosi,n2}6/)U
                                                                                 S D   -  mDla=i[lryo u-n d{(lea1s2t[[i']d-aet2e6'[]i}]\,n6\)n AiKfT UeE1L2L[:i\]n "a
                                                                                 n d   e 2c6t[xi ]+ =e lfs"e   NPorneei sf:o r   i{ pixn( lraasntg[e'(plreinc(ep'r]i)c}e\sn) ) ]E
                                                                                 M A   5 0s:t = n{epxxt((lia sfto[r' eim,av5 0i'n] )e}n\unm"e
                                                                                 r a t e (cmtlx)  +i=f  fv"  i sE MnAo t2 0N0o:n e{)p
                                                                                 x ( l a sstr[='eemmaa(2[0v0 'f]o)r} \vn  i nR SmIl( 1i4f) :v  {ilsa snto[t' rNsoin'e]]},\9n)"
                                                                                 
                                                                                         scitgx= [+N=o nfe"  i fM AmClD[:i ]   i s{ lNaosnte[ 'emlasced 's]r}[ i -Ssitg]n aflo:r  {il aisnt [r'asniggen(alle'n](}p r iHciesst):) ]{
                                                                                         l a s t [h'ihsits=t['r]o}u\nnd\(nmLlE[TiZ]T-Es i3g0[ iT]A,G6E): \inf" 
                                                                                         m l [ i ]f oirs  dn oitn  Ndoantea [a-n3d0 :s]i:g
                                                                                         [ i ]   i s   n octt xN o+n=e  fe"l s e{ dN[o'ndea tfeo'r] }i:  i{np xr(adn[g'ep(rliecne('p]r)i}c e|s )R)S]I
                                                                                         : { d [ 'rrestiu'r]n}  m|l ,M AsCiDg:,{ dh[i'smta
                                                                                         c
                                                                                         dd'e]f}  b|u iHlids(tr:a{wd)[:'
                                                                                         h i s t 'p]r}i\cne"s
                                                                                         =
                                                                                         [ r [ " cplaoysleo"a]d  f=o rj sro ni.nd urmapws](
                                                                                         { 
                                                                                               e 5 0 = e m"am(opdreilc"e:s ,"5c0l)a;u dee2-0o0p=uesm-a4(-p5r"i,c
                                                                                               e s , 2 0 0 ) 
                                                                                                 " m a xr_1t4o=kresnis("p:r i2c0e0s0),;
                                                                                                   m l , s i g , h"issyts=tmeamc"d:( p"rDiuc ebsi)s
                                                                                                   t   e i nr eetrufranh r[e{n"edra tKer"y:prtaow-[Tie]c[h"ndiastceh"e]r,-"Apnrailcyes"t: rmaiwt[ iE]x[p"ecrltoissee" ]i,n
                                                                                                     E l l i o t t - W e l l e"ne,m aR5S0I",: eM5A0C[Di ]u,n"de mEaM2A0s0." :Aen2a0l0y[sii]e,r
                                                                                                     e   p r a e w e i s e   u n"dr smie"i:nru1n4g[sis]t,a"rmka cadu"f: mDle[uit]s,c"hs.i gSneail "k:osnikgr[eit] ,m"ihti sPtr"e:ihsinsitv[eia]u}s
                                                                                                     . " , 
                                                                                                                      "fmoers sia giens "r:a n[g{e"(rloelne("r:a"wu)s)e]r
                                                                                                                      "
                                                                                                                      ,d"ecfo nctleanutd"e:_(a
                                                                                                                      n a l y s e ( c o i n ,  fd"a{tcat)x:}
                                                                                                                      \ n \ n Gliabs te=idnaet av[o-l1l]s
                                                                                                                      t a e n ddiegfe  ptxe(cvh)n:i srcehteu rAnn afl"y$s{ev :m,i.t2 fd}i"e siefn  vA basncdh nvi>t=t1e ne:l\sne" 
                                                                                                                      ( f " $ { v : . 5 f } "  "i#f#  v1 .e lEslel i"o-t"t)-
                                                                                                                      W e l l ecnt-xA n a=l yfs"eC\oni"n
                                                                                                                      :   { c o i n } / U S D  "-A kDtaiivley  W-e l{llea?s tI[m'pdualtse 'o]d}e\rn \KnoArKrTeUkEtLuLr:?\ nP"o
                                                                                                                      s i t i ocnt xi m+ =Z yfk"l u sP?r\eni\sn:" 
                                                                                                                          { p x ( l a s t [ ' p"r#i#c e2'.] )E}M\An- T rEeMnAd s5t0r:u k t{uprx\(nl"a
                                                                                                                          s t [ ' e m a 5 0 ' ] ) }"\Pnr"e
                                                                                                                          i s   v sc.t xE M+A=5 0f "v s .E MEAM A220000:.  {Gpoxl(dleans/tD[e'aetmha 2C0r0o's]s)?}\\nn\ n "R
                                                                                                                          S I ( 1 4 ) :   { l a s t"[#'#r s3i.' ]R}S\In-"A
                                                                                                                          n a l y scet\xn "+
                                                                                                                          =   f "     M A C D :    " M o{mleansttu[m',m aZcodn'e]n},   DSiivgenragle:n z{elna?s\tn[\'ns"i
                                                                                                                          g n a l ' ] }     H i s t":# #{ l4a.s tM[A'ChDi-sAtn'a]l}y\sne\\nnL"E
                                                                                                                          T Z T E   3 0   T A G E :"\Cnr"o
                                                                                                                          s s o v efro,r  Hdi sitno gdraatmam[,- 3M0o:m]e:n
                                                                                                                          t u m ? \ n \ n "c
                                                                                                                          t x   + =   f "     { d ["'#d#a t5e.' ]G}e:s a{mptxb(idl[d' p&r iScceh'l]u)e}s s|e lRnSiIv:e{adu[s'\rns"i
                                                                                                                          ' ] }   |   M A C D : { d"[B'imaasc d+' ]k}o n|k rHeitset :S{udp[p'ohrits/tR'e]s}i\snt"a
                                                                                                                          n
                                                                                                                          c e - P rpeaiyslzooande n=. \jns\onn".
                                                                                                                          d u m p s ( { 
                                                                                                                                    " # #  "6m.o d2e-lT"a:g e"sc-lParuodgen-oospeu\sn-"4
                                                                                                                                    - 5 " , 
                                                                                                                                                    ""Wmaasx _wtiorkde nisn" :d e2n0 0n0a,e
                                                                                                                                                    c h s t e n   4 8" sSytsutnedme"n:  W"ADHuR SbCiHsEtI NeLiInC He rpfaashsrieenreern ?K r"y
                                                                                                                                                    p t o - T e c h n i s c h"eNre-nAnnea leyisnt  kmointk rEextpeesr tKiusres ziine lE lnlaicoht to-bWeenl lUeNnD,  nRaScIh,  uMnAtCeDn  umnidt  EPMrAosz.e nAtnaanlgyasbieenr.e  "p
                                                                                                                                                    r a e w e i s e   u n d  "mBeeinneunnnges sdtaasr kw aahurfs cDheeuitnslcihc.h sSteei  Skzoennkarreito  m(izt. BP.r e7i0s%n iWvaeharussc.h"e,i
                                                                                                                                                    n l i c h k e i t")m eusnsda gdeass" :a l[t{e"rrnoaltei"v:e" uSszeern"a,r"icoo n(t3e0n%t)".: ("
                                                                                                                                                    
                                                                                                                                                                            f""W{ecltcxh}e\ nK\unrGsimba rekienne  svionldl setnatesncdhiegied etnedc?h nWiassc hmeu sAsn aeliynster emtietn  ddiaemsietn  dAabss cHhanuiptttsezne:n\anr"i
                                                                                                                                                                            o   u n g u e l t i g   w"i#r#d  1(.I nEvlalliiodtite-rWuenlglselne-vAenla)l?y s"e
                                                                                                                                                                            \ n " 
                                                                                                                                                                                              " K l a"rAek tHiavned lWuenlglsee?m pIfmephullusn go:d eArb wKaorrtreenk,t uLro?n gPso saiutfiboanu einm,  Zoydkelru sV?o\rns\inc"h
                                                                                                                                                                                              t   g e b o t e n ? " 
                                                                                                                                                                                                " # #   2 .   E)M}A]-
                                                                                                                                                                                                T r e n d}s)t.reunkctoudre\(n)"
                                                                                                                                                                                                
                                                                                                                                                                                                
                                                                                                                                                                                                         r e q   =   u r"lPlriebi.sr evqsu.e sEtM.AR5e0q uvess.t (E
                                                                                                                                                                                                         M A 2 0 0 .   G o"lhdtetnp/sD:e/a/tahp iC.raonstsh?r\onp\inc".
                                                                                                                                                                                                         c o m / v 1 / m e s s a g"e#s#" ,3 .d aRtSaI=-pAanyalloyasde,\
                                                                                                                                                                                                         n " 
                                                                                                                                                                                                                     h e a d e r s"=M{o"mCeonnttuemn,t -ZToynpeen",: "Daipvpelrigceantzieonn?/\jns\onn""
                                                                                                                                                                                                                     , 
                                                                                                                                                                                                                                           " # #   4 .  "MxA-CaDp-iA-nkaelyy"s:e \AnN"T
                                                                                                                                                                                                                                           H R O P I C _ A P I _ K E"YC,r
                                                                                                                                                                                                                                           o s s o v e r ,   H i s t o g r a m"ma,n tMhormoepnitcu-mv?e\rns\ino"n
                                                                                                                                                                                                                                           " : " 2 0 2 3 - 0 6 - 0 1""#}#,  5m.e tGheosda=m"tPbOiSlTd" )&
                                                                                                                                                                                                                                             S c h lwuietshs eulrnlilvieba.urse\qnu"e
                                                                                                                                                                                                                                             s t . u r l o p e n ( r e"qB,i atsi m+e okuotn=k6r0e)t ea sS urp:p
                                                                                                                                                                                                                                             o r t / R e s i srteatnucren- Pjrseoins.zloonaedns.(\rn.\rne"a
                                                                                                                                                                                                                                             d ( ) ) [ " c o n t e n t""#]#[ 06].[ "2t-eTxatg"e]s
                                                                                                                                                                                                                                             -
                                                                                                                                                                                                                                             Pdreofg naonsael\yns"e
                                                                                                                                                                                                                                             _ t o _ h t m l ( c o i n",W adsa twai,r dt eixnt )d:e
                                                                                                                                                                                                                                             n   n a elcahsstt=edna t4a8[ -S1t]u
                                                                                                                                                                                                                                             n d e n  dWeAfH RpSxC(HvE)I:N LrIeCtHu rpna sfs"i$e{rve:n,?. 2"f
                                                                                                                                                                                                                                             } "   i f   v   a n d   v">N=e1n neel seei n( fk"o$n{kvr:e.t5efs} "K uirfs zvi eell snea c"h- "o)b
                                                                                                                                                                                                                                             e n   U NdDe fn arcshi _ucnotleonr (mvi)t: 
                                                                                                                                                                                                                                             P r o z e n t a nigfa bneont.  v":
                                                                                                                                                                                                                                               r e t u r n   " # 8 8 8""B
                                                                                                                                                                                                                                               e n e n n e   d arse twuarhnr s"c#hee7i4ncl3icc"h sitfe  vS>z7e0n aerlisoe  ((z".#B2.7 a7e06%0 "W aihfr svc<h3e0i nellisceh k"e#ift3)9 cu1n2d" )d
                                                                                                                                                                                                                                               a s   a ldteefr ntact(ivv)e:  Srzeetnuarrni o" #(2370a%e)6.0 "" 
                                                                                                                                                                                                                                               i f   ( v   o r   0 ) > 0" Weellsceh e" #Keu7r4scm3acr"k
                                                                                                                                                                                                                                               e
                                                                                                                                                                                                                                               n   s i ncdo ienn_tcsoclhoeri d e n=d ?" #Wfa7s9 3m1uas"s  iefi nctorient=e=n" BdTaCm"i te ldsaes  "H#a3u4p6tasaz9e"n
                                                                                                                                                                                                                                               a r i o  eumnag5u0e_lotki g   w i r=d  ((lIansvta[l"ipdriiecreu"n]g solre v0e)l )>?  ("l
                                                                                                                                                                                                                                               a s t [ " e m a 5 0 " ]  " Kolra r0e) 
                                                                                                                                                                                                                                               H a n d leumnag2s0e0m_pofke h l u n=g :( lAabswta[r"tperni,c eL"o]n gosr  a0u)f b>a u(elna,s to[d"eerm aV2o0r0s"i]c hotr  g0e)b
                                                                                                                                                                                                                                               o
                                                                                                                                                                                                                                               t e n ? "h
                                                                                                                                                                                                                                               t m l _ t e x t  )=} ]"
                                                                                                                                                                                                                                               " 
                                                                                                                                                                                                                                                     } )f.oern cloidnee( )i
                                                                                                                                                                                                                                                     n
                                                                                                                                                                                                                                                       t e x tr.esqp l=i tu(r"l\lni"b).:r
                                                                                                                                                                                                                                                       e q u e s t . R eiqfu elsitn(e
                                                                                                                                                                                                                                                       . s t a r t s w i"thht(t"p#s#: /"/)a:p
                                                                                                                                                                                                                                                       i . a n t h r o p i c . csoemc/tvi1o/nm e=s slaignees["3,: ]d
                                                                                                                                                                                                                                                       a t a = p a y l o a d , 
                                                                                                                                                                                                                                                       c o l o r   =   "h#eea7d4ecr3sc="{ "iCfo n"t2e-nTta-gTeysp"e "i:n" aspepcltiicoant ioorn /"jPsroong"n,o
                                                                                                                                                                                                                                                       s e "   i n   s e c t i o n   e l s"ex -"a#p2ic-3kee5y0"":
                                                                                                                                                                                                                                                         A N T H R O P I C _ A PbIg_ K=E Y",b
                                                                                                                                                                                                                                                         a c k g r o u n d : # 1 a 0 a 0 a ;""a nitfh r"o2p-iTca-gveesr"s iionn "s:e"c2t0i2o3n- 0o6r- 0"1P"r}o,g nmoesteh"o di=n" PsOeScTt"i)o
                                                                                                                                                                                                                                                         n   e l swei t"h" 
                                                                                                                                                                                                                                                         u r l l i b . r e q u e shtt.mulr_ltoepxetn (+r=e qf,' <thi3m esotuytl=e6=0")c oalso rr::{
                                                                                                                                                                                                                                                         c o l o r } ; b orredteurr-nb ojtstoonm.:l2opaxd ss(orl.irde a{dc(o)i)n[_"ccoolnotre}n;tp"a]d[d0i]n[g"-tbeoxttt"o]m
                                                                                                                                                                                                                                                         :
                                                                                                                                                                                                                                                         4dpexf; maanragliyns-et_otpo:_2h4tpmxl;({cbogi}n",> {dsaetcat,i otne}x<t/)h:3
                                                                                                                                                                                                                                                         > ' 
                                                                                                                                                                                                                                                             l a s t = d aetlai[f- 1"]*
                                                                                                                                                                                                                                                             * "   i nd elfi npex:(
                                                                                                                                                                                                                                                             v ) :   r e t u r n   f "h$t{mvl:_,t.e2xft} "+ =i ff 'v< pa nsdt yvl>e==1" mealrsgei n(:f4"p$x{ v0:;.l5ifn}e"- hiefi gvh te:l1s.e7 "">-<"s)t
                                                                                                                                                                                                                                                             r o n g >d{ehft mrls.ie_sccoalpoer((lvi)n:e
                                                                                                                                                                                                                                                             . r e p l a c e (i"f* *n"o,t" "v):) }r<e/tsutrrno n"g#>8<8/8p">
                                                                                                                                                                                                                                                             ' 
                                                                                                                                                                                                                                                                           r eetluirfn  l"i#nee7.4sct3rci"p (i)f: 
                                                                                                                                                                                                                                                                           v > 7 0   e l s e   ( " ##2 7Haieg6h0l"i gihft  vp<r3o0b aeblislei t"y# fl3i9nce1s2
                                                                                                                                                                                                                                                                           " ) 
                                                                                                                                                                                                                                                                                    d e f   t cs(tvy)l:e  r=e t"ucronl o"r#:2#7ea7e46c03"c ;iffo n(tv- woeri g0h)t>:0b oellds;e"  "i#fe 7"4%c"3 ci"n
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     l i n e  caonidn _(c"oWlaohrr s c h=e i"n#lfi7c9h3k1eai"t "i fi nc oliinn=e= "oBrT C""S zeelnsaer i"o#"3 4i6na al9i"n
                                                                                                                                                                                                                                                                                     e )   e lesmea 5"0"_
                                                                                                                                                                                                                                                                                     o k           =   ( l a shtt[m"lp_rtiecxet" ]+ =o rf '0<)p  >s t(yllaes=t"[m"aermgai5n0:"4]p x  o0r; l0i)n
                                                                                                                                                                                                                                                                                     e - h e iegmhat2:010._7o;k{ s t y l=e }("l>a{shtt[m"lp.reisccea"p]e (olri n0e)) }>< /(pl>a's
                                                                                                                                                                                                                                                                                     t
                                                                                                                                                                                                                                                                                     [ " e m ad2e0f0 "r]o wo(rb g0,) 
                                                                                                                                                                                                                                                                                     l
                                                                                                                                                                                                                                                                                     a b e l ,h tvmall_utee,x tc o=l o"r",
                                                                                                                                                                                                                                                                                       s t a tfuosr,  lsitnaet uisn_ ctoelxotr.)s:p
                                                                                                                                                                                                                                                                                       l i t ( " \ n " )r:e
                                                                                                                                                                                                                                                                                       t u r n   ( f ' <itfr  lsitnyel.es=t"abrotrsdweirt-hb(o"t#t#o m":)1:p
                                                                                                                                                                                                                                                                                       x   s o l i d   # e e e ;sbeacctkigorno u=n dl:i{nbeg[}3":>]'
                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                               c o l o rf '=< t"d# es7t4ycl3ec="" piafd d"i2n-gT:a1g1epsx"  1i6np xs;eccotlioorn: #o5r5 5";Pfroongtn-ossiez"e :i1n3 psxe"c>t{iloanb eell}s<e/ t"d#>2'c
                                                                                                                                                                                                                                                                                                               3 e 5 0 " 
                                                                                                                                                                                                                                                                                                                                     f 'b<gt d=  s"tbyalcek=g"rpoaudnddi:n#g1:a101ap0xa ;1"6 pixf; f"o2n-tT-awgeeisg"h ti:nb osledc;tcioolno ro:r{ c"oPlroorg}n"o>s{ev"a liune }s<e/cttdi>o'n
                                                                                                                                                                                                                                                                                                                                       e l s e   " " 
                                                                                                                                                                                                                                                                                                                                                       f ' < t dh tsmtly_ltee=x"tp a+d=d ifn'g<:h131 psxt y1l6ep=x";cfoolnotr-:s{iczoel:o1r2}p;xb;ofrodnetr--wbeoitgthotm::b2oplxd ;scoolliodr :{{csotiant_ucso_lcoorl}o;rp}a"d>d{isntga-tbuost}t<o/mt:d4>p<x/;tmra>r'g)i
                                                                                                                                                                                                                                                                                                                                                       n
                                                                                                                                                                                                                                                                                                                                                       - t o p :r2e4tpuxr;n{ bfg"}""">
                                                                                                                                                                                                                                                                                                                                                       {<sdeicvt isotny}l<e/=h"3f>o'n
                                                                                                                                                                                                                                                                                                                                                       t - f a m i l y :eAlriifa l",*s*a"n si-ns elriinfe;:m
                                                                                                                                                                                                                                                                                                                                                       a x - w i d t h : 6 8 0 phxt;mmla_rtgeixnt: 0+ =a uft'o< p4 0sptxy laeu=t"om;abragcikng:r4opuxn d0:;#lfi8nfe9-fhae;ipgahdtd:i1n.g7:"2>0<psxt;rboonrgd>e{rh-trmald.ieussc:a8ppex("l>i
                                                                                                                                                                                                                                                                                                                                                       n e .<rdeipvl asctey(l"e*=*""b,a"c"k)g)r}o<u/nsdt:rloinnge>a<r/-pg>r'a
                                                                                                                                                                                                                                                                                                                                                       d i e n t ( 1 3 5edleigf, #l1ian1ea.2set,r#i1p6(2)1:3
                                                                                                                                                                                                                                                                                                                                                       e ) ; c o l o r : w h i t#e ;Hpiagdhdliinggh:t2 0pprxo;bbaobridleirt-yr aldiinuess:
                                                                                                                                                                                                                                                                                                                                                       8 p x ; m a r g i n - b ostttyolme: 2=0 p"xc;obloorrd:e#re-7l4ecf3tc:;5fpoxn ts-owleiidg h{tc:obionl_dc;o"l oirf} "">%
                                                                                                                                                                                                                                                                                                                                                       "   i n  <ldiinve  satnydl e(=""Wfaohnrts-cshiezien:l1i1cphxk;eliett"t eirn- slpiancei nogr: 2"pSxz;eonpaarciiot"y :i0n. 6l"i>nTeE)C HeNlIsSeC H"E" 
                                                                                                                                                                                                                                                                                                                                                       A N A L Y S E   -   D A IhLtYm l-_ t{elxats t+[=' dfa't<ep' ]s}t<y/ldei=v">m
                                                                                                                                                                                                                                                                                                                                                       a r g i n<:d4ipvx  s0t;yllien=e"-fhoenitg-hsti:z1e.:72;4{psxt;yfloen}t"->w{ehitgmhlt.:ebsocladp;em(alrignien)-}t<o/pp:>4'p
                                                                                                                                                                                                                                                                                                                                                       x
                                                                                                                                                                                                                                                                                                                                                       ; c o l odre:f{ crooiwn(_bcgo,l olra}b"e>l{,c ovianl}u/USD</div>
                                                                                                                                                                                                                                                                                                                                                           <div style="font-size:13px;opacity:0.7;margin-top:2px">Elliott WaveKONFIGURATION
# ══════════════════════════════════════════════════════════════

ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
GMAIL_ABSENDER     = os.environ["GMAIL_ABSENDER"]
GMAIL_APP_PASSWORT = os.environ["GMAIL_APP_PASSWORT"]
EMPFAENGER         = os.environ["EMPFAENGER"]

# Kraken-Paare  (nicht ändern)
COINS = [
    {"name": "BTC", "pair": "XBTUSD",  "kraken": "XXBTZUSD"},
    {"name": "XRP", "pair": "XRPUSD",  "kraken": "XXRPZUSD"},
]

# ══════════════════════════════════════════════════════════════
#  DATENABRUF  (Kraken – kein API-Key, kein Geo-Block)
# ══════════════════════════════════════════════════════════════

def fetch_kraken(pair, kraken_key, limit=720):
    # since = Unix-Timestamp vor 'limit' Tagen
    since = int((datetime.datetime.utcnow() -
                 datetime.timedelta(days=limit)).timestamp())
    url = (f"https://api.kraken.com/0/public/OHLC"
           f"?pair={pair}&interval=1440&since={since}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())
    if data.get("error"):
        raise Exception(f"Kraken-Fehler: {data['error']}")
    candles = data["result"][kraken_key]
    return [
        {"date":  datetime.date.fromtimestamp(int(c[0])).isoformat(),
         "close": float(c[4])}          # index 4 = close
        for c in candles
        if float(c[4]) > 0
    ]

# ══════════════════════════════════════════════════════════════
#  INDIKATOREN
# ══════════════════════════════════════════════════════════════

def ema(prices, period):
    k = 2/(period+1); out=[]; prev=None
    for i,p in enumerate(prices):
        if i < period-1: out.append(None); continue
        if prev is None: prev = sum(prices[:period])/period
        else: prev = p*k + prev*(1-k)
        out.append(round(prev, 6))
    return out

def rsi(prices, period=14):
    out=[None]*period; ag=al=0.0
    for i in range(1, period+1):
        d=prices[i]-prices[i-1]
        if d>0: ag+=d
        else: al-=d
    ag/=period; al/=period
    out.append(round(100 if al==0 else 100-100/(1+ag/al), 2))
    for i in range(period+1, len(prices)):
        d=prices[i]-prices[i-1]
        ag=(ag*(period-1)+max(d,0))/period
        al=(al*(period-1)+max(-d,0))/period
        out.append(round(100 if al==0 else 100-100/(1+ag/al), 2))
    return out

def macd(prices):
    e12=ema(prices,12); e26=ema(prices,26)
    ml=[round(e12[i]-e26[i],6) if e12[i] and e26[i] else None for i in range(len(prices))]
    st=next(i for i,v in enumerate(ml) if v is not None)
    sr=ema([v for v in ml if v is not None],9)
    sig=[None if ml[i] is None else sr[i-st] for i in range(len(prices))]
    hist=[round(ml[i]-sig[i],6) if ml[i] is not None and sig[i] is not None else None
          for i in range(len(prices))]
    return ml, sig, hist

def build(raw):
    prices=[r["close"] for r in raw]
    e50=ema(prices,50); e200=ema(prices,200)
    r14=rsi(prices); ml,sig,hist=macd(prices)
    return [{"date":raw[i]["date"],"price":raw[i]["close"],
             "ema50":e50[i],"ema200":e200[i],
             "rsi":r14[i],"macd":ml[i],"signal":sig[i],"hist":hist[i]}
            for i in range(len(raw))]

# ══════════════════════════════════════════════════════════════
#  CLAUDE-ANALYSE
# ══════════════════════════════════════════════════════════════

def claude_analyse(coin, data):
    last=data[-1]
    def px(v): return f"${v:,.2f}" if v and v>=1 else (f"${v:.5f}" if v else "—")
    ctx  = f"Coin: {coin}/USD · Daily · {last['date']}\n\nAKTUELL:\n"
    ctx += f"  Preis:   {px(last['price'])}\n  EMA 50:  {px(last['ema50'])}\n"
    ctx += f"  EMA 200: {px(last['ema200'])}\n  RSI(14): {last['rsi']}\n"
    ctx += f"  MACD:    {last['macd']}  Signal: {last['signal']}  Hist: {last['hist']}\n\nLETZTE 30 TAGE:\n"
    for d in data[-30:]:
        ctx += f"  {d['date']}: {px(d['price'])} | RSI:{d['rsi']} | MACD:{d['macd']} | Hist:{d['hist']}\n"

    payload = json.dumps({
        "model": "claude-opus-4-5",
        "max_tokens": 1500,
        "system": "Du bist ein professioneller Krypto-Technischer-Analyst mit Expertise in Elliott-Wellen. Analysiere präzise auf Deutsch.",
        "messages": [{"role":"user","content":(
            f"{ctx}\n\nGib eine vollständige technische Analyse:\n"
            "## 1. Elliott-Wellen-Analyse\n## 2. EMA-Trendstruktur\n"
            "## 3. RSI-Analyse\n## 4. MACD-Analyse\n## 5. Gesamtbild & Schlüsselniveaus"
        )}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=payload,
        headers={"Content-Type":"application/json",
                 "x-api-key": ANTHROPIC_API_KEY,
                 "anthropic-version":"2023-06-01"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["content"][0]["text"]

# ══════════════════════════════════════════════════════════════
#  HTML-EMAIL
# ══════════════════════════════════════════════════════════════

def analyse_to_html(coin, data, text):
    last=data[-1]
    def px(v): return f"${v:,.2f}" if v and v>=1 else (f"${v:.5f}" if v else "—")
    def rsi_color(v):
        if not v: return "#888"
        return "#e74c3c" if v>70 else ("#27ae60" if v<30 else "#f39c12")
    def tc(v): return "#27ae60" if (v or 0)>0 else "#e74c3c"

    coin_color   = "#f7931a" if coin=="BTC" else "#346aa9"
    ema50_ok     = (last["price"] or 0) > (last["ema50"]  or 0)
    ema200_ok    = (last["price"] or 0) > (last["ema200"] or 0)

    html_text = ""
    for line in text.split("\n"):
        if line.startswith("## "):
            html_text += f'<h3 style="color:#2c3e50;border-bottom:2px solid {coin_color};padding-bottom:4px;margin-top:24px">{line[3:]}</h3>'
        elif "**" in line:
            html_text += f'<p style="margin:4px 0;line-height:1.7"><strong>{html.escape(line.replace("**",""))}</strong></p>'
        elif line.strip():
            html_text += f'<p style="margin:4px 0;line-height:1.7">{html.escape(line)}</p>'

    def row(bg, label, value, color, status, status_color):
        return (f'<tr style="border-bottom:1px solid #eee;background:{bg}">'
                f'<td style="padding:11px 16px;color:#555;font-size:13px">{label}</td>'
                f'<td style="padding:11px 16px;font-weight:bold;color:{color}">{value}</td>'
                f'<td style="padding:11px 16px;font-size:12px;font-weight:bold;color:{status_color}">{status}</td></tr>')

    return f"""
<div style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto 40px auto;background:#f8f9fa;padding:20px;border-radius:8px">
  <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:20px;border-radius:8px;margin-bottom:20px;border-left:5px solid {coin_color}">
    <div style="font-size:11px;letter-spacing:2px;opacity:0.6">TECHNISCHE ANALYSE · DAILY · {last['date']}</div>
    <div style="font-size:24px;font-weight:bold;margin-top:4px;color:{coin_color}">{coin}/USD</div>
    <div style="font-size:13px;opacity:0.7;margin-top:2px">Elliott Wave · RSI · MACD · EMA 50/200</div>
  </div>

  <table style="width:100%;border-collapse:collapse;margin-bottom:20px;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
    <tr style="background:#2c3e50;color:white">
      <td style="padding:10px 16px;font-size:11px;letter-spacing:1px;font-weight:bold">INDIKATOR</td>
      <td style="padding:10px 16px;font-size:11px;letter-spacing:1px;font-weight:bold">WERT</td>
      <td style="padding:10px 16px;font-size:11px;letter-spacing:1px;font-weight:bold">STATUS</td>
    </tr>
    {row("white",      "Preis",      f'<span style="font-size:17px">{px(last["price"])}</span>', coin_color, "", "")}
    {row("#fafafa",    "EMA 50",     px(last["ema50"]),  "#2980b9", "Preis ÜBER EMA50 ▲" if ema50_ok  else "Preis UNTER EMA50 ▼",  "#27ae60" if ema50_ok  else "#e74c3c")}
    {row("white",      "EMA 200",    px(last["ema200"]), "#c0392b", "Preis ÜBER EMA200 ▲" if ema200_ok else "Preis UNTER EMA200 ▼", "#27ae60" if ema200_ok else "#e74c3c")}
    {row("#fafafa",    "RSI (14)",   str(last["rsi"]),   rsi_color(last["rsi"]), "🔴 Überkauft" if (last["rsi"] or 0)>70 else ("🟢 Überverkauft" if (last["rsi"] or 0)<30 else "🟡 Neutral"), rsi_color(last["rsi"]))}
    {row("white",      "MACD",       str(last["macd"]),  tc(last["macd"]), "🟢 Bullish" if (last["macd"] or 0)>0 else "🔴 Bearish", tc(last["macd"]))}
    {row("#fafafa",    "Histogramm", str(last["hist"]),  tc(last["hist"]), "↑ Momentum steigt" if (last["hist"] or 0)>0 else "↓ Momentum fällt", tc(last["hist"]))}
  </table>

  <div style="background:white;border-radius:8px;padding:22px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
    <div style="font-size:11px;color:#888;letter-spacing:1px;margin-bottom:14px">⚡ KI ELLIOTT WAVE ANALYSE · CLAUDE AI</div>
    {html_text}
  </div>
  <div style="text-align:center;margin-top:14px;font-size:11px;color:#aaa">
    Automatisch generiert · Nur zu Informationszwecken · Keine Anlageberatung
  </div>
</div>"""

# ══════════════════════════════════════════════════════════════
#  E-MAIL VERSAND
# ══════════════════════════════════════════════════════════════

def send_email(subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_ABSENDER
    msg["To"]      = EMPFAENGER
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL_ABSENDER, GMAIL_APP_PASSWORT)
        s.sendmail(GMAIL_ABSENDER, EMPFAENGER, msg.as_string())

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    heute = datetime.date.today().strftime("%d.%m.%Y")
    print(f"=== BTC & XRP Analyse {heute} ===\n")
    alle_html = ""

    for coin in COINS:
        name = coin["name"]
        print(f"⟳  {name}: Lade Kraken-Daten …")
        try:
            raw  = fetch_kraken(coin["pair"], coin["kraken"])
            data = build(raw)
            print(f"   ✓ {len(data)} Tage geladen, letzter Kurs: ${data[-1]['price']:,.2f}")
        except Exception as e:
            print(f"   ⚠ Datenfehler: {e}"); continue

        print(f"⟳  {name}: Claude analysiert …")
        try:
            text = claude_analyse(name, data)
            print(f"   ✓ Analyse erhalten ({len(text)} Zeichen)")
        except Exception as e:
            print(f"   ⚠ API-Fehler: {e}"); continue

        alle_html += analyse_to_html(name, data, text)
        alle_html += '<hr style="margin:10px 0 30px 0;border:none;border-top:3px solid #eee">'

        # Kurze Pause zwischen den Coins (CoinGecko Rate-Limit)
        time.sleep(2)

    if not alle_html:
        print("⚠ Keine Daten – E-Mail wird nicht gesendet."); return

    print(f"\n⟳  Sende E-Mail an {EMPFAENGER} …")
    try:
        send_email(f"📊 BTC & XRP Elliott-Wave-Analyse · {heute}", alle_html)
        print(f"✅ E-Mail erfolgreich gesendet!")
    except Exception as e:
        print(f"⚠ E-Mail-Fehler: {e}")
        print("\n→ Gmail App-Passwort prüfen:")
        print("  1. myaccount.google.com → Sicherheit")
        print("  2. '2-Schritt-Verifizierung' muss AN sein")
        print("  3. Suche nach 'App-Passwörter'")
        print("  4. Neues App-Passwort erstellen → in Zeile 19 eintragen")

if __name__ == "__main__":
    main()
