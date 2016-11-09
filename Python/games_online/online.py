#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '16/8/8'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
             ┏┓   ┏┓
            ┏┛┻━━━┛┻┓
            ┃    ☃   ┃
            ┃ ┳┛  ┗┳┃
            ┃    ┻  ┃
            ┗━┓   ┏━┛
              ┃   ┗━━━┓
              ┃ 神兽保佑 ┣┓
              ┃ 永无BUG ! ┏┛
              ┗┓┓┏━┳┓┏┛
               ┃┫┫ ┃┫┫
               ┗┻┛ ┗┻┛
"""
import json
import sys
import time
import urllib2
from threading import Thread, Timer
from sqlalchemy import create_engine, Table, Column, MetaData, select, INTEGER, VARCHAR, and_
import SendMail as sm

reload(sys)
sys.setdefaultencoding('utf-8')

class online(object):
    def __init__(self):
        metadata = MetaData()
        self.engine = create_engine('mysql://root:123456@localhost:3006/games_online', encoding='utf-8',
                                    pool_recycle=7200, pool_size=300, max_overflow=500)
        
        # self._dbSession = scoped_session(
        #    sessionmaker(
        #        bind=self.engine
        #    )
        # )
        self.games_info = Table('games_info', metadata,
                                Column('id', INTEGER, primary_key=True),
                                Column('gamecode', VARCHAR(20)),
                                Column('language', VARCHAR(20)),
                                Column('sid_api', VARCHAR(255)),
                                Column('online_api', VARCHAR(255)))
        self.games_online = Table('games_online', metadata,
                                  Column('id', INTEGER, primary_key=True),
                                  Column('gamecode', VARCHAR(20)),
                                  Column('language', VARCHAR(20)),
                                  Column('region', VARCHAR(20)),
                                  Column('serverid', INTEGER),
                                  Column('online', INTEGER),
                                  Column('time', INTEGER))
        self.games_triggers = Table('games_triggers', metadata,
                                    Column('id', INTEGER, primary_key=True),
                                    Column('gamecode', VARCHAR(20)),
                                    Column('language', VARCHAR(20)),
                                    Column('region', VARCHAR(20)),
                                    Column('serverid', INTEGER),
                                    Column('time', INTEGER))
        metadata.create_all(self.engine)
    
    def update_games_info(self):
        pass
    
    def get_games_info(self):
        dbConn = self.engine.connect()
        s = select([self.games_info.c.gamecode,
                    self.games_info.c.language,
                    self.games_info.c.sid_api,
                    self.games_info.c.online_api])
        r = dbConn.execute(s)
        r_res = r.fetchall()
        dbConn.close()
        return r_res
    
    def update_games_online(self, game_info):
        dbConn = self.engine.connect()
        gamecode = game_info[0]
        language = game_info[1]
        sid_api = game_info[2]
        online_api = game_info[3]
        try:
            sid_api_response = json.loads(urllib2.urlopen(sid_api).read())
        except urllib2.URLError:
            print 'From %s get games server id list error!' % (sid_api)
            return
        for res in sid_api_response.get('all'):
            server_sid = res.get('server_sid')
            server_region = res.get('server_area')
            try:
                server_online = urllib2.urlopen(online_api + server_sid).read()
            except:
                server_online = 0
            if server_online < 1:
                server_online = 0
            now = int(time.time())
            ins = self.games_online.insert().values(gamecode=gamecode,
                                                    language=language,
                                                    region=server_region,
                                                    serverid=server_sid,
                                                    online=server_online,
                                                    time=now)
            ins.compile()
            dbConn.execute(ins)
        dbConn.close()
    
    def check_online(self, game_info):
        print 'oper !'
        try:
            dbConn = self.engine.connect()
        except:
            print 'Connect database error!'
            return
        gamecode = game_info[0]
        language = game_info[1]
        sid_api = game_info[2]
        try:
            sid_api_response = json.loads(urllib2.urlopen(sid_api).read())
        except:
            print 'From %s get server id list error!' % (sid_api)
            return
        
        # 获取现在及15分钟之前的时间戳,并获取前五天中每天的这个时间的时间戳
        end_time = int(time.time())
        start_time = end_time - 900
        before_five_days_time = [(start_time, end_time)]
        for i in range(1, 7):
            before_day_sec = 86400 * i
            before_day_end_time = end_time - before_day_sec
            before_day_start_time = before_day_end_time - 900
            before_five_days_time.append((before_day_start_time, before_day_end_time))
        
        def query_old_online(each_serverid):
            server_sid = each_serverid.get('server_sid')
            server_region = each_serverid.get('server_area')
            # before_online = {'today': 'default', 'before': 0}
            before_online = {'before': []}
            suc_num = 0
            res_list = []
            for before_time in before_five_days_time:
                if suc_num >= 6:
                    break
                start_time = before_time[0]
                end_time = before_time[1]
                where_now_online_sql = and_(
                    self.games_online.c.time.between(start_time, end_time),
                    self.games_online.c.gamecode == gamecode,
                    self.games_online.c.language == language,
                    self.games_online.c.region == server_region,
                    self.games_online.c.serverid == server_sid
                )
                s = select([self.games_online]).where(where_now_online_sql)
                r = dbConn.execute(s)
                
                res = r.fetchall()
                
                if not before_online.get('today'):
                    fifteen_online_list = [item[5] for item in res]
                    
                    if not fifteen_online_list:
                        break
                    fifteen_online_avg = sum(fifteen_online_list) / len(fifteen_online_list)
                    before_online['today'] = fifteen_online_avg
                else:
                    fifteen_online_list = [item[5] for item in res if item[5] > 0]
                    
                    if not fifteen_online_list:
                        break
                    
                    before_fifteen_online_avg = sum(fifteen_online_list) / len(fifteen_online_list)
                    before_online.get('before').append(before_fifteen_online_avg)
                res_list.append(res)
                suc_num += 1
            
            now_online_avg = before_online.get('today')
            before_online_avg_list = before_online.get('before')
            
            if not before_online_avg_list:
                return
            
            history_online_avg = sum(before_online_avg_list) / len(before_online_avg_list)
            alert_per = 0.3
            if history_online_avg < 50:
                alert_per = 0.1
            if history_online_avg < 20:
                alert_per = 0
            alert_value = int(history_online_avg * alert_per)
            
            if now_online_avg < alert_value:
                print res_list
                self.alert(gamecode, language, server_region, server_sid, alert_per, now_online_avg, history_online_avg,
                           alert_value, dbConn)
        
        map(query_old_online, sid_api_response.get('all'))
        self.del_old_tris(dbConn)
        dbConn.close()
    
    def del_old_tris(self, conn):
        
        del_time = int(time.time()) - 900
        d = self.games_triggers.delete().where(self.games_triggers.c.time < del_time)
        conn.execute(d)
    
    def alert(self, gamecode, language, region, server_id, alert_per, now_online, his_online, alert_value, dbconn):
        w = and_(
            self.games_triggers.c.gamecode == gamecode,
            self.games_triggers.c.language == language,
            self.games_triggers.c.region == region,
            self.games_triggers.c.serverid == server_id,
        )
        s = select([self.games_triggers]).where(w)
        r = dbconn.execute(s)
        if r.rowcount == 0:
            ins = self.games_triggers.insert().values(
                gamecode=gamecode,
                language=language,
                region=region,
                serverid=server_id,
                time=int(time.time())
            )
            dbconn.execute(ins)
        else:
            u = self.games_triggers.update().where(w).values(time=int(time.time()))
            dbconn.execute(u)
            return
        
        mail_to = 'qinjiaoxingrong@163.com,oaszabbix@163.com'
        subject = 'Problem: %s-%s-S%s 在线人数报警!' % (gamecode, region, server_id)
        content = '''
            <h6 id="toc_0">在线人数报警</h6>

            <blockquote>
            <p>游戏: <code>%s</code><br/>
            语言: <code>%s</code><br/>
            地区: <code>%s</code><br/>
            游戏服: <code>%s</code><br/>
            下跌百分比: <code>%s</code><br/>
            当前15分钟内平均在线人数: <code>%s</code><br/>
            历史五天同一时间平均在线人数: <code>%s</code><br/>
            报警阈值: <code>%s</code><br/>
            【可通过信息自行判断是否为异常】</p>
            </blockquote>
        ''' % (gamecode, language, region, server_id, alert_per, now_online, his_online, alert_value)
        sm.send_mail(mail_to, subject, content)


def main():
    def uonline():
        ol = online()
        games_info = ol.get_games_info()
        tl = []
        for info in games_info:
            t = Thread(target=ol.update_games_online, args=[info])
            tl.append(t)
        for i in range(len(tl)):
            tl[i].start()
        Tu = Timer(300.0, uonline)
        Tu.start()
    
    Tu = Timer(300.0, uonline)
    Tu.start()
    
    def conline():
        ol = online()
        games_info = ol.get_games_info()
        tl = []
        for info in games_info:
            t = Thread(target=ol.check_online, args=[info])
            tl.append(t)
        for i in range(len(tl)):
            tl[i].start()
        Tc = Timer(300.0, conline)
        Tc.start()
    
    Tc = Timer(300.0, conline)
    Tc.start()


if __name__ == '__main__':
    main()
