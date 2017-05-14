from piston.steem import Steem
from piston.blockchain import Blockchain
from piston.account import Account
from piston.account import Amount
from piston.utils import parse_time
from piston.post import Post
import time
import datetime
import schedule

account = Account("deutschbot")

def bericht():

    steem = Steem(node="wss://gtg.steem.house:8090")

    main_report = ("|| Autor | Beitrag | $$$ |\n"+
               "| --- | --- | --- | --- |\n")
    
    trailing_in_minutes=1440
    total_rewards = 0
    total_posts = 0
    trailing_time = time.time() - datetime.timedelta(minutes=trailing_in_minutes).total_seconds()

    stoptime = time.time()
    starttime = trailing_time

    for i in account.history2(filter_by="vote", take=100000):

        timestamp = parse_time(i['timestamp']).timestamp()

        if timestamp > trailing_time:

            if i["voter"]=="deutschbot":


                link=str("@"+i["author"]+"/"+i["permlink"])
                full_link=("https://steemit.com/tag/" + link)
                post=Post(link)
                reward=(Amount(post.get("total_payout_value")) + Amount(post.get("pending_payout_value")))
                total_posts = total_posts + 1
                tags = (post["json_metadata"].get("tags", []))
                category = post.category
             
                if post.is_main_post() and not i["author"] == "deutschbot":

                    if "deutsch" in tags or "deutsch" in category:

                        if total_rewards == 0:

                            total_rewards = reward

                        else:

                            total_rewards = total_rewards + reward

                        try:
                            imagelink =  post["json_metadata"].get("image")[0]
                                            
                        except:

                            imagelink = "https://steem.io/images/steem.png"
            
                       if len(imagelink) > 100:

                            imagelink = "https://steem.io/images/steem.png"

                        image=("![main_image](https://img1.steemit.com/128x256/" + imagelink +")")
            
                        post_title = (post["title"])

                        if len(post_title) > 30:

                            post_title = post_title[:30] + " ..." 

                        if "|" in post_title:
         
                            post_title = post_title.replace("|", ";")

                        main_report = (main_report + image + "|@" +
                                       i["author"] +"|["+ post_title + "](" + full_link + ")|" + str(reward) +"\n")
 
    date = time.strftime("%d.%m.%Y", time.localtime(stoptime))
    starttime = time.strftime("%d.%m.%Y, %H:%M Uhr", time.localtime(starttime))
    stoptime = time.strftime("%d.%m.%Y, %H:%M Uhr", time.localtime(stoptime))
    a = Amount(total_rewards)    
    average_rewards = a * (1/total_posts)

    with open("header.txt") as readheader:
        header = readheader.read() 

    with open("footer.txt") as readfooter:
        footer = readfooter.read() 

    description = "Alle posts, die @deutschbot mochte, vom "+str(starttime)+" bis zum "+str(stoptime)+
                  ". In dieser Zeit wählte @deutschbot "+str(total_posts)+" Beiträge. Die Beiträge erhielten bisher insgesamt "+
                  str(total_rewards)+" als _potentielle_ Auszahlung, mit durchschnittlich "+str(average_rewards)+" pro Beitrag.\n___\n"


    report = header + "\n" + description + main_report + "\n___\n" + footer

    print(report)
    
    deutschtitle= ("@deutschbot's täglicher Bericht: "+str(date))

#uncomment this to post automatically:
    #steem=Steem(keys="postingkeyhere",node="wss://gtg.steem.house:8090")
    #steem.post(title=deutschtitle, body=report, author="deutschbot", category="deutsch", tags=["deutschbot"])

schedule.every().day.at("20:00").do(bericht)

while True:
    schedule.run_pending()
    time.sleep(10) # wait 10 secs
