# The Jukebox From Hell

---

Just scrapes songs off the internet for you, nothing you couldn't have clicked on yourself. It doesn't read minds. If you ask for a title that is common or many versions, it usually just spits back the most popular. You may have to provide more information, just try again.

It also errors out and times out, and just plain fails. In the event that happens, please try again. There is no need to let me know about the failure because:
    a) I have logs.
    b) I don't care.
    You get what you pay for, and if you pay nothing? Well that is probably because you are the product.
    The cow doesn't get to complain how the steak gets served, moove along.

Shamlessly copied from the hard work MD5HashBrowns did on the [Apollo Cloud](https://raw.githubusercontent.com/MD5HashBrowns/apollo-cloud) 


What, you might ask, is Apollo Cloud?

Apollo Cloud is a Python Flask powered MP3 downloader webapp, built off of [Craicerjack's apache-flask docker image](https://hub.docker.com/r/craicerjack/apache-flask/) with a sprinkle of [youtube-dl](https://rg3.github.io/youtube-dl/) youtube-dl for some awesomeness. One challenge is maintaining the youtube-dl version as the web site is updated, but with this version the container updates itself on restart. 

I run two instances that take turns recycling themselves without even a blip in service.



Working with this code was both inspirational and educational. I used this as the basis of a test app that would accept bad input without any validation. I didn't even care if the app worked, I was just planning on using it for target practice in my security research. To my surprise, it not only works very well getting me music to dance to while we hack away, but it turned out to be incredibly reslient to the attacks. 

It inspired me to look closer at the application and sent me down an entirely new way of thinking about our infrastructure as dynamic code. It was always there, and apollo cloud helped me realize the potential, instead of seeing limits.
