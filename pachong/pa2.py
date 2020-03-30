import requests
from pymongo import MongoClient
import time
client=MongoClient()
db=client.lagou
my_set=db.jobs

url='https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'

headers={
    'cookie':'JSESSIONID=ABAAABAABEEAAJAD8BCDA5DBD50D6E19B668EB516BF7AD0; WEBTJ-ID=20191003133851-16d9020cafa182-00ff6112261a9b-5373e62-1049088-16d9020caffc2; _ga=GA1.2.1073498606.1570081132; user_trace_token=20191003133850-143d0302-e5a0-11e9-a53a-5254005c3644; LGUID=20191003133850-143d089c-e5a0-11e9-a53a-5254005c3644; _gid=GA1.2.2053712974.1570081132; index_location_city=%E5%85%A8%E5%9B%BD; sajssdk_2015_cross_new_user=1; X_MIDDLE_TOKEN=306d9042831f5ac20455257092c5edc0; PRE_UTM=; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216d9020f7ce14-0a39f6889bbdcb-5373e62-1049088-16d9020f7cf6f7%22%2C%22%24device_id%22%3A%2216d9020f7ce14-0a39f6889bbdcb-5373e62-1049088-16d9020f7cf6f7%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _gat=1; LGSID=20191003150348-f287a3eb-e5ab-11e9-a53a-5254005c3644; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DO-d0TcV_zLHFcDm9LyDx6laoxNnFzr7Rxc5FDgqrxVS%26wd%3D%26eqid%3D8f4ddbe200010a94000000055d958bbb%26ck%3D4684.1.65.242.150.241.141.166%26shh%3Dwww.baidu.com; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; ab_test_random_num=0; sm_auth_id=ue6j3dzoqaluzuup; TG-TRACK-CODE=index_search; gate_login_token=a48792524a9322317b118291241ac662b9b01e228969d91cddff5e4b9a71c52b; LG_HAS_LOGIN=1; _putrc=91D2E78D2F77D7FF123F89F2B170EADC; login=true; unick=%E6%8B%89%E5%8B%BE%E7%94%A8%E6%88%B71539; hasDeliver=0; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1570081727,1570086229,1570086346,1570086406; privacyPolicyPopup=false; X_HTTP_TOKEN=fddccf5dfa4ef4262146800751d275703228336a2a; LGRID=20191003150652-609b8915-e5ac-11e9-97c5-525400f775ce; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1570086414; SEARCH_ID=2f98a55f4cb54598a5b6417c0d099a52',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'Referer': 'https://www.lagou.com/jobs/list_%E7%88%AC%E8%99%AB?labelWords=&fromSearch=true&suginput='
}
def get_job_info(page):
    for i in range(page):
        payload = {
            'first': 'false',
            'pn': i+12,
            'kd': '爬虫',
            'sid': '93b9b8709a7b498095b096940fc70fd5'
        }
        headers = {
            'cookie':'JSESSIONID=ABAAABAABEEAAJAD8BCDA5DBD50D6E19B668EB516BF7AD0; WEBTJ-ID=20191003133851-16d9020cafa182-00ff6112261a9b-5373e62-1049088-16d9020caffc2; _ga=GA1.2.1073498606.1570081132; user_trace_token=20191003133850-143d0302-e5a0-11e9-a53a-5254005c3644; LGUID=20191003133850-143d089c-e5a0-11e9-a53a-5254005c3644; _gid=GA1.2.2053712974.1570081132; index_location_city=%E5%85%A8%E5%9B%BD; sajssdk_2015_cross_new_user=1; X_MIDDLE_TOKEN=306d9042831f5ac20455257092c5edc0; PRE_UTM=; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216d9020f7ce14-0a39f6889bbdcb-5373e62-1049088-16d9020f7cf6f7%22%2C%22%24device_id%22%3A%2216d9020f7ce14-0a39f6889bbdcb-5373e62-1049088-16d9020f7cf6f7%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; LGSID=20191003150348-f287a3eb-e5ab-11e9-a53a-5254005c3644; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DO-d0TcV_zLHFcDm9LyDx6laoxNnFzr7Rxc5FDgqrxVS%26wd%3D%26eqid%3D8f4ddbe200010a94000000055d958bbb%26ck%3D4684.1.65.242.150.241.141.166%26shh%3Dwww.baidu.com; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; ab_test_random_num=0; TG-TRACK-CODE=index_search; gate_login_token=a48792524a9322317b118291241ac662b9b01e228969d91cddff5e4b9a71c52b; LG_HAS_LOGIN=1; _putrc=91D2E78D2F77D7FF123F89F2B170EADC; login=true; unick=%E6%8B%89%E5%8B%BE%E7%94%A8%E6%88%B71539; hasDeliver=0; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1570081727,1570086229,1570086346,1570086406; privacyPolicyPopup=false; _gat=1; SEARCH_ID=bba5596fc9cd455d8a28524f687e9549; X_HTTP_TOKEN=fddccf5dfa4ef4269717800751d275703228336a2a; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1570087181; LGRID=20191003151939-29ce9b1e-e5ae-11e9-97c5-525400f775ce',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Referer': 'https://www.lagou.com/jobs/list_%E7%88%AC%E8%99%AB?labelWords=&fromSearch=true&suginput='
        }
        response=requests.post(url,data=payload,headers=headers)
        if response.status_code==200:
            # print(response.json())
            my_set.insert_many(response.json()['content']['positionResult']['result'])
        else:
            print('something wrong')
        print('正在爬取'+str(i+12)+'页')
        time.sleep(1)
if __name__=='__main__':
    get_job_info(5)
    # get_job_info(1)