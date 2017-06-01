from steem.steem import Steem
from steem.blockchain import Blockchain
from steem.account import Account
from steem.account import Amount
from steem.utils import parse_time
from steem.post import Post
import time
import datetime
import schedule

report_author = 'youraccount'
report_author_key = 'yourpostingkey'

report_tags = ['curation','statistics']
scan_tag = 'deutsch'
time_format = '%d.%m.%Y, %H:%M Uhr' 
date_format = '%d.%m.%Y'
report_title = ('@' + str(report_author) + 's daily report: ') # date added later

account = Account(report_author)

# titles

column_title_thumbnail = ''
column_title_author = 'Author'
column_title_post_title = 'Post'
column_title_payout = '$$$'

def report():

    with open('reportlayout.txt') as layout:
    report_layout = layout.read()

    steem = Steem(node = 'wss://gtg.steem.house:8090')

    main_report = (
                  '|' + 
                  column_title_thumbnail + ' | ' +
                  column_title_author + ' | ' +
                  column_title_post_title + ' | ' + 
                  column_title_payout + ' |\n'+
                  '| --- | --- | --- | --- |\n'
                  )

    total_rewards = 0
    total_posts = 0
    trailing_24h_t = time.time() - datetime.timedelta(minutes=1440).total_seconds() # 24 * 60 = 1440

    stoptime = time.time()
    starttime = trailing_24h_t

    author_list = []

    for i in account.history_reverse(filter_by = "vote", batch_size = 100000):

        timestamp = parse_time(i['timestamp']).timestamp()

        if timestamp > trailing_24h_t:

            if i['voter'] == report_author:


                link = str('@' + i["author"] + "/" +i["permlink"])
                full_link = ('https://steemit.com/tag/' + link)
                post = Post(link)
                reward = (Amount(post.get('total_payout_value')) + Amount(post.get('pending_payout_value')))
                total_posts = total_posts + 1
                tags = (post['json_metadata'].get('tags', []))
                category = post.category
             
                if post.is_main_post() and not i['author'] == report_author:

                    if scan_tag in tags or scan_tag in category:

                        if total_rewards == 0:

                            total_rewards = reward

                        else:

                            total_rewards = total_rewards + reward

                        try:
                            imagelink =  post['json_metadata'].get('image')[0]
                                            
                        except:

                            imagelink = 'https://steem.io/images/steem.png'
            
                        if len(imagelink) > 100: # prevents problems with some image-links

                            imagelink = 'https://steem.io/images/steem.png'

                        image=('![main_image](https://img1.steemit.com/128x256/' + imagelink +')')
            
                        post_title = (post['title'])

                        if len(post_title) > 30: # cut off long titles, so the images scale properly

                            post_title = post_title[:30] + " ..." 

                        if '|' in post_title: # these symbols mess with the markdown layout
         
                            post_title = post_title.replace('|', ';')

                        if '[' in post_title:
         
                            post_title = post_title.replace('[', '')

                        if ']' in post_title:
         
                            post_title = post_title.replace(']', '')

                        main_report = (
                                      main_report + 
                                      image + 
                                      '|@' +
                                      i['author'] + 
                                      '|[' + 
                                      post_title + 
                                      '](' + 
                                      full_link +
                                      ')|' + 
                                      str(reward) + 
                                      '\n'
                                      )

                        if not i['author'] in author_list:

                            author_list.append(i['author'])
 
    date = time.strftime(date_format, time.localtime(stoptime))
    report_starttime = time.strftime(time_format, time.localtime(starttime))
    report_stoptime = time.strftime(time_format, time.localtime(stoptime))
    a = Amount(total_rewards)    
    average_rewards = a * (1/total_posts)

    total_authors = len(author_list)

 
    
    dated_report_title = (report_title + str(date))


    beneficiaries = author_list 

    beneficiaries.append(report_author)

    bene_list = []

    for author in beneficiaries:

        bene_dict = {}
        bene_weight = 10000 // len(beneficiaries)
        bene_rest = 10000 - (bene_weight * len(beneficiaries))

        bene_dict['account'] = author
        bene_dict['weight'] = bene_weight

        if author == report_author:
        
            bene_dict['weight'] = bene_weight + bene_rest

        bene_list.append(bene_dict)

    report = report_layout

    report = report.replace('STARTTIME_GOES_HERE', str(report_starttime))
    report = report.replace('STOPTIME_GOES_HERE', str(report_stoptime))
    report = report.replace('REPORT_AUTHOR_GOES_HERE', str(report_author))
    report = report.replace('TOTAL_POSTS_GOES_HERE', str(total_posts))
    report = report.replace('TOTAL_AUTHORS_GOES_HERE', str(len(author_list)))
    report = report.replace('TOTAL_REWARDS_GOES_HERE', str(total_rewards))
    report = report.replace('AVERAGE_REWARDS_GOES_HERE', str(average_rewards))
    report = report.replace('TOTAL_BENEFICIARIES_GOES_HERE', str(len(beneficiaries)))
    report = report.replace('REPORT_GOES_HERE', str(main_report))

    steem=Steem(keys=report_author_key, node='wss://gtg.steem.house:8090') # instanciate again, for good measure
    
    """ steem.post(
              title=dated_report_title, 
              body=report, 
              author=report_author, 
              tags= report_tags, 
              beneficiaries = bene_list) 
    """

    print(report)
    
    print('\nBeneficiaries:\n##############\n' + str(bene_list))     

def job():
    try:
        report()
    except:
        time.sleep(10)
        report()

schedule.every().day.at('20:00').do(job)

while True:
    schedule.run_pending()
    time.sleep(10) 
