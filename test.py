from dbs.pipelines import MongoPipeline

for num, info in enumerate(MongoPipeline('products').find({'domain': 'www.xinbeijx.com'})):
    MongoPipeline('products').update_item({'_id': None},
                                          {
                                              '_id': info['_id'],
                                              'pro_desc': '',
                                              'pro_images_back': '',
                                              'pro_images_front': '',
                                              'pro_video_back': '',
                                              'pro_video_front': '',
                                              'pro_jscs_html': '',
                                              'pro_yyly': '',
                                              'series': ''
                                          })