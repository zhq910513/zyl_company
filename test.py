from dbs.pipelines import MongoPipeline

# replace_text = """<script>window.onload=function(){  changeTableHeight();  }  window.onresize=function(){ changeTableHeight();  }  function changeTableHeight(){ $('.proshowParameter table th').each(function (i,o){    var $this=$(o),     height=$this.next().height();    $(this).css('height',height);var obj = $(o);var val = obj.text();if(val == '' || val == null || val == undefined){$(this).addClass('none');}else{$(this).removeClass('none');}});$('.proshowParameter table td').each(function (i,o){var obj = $(o);var val = obj.text();if(val == '' || val == null || val == undefined){$(this).addClass('none');}else{$(this).removeClass('none');}});}</script>"""

for num, info in enumerate(MongoPipeline('products').find({'domain': 'www.syntop-ien.com'})):
    # _html = info['pro_jscs_html']
    # _html = _html.replace(replace_text, '')
    MongoPipeline('products').update_item({'_id': None}, {
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