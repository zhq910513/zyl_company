import requests

import json

import time

import xlwt
from scipy.stats._mstats_basic import trim


def CityName2Code(dt,cityName):

    """城市名/省名转换为编码

    Arguments:

        dt {str} -- [description]

        cityName {str} -- [description]

    """

    cityCode=''

    searchKey=''

    codeKey=''

    #城市编码的相对路径

    cityCodePath ='migration/CityCode.json'

    #打开文件，文件编码格式为UTF-8

    data = open((cityCodePath), encoding='utf-8')

    result = json.load(data)

    if dt=='province':

        searchKey='省名称'

        codeKey='省代码'

    elif dt =='city':

        searchKey='地级市名称'

        codeKey='地级市代码'

    for rowNum in range(len(result)):

        if result[rowNum][searchKey]==cityName:

            cityCode = result[rowNum][codeKey]

    return cityCode

def UrlFormat(rankMethod,dt,name,migrationType,date):

    """字符串定义,默认时间为00:00:00,精确到分钟级别

    Arguments:

        rankMethod {str} -- city||province 获得数据的行政级别

        dt {str} -- city||province 中心地行政级别

        name {str} -- example:'温州市||浙江省' 作为中心地的地名

        migrationType {str} -- in||out

        date {str} -- example:20200202

    """

    list_date = list(date)

    list_date.insert(4,'-')

    list_date.insert(7,'-')

    formatDate = ''.join(list_date)

    formatDate= formatDate+" 00:00:00"

    #转换成时间数组

    timeArray = time.strptime(formatDate, "%Y-%m-%d %H:%M:%S")

    #转换成时间戳

    timeUnix = time.mktime(timeArray)

    ID = CityName2Code(dt,name)

    url='http://huiyan.baidu.com/migration/{0}rank.jsonp?dt={1}&id={2}&type=move_{3}&date={4}&callback' \

    '=jsonp_{5}000_0000000'.format(rankMethod,dt,ID,migrationType,date,int(timeUnix))

    return url

#返回数据处理

def JsonTextConvert(text):

    """Text2Json

    Arguments:

        text {str} -- webContent

    Returns:

        str -- jsonText

    """

    text = text.encode('utf-8').decode('unicode_escape')

    head, sep, tail = text.partition('(')

    tail=tail.replace(")","")

    return tail

def GetData(rankMethod,dt,name,migrationType,date,isExcel):

    """

    Arguments:

        rankMethod {str} -- city||province 获得数据的行政级别

        dt {str} -- city||province 中心地行政级别

        name {str} -- example:'温州市||浙江省' 作为中心地的地名

        migrationType {str} -- in||out

        date {str} -- example:20200202

        isExcel {bool} -- true转出为excel格式

    """

    r = requests.get(url=UrlFormat(rankMethod,dt,name,migrationType,date))

    text = r.text

    rawData=json.loads(JsonTextConvert(text))

    data= rawData['data']

    list = data['list']

    nameKey = ''

    if rankMethod=='province':

        nameKey = 'province_name'

    else:

        nameKey = 'city_name'

    if isExcel == True:

        #输出excel格式数据

        workbook = xlwt.Workbook(encoding='utf-8') #创建workbook 对象

        worksheet = workbook.add_sheet('sheet1',cell_overwrite_ok=True) #创建工作表sheet

        table_head = [nameKey,'value']#表头

        index = 1

        for i in range(len(table_head)):

            worksheet.write(0,i,table_head[i])

        for l in list:

            worksheet.write(index,0,l[nameKey])

            worksheet.write(index,1,l['value'])

            index=index+1

        filename = name+date+'.xls'

        workbook.save('migration/'+filename) #保存表

    else:

        #打印数据

        for l in list:

            print(l[nameKey],':',l['value'])

def main():

    #第一个参数填‘city‘或’province’，为获取数据的行政级别，分别为市级或省级

    #第二个参数填‘city‘或’province’，为中心地的行政级别

    #第三个参数填‘中心地名’，例如‘浙江省’或‘杭州市’

    #第四个参数填时间，例如‘20200210’，默认每天的零点

     #第四个参数填True或False,True则输出Excel(文件路径注意)，否则打印出来

    GetData('city','province','浙江省','in','20200210',True)

if __name__ == '__main__':
    main()
