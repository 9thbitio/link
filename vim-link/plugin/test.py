# coding: utf-8


from usr.dave import *
get_ipython().magic(u"""prun -s cum d = repomgr.backdoor("select * from agg_dw_intermediate_analytics_adjusted where ymdh >= '2011-10-29 09:04:00' and buyer_member_id = 100 and imp_type=7 limit 10000", 'vt_jayz_internal', 'alpha')""")
d.report_id
get_ipython().magic(u"""prun -s cum d = repomgr.backdoor("select * from agg_dw_intermediate_analytics_adjusted where ymdh >= '2011-10-29 09:04:00' and buyer_member_id = 100 and imp_type=7 limit 200000", 'vt_jayz_internal', 'alpha')""")
d
d.report_id
d.save('usr/dave/big.pnds')
d.to_csv('usr/dave/big.csv')
get_ipython().system(u"ls -F ")
get_ipython().system(u"ls -F -lth usr/dave/")

d = {'this':'that', 'thaiaou':[1,2,3,4,5,6,6,7,8,9,9,7,8,0,8,0,], 'saeuhasouhanoh':d, "thisoheusaehouih":True}
