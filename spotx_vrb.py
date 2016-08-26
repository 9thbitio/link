from link import lnk
import json
import pandas

msg = lnk.msg

def change_names():
    csv = pandas.read_csv('varb.csv', header=None)
    spotx = lnk.apis.spotx
    failed_channels = []
    no_name = []

    for i, row in csv.iterrows():
        msg.info('--- Checking channel {} ---'.format(row[1]))
        try:
            channel = spotx.get("/Publisher(111271)/Channel({})".format(row[1]))
        except:
            msg.error('Error retreiving channel {}'.format(row[1]))
            failed_channels.append(row[1])
            continue

        try:
            channel.json['name']
        except:
            msg.error('Channel {} has no name'.format(row[1]))
            no_name.append(row[1])
            continue
            
        if len(channel.json['name']) > 46:
            msg.info('Channel name too long for tag {}'.format(row[1]))

        elif channel.json['name'][-3:] == 'VRB':
            msg.info('Name already changed for tag {}.'.format(row[1]))

        else:
            name = channel.json['name'] + ' VRB'
            channel.json['name'] = name
            spotx.put("/Publisher(111271)/Channel({})".format(row[1]),
                    data=json.dumps(channel.json))
            msg.info('Changed name for tag {}'.format(row[1]))
    
    print "FAILED CHANNELS"
    print failed_channels
    print "CHANNELS WITH NO NAME"
    print no_name

if __name__ == '__main__':
    change_names()
            
