from dbs.pipelines import MongoPipeline

replace_text = """<i>/ Product parameter</i>"""
for num, info in enumerate(MongoPipeline('products').find({"domain" : "www.tongjia.com"})):
    # _html = info['pro_jscs_html']
    # _html = _html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")
    # if "style='background-image" in info['pro_jscs_html']:
    MongoPipeline('products').update_item({'_id': None}, {
                                                  '_id': info['_id'],
                                                  # 'pro_desc': '',
                                                  'pro_images_back': '',
                                                  'pro_images_front': '',
                                                  'pro_video_back': '',
                                                  'pro_video_front': '',
                                                  'pro_jscs_html': '',
                                                  'pro_yyly': '',
                                                  'series': ''
                                              })
