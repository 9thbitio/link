import argparse
import json
from link import lnk

msg = lnk.msg
spotx = lnk.apis.spotx

def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--campaign_id', help='spotx campaign id', type=str, required=True)
    parser.add_argument('--cpm', help='cpm rate to filter channels', type=int,
            required=True)
    return parser.parse_args()


def check_campaign(campaign_id):

    """Checking if campaign is on do not target list"""
    campaign_dnt = ['1b2a7.a3f6e.cb48', '1b2a7.2c271.5830', '1b2a7.9f200.f122']
    if campaign_id in campaign_dnt:
        msg.info('No targeting is allowed for this campaign')
        return None
    
    return campaign_id


def get_channels(campaign_id):

    """Get channels from SpotX API to filter"""
    msg.info("Getting Channel IDs")

    length = 500
    skip = 0
    channels = []
    while length == 500:
        page = spotx.get("/Publisher(111271)/Channel?$skip={}&$top=500".format(skip)).json['value']
        channels.extend(page)
        skip += 500
        msg.info("Checking next page")
        length = len(page)

    # find cpm or cpm once spotx fixes their defect
    # campaign = spotx.get("/Publisher(111271)/Campaign({})/".format(campaign_id)).json
    # cpm = campaign['creative']['fixed_cpm']

    return channels


def filter_channels(channels, cpm):

    """Filter through channels by naming conventions and rate"""
    msg.info("Filtering channels")
    channels = [channel for channel in channels if channel['name'][-3:] != 'DNT']

    channel_ids = [channel['id'] for channel in channels if (channel['price_floor']
        <= cpm) or (channel['name'][-3:] == 'VRB')]

    return channel_ids


def targeting(campaign_id, channel_ids):

    """Target channels to campaign"""
    updating_data = {
        'targeting_options' : [
            {
                "category_id" : 7,
                "operator": "is any of",
                "options": channel_ids
            }
        ]
    }

    spotx.patch("/Publisher(111271)/Campaign({})/".format(campaign_id),
            data=json.dumps(updating_data))


if __name__ == '__main__':
    # argparse for demand_tag_id and cpm
    _args = get_args()
    campaign_id = _args.campaign_id
    cpm = _args.cpm

    # get channel_ids filtered by cpm
    campaign_id = check_campaign(campaign_id)
    channels = get_channels(campaign_id)
    channel_ids = filter_channels(channels, cpm)
    targeting(campaign_id, channel_ids)


