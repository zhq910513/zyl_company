from dbs.pipelines import MongoPipeline

for num, info in enumerate(MongoPipeline('products').find({})):
    print(num)
    html_css = info['pro_jscs_html']

    html_css = html_css.replace('\"', "'")

    MongoPipeline('products').update_item({'pro_link': None, 'pro_name': None}, {'pro_link': info['pro_link'],'pro_name': info['pro_name'],'pro_jscs_html': html_css})
    # break
