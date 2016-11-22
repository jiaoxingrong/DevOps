#!/bin/env python
#coding: utf-8

import time
import json
from sqlalchemy import create_engine, Table, Column, MetaData, select, INTEGER, VARCHAR, TEXT, and_
import datetime
import calendar

def main():
    metadata = MetaData()
    engine = create_engine('mysql+mysqlconnector://ops:McudGpjNIViP@108.61.76.139:3306/oas_server_yw', encoding='utf-8',pool_recycle=7200,pool_size=15,max_overflow=30)

    game_online_stat = Table('game_online_stat',metadata,
            Column('id', INTEGER, primary_key=True),
            Column('area', VARCHAR(30)),
            Column('server_id', INTEGER),
            Column('s_merge', VARCHAR(50)),
            Column('count', INTEGER),
            Column('cj_date', INTEGER),
            Column('code', VARCHAR(4)),
            Column('error', INTEGER),
            Column('game', VARCHAR(50)))

    game_online_stat_day = Table('game_online_stat_day',metadata,
        Column('id', INTEGER, primary_key=True),
        Column('game', VARCHAR(20)),
        Column('area', VARCHAR(20)),
        Column('server_id', INTEGER),
        Column('data', TEXT),
        Column('date', INTEGER))

    conn = engine.connect()

    yesterday = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
    start_ts = calendar.timegm(yesterday.timetuple()) - 28800
    end_ts = start_ts + 86400

    w_sql = and_(
            game_online_stat.c.cj_date > 1475683200,
            game_online_stat.c.cj_date < 1475769600
        )

    s = select([game_online_stat.c.game,
        game_online_stat.c.area,
        game_online_stat.c.server_id,
        game_online_stat.c.cj_date,
        game_online_stat.c.count
        ]).where(w_sql)
    r = conn.execute(s)

    ins_dic = {}
    while True:
        res = r.fetchone()
        if not res:
            break
        game      = res[0]
        area      = res[1]
        server_id = res[2]
        ts        = res[3]
        count     = res[4]

        if ins_dic.get(game):
            if ins_dic.get(game).get(area):
                if ins_dic.get(game).get(area).get(server_id):
                    append_data = {'num': count,'dt': ts}
                    ins_dic.get(game).get(area).get(server_id).append(append_data)
                else:
                    ins_dic.get(game).get(area)[server_id] = []
                    append_data = {'num': count,'dt': ts}
                    ins_dic.get(game).get(area).get(server_id).append(append_data)
            else:
                ins_dic.get(game)[area] = {}
                ins_dic.get(game).get(area)[server_id] = []
                append_data = {'num': count,'dt': ts}
                ins_dic.get(game).get(area).get(server_id).append(append_data)
        else:
            ins_dic[game] = {}
            ins_dic.get(game)[area] = {}
            ins_dic.get(game).get(area)[server_id] = []
            append_data = {'num': count,'dt': ts}
            ins_dic.get(game).get(area).get(server_id).append(append_data)

    for item in ins_dic:
        game_code = item
        for area in ins_dic.get(item):
            game_area = area
            for server_id in ins_dic.get(item).get(area):
                game_server_id = server_id
                online_all_data = {}
                for online_data in ins_dic.get(item).get(area).get(server_id):
                    online_all_data[online_data.get('dt')] = online_data

                ins_sql = game_online_stat_day.insert().values(
                        game = game_code,
                        area = game_area,
                        server_id = game_server_id,
                        data = json.dumps(online_all_data),
                        date = start_ts
                )

                ins_sql.compile()
                conn.execute(ins_sql)
    conn.close()
if __name__ == '__main__':
    main()
