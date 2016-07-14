import datetime 
import db
import json
from link import lnk
import springserve as ss

msg = lnk.msg


def get_date():

    today = datetime.datetime.utcnow().date()
    last_week = today - datetime.timedelta(days=6)
    return last_week

def get_spotx_report():

    spotx = lnk.apis.spotx

    length = 500
    skip = 0
    report = []
    while length == 500:
        page = spotx.get("/Publisher(111271)/Channels/RevenueReport?date_range=last_7_days&$skip={}&$top=500".format(skip)).json['value']['data']
        report.extend(page)
        skip += 500
        print "Looking for next page"
        length = len(page)

    return [channel for channel in report if int(channel['impressions']) > 0]

def get_imps(date_last_week):
    
    try:
        conn = db.connect_redshift()

        query = ("""
            SELECT
                demand_tag_id, 
                sum(impressions) as imps
            FROM
                vd.demand_domain_aggregations
            WHERE
                account_id = 1 and ymdh > {}
            GROUP by
                demand_tag_id;
            """).format(date_last_week)

        imps = conn.select_dataframe(query)
        return imps

    except:
        msg.error("Error fetching data")
        raise
    finally:
        if conn:
            try:
                conn.close()
            except:
                msg.warn('Error closing connection', exec_info=True)


def find_rpm(ss_df, spotx_list):
    ss_df['channel_id'] = ss.deman_tags.get(ss_df['demand_tag_id']).demand_code

    spotx_dict = {}
    for channel in spotx_list:
        spotx_dict[channel['channel_id']] = channel['payout']

    spotx_df = pandas.DataFrame(columns=['channel_id', 'revenue'])
    spotx_df.from_dict(spotx_dict.items())

    data = spotx_df.merge(ss_df, how='left', on= 'channel_id')

    # rounds to nearest .05
    data['rpm'] = round(((1.0*data['revenue']/data['imps'])*1000)*2)/2.0

    return data

def apply_rpm(data):
    # take rpm and demand_tag_id from data and update springserve
