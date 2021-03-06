######################################################################################
#
#	OnlineMovies.Pro - v0.01
#
######################################################################################

TITLE = "OnlineMovies.pro"
PREFIX = "/video/onlinemoviespro"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"
BASE_URL = "http://onlinemovies.pro"
CATEGORY_URL = "http://onlinemovies.pro/category"
CATEGORIES_URL = "http://onlinemovies.pro/categories/"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_COVER)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_COVER)
	VideoClipObject.art = R(ART)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36"
	HTTP.Headers['Referer'] = "http://onlinemovies.pro/"
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	channel_page = HTML.ElementFromURL(CATEGORIES_URL)
	channels = channel_page.xpath("//ul[@class='listing-cat']/li")
	for each in channels:
		url = each.xpath("./a/@title")[0]
		title = each.xpath("./a/@title")[0]
		thumb = each.xpath("./img/@src")[0]
		url = url.replace('%2b','-')
		url = url.replace(' ', '-')
		oc.add(DirectoryObject(key = Callback(ShowCategory, title = title, category = url, page_count = 1), title = title, thumb = thumb))
	oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.onlinemoviespro', title='Search', summary='Search Movies on OnlineMovies.Pro', prompt='Search for...'))

	return oc

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	if str(page_count) == "1":
		page_data = HTML.ElementFromURL(CATEGORY_URL + '/' + str(category) + '/?filtre=date')
	else:
		page_data = HTML.ElementFromURL(CATEGORY_URL + '/' + str(category) + '/page/' + str(page_count) + '/')

	for each in page_data.xpath("//ul[@class='listing-videos listing-tube']/li"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./img/@alt")[0]
		thumb = each.xpath("./img/@src")[0]

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
			)
		)

	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = category, category = category, page_count = int(page_count) + 1),
		title = "Next...",
		thumb = R(ICON_NEXT)
			)
		)
	
	return oc

######################################################################################
# Gets metadata and google docs link from episode page. Checks for trailer availablity.

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):
	
	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(url)
	title = page_data.xpath("//div[@id='video']/h1/span/text()")[0]
	thumb = page_data.xpath("//div[@id='video']/meta/@content")

	#load recursive iframes to find google docs url
	try:
		first_frame_url = page_data.xpath("//div[@class='video-embed']/iframe/@src")[0]
	except:
		return ObjectContainer(header="Error", message="Unfortunately this video is unavailable")
	
	oc.add(VideoClipObject(
		url = first_frame_url,
		title = title,
		thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-movies.png')
		)
	)	
	
	return oc