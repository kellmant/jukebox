# coding=utf-8

import youtube_dl
from flask import render_template, flash, redirect, session, url_for, request, g, Markup
from app import app
app.debug = True





@app.route('/')
def index():
    return render_template('index.html')


@app.route('/downloading/', methods=['POST'])
def data():
    url = request.form['url']
    if "youtube.com" not in url:
	thesearch = url + " audio"
    ytdl_options = { 'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '128',}],'default_search': 'auto','quiet': 'off', 'outtmpl': '/var/www/apollo-cloud/app/static/songs/' + url + ".webm"}
    with youtube_dl.YoutubeDL(ytdl_options) as ytdl:
        ytdl.download([thesearch])
    return render_template('downloading.html', url = url)

@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/DMCA')
def DMCA():
   return render_template('DMCA.html')
    






