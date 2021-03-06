import httplib2
import couchquery
try:
    import json
except:
    import simplejson as json
from threading import Thread
from wsgiref.simple_server import make_server
from time import sleep
from brasstacks import Stub

http = httplib2.Http()

# crashtestapi = 'http://10.2.76.100:8080/crashtest/api'
crashtestapi = 'http://localhost:8888/crashtest/api'

# crashtestcouch = 'http://10.2.76.100:5984/crashtest'
crashtestcouch = 'http://localhost:5984/crashtest'

def setup_module(module):
#     from brasstacks import crashtest
    crashdb = couchquery.Database(crashtestcouch + '/crashtest')
    resultdb = couchquery.Database(crashtestcouch + '/crashtest_results')
#     crashdb.sync_design_doc("crashes", crashtest.crashes_design_doc)
#     resultdb.sync_design_doc("jobs", crashtest.jobs_design_doc)
#     resultdb.sync_design_doc("results", crashtest.results_design_doc)
#     a = Stub()
#     a.add_resource('crashtest', crashtest.CrashTestApplication(crashdb, resultdb))
#     httpd = make_server('', 8888, a)
#     thread = Thread(target=httpd.serve_forever)
#     thread.start()
#     
#     # Global these boys
#     module.thread = thread
#     module.httpd = httpd
    module.crashdb = crashdb
    module.resultdb = resultdb
#     sleep(1)

jobstore = []

def test_getJob():
    body = json.dumps({"os":"Linux", "machine_name":"testmachine"})
    resp, content = http.request(crashtestapi + '/getJob', method="POST", body=body)
    assert resp.status == 200
    job = json.loads(content)
    assert job
    assert 'urls' in job
    print len(job['urls'])
    assert len(job['urls']) == 4000
    jobstore.append(job)
    
def test_result():
    job = jobstore[0]
    job['results'] = [{"url":url, "reproduced":True} for url in job['urls']]
    job['status'] = 'done'
    body = json.dumps(job)
    resp, content = http.request(crashtestapi + '/result', method="POST", body=body)
    assert resp.status == 200
    
    info = json.loads(content)
    assert info['id'] and info['rev']
    jobstore[0] = resultdb.get(info['id'])

def teardown_module(module):
    job = jobstore[0]
    resultdb.delete(job)
#     while thread.isAlive():
#         httpd.shutdown()
