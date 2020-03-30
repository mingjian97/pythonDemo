# import requests
# from lxml import etree
# import pandas as pd
# url='https://movie.douban.com/subject/32659890/comments'
# r=requests.get(url).text
# s=etree.HTML(r)
# file=s.xpath('//div[@class="comment"]/p/span/text()')
#
# import pandas as pd
# df=pd.DataFrame(file)
# print(df.head())
# df.to_excel('pinglun.xlsx')
import requests
import pandas as pd
import time
headers={
    # 'cookie':'_zap=22cef418-c031-4f1d-9180-0a931a7a88ee; d_c0="AJAiKVOgARCPTowSaD3MgkGGOkUrjCvXs10=|1567767044"; _xsrf=MDmLhFoBIinrfF7atZZxXFntXZ1zOchK; capsion_ticket="2|1:0|10:1569940164|14:capsion_ticket|44:Mjk3MWFiNTFkZDk1NGUxNWI5YWNkMDdiOWZhYjdlOTM=|ef973540138b36dcef0c228a4eb1d65e298ea307c699ac841d77724cdc55a72c"; z_c0="2|1:0|10:1569940213|4:z_c0|92:Mi4xbWMzbERnQUFBQUFBa0NJcFU2QUJFQ1lBQUFCZ0FsVk45YkNBWGdDVDBDenFPOXduX2JqbVZHS0tMRGhzM3pjYi13|70c92a83d300abde27330838eca81f580ba2fe1246b420d94221778d1c6126ae"; tst=r; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1569938727,1569940156,1570023570; tgw_l7_route=73af20938a97f63d9b695ad561c4c10c; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1570026047',
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}
user_data=[]
def get_user_data(page):
    # for i in range(page):
    url='https://www.toutiao.com/api/pc/feed/?max_behot_time=1570022471&category=__all__&utm_source=toutiao&widen=1&tadrequire=true&as=A1B5BDB904BB422&cp=5D94CB540262CE1&_signature=iz3fThAS1raCcaVbHVOqC4s931'
    response = requests.get(url,headers=headers).json()['data']
    user_data.extend(response)
    # print('正在爬取第%s页'%str(i+1))
    time.sleep(1)

if __name__=='__main__':
    get_user_data(10)
    df = pd.DataFrame.from_dict(user_data)
    df.to_excel('zhihu1.xlsx')
