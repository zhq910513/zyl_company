#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: product_list.py
@time: 2022/4/21 14:17
"""
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import copy
from common.log_out import log_err, log
from dbs.pipelines import MongoPipeline


# 请求列表
def next_product_list(company_info):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        resp = requests.get(company_info['company_url'], headers=headers, verify=False)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            parse_list(company_info, resp.text)
        else:
            print(resp.status_code)
    except Exception as error:
        log_err(error)


# 解析列表
def parse_list(company_info, html):
    soup = BeautifulSoup(html, 'lxml')
    domain = urlparse(company_info['company_url']).netloc
    print(domain)

    try:
        if domain == "www.oubeitejx.com":
            cate_1_name = soup.find('div', {'class': 'weizhi'}).find('h2').get_text()
            for pro in soup.find('div', {'class': 'pro'}).find_all('div', {'class': 'proimg'}):
                pro_name = pro.find_all('a')[0].get('title')
                pro_link = 'http://www.oubeitejx.com' + pro.find_all('a')[0].get('href')
                pro_data = {
                    'company_name': company_info['company_name'],
                    'company_url': 'http://www.oubeitejx.com/cp/',
                    'domain': domain,
                    'cate_1_name': cate_1_name,
                    'cate_2_name': None,
                    'cate_3_name': None,
                    'categories': f'{cate_1_name}',
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
        if domain == "www.njkwls.com":
            for li in soup.find('ul', {'class': 'info_pro_list'}).find_all('li'):
                try:
                    cate_1_name = li.find('p').find('b').get_text()
                    pro_name = cate_1_name
                    pro_link = 'http://www.njkwls.com/' + li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    # print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except:
                    pass
        if domain == "www.lk.world":
            for cate_li in soup.find_all('div', {'class': 'container'})[1].find_all('li'):
                if '解决方案' in str(cate_li):
                    for pro in cate_li.find_all('div', {'class': 'sub_menu_item'}):
                        cate_1_name = pro.find('a').get_text().strip()

                        try:
                            for item in pro.find('ul', {'class': 'dropdown_lv2'}).find_all('a'):
                                pro_name = item.get_text().replace('\n', '').replace('\t', '').replace('\r',
                                                                                                       '').strip()
                                pro_link = 'https://www.lk.world/sc/' + item.get('href')
                                pro_data = {
                                    'company_name': company_info['company_name'],
                                    'company_url': company_info['company_url'],
                                    'domain': domain,
                                    'cate_1_name': cate_1_name,
                                    'cate_2_name': None,
                                    'cate_3_name': None,
                                    'categories': f'{cate_1_name}',
                                    'pro_name': pro_name,
                                    'pro_link': pro_link
                                }
                                print(pro_data)
                                MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                        except:
                            continue
        if domain == "www.jmjj.com":
            for li in soup.find_all('li', {'class': 'nav-item'}):
                try:
                    if li.find('a', {'id': 'product-list'}):
                        for num, cate_li in enumerate(
                                li.find('div', {'id': 'product-dropdown'}).find('ul', {'id': 'pills-tab'}).find_all(
                                    'li')):
                            cate_1_name = cate_li.find('a').get_text().replace('\n', '').replace('\t', '').replace('\r',
                                                                                                                   '').strip()
                            cate_2_info = li.find('div', {'id': 'product-dropdown'}).find('div', {
                                'id': f'product-{num}-content'})

                            for item in cate_2_info.find_all('div', {'class': 'item'}):
                                cate_2_name = item.find('a', {'class': 'product_sub'}).get('title').replace('\n',
                                                                                                            '').replace(
                                    '\t', '').replace('\r', '').strip()

                                for cate_3_info in item.find_all('li', {'class': 'mb-20'}):
                                    cate_3_name = cate_3_info.find('h4').get_text().replace('\n', '').replace('\t',
                                                                                                              '').replace(
                                        '\r', '').strip()

                                    for pro_info in cate_3_info.find_all('a'):
                                        pro_name = pro_info.get_text().replace('\n', '').replace('\t', '').replace('\r',
                                                                                                                   '').strip()
                                        pro_link = pro_info.get('href')
                                        if not str(pro_link).startswith('https:'):
                                            pro_link = 'https:' + pro_link

                                        if cate_3_name in cate_2_name:
                                            pro_data = {
                                                'company_name': company_info['company_name'],
                                                'company_url': company_info['company_url'],
                                                'domain': domain,
                                                'cate_1_name': cate_1_name,
                                                'cate_2_name': cate_2_name,
                                                'cate_3_name': None,
                                                'categories': f'{cate_1_name}-{cate_2_name}',
                                                'pro_name': pro_name,
                                                'pro_link': pro_link
                                            }
                                        else:
                                            pro_data = {
                                                'company_name': company_info['company_name'],
                                                'company_url': company_info['company_url'],
                                                'domain': domain,
                                                'cate_1_name': cate_1_name,
                                                'cate_2_name': cate_2_name,
                                                'cate_3_name': cate_3_name,
                                                'categories': f'{cate_1_name}-{cate_2_name}-{cate_3_name}',
                                                'pro_name': pro_name,
                                                'pro_link': pro_link
                                            }
                                        MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None},
                                                                              pro_data)
                except Exception as error:
                    log(error)
        if domain == "faygoplast.cn":
            for li in soup.find('div', {'class': 'fusion-portfolio-1'}).find_all('article'):
                try:
                    cate_1_name = li.get('class')[1]
                    pro_name = li.find('a', {'class': 'fusion-link-wrapper'}).get('aria-label')
                    pro_link = li.find('a', {'class': 'fusion-link-wrapper'}).get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.gdhuaxing.com":
            for a in soup.find_all('a', {'class': 'nycqlbrbox_cta'}):
                try:
                    cate_1_name = a.find('div', {'class': 'nycqlbrbox_ctatxtct'}).get_text()
                    pro_name = cate_1_name
                    pro_link = a.get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except:
                    pass
        if domain == "www.xinbeijx.com":
            cate_1_name = company_info['cate_1_name']
            cate_2_name = company_info['cate_2_name']
            for pro in soup.find('div', {'class': 'pro_main'}).find_all('dl'):
                try:
                    pro_name = pro.find('dt').find('a').get('title').replace('\n', '').replace('\t', '').replace('\r',
                                                                                                                 '').strip()
                    pro_link = pro.find('dt').find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': cate_2_name,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}-{cate_2_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except:
                    continue

            try:
                for a in soup.find('div', {'class': 'pagess'}).find_all('a'):
                    try:
                        if '下一页' in a.get_text():
                            next_page = {
                                'company_name': '张家港市新贝机械有限公司',
                                'cate_1_name': company_info['cate_1_name'],
                                'cate_2_name': company_info.get('cate_2_name'),
                                'company_url': company_info['company_url'] + a.get('href')
                            }
                            return next_product_list(next_page)
                    except:
                        pass
            except:
                pass
        if domain == "www.asiastarpm.com":
            cate_1_name = soup.find('div', {'class': 'cont_body'}).find('div', {'class': 'title'}).get_text()
            for pro in soup.find('ul', {'id': 'product'}).find_all('li'):
                pro_name = pro.find_all('a')[0].get('title')
                pro_link = pro.find_all('a')[0].get('href')
                pro_data = {
                    'company_name': company_info['company_name'],
                    'company_url': 'http://www.asiastarpm.com/html/product/',
                    'domain': domain,
                    'cate_1_name': cate_1_name,
                    'cate_2_name': None,
                    'cate_3_name': None,
                    'categories': f'{cate_1_name}',
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
        if domain == "www.syntop-ien.com":
            cate_1_name = soup.find('div', {'class': 'ny_pos'}).find_all('a')[2].get_text()
            cate_2_name = soup.find('div', {'class': 'ny_pos'}).find_all('a')[3].get_text()
            for pro in soup.find('div', {'class': 'pro_list2'}).find_all('li'):
                pro_name = pro.find('div', {'class': 'pro_img'}).find('img').get('alt')
                pro_link = 'http://www.syntop-ien.com' + pro.find('div', {'class': 'pro_img'}).find('a').get('href')
                pro_data = {
                    'company_name': company_info['company_name'],
                    'company_url': 'http://www.syntop-ien.com/products.html',
                    'domain': domain,
                    'cate_1_name': cate_1_name,
                    'cate_2_name': cate_2_name,
                    'cate_3_name': None,
                    'categories': f'{cate_1_name}-{cate_2_name}',
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
            try:
                for a in soup.find('div', {'class': 'ly_page'}).find_all('a'):
                    try:
                        if '下一页' in a.get_text():
                            next_page = {
                                'company_name': '南京新拓智能装备有限公司',
                                'company_url': 'http://www.syntop-ien.com' + a.get('href')
                            }
                            return next_product_list(next_page)
                    except:
                        pass
            except:
                pass
        if domain == "www.gelanjx.com":
            cate_1_name = soup.find('h3', {'class': 'leftnav-z1-tit'}).get_text().strip()
            for pro in soup.find('div', {'class': 'leftnav-z1-list'}).find_all('dl'):
                pro_name = pro.find_all('a')[0].get('title')
                pro_link = 'https://www.gelanjx.com/' + pro.find_all('a')[0].get('href')
                pro_data = {
                    'company_name': company_info['company_name'],
                    'company_url': 'https://www.gelanjx.com/product.html',
                    'domain': domain,
                    'cate_1_name': cate_1_name,
                    'cate_2_name': None,
                    'cate_3_name': None,
                    'categories': f'{cate_1_name}',
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
        if domain == "www.tieljx.com":
            cate_1_name = company_info['cate_1_name']
            for td in soup.find('div', {'class': 'neiyer'}).find_all('td'):
                try:
                    pro_name = td.find_all('a')[-1].get_text()
                    if not pro_name:continue
                    pro_link = 'http://www.tieljx.com/product.asp' + td.find_all('a')[-1].get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except:
                    pass
        if domain == "www.jwell.cn":
            cate_1_name = company_info['cate_1_name']
            for pro in soup.find_all('div', {'class': 'infobox'}):
                pro_name = pro.find('h2').get_text()
                pro_link = company_info['company_url']
                pro_data = {
                    'company_name': company_info['company_name'],
                    'company_url': 'https://www.jwell.cn/products.html',
                    'domain': domain,
                    'cate_1_name': cate_1_name,
                    'cate_2_name': None,
                    'cate_3_name': None,
                    'categories': f'{cate_1_name}',
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
        if domain == "www.useon.cn":
            for _class in [
                'menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children menu-item-13790 astra-megamenu-li full-width-mega',
                'menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children menu-item-13779 astra-megamenu-li full-width-mega',
                'menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children menu-item-15188 astra-megamenu-li full-width-mega'
            ]:
                info = soup.find('li', {'class': _class})
                cate_1_name = info.find('span', {'class': 'menu-text'}).get_text().strip()
                for li in info.find('ul', {'class': 'astra-megamenu sub-menu astra-mega-menu-width-full ast-hidden'}).find_next('li').find_all('li'):
                    try:
                        pro_name = li.find('a').get_text().replace('\n', '').strip()
                        pro_link = li.find('a').get('href')
                        pro_data = {
                            'company_name': company_info['company_name'],
                            'company_url': company_info['company_url'],
                            'domain': domain,
                            'cate_1_name': cate_1_name,
                            'cate_2_name': None,
                            'cate_3_name': None,
                            'categories': f'{cate_1_name}',
                            'pro_name': pro_name,
                            'pro_link': pro_link
                        }
                        print(pro_data)
                        MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                    except Exception as error:
                        log(error)
        if domain == "www.huabaosuliaojixie.com":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find('section', {'id': 'plist'}).find_all('li'):
                try:
                    pro_name = li.find('h3').get_text()
                    pro_link = 'http://www.huabaosuliaojixie.com' + li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.kymach.com":
            cate_1_name = company_info['cate_1_name']
            pro_name = company_info['cate_1_name']
            pro_link = company_info['company_url']
            pro_data = {
                'company_name': company_info['company_name'],
                'company_url': 'http://www.kymach.com/product/1006/',
                'domain': domain,
                'cate_1_name': cate_1_name,
                'cate_2_name': None,
                'cate_3_name': None,
                'categories': f'{cate_1_name}',
                'pro_name': pro_name,
                'pro_link': pro_link
            }
            print(pro_data)
            MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
        if domain == "www.topstarltd.com":
            for pro in soup.find_all('div', {'class': 'product_list'}):
                cate_3_name = pro.find('div', {'class': 'product_list_name fl'}).get_text().strip()

                for li in pro.find_all('li'):
                    pro_name = li.find('div', {'class': 'product_list_productname'}).get_text().strip()
                    pro_link = 'http://www.topstarltd.com' + li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': 'http://www.topstarltd.com/products',
                        'domain': domain,
                        'cate_1_name': company_info['cate_1_name'],
                        'cate_2_name': company_info['cate_2_name'],
                        'cate_3_name': cate_3_name,
                        'categories': f'{company_info["cate_1_name"]}-{company_info["cate_2_name"]}-{cate_3_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)

                try:
                    more = pro.find('div', {'class': 'product_list_more fr'})
                    if more:
                        more_data = copy.deepcopy(company_info)
                        more_data['company_url'] = 'http://www.topstarltd.com' + more.find('a').get('href')
                        # print(more_data)
                        next_product_list(more_data)
                except:
                    pass
        if domain == "www.donghua-ml.com":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find('div', {'class': 'news_box'}).find_all('li'):
                try:
                    pro_name = li.find('div', {'class': 'article_title'}).find('a').get('title')
                    pro_link = 'http://www.donghua-ml.com' + li.find('div', {'class': 'article_title'}).find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.logge.com.cn":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find('div', {'class': 'right-p-k'}).find_all('div', {'class': 'right-product-single'}):
                try:
                    pro_name = li.find('a', {'class': 'rpname'}).get_text()
                    pro_link = 'https://www.logge.com.cn' + li.find('a', {'class': 'rpname'}).get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.yonghuazhusuji.com":
            for num, pro in enumerate(soup.find('div', {'class': 'series'}).find_all('a')):
                cate_1_name = pro.get_text().strip()

                try:
                    for item in soup.find_all('div', {'class': 'pcon'})[num].find_all('a', {'class': 'item'}):
                        pro_name = item.get_text().replace('\n', '').replace('\t', '').replace('\r',
                                                                                               '').strip()
                        pro_link = 'http://www.yonghuazhusuji.com' + item.get('href')
                        pro_data = {
                            'company_name': company_info['company_name'],
                            'company_url': company_info['company_url'],
                            'domain': domain,
                            'cate_1_name': cate_1_name,
                            'cate_2_name': None,
                            'cate_3_name': None,
                            'categories': f'{cate_1_name}',
                            'pro_name': pro_name,
                            'pro_link': pro_link
                        }
                        print(pro_data)
                        MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except:
                    continue
        if domain == "www.tongdamachine.com":
            for num, cate in enumerate(soup.find('div', {'id': 'formTabButtonList5122'}).find_all('span')):
                cate_1_name = cate.get_text().strip()
                print(cate_1_name)

                try:
                    info = soup.find('div', {'id': 'formTabContent5122'}).find('div',
                                                                               {'id': f'tabPackContent5122-{num}'})
                    for item in info.find_all('div', {"topclassname": "productListTopIcon"}):
                        pro_name = item.find('a', {'class': 'fk-productName'}).get('title').replace('\n', '').replace(
                            '\t', '').replace('\r',
                                              '').strip()
                        pro_link = item.find('a', {'class': 'fk-productName'}).get('href')
                        pro_data = {
                            'company_name': company_info['company_name'],
                            'company_url': company_info['company_url'],
                            'domain': domain,
                            'cate_1_name': cate_1_name,
                            'cate_2_name': None,
                            'cate_3_name': None,
                            'categories': f'{cate_1_name}',
                            'pro_name': pro_name,
                            'pro_link': pro_link
                        }
                        print(pro_data)
                        MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except:
                    continue
        if domain == "www.victorpm.com":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find_all('figure', {'class': 'wp-caption'}):
                try:
                    pro_name = li.find('figcaption').get_text()
                    if pro_name == 'English':continue
                    pro_link = 'https://www.victorpm.com' + li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.yizumi.com":
            for num, li in enumerate(soup.find('div', {'class': 'caste_2-top'}).find_all('li'),start=1):
                cate_1_name = li.find('a').get_text().strip()
                info = soup.find('div', {'class': 'caste_2-main'}).find_all('ul')[num]
                if info:
                    for info_li in info.find_all('li'):
                        try:
                            pro_name = info_li.find('p').get_text()
                            pro_link = 'https://www.yizumi.com' + info_li.find('a').get('href')
                            pro_data = {
                                'company_name': company_info['company_name'],
                                'company_url': company_info['company_url'],
                                'domain': domain,
                                'cate_1_name': cate_1_name,
                                'cate_2_name': None,
                                'cate_3_name': None,
                                'categories': f'{cate_1_name}',
                                'pro_name': pro_name,
                                'pro_link': pro_link
                            }
                            print(pro_data)
                            MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                        except Exception as error:
                            log(error)
        if domain == "www.beierpm.com":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find('div', {'class': 'proList'}).find_all('li'):
                try:
                    pro_name = li.find('div', {'class': 'name'}).get_text().replace('\n', '').replace('\t', '').strip()
                    pro_link = li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.dekuma.com":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find('ul', {'class': 'products columns-4'}).find_all('li'):
                try:
                    pro_name = li.find('h3').get_text().replace('\n', '').replace('\t', '').strip()
                    pro_link = li.find_all('a')[0].get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.tongjia.com":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find('div', {'class': 'p_list'}).find_all('div', {'class': 'cbox-10-1 p_item'}):
                try:
                    pro_name = li.find('p', {'class': 'e_text-12 s_title'}).get_text().replace('\n', '').replace('\t', '').strip()
                    pro_link = 'https://www.tongjia.com' + li.find_all('a')[0].get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.yankanggroup.com":
            cate_1_name = company_info['cate_1_name']
            cate_2_name = company_info['cate_2_name']
            for li in soup.find('div', {'id': 'post-items'}).find_all('div', {'class': 'project'}):
                try:
                    pro_name = li.find('h2').find('a').get_text().replace('\n', '').replace('\t', '').strip()
                    pro_link = 'http://www.yankanggroup.com' + li.find('h2').find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': cate_2_name,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}-{cate_2_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.qinchuan.com":
            cate_1_name = company_info['cate_1_name']
            cate_2_name = company_info['cate_2_name']
            cate_3_name = company_info['cate_3_name']
            for li in soup.find('ul', {'class': 'piclist'}).find_all('li'):
                try:
                    pro_name = li.find('p').get_text().replace('\n', '').replace('\t', '').strip()
                    pro_link = li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': cate_2_name,
                        'cate_3_name': cate_3_name,
                        'categories': f'{cate_1_name}-{cate_2_name}-{cate_3_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.shini.com.cn":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find('ul', {'id': 'prod_list'}).find_all('li'):
                try:
                    pro_name = li.find('a').get('title').replace('\n', '').replace('\t', '').strip()
                    pro_link = 'https://www.shini.com.cn/cn/' + li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.kraussmaffei.ltd":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find('div', {'class': 'pro_list_lilst__con'}).find_all('li'):
                try:
                    pro_name = li.find('p').get_text().replace('\n', '').replace('\t', '').strip()
                    pro_link = 'http://www.kraussmaffei.ltd' + li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.arburg.com":
            for li in soup.find_all('div', {'class': 'dottedDivider'}):
                try:
                    cate_1_name = li.find('h4').get_text()
                    pro_name = cate_1_name
                    pro_link = 'https://www.arburg.com' + li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.akei.com.cn":
            cate_1_name = company_info['cate_1_name']
            cate_2_name = company_info['cate_2_name']
            for li in soup.find('div', {'class': 'product_list product_list2'}).find_all('div', {'class': 'col-sm-4 col-md-4 col-mm-6 product_img'}):
                try:
                    pro_name = li.find_all('a')[-1].get('title')
                    pro_link = 'https://www.akei.com.cn' + li.find_all('a')[-1].get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': cate_2_name,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}-{cate_2_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.china-leshan.com":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find('div', {'class': 'row productlist'}).find_all('div', {'class': 'col-md-4 col-sm-12'}):
                try:
                    pro_name = li.find('a').get('title')
                    pro_link = li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.fcs.com.tw":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find_all('div', {'class': 'col-sm-6 m-bottom6'}):
                try:
                    pro_name = li.find('a').get('title')
                    pro_link = 'https://www.fcs.com.tw/cn/' + li.find('a').get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
        if domain == "www.kshrjx.com":
            cate_1_name = company_info['cate_1_name']
            for li in soup.find_all('div', {'class': 'pro_one_box'}):
                try:
                    pro_name = li.find_all('a')[0].get('title')
                    pro_link = 'http://www.kshrjx.com/' + li.find_all('a')[0].get('href')
                    pro_data = {
                        'company_name': company_info['company_name'],
                        'company_url': company_info['company_url'],
                        'domain': domain,
                        'cate_1_name': cate_1_name,
                        'cate_2_name': None,
                        'cate_3_name': None,
                        'categories': f'{cate_1_name}',
                        'pro_name': pro_name,
                        'pro_link': pro_link
                    }
                    print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, pro_data)
                except Exception as error:
                    log(error)
    except Exception as error:
        log_err(error)
