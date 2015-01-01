#!/usr/bin/python

import sqlite3
import os
from time import sleep

os.chdir('/home/mribeirodantas/.gkeeptrack/data/')
conn = sqlite3.connect('gkt.db')
conn.text_factory = str
c = conn.cursor()
#sql = c.execute("SELECT A.timestamp AS starttime, B.timestamp AS stoptime FROM actions A, actions B WHERE A.app_id_fk='1' AND B.app_id_fk='1' AND A.action='Focus' AND B.action='Unfocus' AND A.timestamp<B.timestamp AND B.timestamp=(SELECT MIN(timestamp) FROM actions Q WHERE Q.action='Unfocus' AND Q.timestamp>A.timestamp)")
#tempo = 0
#for caso in sql:
#   tempo += caso[1] - caso[0]
#print tempo

total_time = 0
while True:
    sleep(5)
    app_name = c.execute("SELECT app_name FROM applications WHERE app_id='1'")
    app_name = app_name.fetchone()[0]
    total_time = c.execute("SELECT SUM(B.timestamp - A.timestamp) FROM actions A, actions B WHERE A.app_id_fk='1' AND B.app_id_fk='1' AND A.action='Focus' AND B.action='Unfocus' AND A.timestamp<B.timestamp AND B.timestamp=(SELECT MIN(timestamp) FROM actions Q WHERE Q.action='Unfocus' AND Q.timestamp>A.timestamp)")
    total_time = total_time.fetchone()[0]
    print(app_name + ' for ' + str(total_time) + ' seconds.')

