from link import lnk
import json
import pandas


def change_names():
    csv = pandas.read_csv('varb.csv')
    spotx = lnk.apis.spotx

    for i, row in csv:
        channel = spotx.get("/Publisher(111271)/Channel()".format(row['id']))

        if not channel.json['name']:
            lnk.msg('Error with tag {}'.format(row['id']))
            
        elif len(channel.json['name']) > 46:
            lnk.msg('Channel name too long for tag {}'.format(row['id']))

        else:
            name = channel.json['name'] + ' VRB'
            spotx.put("/Publisher(111271)/Channel()".format(row['id']),
                    data=json.dumps(name))


if __name__ == '__main__':
    change_names()
            
