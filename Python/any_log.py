#!/bin/env python
# coding: utf-8

f = file('test.txt')

log = True

result = {}
while log:
    try:
        log = f.readline().strip('\n').split(',')
        if int(log[15]) == 2:
            uid = int(log[5])
            prop_id = int(log[13])
            prop_num = int(log[14])
            diamond_num = int(log[16])
            if result.get(uid):
                if result.get(uid).get(prop_id):
                    result.get(uid).get(prop_id)[0] += prop_num
                    result.get(uid).get(prop_id)[1] += diamond_num
                else:
                    result.get(uid)[prop_id] = [prop_num,diamond_num]
            else:
                result[uid] = {prop_id:[prop_num,diamond_num]}
    except:
        break

for uid,props in result.iteritems():
    for prop_id,prop_item in props.iteritems():
        print('%s,%s,%s,%s') % (uid,prop_id,prop_item[0],prop_item[1])

