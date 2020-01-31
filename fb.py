from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
from sys import exit
class FacebookPipe:
    def __init__(self, page_id, token):
        self.page_id = page_id
        self.token = token
        self.global_page_ids = []

    def get_recent_posts(self):
        """
        for FB PAGE
        Get the most recent 24 posts on an FB Page
        """
        posts_on_page = requests.get("https://graph.facebook.com/{}/posts?access_token={}".format(self.page_id, self.token))
        parsed_output = BeautifulSoup(posts_on_page.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        return json_data

    def get_posts_ids(self, posts):
        """
        for FB PAGE
        Get the ID's of all POSTS on a FB Page
        """
        posts_ids = []
        for ids in posts['data']:
            posts_ids.append(ids['id'])
        return posts_ids
    
    def get_all_post_ids(self, list_of_ids, index, next_page):
        """
        for FB Page
        Get all post ID's recurrsively. This function will add List's to the GLOBAL List
        ''global_page_ids''
        this will then be used by other functions
        """
        if index == 1:
            posts_on_page = requests.get("https://graph.facebook.com/%s/?fields=published_posts{id}&access_token=%s" % (self.page_id, self.token)) #Quick and dirty fix to FB's weird {} parameters in the URL {id} is not a variable, it's a URL paramter
            parsed_output = BeautifulSoup(posts_on_page.text, "html.parser")
            json_data = json.loads(parsed_output.get_text())
            list_of_ids.append(self._all_post_ids(json_data, 1))
            next_page = self._next_page_url(json_data)
            self.get_all_post_ids(list_of_ids, 2, next_page)
        else:
                posts_on_page = requests.get(next_page)
                parsed_output = BeautifulSoup(posts_on_page.text, "html.parser")
                json_data = json.loads(parsed_output.get_text())
                list_of_ids.append(self._all_post_ids(json_data, 2))
                page_recursive = self._next_page_url(json_data)
                last_id_on_page = self._all_post_ids(json_data, 2)
                try:
                    paging = json_data['data'][0]
                    self.get_all_post_ids(list_of_ids,2, page_recursive)
                except IndexError:
                    self.global_page_ids = list_of_ids
                    return
     
    def _next_page_url(self, json_data):
        if json_data.get('published_posts'):
            return json_data['published_posts']['paging']['next']
        elif json_data.get('paging'):
            return json_data['paging']['next']
        elif json_data.get('error'):
            exit("Key not valid? \r\nREASON: {}".format(json_data['error']['message']))

    def _all_post_ids(self, json_data, index):
        """
        Internal function used in get_all_post_ids to get the ID's of all the posts on the page
        """
        if index == 1:
            all_post_ids = []
            try:
                for items in range(0, len(json_data['published_posts']['data'])):
                    all_post_ids.append(json_data['published_posts']['data'][items]['id'])
            except(KeyError):
                all_post_ids = []
        else:
            all_post_ids = []
            try:
                for items in range(0, len(json_data['data'])):
                    all_post_ids.append(json_data['data'][items]['id'])
            except(KeyError):
                all_post_ids = []
        return all_post_ids
     
    def get_page_engaged_users(self):
        """
        For FB PAGE
        Gets the number of engaged users (Needs a page token)
        """
        page_engaged_users = requests.get("https://graph.facebook.com/{}/insights/page_engaged_users?access_token={}".format(self.page_id, self.token))
        return page_engaged_users.json()

    def get_page_fans(self):
        """
        For FB PAGE
        Gets the number of fans / likes of a page
        """
        page_engaged_users = requests.get("https://graph.facebook.com/{}/insights/page_fans?access_token={}".format(self.page_id, self.token))
        return page_engaged_users.json()
    
    def get_page_impressions_unique(self):
        """
        For FB PAGE
        Gets the number of impressions (unuque) (Needs a page token)
        """
        page_unique_users = requests.get("https://graph.facebook.com/{}/insights/page_impressions_unique?access_token={}".format(self.page_id, self.token))
        return page_unique_users.json()

    def get_post_reactions_count(self, post_id):
        """
        for FB POST
        Get total reactions for a post
        """
        post_likes = requests.get("https://graph.facebook.com/{}/likes?summary=total_count&access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_likes.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError, IndexError):
            return 0

    def get_post_reactions_by_type_total(self, post_id): 
        """
        for FB POST
        breakdown of all reactions by type, retuned as ditionary
        """   
        post_reactions = requests.get("https://graph.facebook.com/{}/insights/post_reactions_by_type_total?access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_reactions.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0

    def get_post_activity_by_action_type(self, post_id):
        """
        for FB POST
        Get number of Shares, Likes Comments
        """
        post_activity = requests.get("https://graph.facebook.com/{}/insights/post_activity_by_action_type?access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_activity.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0

    def get_post_clicks_by_types(self, post_id):
        """
        for FB POST
        Get types of clicks: Link Clicks, Other Clicks, Photo Clicks, etc.
        """
        post_clicks = requests.get("https://graph.facebook.com/{}/insights/post_clicks_by_type?access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_clicks.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0
    
    def get_posts_impressions_unique(self, post_id):
        """
        for FB POST
        Return the number of unique impressions a post has
        """
        post_shared = requests.get("https://graph.facebook.com/{}/insights?metric=post_impressions_unique&access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_shared.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0
    
    def get_post_date(self, post_id):
        """
        for FB POST
        Return the date a post was made
        """
        post_created = requests.get("https://graph.facebook.com/{}/?access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_created.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            date = json_data['created_time'].split('T')
            return date[0]
        except(KeyError):
            return 0

    def get_page_impressions_paid(self, post_id):
        """
        for FB POST
        Return the number of impressions sent by ads
        """
        post_shared = requests.get("https://graph.facebook.com/{}/insights?metric=post_impressions_paid&access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_shared.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0
        
    def get_page_posts_impressions_organic_unique(self, post_id):
        """
        for FB POST
        Get the unique impressions a post received organically
        """
        post_shared = requests.get("https://graph.facebook.com/{}/insights?metric=post_impressions_organic_unique&access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_shared.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0

    def get_page_video_views_organic(self, post_id):
        """
        for FB POST
        Get the unique impressions a video received organically
        """
        post_shared = requests.get("https://graph.facebook.com/{}/insights?metric=post_video_views_organic&access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_shared.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0
    
    def get_page_video_views_paid(self, post_id):
        """
        for FB POST
        Get the unique impressions a video received by ads
        """
        post_shared = requests.get("https://graph.facebook.com/{}/insights?metric=post_video_views_paid&access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_shared.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0

    def get_page_video_views(self, post_id):
        """
        for FB POST
        Get the total video views
        """
        post_video_views = requests.get("https://graph.facebook.com/{}/insights?metric=post_video_views&access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_video_views.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0
    
    def get_post_video_complete_views_paid(self, post_id):
        """
        How many paid views completed the video
        """
        post_video_views = requests.get("https://graph.facebook.com/{}/insights/post_video_complete_views_paid?access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_video_views.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0

    def get_post_video_complete_views_organic(self, post_id):
        """
        How many organic views completed the video
        """
        post_video_views = requests.get("https://graph.facebook.com/{}/insights/post_video_complete_views_organic?access_token={}".format(post_id, self.token))
        parsed_output = BeautifulSoup(post_video_views.text, "html.parser")
        json_data = json.loads(parsed_output.get_text())
        try:
            return json_data['data'][0]['values'][0]['value']
        except(KeyError):
            return 0
    
    def get_video_conversion_rate(self, post_id):
        """
        get the conversion rate of a videos views by paid traffic
        """
        try:
            conversion_rate = int(self.get_post_video_complete_views_paid) / int(self.get_post_video_complete_views_organic)
            return conversion_rate
        except(TypeError):
            return 0

    def fetch_posts_by_date(self, date):
        """
        Fetches the date of all FB Posts via IDS
        returns pruned output lists by date
        """
        output_list = []
        end_date = date.split("-")

        for arrays in self.global_page_ids:
            for post_id in arrays:
                post_date = self.get_post_date(post_id).split("-")
                if  datetime(int(post_date[0]), int(post_date[1]), int(post_date[2])) >=  datetime(int(end_date[0]), int(end_date[1]), int(end_date[2])):
                    output_list.append(post_id)
                else:
                    break
        print("found {} posts that match the timeframe for {}".format(len(output_list), date))
        return output_list

    def build_object(self, data):
        """
        Turns every ID in data into a JSON object using the methods above.
        saves to ''output_list''.
        """
        output_list = []
        for items in data:
            _object = {}
            _object['post_id'] = items
            _object['date'] = self.get_post_date(items)
            _object['post_reactions_count'] = self.get_post_reactions_count(items)
            _object['post_reactions_by_type_total'] = self.get_post_reactions_by_type_total(items)
            _object['post_activity_by_action_type'] = self.get_post_activity_by_action_type(items)
            _object['get_post_clicks_by_types'] = self.get_post_clicks_by_types(items)
            _object['posts_impressions_unique'] = self.get_posts_impressions_unique(items)
            _object['page_impressions_paid'] = self.get_page_impressions_paid(items)
            _object['page_posts_impressions_organic_unique'] = self.get_page_posts_impressions_organic_unique(items)
            _object['page_video_views_organic'] = self.get_page_video_views_organic(items)
            _object['page_video_views_paid'] = self.get_page_video_views_paid(items)
            _object['page_video_views'] = self.get_page_video_views(items)
            _object['post_video_complete_views_paid'] = self.get_post_video_complete_views_paid(items)
            _object['post_video_complete_views_organic'] = self.get_post_video_complete_views_organic(items)
            _object['video_conversion_rate'] = self.get_video_conversion_rate(items)
            json_data = json.dumps(_object)
            output_list.append(json_data)
            print("{} - spidered".format(items))
        return output_list

fb = FacebookPipe('', '')

fb.get_all_post_ids([], 1, "")
fb.build_object(fb.fetch_posts_by_date("2018-06-10"))
