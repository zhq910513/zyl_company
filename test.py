from dbs.pipelines import MongoPipeline
import pprint
pp=pprint.PrettyPrinter(indent=4)

replace_text = """<i>/ Product parameter</i>"""
for num, info in enumerate(MongoPipeline('products').find({"company_name" : "南京越升挤出机械有限公司"})):
    print(num)
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

    # pro_file_front = info.get('pro_file_front', [])
    # pro_file_back = info.get('pro_file_back', [])
    # new_pro_images_front = []
    # pro_images_front = info.get('pro_images_front')
    # new_pro_images_back = []
    # pro_images_back = info.get('pro_images_back')
    #
    # if not pro_images_front and not pro_images_back:continue
    #
    # for i in pro_images_front:
    #     if isinstance(i, str):
    #         img_url = str(i)
    #         if img_url.endswith('pdf') or img_url.endswith('PDF'):
    #             pro_file_front.append(i)
    #         elif img_url.endswith('zip'):
    #             print(i)
    #         else:
    #             new_pro_images_front.append(i)
    #     elif isinstance(i, list):
    #         img_url = str(i[0])
    #         if img_url.endswith('pdf') or img_url.endswith('PDF'):
    #             pro_file_front.append(i)
    #         elif img_url.endswith('zip'):
    #             print(i)
    #         else:
    #             new_pro_images_front.append(i)
    #     else:
    #         print(i)
    #
    # for j in pro_images_back:
    #     img_url = str(j)
    #     if img_url.endswith('pdf') or img_url.endswith('PDF'):
    #         pro_file_back.append(j)
    #     elif img_url.endswith('zip'):
    #         print(j)
    #     else:
    #         new_pro_images_back.append(j)
    #
    # data = ({
    #     '_id': info['_id'],
    #     'pro_file_front': pro_file_front,
    #     'pro_file_back': pro_file_back,
    #     'pro_images_front': new_pro_images_front,
    #     'pro_images_back': new_pro_images_back
    # })
    # MongoPipeline('products').update_item({'_id': None}, data)
    # # break

