#!/bin/env python
# coding: utf-8
import json
from flask import Flask, render_template
from sqlalchemy import select
from line_util import online
from get_zabbix_tri import ZabbixTools

app = Flask(__name__)

class GetTriggers(online):
      def main(self):
        conn = self.engine.connect()
        s = select([self.games_triggers])
        r = conn.execute(s)
        tris_dict = {'online': []}
        for res in r.fetchall():
            tri_text = '%s-%s-S%s 在线人数报警' % (res[1], res[3], res[4])
            tris_dict.get('online').append(tri_text)

        zbx = ZabbixTools()
        zbx_tris = zbx.trigger_get()
        tris_dict['zabbix'] = zbx_tris

        res = json.dumps(tris_dict)
        conn.close()
        return res


@app.route('/')
def index():
    return render_template('mon_show.html')


@app.route('/api')
def alert():
    oGetTri = GetTriggers()
    res = oGetTri.main()
    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
