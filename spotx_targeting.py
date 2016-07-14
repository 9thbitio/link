import argparse
import json
from link import lnk


def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--campaign_id', help='give spotx campaign id', type=str, required=True)
    parser.add_argument('--rpm', help='rpm rate calculated to filter channels', type=int,
            required=True)
    return parser.parse_args()


def get_channel_ids(campaign_id, rpm):

    spotx = lnk.apis.spotx

    length = 500
    skip = 0
    channels = []
    while length == 500:
        page = spotx.get("/Publisher(111271)/Channel?$skip={}&$top=500".format(skip)).json['value']
        channels.extend(page)
        skip += 500
        print "Checking next page"
        length = len(page)

    # find rpm or cpm once spotx fixes their defect
    # campaign = spotx.get("/Publisher(111271)/Campaign({})/".format(campaign_id)).json
    # rpm = campaign['creative']['fixed_cpm']

    # remove DNT channels
    channels = [channel for channel in channels if channel['name'][-3:] != 'DNT']

    # filter channels by RPM or VRB naming convention
    return [channel['id'] for channel in channels if (channel['price_floor']
        <= rpm) or (channel['name'][-3:] == 'VRB')]


def targeting(campaign_id, channel_ids):

    campaign_dnt = ['1b2a7.a3f6e.cb48', '1b2a7.2c271.5830', '1b2a7.9f200.f122']
    if campaign_id in campaign_dnt:
        print 'No targeting is allowed for this campaign'
        return None

    spotx = lnk.apis.spotx

    updating_data = {
        'targeting_options' : [
            {
                "category_id" : 7,
                "operator": "is any of",
                "options": channel_ids
            }
        ]
    }

    return spotx.patch("/Publisher(111271)/Campaign({})/".format(campaign_id),
            data=json.dumps(updating_data))


if __name__ == '__main__':
    # argparse for demand_tag_id and rpm
    _args = get_args()
    campaign_id = _args.campaign_id
    rpm = _args.rpm

    # open session with api
    # spotx = connect_api

    # get channel_ids filtered by rpm
    channel_ids = get_channel_ids(campaign_id, rpm)

    # add channels to campaign targeting
    # campaign = targeting(campaign_id, channel_ids)
    # campaign


